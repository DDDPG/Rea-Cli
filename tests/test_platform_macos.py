import json
from pathlib import Path
import pytest

from rac.runner import platform as P


def test_native_vst_index_is_seeded_once_without_copying_preferences(monkeypatch, tmp_path):
    monkeypatch.setattr(P, "IS_MAC", True)
    monkeypatch.setattr(P, "IS_LINUX", False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")
    native = Path.home() / "Library/Application Support/REAPER"
    native.mkdir(parents=True)
    index = native / "reaper-vstplugins_arm64.ini"
    index.write_text("[vstcache]\nreaeq.vst.dylib=known-index\n")
    (native / "reaper.ini").write_text("[reaper]\ncoreaudiooutdevnew=Test Output\nsecret=keep-private\n")
    target = tmp_path / "worker"
    P.ensure_resource(target)
    assert (target / index.name).read_bytes() == index.read_bytes()
    assert "secret" not in (target / "reaper.ini").read_text()
    (target / index.name).write_text("worker-owned")
    P.ensure_resource(target)
    assert (target / index.name).read_text() == "worker-owned"


def test_missing_plugin_preferences_are_migrated_without_overwriting_overrides(monkeypatch, tmp_path):
    import configparser
    monkeypatch.setattr(P, "IS_MAC", True)
    monkeypatch.setattr(P, "IS_LINUX", False)
    ini = tmp_path / "reaper.ini"
    ini.write_text("[reaper]\naudiocfgopen=0\ncoreaudiooutdevnew=Test Output\n")
    P.ensure_resource(tmp_path)
    config = configparser.ConfigParser()
    config.read(ini)
    assert config.getint("reaper", "vst_scan") == 2
    assert config.get("reaper", "clap_path_macos-aarch64") == str(tmp_path / "UserPlugins/CLAP")
    first = ini.read_bytes()
    P.ensure_resource(tmp_path)
    assert ini.read_bytes() == first
    ini.write_text("[reaper]\naudiocfgopen=0\ncoreaudiooutdevnew=Test Output\n"
                   "vst_scan=0\nclap_path_macos-aarch64=/custom/plugins\n")
    P.ensure_resource(tmp_path)
    config.read(ini)
    assert config.getint("reaper", "vst_scan") == 0
    assert config.get("reaper", "clap_path_macos-aarch64") == "/custom/plugins"


def test_macos_config_preserves_coreaudio_and_avoids_linux_settings(monkeypatch, tmp_path):
    monkeypatch.setattr(P, "IS_MAC", True)
    monkeypatch.setattr(P, "IS_LINUX", False)
    ini = tmp_path / "reaper.ini"
    ini.write_text("; native settings\n[reaper]\naudiocfgopen=1\n"
                   "coreaudiooutdevnew=My Interface\ncoreaudiosrate=48000\n")
    P.ensure_resource(tmp_path)
    first = ini.read_text()
    assert P.resource_ready(tmp_path)
    assert "coreaudiooutdevnew=My Interface" in first
    assert "coreaudiosrate=48000" in first
    assert "; native settings" in first
    assert "[audioconfig]" not in first and "audiodev=dummy" not in first
    P.ensure_resource(tmp_path)
    assert ini.read_text() == first


def test_macos_init_uses_automation_cache(monkeypatch, tmp_path, capsys):
    from rac.__main__ import main
    monkeypatch.setattr(P, "IS_MAC", True)
    monkeypatch.setattr(P, "IS_LINUX", False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.delenv("RAC_REAPER_RESOURCE", raising=False)
    monkeypatch.delenv("RAC_RESOURCE_DIR", raising=False)
    native = tmp_path / "Library/Application Support/REAPER/reaper.ini"
    native.parent.mkdir(parents=True)
    original = "[reaper]\ncoreaudiooutdevnew=Test Output\ncoreaudiosrate=48000\nlastproject=private.rpp\n"
    native.write_text(original)
    scripts = native.parent / "Scripts"
    scripts.mkdir()
    (scripts / "__startup.lua").write_text("error('must not copy')")
    assert main(["init"]) == 0
    report = json.loads(capsys.readouterr().out)
    resource = tmp_path / "Library/Caches/reacli/reaper"
    assert report["resource"] == str(resource)
    assert P.resource_ready(resource)
    assert native.read_text() == original
    assert not (resource / "Scripts").exists()
    assert "lastproject" not in (resource / "reaper.ini").read_text()
    assert "coreaudiosrate=48000" in (resource / "reaper.ini").read_text()


def test_macos_missing_audio_selection_fails_before_reaper_launch(monkeypatch, tmp_path):
    from rac.environment import EnvironmentError
    monkeypatch.setattr(P, "IS_MAC", True)
    monkeypatch.setattr(P, "IS_LINUX", False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "empty-home")
    with pytest.raises(EnvironmentError, match="Preferences > Audio > Device"):
        P.ensure_resource(tmp_path / "resource")
    assert not P.resource_ready(tmp_path / "resource")
