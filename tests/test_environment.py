import os
import subprocess
from pathlib import Path

import pytest
from rac import environment as E
from rac.runner import platform as P


def test_offline_does_not_probe_external_programs(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Offline profile launched an external probe")
    monkeypatch.setattr(E.subprocess, "run", forbidden)
    monkeypatch.setattr(E.shutil, "which", forbidden)
    assert E.doctor(profile="offline")["ok"]


def test_missing_reaper_and_display_are_actionable(monkeypatch, tmp_path):
    monkeypatch.setattr(P, "IS_LINUX", True)
    monkeypatch.setattr(P, "IS_MAC", False)
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("RAC_NO_XVFB", raising=False)
    monkeypatch.setattr(E.shutil, "which", lambda _: None)
    report = E.doctor(profile="runner", reaper_bin="missing", resource=tmp_path / "not-created")
    assert not report["ok"]
    checks = {c["name"]: c for c in report["checks"]}
    assert checks["reaper"]["status"] == "error"
    assert checks["xauth"]["status"] == "error"
    assert not (tmp_path / "not-created").exists()


def test_compiler_discovery_versioned(monkeypatch):
    monkeypatch.delenv("RAC_LUAC_BIN", raising=False)
    monkeypatch.setattr(E.shutil, "which", lambda value: "/usr/bin/luac5.4" if value == "luac5.4" else None)
    monkeypatch.setattr(E.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0, "", "Lua 5.4.4"))
    assert E.find_luac() == "/usr/bin/luac5.4"


@pytest.mark.parametrize("version", ["Lua 5.1.5", "Lua 5.2.4", "not a compiler"])
def test_old_or_invalid_lua_rejected(monkeypatch, version):
    monkeypatch.setattr(E.shutil, "which", lambda _: "/usr/bin/luac")
    monkeypatch.setattr(E.subprocess, "run", lambda *a, **k: subprocess.CompletedProcess(a, 0, version, ""))
    with pytest.raises(E.EnvironmentError, match="5.3 or 5.4"):
        E.find_luac("luac")


def test_missing_explicit_compiler_does_not_fallback(monkeypatch):
    monkeypatch.setattr(E.shutil, "which", lambda value: None if value == "bad" else "/usr/bin/luac5.4")
    with pytest.raises(E.EnvironmentError, match="bad"):
        E.find_luac("bad")


def test_headless_missing_xauth_fails_before_launch(monkeypatch):
    monkeypatch.setattr(P, "IS_LINUX", True)
    monkeypatch.setattr(P, "IS_MAC", False)
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("RAC_NO_XVFB", raising=False)
    monkeypatch.setattr(P.shutil, "which", lambda value: None if value == "xauth" else value)
    with pytest.raises(E.EnvironmentError, match="xauth"):
        P.build_command("reaper", "project.rpp")


def test_ini_repairs_actual_sections_and_preserves_custom_values(tmp_path, monkeypatch):
    monkeypatch.setattr(P, "IS_LINUX", True)
    monkeypatch.setattr(P, "IS_MAC", False)
    ini = tmp_path / "reaper.ini"
    ini.write_text("; audiodev=dummy is just a comment\n[audioconfig]\naudiodev=ALSA\nmode=1\n"
                   "custom=keep\n[reaper]\naudiocfgopen=1\nmysetting=42\n")
    P.ensure_resource(tmp_path)
    assert P.resource_ready(tmp_path)
    content = ini.read_text()
    assert "; audiodev=dummy is just a comment" in content
    assert "custom=keep" in content and "mysetting=42" in content
    assert content.count("[reaper]") == 1
    P.ensure_resource(tmp_path)
    assert ini.read_text() == content


def test_ini_duplicate_sections_and_missing_mode(tmp_path, monkeypatch):
    monkeypatch.setattr(P, "IS_LINUX", True)
    monkeypatch.setattr(P, "IS_MAC", False)
    ini = tmp_path / "reaper.ini"
    ini.write_text("[audioconfig]\naudiodev=dummy\n[reaper]\naudiocfgopen=0\n"
                   "[audioconfig]\naudiodev=ALSA\n")
    P.ensure_resource(tmp_path)
    assert P.resource_ready(tmp_path)
    assert "ALSA" not in ini.read_text()


def test_malformed_ini_is_not_overwritten(tmp_path):
    ini = tmp_path / "reaper.ini"
    ini.write_text("broken INI without a section")
    with pytest.raises(E.EnvironmentError, match="Invalid"):
        P.ensure_resource(tmp_path)
    assert ini.read_text() == "broken INI without a section"


def test_xdg_and_relative_resources(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(P, "IS_LINUX", True)
    monkeypatch.delenv("RAC_REAPER_RESOURCE", raising=False)
    monkeypatch.delenv("RAC_RESOURCE_DIR", raising=False)
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    assert P.resource_dir() == tmp_path / "cache/reacli/reaper"
    assert P.resource_dir("relative") == tmp_path / "relative"


def test_macos_explicit_resource_is_honored(monkeypatch, tmp_path):
    monkeypatch.setattr(P, "IS_MAC", True)
    cmd = P.build_command("REAPER", "test.lua", resource=tmp_path)
    assert cmd == ["REAPER", "-newinst", "-cfgfile", str(tmp_path / "reaper.ini"), "test.lua"]
