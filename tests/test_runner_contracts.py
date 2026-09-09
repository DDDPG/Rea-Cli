import json
import math
import os
import sys

import pytest
from rac.runner import run
from rac.runner.pool import Pool
from rac.runner.runner import _validate_proof


@pytest.mark.parametrize("workers", [0, -1, True, 1.5])
def test_invalid_worker_count_rejected(workers, tmp_path):
    with pytest.raises(ValueError, match="positive integer"):
        Pool(tmp_path, n_workers=workers)


@pytest.mark.parametrize("timeout", [0, -1, math.nan, math.inf])
def test_invalid_timeout_returns_fatal_proof(timeout):
    proof = run("missing.rpp", "missing.lua", timeout=timeout)
    assert proof.reason_code == "fatal"
    assert "positive and finite" in proof.error["message"]


def test_non_object_proof_is_invalid():
    assert _validate_proof([]) == "proof is not an object"


def test_relative_run_root_and_inherited_env(tmp_path, monkeypatch):
    import rac.runner.runner as R
    import rac.environment as E
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("RAC_SAVE_AS", "/should/not/save.rpp")
    monkeypatch.setenv("RAC_EXPECT_STATE_HASH", "deadbeef")
    monkeypatch.setattr(E, "resolve_executable", lambda _: sys.executable)
    monkeypatch.setattr(R.platform, "resource_dir", lambda _: None)
    captured = {}
    def command(*args, **kwargs):
        return [sys.executable, "-c", "pass"]
    monkeypatch.setattr(R.platform, "build_command", command)
    real_popen = R.subprocess.Popen
    def popen(*args, **kwargs):
        captured.update(kwargs["env"])
        return real_popen(*args, **kwargs)
    monkeypatch.setattr(R.subprocess, "Popen", popen)
    (tmp_path / "p.rpp").write_text("<REAPER_PROJECT\n>\n")
    (tmp_path / "s.lua").write_text("-- test")
    proof = run("p.rpp", "s.lua", reaper_bin=sys.executable, run_root="relative")
    assert proof.reason_code == "proof_missing"
    assert proof.run_dir.is_absolute()
    assert captured["RAC_RUN_DIR"] == str(proof.run_dir)
    assert "RAC_SAVE_AS" not in captured
    assert "RAC_EXPECT_STATE_HASH" not in captured


def test_timeout_reaps_spawned_process(tmp_path, monkeypatch):
    import rac.runner.runner as R
    monkeypatch.setattr(R.platform, "resource_dir", lambda _: None)
    monkeypatch.setattr(R.platform, "build_command", lambda *a, **kw:
                        [sys.executable, "-c", "import time; time.sleep(30)"])
    project = tmp_path / "p.rpp"
    script = tmp_path / "s.lua"
    project.write_text("<REAPER_PROJECT\n>\n")
    script.write_text("-- test")
    proof = run(project, script, reaper_bin=sys.executable, timeout=0.1, run_root=tmp_path / "runs")
    assert proof.reason_code == "timeout" and proof.retriable
