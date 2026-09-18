"""macOS environment diagnostics without launching REAPER or changing its files."""

import importlib.resources
import os
import subprocess
from pathlib import Path

import pytest

from rac import environment as E
from rac.runner import platform as P


OFFICIAL_HELP = (
    "Usage: reaper [options] [projectfile.rpp | mediafile.wav | scriptfile.lua [...]]\n"
    "  -cfgfile file.ini : use full path for alternate resource directory\n"
    "  -renderproject filename.rpp : render project and exit\n"
)
MAC_REAPER = "/Applications/REAPER.app/Contents/MacOS/REAPER"


@pytest.fixture(autouse=True)
def mac_user_home(monkeypatch, tmp_path):
    """Never let diagnostics depend on the developer's real REAPER preferences."""
    home = tmp_path / "home"
    native = home / "Library/Application Support/REAPER/reaper.ini"
    native.parent.mkdir(parents=True)
    native.write_text("[reaper]\ncoreaudiooutdevnew=Test Output\ncoreaudiosrate=48000\n"
                      "lastproject=private-user-project.rpp\n")
    monkeypatch.setattr(Path, "home", lambda: home)
    return home


@pytest.mark.parametrize("prefix", ["/opt/homebrew", "/usr/local"])
def test_keg_only_lua54_found_after_unversioned_lua55(monkeypatch, prefix):
    monkeypatch.setattr(E.sys, "platform", "darwin")
    monkeypatch.delenv("RAC_LUAC_BIN", raising=False)
    keg = f"{prefix}/opt/lua@5.4/bin/luac"
    probes = []

    def resolve(value):
        if value in {"luac", keg}:
            return value
        raise E.EnvironmentError(f"Executable not found: {value}")

    def run(command, **kwargs):
        probes.append(command[0])
        version = "Lua 5.5.0" if command[0] == "luac" else "Lua 5.4.8"
        return subprocess.CompletedProcess(command, 0, "", version)

    monkeypatch.setattr(E, "resolve_executable", resolve)
    monkeypatch.setattr(E.subprocess, "run", run)
    assert E.find_luac() == keg
    assert probes == ["luac", keg]


@pytest.mark.parametrize("source", ["argument", "environment"])
def test_incompatible_lua_override_is_not_replaced_by_homebrew(monkeypatch, source):
    monkeypatch.setattr(E.sys, "platform", "darwin")
    monkeypatch.setenv("RAC_LUAC_BIN", "chosen-env-luac")
    explicit = "chosen-argument-luac" if source == "argument" else None
    expected = explicit or "chosen-env-luac"
    candidates = []

    def resolve(value):
        candidates.append(value)
        return value

    monkeypatch.setattr(E, "resolve_executable", resolve)
    monkeypatch.setattr(E.subprocess, "run", lambda command, **kwargs:
                        subprocess.CompletedProcess(command, 0, "Lua 5.5.0", ""))
    with pytest.raises(E.EnvironmentError, match="requires Lua 5.3 or 5.4"):
        E.find_luac(explicit)
    assert candidates == [expected]


def _mock_mac_reaper(monkeypatch, *, returncode=1, stdout="", stderr=OFFICIAL_HELP):
    monkeypatch.setattr(P, "IS_MAC", True)
    monkeypatch.setattr(P, "IS_LINUX", False)
    monkeypatch.setattr(P, "find_reaper", lambda value=None: MAC_REAPER)
    monkeypatch.setattr(E, "resolve_executable", lambda value: value)

    def probe(command, **kwargs):
        assert command == [MAC_REAPER, "-help"]
        return subprocess.CompletedProcess(command, returncode, stdout, stderr)

    def forbidden(*args, **kwargs):
        raise AssertionError("macOS diagnostics attempted a Linux dependency probe")

    monkeypatch.setattr(E, "run_bounded", probe)
    monkeypatch.setattr(E.ctypes.util, "find_library", forbidden)
    monkeypatch.setattr(E.shutil, "which", forbidden)


@pytest.mark.parametrize("stream", ["stdout", "stderr"])
def test_official_macos_help_exit_one_is_supported(monkeypatch, tmp_path, stream):
    _mock_mac_reaper(monkeypatch, stdout=OFFICIAL_HELP if stream == "stdout" else "",
                    stderr=OFFICIAL_HELP if stream == "stderr" else "")
    report = E.doctor(profile="runner", resource=tmp_path / "new-resource")
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["reaper_cli"]["status"] == "ok"
    assert "macOS help exits 1" in checks["reaper_cli"]["detail"]
    assert report["ok"]


@pytest.mark.parametrize("returncode, usage", [
    (1, "Unable to initialize REAPER"),
    (1, "scriptfile.lua -cfgfile -renderproject"),
    (1, OFFICIAL_HELP.replace("-cfgfile", "-other-option")),
    (0, OFFICIAL_HELP.replace("-renderproject", "-other-option")),
    (2, OFFICIAL_HELP),
])
def test_macos_failed_or_incomplete_help_still_fails(monkeypatch, tmp_path, returncode, usage):
    _mock_mac_reaper(monkeypatch, returncode=returncode, stderr=usage)
    report = E.doctor(profile="runner", resource=tmp_path / "new-resource")
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["reaper_cli"]["status"] == "error"
    assert not report["ok"]


def test_help_exit_one_remains_an_error_on_linux(monkeypatch, tmp_path):
    _mock_mac_reaper(monkeypatch)
    monkeypatch.setattr(P, "IS_MAC", False)
    monkeypatch.setattr(P, "IS_LINUX", True)
    monkeypatch.setattr(E.ctypes.util, "find_library", lambda name: f"lib{name}.so")
    monkeypatch.setattr(E.shutil, "which", lambda value: None)
    monkeypatch.delenv("DISPLAY", raising=False)
    report = E.doctor(profile="runner", resource=tmp_path / "new-resource")
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["reaper_cli"]["status"] == "error"
    assert checks["reaper_cli"]["detail"] == "Help exited 1"
    assert "Linux" in checks["resource_config"]["detail"]
    assert not (tmp_path / "new-resource").exists()


def test_macos_diagnostics_leave_default_resource_uncreated(monkeypatch, mac_user_home):
    _mock_mac_reaper(monkeypatch)
    monkeypatch.delenv("RAC_REAPER_RESOURCE", raising=False)
    monkeypatch.delenv("RAC_RESOURCE_DIR", raising=False)
    expected = mac_user_home / "Library/Caches/reacli/reaper"
    native = mac_user_home / "Library/Application Support/REAPER/reaper.ini"
    native_before = native.read_bytes()
    report = E.doctor(profile="runner")
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["resource_writable"]["detail"] == str(expected)
    assert checks["resource_config"]["status"] == "warning"
    assert "macOS" in checks["resource_config"]["detail"]
    assert "reacli init" in checks["resource_config"]["hint"]
    assert "CoreAudio" in checks["resource_config"]["hint"]
    assert "dummy" not in checks["resource_config"]["hint"]
    assert not expected.parent.parent.exists()
    assert native.read_bytes() == native_before


def test_macos_diagnostics_do_not_repair_existing_ini(monkeypatch, tmp_path):
    _mock_mac_reaper(monkeypatch)
    ini = tmp_path / "reaper.ini"
    content = b"; Preserve device preferences\n[reaper]\naudiocfgopen=1\ncoreaudiooutdevnew=My output\n"
    ini.write_bytes(content)
    report = E.doctor(profile="runner", resource=tmp_path)
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["resource_config"]["status"] == "warning"
    assert "startup" in checks["resource_config"]["hint"]
    assert "dummy" not in checks["resource_config"]["hint"]
    assert ini.read_bytes() == content


def test_macos_unwritable_ini_is_reported_without_changes(monkeypatch, tmp_path):
    _mock_mac_reaper(monkeypatch)
    ini = tmp_path / "reaper.ini"
    content = b"[reaper]\naudiocfgopen=0\ncoreaudiooutdevnew=Test Output\n"
    ini.write_bytes(content)
    real_access = os.access
    monkeypatch.setattr(E.os, "access", lambda path, mode:
                        False if Path(path) == ini else real_access(path, mode))
    report = E.doctor(profile="runner", resource=tmp_path)
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["resource_writable"]["status"] == "error"
    assert not report["ok"]
    assert ini.read_bytes() == content


@pytest.mark.parametrize("native_content", [None, "[reaper]\ncoreaudiooutdevnew=   \n"])
def test_macos_diagnostics_require_an_initialized_output(monkeypatch, tmp_path, mac_user_home,
                                                       native_content):
    _mock_mac_reaper(monkeypatch)
    native = mac_user_home / "Library/Application Support/REAPER/reaper.ini"
    if native_content is None:
        native.unlink()
    else:
        native.write_text(native_content)
    target = tmp_path / "new-resource"
    report = E.doctor(profile="runner", resource=target)
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["resource_config"]["status"] == "error"
    assert "CoreAudio output selection" in checks["resource_config"]["detail"]
    assert "Preferences > Audio > Device" in checks["resource_config"]["hint"]
    assert "reacli init" in checks["resource_config"]["hint"]
    assert not report["ok"]
    assert not target.exists()
    if native_content is None:
        assert not native.exists()
    else:
        assert native.read_text() == native_content


def test_minimal_mac_template_is_not_treated_as_initialized(monkeypatch, tmp_path):
    _mock_mac_reaper(monkeypatch)
    ini = tmp_path / "reaper.ini"
    content = b"[reaper]\naudiocfgopen=0\n"
    ini.write_bytes(content)
    report = E.doctor(profile="runner", resource=tmp_path)
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["resource_config"]["status"] == "warning"
    assert "copy missing CoreAudio" in checks["resource_config"]["hint"]
    assert ini.read_bytes() == content


def test_initialized_explicit_mac_resource_does_not_read_native_ini(monkeypatch, tmp_path,
                                                                 mac_user_home):
    _mock_mac_reaper(monkeypatch)
    native = mac_user_home / "Library/Application Support/REAPER/reaper.ini"
    native.write_text("Invalid user INI must not be read")
    ini = tmp_path / "reaper.ini"
    content = b"[reaper]\naudiocfgopen=0\ncoreaudiooutdevnew=Explicit output\n"
    ini.write_bytes(content)
    report = E.doctor(profile="runner", resource=tmp_path)
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["resource_config"]["status"] == "ok"
    assert checks["resource_config"]["hint"] == ""
    assert report["ok"]
    assert ini.read_bytes() == content
    assert native.read_text() == "Invalid user INI must not be read"


def test_missing_packaged_mac_ini_is_detected(monkeypatch, tmp_path):
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "reaper_headless.ini").write_text("[reaper]\naudiocfgopen=0\n")
    actual_files = importlib.resources.files
    monkeypatch.setattr(importlib.resources, "files", lambda package:
                        tmp_path if package == "rac.runner" else actual_files(package))
    report = E.doctor(profile="offline")
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["package_data"]["status"] == "error"
    assert "reaper_macos.ini" in checks["package_data"]["detail"]


def test_lua_install_hint_names_the_compatible_homebrew_formula(monkeypatch):
    def missing_compiler(*args, **kwargs):
        raise E.EnvironmentError("compiler unavailable")

    monkeypatch.setattr(E, "find_luac", missing_compiler)
    report = E.doctor(profile="lua")
    checks = {check["name"]: check for check in report["checks"]}
    assert checks["luac"]["status"] == "error"
    assert "brew install lua@5.4" in checks["luac"]["hint"]
