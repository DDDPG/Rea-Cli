#!/usr/bin/env python3
"""Check wheel/sdist contents and versions without installing or extracting them.

Run from a source checkout: python scripts/check_dist.py dist
"""
from __future__ import annotations

import argparse
import ast
from email.parser import BytesParser
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import tarfile
import zipfile


FORBIDDEN_PARTS = {
    "reference", ".git", "__pycache__", ".pytest_cache", ".state",
    "runs", "workers", "smoke-artifacts", ".DS_Store", "REAPER.app",
}
SUPPLEMENTAL_FILES = {
    "actions_index.json", "api_pitfalls.json", "jsfx_reference.json",
    "source-manifest.json", "inspect_project.body.lua", "build_inspector.py",
    "gain_simple.jsfx", "delay_basic.jsfx", "midi_monitor.jsfx",
}
RUNTIME_SUFFIXES = {".py", ".lua", ".json", ".ini", ".rpp"}


def check_members(names: list[str]) -> None:
    """Reject repository-only payload, unsafe paths and duplicate members."""
    if len(names) != len(set(names)):
        raise ValueError("Duplicate archive members")
    for name in names:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name:
            raise ValueError(f"Unsafe archive path: {name}")
        if (FORBIDDEN_PARTS.intersection(path.parts)
                or any(part.startswith(".venv") or part.startswith(".env")
                       for part in path.parts)
                or path.name in SUPPLEMENTAL_FILES
                or path.suffix in {".pyc", ".pyo"}):
            raise ValueError(f"Excluded payload in archive: {name}")


def source_version(root: Path) -> str:
    """Read the same literal version used by setuptools' dynamic metadata."""
    tree = ast.parse((root / "src/rac/__init__.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "__version__"
                for target in node.targets):
            value = ast.literal_eval(node.value)
            if isinstance(value, str):
                return value
    raise ValueError("src/rac/__init__.py must define a literal __version__")


def check_metadata(content: bytes, version: str) -> None:
    metadata = BytesParser().parsebytes(content)
    if metadata["Name"] != "reacli" or metadata["Version"] != version:
        raise ValueError(f"Metadata mismatch: {metadata['Name']} {metadata['Version']}; expected reacli {version}")


def check_dist(directory: Path, root: Path) -> dict:
    wheels = sorted(directory.glob("*.whl"))
    sdists = sorted(directory.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise ValueError("Expected exactly one wheel and one sdist; use a fresh output directory")
    version = source_version(root)
    runtime = {
        file.relative_to(root / "src").as_posix(): file.read_bytes()
        for file in (root / "src/rac").rglob("*")
        if file.is_file() and file.suffix in RUNTIME_SUFFIXES
    }
    if not runtime:
        raise ValueError("No runtime files found in source checkout")
    wheel, sdist = wheels[0], sdists[0]
    if wheel.name != f"reacli-{version}-py3-none-any.whl" or sdist.name != f"reacli-{version}.tar.gz":
        raise ValueError("Distribution filenames do not match the source version/platform-independent package")

    with zipfile.ZipFile(wheel) as archive:
        check_members(archive.namelist())
        if any(info.create_system == 3 and stat.S_IFMT(info.external_attr >> 16)
               not in (0, stat.S_IFREG, stat.S_IFDIR) for info in archive.infolist()):
            raise ValueError("Wheel contains links or special files")
        prefix = f"reacli-{version}.dist-info/"
        check_metadata(archive.read(prefix + "METADATA"), version)
        payload = {name for name in archive.namelist()
                   if name.startswith("rac/") and not name.endswith("/")}
        if payload != set(runtime):
            raise ValueError("Wheel runtime file set differs from source checkout")
        for name, content in runtime.items():
            if archive.read(name) != content:
                raise ValueError(f"Wheel differs from source: {name}")
        for name in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
            if archive.read(prefix + "licenses/" + name) != (root / name).read_bytes():
                raise ValueError(f"Wheel license differs from source: {name}")

    with tarfile.open(sdist, "r:gz") as archive:
        members = archive.getmembers()
        check_members([member.name for member in members])
        prefix = f"reacli-{version}/"
        if any(not (member.name == prefix.rstrip("/") or member.name.startswith(prefix))
               or not (member.isfile() or member.isdir()) for member in members):
            raise ValueError("sdist contains unexpected roots, links or special files")

        def read(name: str) -> bytes:
            stream = archive.extractfile(prefix + name)
            if stream is None:
                raise ValueError(f"Missing file in sdist: {name}")
            return stream.read()

        check_metadata(read("PKG-INFO"), version)
        payload = {member.name[len(prefix + "src/"):]
                   for member in members
                   if member.isfile() and member.name.startswith(prefix + "src/rac/")}
        if payload != set(runtime):
            raise ValueError("sdist runtime file set differs from source checkout")
        for name, content in runtime.items():
            if read("src/" + name) != content:
                raise ValueError(f"sdist differs from source: {name}")
        for name in ("pyproject.toml", "LICENSE", "THIRD_PARTY_NOTICES.md",
                     "README.md", "README.zh-CN.md", "CONTRIBUTING.md", "SECURITY.md",
                     "scripts/check_dist.py", "tests/test_distribution.py"):
            if read(name) != (root / name).read_bytes():
                raise ValueError(f"sdist differs from source: {name}")

    return {
        "ok": True, "version": version, "runtime_files_verified": len(runtime),
        "supplemental_reference_included": False,
        "artifacts": [{"file": path.name, "bytes": path.stat().st_size,
                       "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                      for path in (wheel, sdist)],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", type=Path, default=Path("dist"))
    args = parser.parse_args()
    try:
        result = check_dist(args.directory, Path(__file__).resolve().parents[1])
    except (OSError, ValueError, KeyError, tarfile.TarError, zipfile.BadZipFile) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
