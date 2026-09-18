"""macOS worker contracts without launching REAPER or running codesign."""
from pathlib import Path
import subprocess
import threading
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from rac.runner import pool as P


@pytest.fixture
def mac_worker(tmp_path, monkeypatch):
    monkeypatch.setattr(P.platform, "IS_MAC", True)
    monkeypatch.setattr(P.platform, "IS_LINUX", False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")
    native = Path.home() / "Library/Application Support/REAPER/reaper.ini"
    native.parent.mkdir(parents=True)
    native.write_text("[reaper]\ncoreaudiooutdevnew=Test Output\n")
    app = tmp_path / "source" / "REAPER.app"
    binary = app / "Contents" / "MacOS" / "REAPER"
    binary.parent.mkdir(parents=True)
    binary.write_text("source binary")
    (app / "Contents" / "Executable").symlink_to("MacOS/REAPER")
    sign = Mock()
    monkeypatch.setattr(P.subprocess, "run", sign)
    return app, sign


def test_mac_worker_prepares_resource_and_keeps_binary_return(mac_worker, tmp_path):
    app, sign = mac_worker
    worker = tmp_path / "worker"
    binary = P.make_worker(worker, copy_app=True, source_app=str(app))

    assert binary == worker / "REAPER.app" / "Contents" / "MacOS" / "REAPER"
    assert binary.read_text() == "source binary"
    assert (worker / "REAPER.app" / "Contents" / "Executable").is_symlink()
    assert P.platform.resource_ready(worker)
    sign.assert_called_once_with(
        ["codesign", "--force", "--deep", "--sign", "-", str(worker / "REAPER.app")],
        check=True, capture_output=True)

    assert P.make_worker(worker, copy_app=True, source_app=str(app)) == binary
    assert sign.call_count == 1


def test_mac_default_worker_reuses_signed_installation(mac_worker, tmp_path):
    app, sign = mac_worker
    worker = tmp_path / "worker"
    binary = P.make_worker(worker, source_app=str(app))
    assert binary == app / "Contents/MacOS/REAPER"
    assert binary.read_text() == "source binary"
    assert P.platform.resource_ready(worker)
    assert not (worker / "REAPER.app").exists()
    sign.assert_not_called()


def test_mac_full_resource_seed_preserves_nested_files_and_source_bundle(
        mac_worker, tmp_path):
    app, _ = mac_worker
    seed = tmp_path / "seed"
    (seed / "Effects").mkdir(parents=True)
    (seed / "Effects" / "custom.jsfx").write_text("desc:custom")
    (seed / "reaper.ini").write_text("[reaper]\ncustom_seed=1\n")
    (seed / "reaper-vstplugins64.ini").write_text("[vstcache]\n")
    seed_bin = seed / "REAPER.app" / "Contents" / "MacOS" / "REAPER"
    seed_bin.parent.mkdir(parents=True)
    seed_bin.write_text("wrong binary")
    legacy = tmp_path / "legacy"
    legacy.mkdir()
    (legacy / "reaper.ini").write_text("[reaper]\nwrong_seed=1\n")

    worker = tmp_path / "worker"
    binary = P.make_worker(worker, copy_app=True, source_app=str(app), seed_resource_dir=seed,
                           seed_config_dir=legacy)

    assert binary.read_text() == "source binary"
    assert (worker / "Effects" / "custom.jsfx").read_text() == "desc:custom"
    assert (worker / "reaper-vstplugins64.ini").read_text() == "[vstcache]\n"
    assert "custom_seed=1" in (worker / "reaper.ini").read_text()
    assert "wrong_seed" not in (worker / "reaper.ini").read_text()
    assert P.platform.resource_ready(worker)
    # Config normalization must not modify the user's seed resource.
    assert (seed / "reaper.ini").read_text() == "[reaper]\ncustom_seed=1\n"
    (worker / "Effects" / "custom.jsfx").write_text("worker change")
    assert (seed / "Effects" / "custom.jsfx").read_text() == "desc:custom"


def test_mac_legacy_cache_seed_still_supported(mac_worker, tmp_path):
    app, _ = mac_worker
    seed = tmp_path / "seed"
    seed.mkdir()
    (seed / "reaper.ini").write_text("[reaper]\nlegacy_seed=1\n")
    (seed / "reaper-jsfx.ini").write_text("[jsfx]\n")
    worker = tmp_path / "worker"

    P.make_worker(worker, copy_app=True, source_app=str(app), seed_config_dir=seed)

    assert "legacy_seed=1" in (worker / "reaper.ini").read_text()
    assert (worker / "reaper-jsfx.ini").read_text() == "[jsfx]\n"
    assert P.platform.resource_ready(worker)


def test_mac_failed_signing_is_retried_instead_of_reusing_partial_bundle(
        mac_worker, tmp_path):
    app, sign = mac_worker
    worker = tmp_path / "worker"
    sign.side_effect = [subprocess.CalledProcessError(1, "codesign"), None]
    with pytest.raises(subprocess.CalledProcessError):
        P.make_worker(worker, copy_app=True, source_app=str(app))
    assert not (worker / "REAPER.app").exists()

    binary = P.make_worker(worker, copy_app=True, source_app=str(app))
    assert binary.is_file()
    assert sign.call_count == 2


@pytest.mark.parametrize("relationship", ["same", "ancestor", "descendant"])
def test_mac_resource_seed_rejects_recursive_overlap(
        mac_worker, tmp_path, relationship):
    app, sign = mac_worker
    worker = tmp_path / "worker"
    seed = {"same": worker, "ancestor": tmp_path,
            "descendant": worker / "nested-seed"}[relationship]
    seed.mkdir(parents=True, exist_ok=True)
    existing_binary = worker / "REAPER.app" / "Contents" / "MacOS" / "REAPER"
    existing_binary.parent.mkdir(parents=True)
    existing_binary.write_text("keep existing worker")
    with pytest.raises(ValueError, match="must not overlap"):
        P.make_worker(worker, copy_app=True, source_app=str(app), seed_resource_dir=seed,
                      force_rebuild=True)
    assert existing_binary.read_text() == "keep existing worker"
    sign.assert_not_called()


def test_mac_pool_uses_separate_resources_despite_environment_override(
        mac_worker, tmp_path, monkeypatch):
    app, _ = mac_worker
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("RAC_REAPER_RESOURCE", str(tmp_path / "global"))
    monkeypatch.setenv("RAC_RESOURCE_DIR", str(tmp_path / "legacy-global"))
    barrier = threading.Barrier(2)
    received = []

    def run(project, script, **kwargs):
        resource = P.platform.resource_dir(kwargs["resource"])
        received.append((project, kwargs["reaper_bin"], resource))
        # Both jobs must be checked out before either can return its worker.
        barrier.wait(timeout=5)
        return SimpleNamespace(reason_code="ok", project=project)

    monkeypatch.setattr(P, "run", run)
    pool = P.Pool("workers", 2, source_app=str(app))
    proofs = pool.map([{"project": "a.rpp", "script": "s.lua"},
                       {"project": "b.rpp", "script": "s.lua"}])

    assert [p.project for p in proofs] == ["a.rpp", "b.rpp"]
    assert {r for _, _, r in received} == {tmp_path / "workers" / "w0",
                                           tmp_path / "workers" / "w1"}
    for _, binary, resource in received:
        assert Path(binary) == app / "Contents" / "MacOS" / "REAPER"
        assert not (resource / "REAPER.app").exists()


@pytest.mark.parametrize("copy_app", [False, True])
def test_mac_pool_retry_keeps_explicit_resource(mac_worker, tmp_path, monkeypatch, copy_app):
    app, sign = mac_worker
    monkeypatch.setenv("RAC_REAPER_RESOURCE", str(tmp_path / "global"))
    received = []

    def run(project, script, **kwargs):
        received.append(P.platform.resource_dir(kwargs["resource"]))
        return SimpleNamespace(reason_code="reaper_crash" if len(received) == 1 else "ok")

    monkeypatch.setattr(P, "run", run)
    pool = P.Pool(tmp_path / "workers", 1, source_app=str(app), copy_app=copy_app)
    proofs = pool.map([{"project": "a.rpp", "script": "s.lua"}])

    assert proofs[0].reason_code == "ok"
    assert received == [tmp_path / "workers" / "w0"] * 2
    assert sign.call_count == (2 if copy_app else 0)
    assert pool._free[0][2] == str(tmp_path / "workers" / "w0")
