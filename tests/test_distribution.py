"""Tests run against the installed package, including when installed from a wheel."""
import importlib.metadata
import json
import subprocess
import sys

import pytest
import rac
from rac.resources import export_resources
from rac.rpp import parse, schema
from rac.verify.semantics import semantic_diff


def test_distribution_import_contract():
    assert importlib.metadata.version("reacli") == rac.__version__
    assert rac.__name__ == "rac"


def test_resource_data_outside_checkout(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    export_resources(tmp_path / "templates")
    project = parse(tmp_path / "templates/minimal.rpp")
    assert semantic_diff(project, parse(project.text())) == []
    assert schema.key_meta("track", "VOLPAN")
    assert len(list((tmp_path / "templates/stdlib").glob("*.lua"))) == 11
    with pytest.raises(FileExistsError):
        export_resources(tmp_path / "templates")


@pytest.mark.parametrize("args,code", [
    (["--help"], 0), (["--version"], 0),
    (["doctor", "--profile", "offline", "--json"], 0),
    (["knowledge", "rpp", "track:VOLPAN"], 0),
    (["knowledge", "api", "GetTrack"], 0),
    (["knowledge", "api", "NonexistentFunction"], 2),
    (["verify", "audio"], 2),
    (["rpp", "validate", "missing.rpp"], 4),
])
def test_cli_outside_checkout(tmp_path, args, code):
    p = subprocess.run([sys.executable, "-I", "-m", "rac", *args],
                       cwd=tmp_path, capture_output=True, text=True, timeout=20)
    assert p.returncode == code, p.stdout + p.stderr
    assert "Traceback" not in p.stderr
    if args[0] not in {"--help", "--version"}:
        assert isinstance(json.loads(p.stdout), dict)


def test_console_entry_points():
    scripts = {e.name: e.value for e in importlib.metadata.distribution("reacli").entry_points}
    assert scripts["reacli"] == scripts["rac"] == "rac.__main__:main"


def test_typo_in_audio_assertion_is_rejected(capsys):
    from rac.__main__ import main
    assert main(["verify", "audio", "missing.wav", "duraton=3"]) == 2
    assert "Unknown audio" in capsys.readouterr().out


def test_pool_guard_is_a_structured_cli_error(monkeypatch, capsys):
    from rac import __main__ as cli
    from rac.runner.pool import PoolBlocked
    def blocked(args):
        raise PoolBlocked("blocked:output_conflict")
    monkeypatch.setattr(cli, "cmd_pool_exec", blocked)
    assert cli.main(["pool", "exec"]) == 4
    assert "blocked:output_conflict" in json.loads(capsys.readouterr().out)["error"]
