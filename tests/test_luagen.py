import hashlib
import math
import shutil
import subprocess

import pytest
from rac.environment import EnvironmentError, find_luac
from rac.luagen import generate, validate
from rac.luagen.generator import _lua_literal


@pytest.fixture
def compiler():
    try:
        return find_luac()
    except EnvironmentError:
        pytest.skip("Lua compiler not installed")


def test_generated_script_behavior_anchor(tmp_path, compiler):
    script = generate({"ops": [{"op": "track.create", "args": [0, "anchor"]}]}, tmp_path / "anchor.lua")
    assert hashlib.sha256(script.read_bytes()).hexdigest() == "2661c07f0ac580fb76274ee5b7149c4781d6ad8f7af50771daf734b0dc81b990"


def test_strings_controls_and_table_keys_are_valid_lua(tmp_path, compiler):
    values = ['中文 "quote" \\ newline\n\t\b\f\x007', {"not-an-identifier": "x"}]
    script = tmp_path / "literals.lua"
    script.write_text("local values = " + _lua_literal(values), encoding="utf-8")
    validate(script, luac_bin=compiler)


@pytest.mark.parametrize("args", [[0, True], [0, math.nan], [0, math.inf]])
def test_invalid_numeric_argument_rejected_before_compiler(args, tmp_path):
    with pytest.raises((TypeError, ValueError)):
        generate({"ops": [{"op": "track.set_volume_db", "args": args}]}, tmp_path / "bad.lua")


def test_modules_cannot_escape_package(tmp_path):
    with pytest.raises(ValueError, match="module"):
        generate({"modules": ["../../arbitrary"]}, tmp_path / "bad.lua")


def test_implicit_output_paths_unique(compiler):
    first = generate({"ops": []})
    second = generate({"ops": []})
    try:
        assert first != second
        assert first.read_bytes() == second.read_bytes()
    finally:
        first.unlink()
        second.unlink()


def test_invalid_script_raises_syntax_error(tmp_path, compiler):
    bad = tmp_path / "bad.lua"
    bad.write_text("local x = )")
    with pytest.raises(SyntaxError):
        validate(bad, luac_bin=compiler)
