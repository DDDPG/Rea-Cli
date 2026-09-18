"""Resource seeding must never consume or modify its source directory."""
from pathlib import Path

import pytest

from rac.runner import pool as P


@pytest.fixture(autouse=True)
def linux_worker(monkeypatch):
    monkeypatch.setattr(P.platform, "IS_LINUX", True)
    monkeypatch.setattr(P.platform, "IS_MAC", False)


def _files(root):
    return {str(path.relative_to(root)): path.read_bytes()
            for path in root.rglob("*") if path.is_file()}


def _existing_worker(worker):
    resource = worker / "resource"
    resource.mkdir(parents=True)
    (resource / "reaper.ini").write_text("[reaper]\nkeep_existing=1\n")
    binary = worker / "REAPER.app/Contents/MacOS/REAPER"
    binary.parent.mkdir(parents=True)
    binary.write_bytes(b"keep existing binary")
    return resource


@pytest.mark.parametrize("seed_argument", ["seed_resource_dir", "seed_config_dir"])
@pytest.mark.parametrize("relationship", ["same", "ancestor", "descendant"])
def test_linux_rejects_overlap_before_rebuilding(tmp_path, seed_argument, relationship):
    worker = tmp_path / "worker"
    resource = _existing_worker(worker)
    seed = {"same": worker, "ancestor": tmp_path,
            "descendant": resource / "saved-seed"}[relationship]
    seed.mkdir(parents=True, exist_ok=True)
    (seed / "source.txt").write_text("source must survive")
    before = _files(tmp_path)

    with pytest.raises(ValueError, match="must not overlap"):
        P.make_worker(worker, force_rebuild=True, **{seed_argument: seed})

    assert _files(tmp_path) == before


@pytest.mark.parametrize("alias_target", ["seed", "worker", "resource"])
def test_linux_rejects_overlap_through_symlink_aliases(tmp_path, alias_target):
    worker = tmp_path / "worker"
    if alias_target == "resource":
        seed = tmp_path / "seed"
        seed.mkdir()
        worker.mkdir()
        (worker / "resource").symlink_to(seed, target_is_directory=True)
    else:
        seed = _existing_worker(worker)
        alias = tmp_path / "alias"
        alias.symlink_to(seed if alias_target == "seed" else worker,
                         target_is_directory=True)
        if alias_target == "seed":
            seed = alias
        else:
            worker = alias
    (seed / "source.txt").write_text("source must survive")
    before = _files(tmp_path)

    with pytest.raises(ValueError, match="must not overlap"):
        P.make_worker(worker, seed_resource_dir=seed)

    assert _files(tmp_path) == before


@pytest.mark.parametrize("seed_argument", ["seed_resource_dir", "seed_config_dir"])
def test_linux_missing_explicit_seed_keeps_existing_worker(tmp_path, seed_argument):
    worker = tmp_path / "worker"
    _existing_worker(worker)
    before = _files(tmp_path)

    with pytest.raises(FileNotFoundError, match="seed resource directory not found"):
        P.make_worker(worker, force_rebuild=True,
                      **{seed_argument: tmp_path / "missing-seed"})

    assert _files(tmp_path) == before


@pytest.mark.parametrize("seed_argument", ["seed_resource_dir", "seed_config_dir"])
def test_linux_seeding_resolves_paths_and_makes_independent_copies(
        tmp_path, monkeypatch, seed_argument):
    monkeypatch.chdir(tmp_path)
    seed = tmp_path / "seed"
    (seed / "Effects").mkdir(parents=True)
    (seed / "Effects/custom.jsfx").write_text("desc: source effect")
    (seed / "reaper.ini").write_text("[audioconfig]\naudiodev=ALSA\n[reaper]\ncustom_seed=1\n")
    original = _files(seed)
    (tmp_path / "seed-alias").symlink_to(seed, target_is_directory=True)
    workers = tmp_path / "workers"
    workers.mkdir()
    (tmp_path / "workers-alias").symlink_to(workers, target_is_directory=True)

    resources = [P.make_worker(Path("workers-alias") / name,
                              **{seed_argument: "seed-alias"})
                 for name in ("first", "second")]

    assert resources == [workers / name / "resource" for name in ("first", "second")]
    assert all(P.platform.resource_ready(resource) for resource in resources)
    assert all("custom_seed=1" in (resource / "reaper.ini").read_text()
               for resource in resources)
    (resources[0] / "Effects/custom.jsfx").write_text("worker modification")
    assert (resources[1] / "Effects/custom.jsfx").read_text() == "desc: source effect"
    assert _files(seed) == original


def test_linux_full_seed_takes_precedence_during_rebuild(tmp_path):
    worker = tmp_path / "worker"
    resource = _existing_worker(worker)
    seed = tmp_path / "seed"
    seed.mkdir()
    (seed / "reaper.ini").write_text("[reaper]\nselected_seed=1\n")
    (resource / "stale.txt").write_text("replace only worker resource")

    result = P.make_worker(worker, seed_resource_dir=seed,
                           seed_config_dir=resource, force_rebuild=True)

    assert result == resource
    assert P.platform.resource_ready(result)
    assert "selected_seed=1" in (result / "reaper.ini").read_text()
    assert not (result / "stale.txt").exists()
    assert (worker / "REAPER.app/Contents/MacOS/REAPER").read_bytes() == b"keep existing binary"
    assert (seed / "reaper.ini").read_text() == "[reaper]\nselected_seed=1\n"


def test_linux_worker_without_seed_uses_isolated_defaults(tmp_path):
    worker = tmp_path / "worker"
    resource = P.make_worker(worker)

    assert resource == worker / "resource"
    assert P.platform.resource_ready(resource)
    assert P.make_worker(worker) == resource


def test_pool_map_rejects_unbounded_job_batch():
    pool = object.__new__(P.Pool)
    with pytest.raises(P.PoolBlocked, match="too_many_jobs"):
        pool.map([{}] * (P.MAX_JOBS + 1))
