"""Build and verify independent candidates; never uploads or changes repository visibility."""

from __future__ import annotations
import argparse, hashlib, importlib.util, json, shutil, subprocess, sys, tarfile, zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath

ROOT = Path(__file__).resolve().parents[1]


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(*args):
    subprocess.run(args, cwd=ROOT, check=True)


def _unsafe_archive_member(name):
    """Reject traversal and absolute names on both POSIX and Windows."""
    posix = PurePosixPath(name)
    windows = PureWindowsPath(name)
    return (
        bool(posix.anchor or windows.anchor)
        or ".." in posix.parts
        or ".." in windows.parts
    )


def zip_files(path, files, roots=()):
    raw_roots = tuple(Path(root) for root in roots)
    if any(root.is_symlink() for root in raw_roots):
        raise ValueError("ZIP source root must not be a symlink")
    roots = tuple(root.resolve() for root in raw_roots)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, p in sorted(files):
            if _unsafe_archive_member(name):
                raise ValueError(f"Unsafe ZIP member path: {name}")
            if p.is_symlink() or not p.is_file():
                raise ValueError(f"ZIP source must be a regular non-symlink file: {p}")
            resolved = p.resolve()
            if roots and not any(resolved == root or root in resolved.parents for root in roots):
                raise ValueError(f"ZIP source escapes its source root: {p}")
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, p.read_bytes())


def _source_files(root: Path):
    """Yield regular files and fail closed on any symlink in a release root."""
    requested = Path(root)
    if requested.is_symlink():
        raise ValueError(f"Release source root must not be a symlink: {requested}")
    root = requested.resolve()
    for p in root.rglob("*"):
        if p.is_symlink():
            raise ValueError(f"Release source root contains a symlink: {p}")
        if p.is_file():
            yield p


def verify_parser(directory):
    wheels = list(directory.glob("*.whl"))
    sdists = list(directory.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise ValueError("Expected one parser wheel and sdist")
    source = ROOT / "packages/reaper-parser/src"
    runtime = {
        p.relative_to(source).as_posix(): p.read_bytes()
        for p in (source / "reaper_parser").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }
    with zipfile.ZipFile(wheels[0]) as z:
        names = z.namelist()
        if any(_unsafe_archive_member(n) for n in names):
            raise ValueError("Unsafe wheel path")
        actual = {n: z.read(n) for n in names if n.startswith("reaper_parser/")}
        if actual != runtime:
            raise ValueError("Parser wheel runtime differs from source")
        metadata = z.read(next(n for n in names if n.endswith("/METADATA"))).decode()
        if "Requires-Dist: rac" in metadata or "Requires-Dist: numpy" in metadata:
            raise ValueError("Parser core has unwanted dependency")
    with tarfile.open(sdists[0]) as tar:
        members = tar.getmembers()
        prefix = members[0].name.split("/")[0] + "/"
        if any(
            not (m.isfile() or m.isdir())
            or _unsafe_archive_member(m.name)
            or not (m.name == prefix[:-1] or m.name.startswith(prefix))
            for m in members
        ):
            raise ValueError("Unsafe parser sdist")
        actual = {
            m.name[len(prefix + "src/") :]: tar.extractfile(m).read()
            for m in members
            if m.isfile() and m.name.startswith(prefix + "src/reaper_parser/")
        }
        if actual != runtime:
            raise ValueError("Parser sdist runtime differs from source")
    return {"runtime_files_verified": len(runtime)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    out = a.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    run(sys.executable, "tools/generate_schema.py", "--check")
    run("npm", "run", "check", "--prefix", "apps/reaperdoc")
    run("npm", "run", "build", "--prefix", "apps/reaperdoc")
    for package in ("reaper-parser", "reacli"):
        run(
            sys.executable,
            "-m",
            "build",
            str(ROOT / "packages" / package),
            "--outdir",
            str(out / package),
        )
        run(
            sys.executable,
            "-m",
            "twine",
            "check",
            *[str(p) for p in sorted((out / package).iterdir())],
        )
    spec = importlib.util.spec_from_file_location(
        "checker", ROOT / "scripts/check_dist.py"
    )
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    checks = {
        "reaper-parser": verify_parser(out / "reaper-parser"),
        "reacli": checker.check_dist(out / "reacli", ROOT / "packages/reacli"),
    }
    agent = ROOT / "integrations/agents/reaper-agent-cli"
    agent_root = agent.resolve()
    files = [
        ("reaper-agent-cli/" + p.relative_to(agent_root).as_posix(), p)
        for p in _source_files(agent)
        if "__pycache__" not in p.parts and p.suffix != ".pyc" and p.name != "runtime.json"
    ]
    files.extend(
        ("reaper-agent-cli/examples/" + name, ROOT / "examples" / name)
        for name in ("create_project.py", "data_roundtrip.py")
    )
    zip_files(out / "reaper-agent-cli.zip", files, [agent, ROOT / "examples"])
    site = ROOT / "apps/reaperdoc/dist"
    if not (site / "index.html").is_file():
        raise ValueError("Build ReaperDoc before building a candidate")
    zip_files(
        out / "reaperdoc-site.zip",
        [(p.relative_to(site).as_posix(), p) for p in _source_files(site)]
        + [(name, ROOT / "apps/reaperdoc" / name)
           for name in ("LICENSE", "THIRD_PARTY_NOTICES.md")],
        [site, ROOT / "apps/reaperdoc"],
    )
    shutil.copyfile(ROOT / "schema/rpp/generated/runtime.json", out / "rpp-schema.json")
    for name in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
        shutil.copyfile(ROOT / "schema/rpp" / name, out / ("rpp-schema-" + name))
    shutil.copyfile(ROOT / "docs/ecosystem/publication.json", out / "publication.json")
    zip_files(
        out / "examples.zip",
        [
            (p.name, p)
            for p in [
                ROOT / "examples/data_roundtrip.py",
                ROOT / "examples/create_project.py",
            ]
        ],
        [ROOT / "examples"],
    )
    if (ROOT / "docs/ecosystem/README.md").exists():
        shutil.copyfile(ROOT / "docs/ecosystem/README.md", out / "README.md")
    meta = json.loads((out / "rpp-schema.json").read_text())["meta"]
    manifest = {
        "status": "candidate; publication prerequisites recorded separately",
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "working_tree_dirty": bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=ROOT, text=True
            ).strip()
        ),
        "schema": meta,
        "compatibility": json.loads((agent / "compatibility.json").read_text()),
        "checks": checks,
        "artifacts": [
            {
                "file": p.relative_to(out).as_posix(),
                "bytes": p.stat().st_size,
                "sha256": digest(p),
            }
            for p in sorted(out.rglob("*"))
            if p.is_file()
        ],
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("Candidate verified:", out)


if __name__ == "__main__":
    main()
