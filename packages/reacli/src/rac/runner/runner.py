"""Run REAPER scripts with isolated resources and structured execution proofs.

Example:
    from rac.runner import run
    proof = run("project.rpp", "edit.lua", save_as="edited.rpp", timeout=60)

The ``reacli exec`` command exposes this runner on the command line.
"""
from __future__ import annotations

import json
import math
import os
import re
import shutil
import signal
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from rac.runner import platform  # noqa: E402  (跨平台路由: find_reaper/build_command/resource)

REASON_CODES = {
    "completed", "completed_noop", "lua_error", "save_failed", "timeout",
    "reaper_crash", "proof_missing", "proof_invalid", "validation_failed", "fatal",
}
RETRIABLE = {"timeout", "reaper_crash", "proof_missing"}
REQUIRED_FIELDS = {"status", "reason_code", "duration_ms", "log", "state",
                   "state_hash", "result", "error"}


def _reason_known(code: object) -> bool:
    return isinstance(code, str) and (code in REASON_CODES
                                      or code.startswith("blocked:"))


@dataclass
class Proof:
    run_id: str
    status: str
    reason_code: str
    duration_ms: int
    log: list
    state: dict
    state_hash: str | None
    result: object
    error: object
    save: object = None
    run_dir: Path | None = None
    teardown_killed: bool = False  # proof 已写但进程未自退出被兜底 kill (如保存确认对话框挂起)

    @property
    def ok(self) -> bool:
        return self.status == "ok"

    @property
    def retriable(self) -> bool:
        return self.reason_code in RETRIABLE

    def to_dict(self) -> dict:
        return {"run_id": self.run_id, "status": self.status,
                "reason_code": self.reason_code, "duration_ms": self.duration_ms,
                "log": self.log, "state": self.state, "state_hash": self.state_hash,
                "result": self.result, "save": self.save, "error": self.error,
                "teardown_killed": self.teardown_killed,
                "run_dir": str(self.run_dir) if self.run_dir else None}


def _alloc_run_id(state_dir: Path, run_root: Path) -> tuple[str, Path]:
    """原子分配 run_id: mkdir 占位 (POSIX 原子), 线程/进程并发安全。
    (原 highwatermark 读-改-写有竞态: pool 并发时两 job 同 run_id 互相覆盖,
    pool 实证抓到)"""
    run_root.mkdir(parents=True, exist_ok=True)
    n = 1
    while True:
        run_id = f"r_{n:06d}"
        try:
            (run_root / run_id).mkdir(parents=False)
            return run_id, run_root / run_id
        except FileExistsError:
            n += 1


def _validate_proof(data: dict) -> str | None:
    """返回 None=合法, 否则错误描述."""
    if not isinstance(data, dict):
        return "proof is not an object"
    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        return f"missing fields: {sorted(missing)}"
    if "save" not in data:
        return "missing field: save"
    if data.get("status") not in ("ok", "error"):
        return f"bad status: {data.get('status')}"
    if not _reason_known(data.get("reason_code")):
        return f"unknown reason_code: {data.get('reason_code')}"
    ok_reasons = {"completed", "completed_noop"}
    if (data["status"] == "ok") != (data["reason_code"] in ok_reasons):
        return f"status/reason inconsistent: {data['status']}+{data['reason_code']}"
    if not isinstance(data.get("log"), list):
        return "log is not array"
    if not isinstance(data.get("state"), dict):
        return "state is not object"
    sh = data.get("state_hash")
    if sh is not None and not (isinstance(sh, str)
                               and re.fullmatch(r"[0-9a-f]{8}", sh)):
        return f"bad state_hash format: {sh!r}"
    sv = data["save"]
    if sv is not None and not isinstance(sv, dict):
        return "save is neither null nor object"
    return None


def run(project: str | Path, script: str | Path, *, timeout: float = 60,
        save_as: str | Path | None = None, expect_state_hash: str | None = None,
        run_root: str | Path = "runs", state_dir: str | Path = ".state",
        reaper_bin: str | None = None, kill_grace: float = 5.0,
        resource: str | Path | None = None) -> Proof:
    """Execute a script and return a Proof, including structured failure details.

    Retry policy belongs to the caller; ``Proof.retriable`` identifies failures
    that may succeed on a subsequent run.
    """
    if not isinstance(timeout, (int, float)):
        import logging
        logging.warning("runner.run: timeout %r 不是数字, 按 60 处理", timeout)
        timeout = 60
    timeout = float(timeout)
    try:
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("timeout must be positive and finite")
        if not math.isfinite(kill_grace) or kill_grace < 0:
            raise ValueError("kill_grace must be nonnegative and finite")
        return _run_impl(project, script, timeout=timeout, save_as=save_as,
                         expect_state_hash=expect_state_hash, run_root=run_root,
                         state_dir=state_dir, reaper_bin=reaper_bin,
                         kill_grace=kill_grace, resource=resource)
    except Exception as e:  # 环境/文件系统级故障 -> fatal
        return Proof(run_id="r_unknown", status="error", reason_code="fatal",
                     duration_ms=0, log=[], state={}, state_hash=None,
                     result=None, error={"class": "runner", "message": str(e),
                                         "retriable": False})


def _run_impl(project: str | Path, script: str | Path, *, timeout: float = 60,
              save_as: str | Path | None = None, expect_state_hash: str | None = None,
              run_root: str | Path = "runs", state_dir: str | Path = ".state",
              reaper_bin: str | None = None, kill_grace: float = 5.0,
              resource: str | Path | None = None) -> Proof:
    project = Path(project).resolve()
    script = Path(script).resolve()
    save_as = Path(save_as).resolve() if save_as else None
    run_root = Path(run_root).expanduser().resolve()
    state_dir = Path(state_dir).expanduser().resolve()
    from rac.environment import resolve_executable
    bin_path = resolve_executable(platform.find_reaper(reaper_bin))
    res = platform.resource_dir(resource)
    if res is not None:
        platform.ensure_resource(res)
    cmd = platform.build_command(bin_path, "-nosplash", "-ignoreerrors",
                                 str(project), str(script), resource=res)

    run_id, run_dir = _alloc_run_id(state_dir, run_root)
    shutil.copy(project, run_dir / "input.rpp")
    shutil.copy(script, run_dir / "script.lua")

    env = dict(os.environ, RAC_RUN_DIR=str(run_dir))
    # Per-run parameters must not leak in from a parent process.
    env.pop("RAC_SAVE_AS", None)
    env.pop("RAC_EXPECT_STATE_HASH", None)
    pre_save_stat = None
    if save_as:
        env["RAC_SAVE_AS"] = str(save_as)
        if save_as.exists():  # stale-output 守卫的基线快照
            st = save_as.stat()
            pre_save_stat = (st.st_mtime_ns, st.st_size)
    if expect_state_hash:
        env["RAC_EXPECT_STATE_HASH"] = expect_state_hash

    stdout_f = open(run_dir / "stdout.log", "w")
    stderr_f = open(run_dir / "stderr.log", "w")
    t0 = time.monotonic()
    try:
        proc = subprocess.Popen(
            cmd, stdout=stdout_f, stderr=stderr_f, env=env,
            start_new_session=True,
        )
    finally:
        # Popen duplicates the file descriptors. Always close our copies,
        # including when the executable fails to start.
        stdout_f.close()
        stderr_f.close()

    proof_path = run_dir / "proof.json"
    reason = None
    while True:
        if proof_path.exists():
            break
        rc = proc.poll()
        if rc is not None:
            reason = "reaper_crash" if rc != 0 else "proof_missing"
            break
        if time.monotonic() - t0 > timeout:
            reason = "timeout"
            try:
                # killpg 命中整个会话组: Linux 下 xvfb-run + 其派生的 Xvfb/reaper
                # 同 pgid, 一并回收 (Xvfb 不留孤儿)。仅当本 Python 进程自身被硬杀
                # (来不及执行 killpg) 时, xvfb-run -a 的锁文件/Xvfb 才可能残留。
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=2)  # 回收僵尸
            except (ProcessLookupError, subprocess.TimeoutExpired):
                pass
            break
        time.sleep(0.2)

    # 有 proof 时给进程一个自退出宽限, 然后兜底 kill (对话框挂起场景)
    teardown_killed = False
    if reason is None:
        t_exit = time.monotonic()
        while proc.poll() is None and time.monotonic() - t_exit < kill_grace:
            time.sleep(0.2)
        if proc.poll() is None:
            teardown_killed = True
            try:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=2)  # 回收僵尸
            except (ProcessLookupError, subprocess.TimeoutExpired):
                pass
    stdout_f.close()
    stderr_f.close()
    duration = int((time.monotonic() - t0) * 1000)

    # stale-output 守卫: 归档前核对 save_as 是否本次运行新写入
    # (entry.lua 临时路径+rename 已保证新鲜性; 此处防"脚本根本没存但目标早已存在"的误归档)
    if save_as and save_as.exists():
        st = save_as.stat()
        if pre_save_stat and pre_save_stat == (st.st_mtime_ns, st.st_size):
            (run_dir / "output.rpp.STALE_WARNING").write_text(
                "save_as existed before run with identical mtime+size; "
                "output may be stale (script did not save)\n")
        else:
            shutil.copy(save_as, run_dir / "output.rpp")

    if reason is not None:  # timeout / crash / proof_missing
        return Proof(run_id=run_id, status="error", reason_code=reason,
                     duration_ms=duration, log=[], state={}, state_hash=None,
                     result=None, error={"class": "runner", "message": reason,
                                         "retriable": reason in RETRIABLE},
                     run_dir=run_dir)

    try:
        data = json.loads(proof_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return Proof(run_id=run_id, status="error", reason_code="proof_invalid",
                     duration_ms=duration, log=[], state={}, state_hash=None,
                     result=None, error={"class": "runner",
                                         "message": f"proof parse failed: {e}",
                                         "retriable": False}, run_dir=run_dir)

    invalid = _validate_proof(data)
    if invalid:
        return Proof(run_id=run_id, status="error", reason_code="proof_invalid",
                     duration_ms=duration, log=[], state={}, state_hash=None,
                     result=None, error={"class": "runner", "message": invalid,
                                         "retriable": False}, run_dir=run_dir)

    return Proof(run_id=run_id, status=data["status"],
                 reason_code=data["reason_code"],
                 duration_ms=data.get("duration_ms", duration),
                 log=data["log"], state=data["state"],
                 state_hash=data.get("state_hash"), result=data.get("result"),
                 save=data.get("save"), error=data.get("error"), run_dir=run_dir,
                 teardown_killed=teardown_killed)


def main():
    import argparse
    p = argparse.ArgumentParser(prog="rac.runner",
                                description="官方 CLI 参考 runner (内部工具)")
    p.add_argument("--project", required=True)
    p.add_argument("--script", required=True)
    p.add_argument("--save-as")
    p.add_argument("--timeout", type=float, default=60)
    p.add_argument("--reaper-bin")
    p.add_argument("--resource")
    p.add_argument("--run-root", default="runs")
    p.add_argument("--state-dir", default=".state")
    a = p.parse_args()
    proof = run(a.project, a.script, timeout=a.timeout, save_as=a.save_as,
                run_root=a.run_root, state_dir=a.state_dir,
                reaper_bin=a.reaper_bin, resource=a.resource)
    out = proof.to_dict()
    print(json.dumps(out, ensure_ascii=False))
    code = {"ok": 0}.get(proof.status, 2 if not proof.retriable else 3)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
