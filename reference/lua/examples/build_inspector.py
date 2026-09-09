"""Build a read-only inspection script from the installed reacli entry template.

Run from a repository checkout after installing reacli and Lua 5.3 or 5.4:
    python reference/lua/examples/build_inspector.py ./inspect-project.lua
This writes a new script, performs syntax validation, and never starts REAPER.
"""
from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path

from rac.luagen import validate
from rac.resources import read_text


def build(output: Path) -> Path:
    """Reuse the installed skeleton while refusing to overwrite an output."""
    body = Path(__file__).with_name("inspect_project.body.lua").read_text(
        encoding="utf-8"
    )
    template = read_text("lua/entry.lua")
    script, count = re.subn(
        r"local function body\(\).*?\nend(?=\n-- ={10,})",
        lambda _: body.rstrip(),
        template,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError("The entry template changed; review its body boundary")
    # Check syntax before creating the requested output, leaving no partial file.
    with tempfile.TemporaryDirectory(prefix="reacli-inspector-") as directory:
        staged = Path(directory) / "inspect-project.lua"
        staged.write_text(script, encoding="utf-8")
        validate(staged)
        with output.open("x", encoding="utf-8") as destination:
            destination.write(script)
    return output.resolve()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(build(args.output))


if __name__ == "__main__":
    main()
