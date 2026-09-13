"""Read bundled assets independently of the working directory or source checkout."""
from importlib.resources import files
from pathlib import Path


def asset(name: str):
    """Return a read-only Traversable under the package's data directory."""
    parts = name.split("/")
    if not name or any(p in ("", ".", "..") or "\\" in p for p in parts):
        raise ValueError("asset name must be a relative POSIX path without '..'")
    return files("rac").joinpath("data", *parts)


def read_text(name: str) -> str:
    return asset(name).read_text(encoding="utf-8")


def export_resources(destination: str | Path) -> Path:
    """Export Lua templates and an example project, refusing to overwrite files."""
    destination = Path(destination).expanduser().resolve()
    contents = {"entry.lua": asset("lua/entry.lua"),
                "minimal.rpp": asset("examples/minimal.rpp")}
    contents.update({"stdlib/" + p.name: p for p in asset("lua/stdlib").iterdir()
                     if p.is_file() and p.name.endswith(".lua")})
    for name in contents:
        if (destination / name).exists():
            raise FileExistsError(f"Refusing to overwrite {destination / name}")
    for name, source in contents.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(source.read_bytes())
    return destination
