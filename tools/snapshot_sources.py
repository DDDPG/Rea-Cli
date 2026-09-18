"""Record source manifests and recoverable archives; excludes caches and environments."""

import argparse, hashlib, json, os, subprocess, tarfile
from pathlib import Path

EXCLUDE = {
    ".git",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".state",
    "dist",
    "build",
    "demo",
    "smoke-artifacts",
    "runs",
    "workers",
    ".DS_Store",
}


def snapshot(root, out):
    files = []
    for base, dirs, names in os.walk(root):
        dirs[:] = sorted(
            d for d in dirs if d not in EXCLUDE and not d.startswith(".venv")
        )
        for name in sorted(names):
            p = Path(base) / name
            if name in EXCLUDE or name.startswith(".env") or p.is_symlink():
                continue
            data = p.read_bytes()
            files.append(
                {
                    "path": p.relative_to(root).as_posix(),
                    "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                }
            )

    def git(*args):
        p = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, text=True
        )
        return p.stdout if p.returncode == 0 else None

    out.mkdir(parents=True, exist_ok=True)
    diff = git("diff", "--binary", "HEAD")
    if diff is not None:
        (out / "working-tree.patch").write_text(diff)
    manifest = {
        "source": str(root),
        "commit": git("rev-parse", "HEAD"),
        "status": git("status", "--porcelain"),
        "files": files,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    with tarfile.open(out / "source.tar.gz", "w:gz") as tar:
        for f in files:
            tar.add(root / f["path"], arcname=f["path"], recursive=False)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("sources", nargs="+", type=Path)
    a = parser.parse_args()
    for root in a.sources:
        m = snapshot(root.resolve(), a.output / root.name)
        print(root.name, len(m["files"]))
