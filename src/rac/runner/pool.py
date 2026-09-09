"""Run concurrent REAPER jobs with a separate resource directory per worker.

macOS shares the installed application and launches independent instances.
Jobs may be retried once after a crash or missing proof.
"""
from __future__ import annotations

import shutil
import subprocess
import threading
from pathlib import Path

from rac.runner import platform
from .runner import Proof, run

IS_MAC = platform.IS_MAC
IS_LINUX = platform.IS_LINUX

PLUGIN_CACHE_FILES = ["reaper.ini", "reaper-vstplugins_arm64.ini",
                      "reaper-jsfx.ini", "reaper-clap-macos-aarch64.ini",
                      "reaper-fxtags.ini"]


def _resource_seed(seed_dir: str | Path | None, *destinations: Path) -> Path | None:
    """Resolve a seed and reject overlap before modifying any worker files."""
    if not seed_dir:
        return None
    seed = Path(seed_dir).expanduser().resolve()
    if not seed.is_dir():
        raise FileNotFoundError(f"REAPER seed resource directory not found: {seed}")
    for destination in destinations:
        target = destination.resolve()
        if seed == target or seed in target.parents or target in seed.parents:
            raise ValueError("REAPER seed resource directory and worker directory must not overlap")
    return seed


def _make_worker_linux(worker_dir: Path, *, seed_resource_dir: str | Path | None,
                       force_rebuild: bool) -> Path:
    """Linux worker: 独立资源目录 (-cfgfile 隔离, 防实例转发/配置互踩)。
    REAPER 二进制共享; xvfb + cfgfile 由 runner 的 platform.build_command 负责。
    返回该 worker 的资源目录 (供 run(resource=...) 使用)。"""
    worker_dir = Path(worker_dir).expanduser().resolve()
    res = worker_dir / "resource"
    # Check the actual resource target too: an existing resource symlink must
    # not make initialization write through into the seed.
    seed = _resource_seed(seed_resource_dir, worker_dir, res)
    if res.exists() and force_rebuild:
        shutil.rmtree(res)
    if not res.exists():
        worker_dir.mkdir(parents=True, exist_ok=True)
        if seed is not None:
            shutil.copytree(seed, res)  # 整份已初始化配置
        else:
            res.mkdir(parents=True, exist_ok=True)
    platform.ensure_resource(res)   # 幂等: 补齐 headless 关键项
    return res


class PoolBlocked(Exception):
    """前置校验拒绝 (guard): 携带 blocked:* reason, 与 proof 词汇表一致。"""
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


def make_worker(worker_dir: str | Path, *,
                source_app: str = "/Applications/REAPER.app",
                seed_config_dir: str | Path | None = None,
                force_rebuild: bool = False,
                seed_resource_dir: str | Path | None = None,
                copy_app: bool = False) -> Path:
    """构造 portable worker。平台分派:
    - Linux: 独立资源目录 (见 _make_worker_linux); 二进制共享, xvfb/cfgfile 由 runner 处理。
    - macOS: 共享已安装 app + 独立配置; copy_app=True 保留旧版拷贝/重签名模式。
    seed_resource_dir 复制完整资源 (优先于兼容用的 seed_config_dir 缓存白名单)。
    幂等; 半截状态清掉重建; seed 缓存缺失补齐。"""
    if platform.IS_LINUX:
        return _make_worker_linux(
            Path(worker_dir),
            seed_resource_dir=seed_resource_dir or seed_config_dir,
            force_rebuild=force_rebuild)
    if not platform.IS_MAC:
        raise PoolBlocked("blocked:unsupported_platform")
    worker_dir = Path(worker_dir).expanduser().resolve()
    seed = _resource_seed(seed_resource_dir, worker_dir)
    source = Path(source_app).expanduser().resolve()
    bin_path = source / "Contents" / "MacOS" / "REAPER"
    if not bin_path.is_file():
        raise FileNotFoundError(f"REAPER app binary not found: {bin_path}")
    worker_dir.mkdir(parents=True, exist_ok=True)
    if copy_app:
        app = worker_dir / "REAPER.app"
        bin_path = app / "Contents" / "MacOS" / "REAPER"
        if app.exists() and (force_rebuild or not bin_path.exists()):
            shutil.rmtree(app)
        if not bin_path.exists():
            try:
                shutil.copytree(source, app, symlinks=True)
                subprocess.run(["codesign", "--force", "--deep", "--sign", "-", str(app)],
                               check=True, capture_output=True)
            except Exception:
                # A partial or unsigned bundle must not be reused after failure.
                if app.exists():
                    shutil.rmtree(app)
                raise
    if seed is not None:
        # A portable resource may contain its own app. Keep the copied, signed
        # source_app; seed only the resources alongside it.
        for src in seed.iterdir():
            if src.name.casefold() == "reaper.app":
                continue
            dst = worker_dir / src.name
            if src.is_dir():
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
    elif seed_config_dir:
        for f in PLUGIN_CACHE_FILES:
            src = Path(seed_config_dir).expanduser() / f
            dst = worker_dir / f
            if src.exists():
                shutil.copy(src, dst)  # 保留旧缓存覆盖行为; 下方补齐平台配置。
    platform.ensure_resource(worker_dir)
    return bin_path


class Pool:
    def __init__(self, workers_root: str | Path, n_workers: int = 2, *,
                 source_app: str = "/Applications/REAPER.app",
                 seed_config_dir: str | Path | None = None,
                 seed_resource_dir: str | Path | None = None,
                 copy_app: bool = False):
        if isinstance(n_workers, bool) or not isinstance(n_workers, int) or n_workers < 1:
            raise ValueError("n_workers must be a positive integer")
        self.workers_root = Path(workers_root).expanduser().resolve()
        self.source_app = source_app
        self.seed_config_dir = seed_config_dir
        self.seed_resource_dir = seed_resource_dir
        self.copy_app = copy_app
        self._lock = threading.Lock()
        self._free: list[tuple[int, str, str | None]] = []
        for i in range(n_workers):
            made = make_worker(self.workers_root / f"w{i}", source_app=source_app,
                               seed_config_dir=seed_config_dir,
                               seed_resource_dir=seed_resource_dir, copy_app=copy_app)
            if platform.IS_LINUX:
                self._free.append((i, platform.find_reaper(), str(made)))
            else:
                self._free.append((i, str(made), str(self.workers_root / f"w{i}")))

    def _checkout(self) -> tuple[int, str, str | None]:
        while True:
            with self._lock:
                if self._free:
                    return self._free.pop(0)
            threading.Event().wait(0.2)

    def _checkin(self, w: tuple[int, str, str | None]):
        with self._lock:
            self._free.append(w)

    def _rebuild(self, worker_idx: int) -> tuple[str, str | None]:
        """崩溃后重新准备 worker，下一次 run 总是启动新进程。"""
        made = make_worker(self.workers_root / f"w{worker_idx}",
                           source_app=self.source_app,
                           seed_config_dir=self.seed_config_dir,
                           seed_resource_dir=self.seed_resource_dir,
                           copy_app=self.copy_app,
                           force_rebuild=True)
        if platform.IS_LINUX:
            return platform.find_reaper(), str(made)
        return str(made), str(self.workers_root / f"w{worker_idx}")

    def map(self, jobs: list[dict], *, timeout: float = 120,
            run_root: str = "runs", state_dir: str = ".state") -> list[Proof]:
        """jobs: [{"project":..., "script":..., "save_as":...(可选)}]"""
        outs = [str(Path(j["save_as"]).resolve()) for j in jobs if j.get("save_as")]
        if len(outs) != len(set(outs)):
            raise PoolBlocked("blocked:output_conflict")  # save_as 路径冲突
        results: list[Proof | None] = [None] * len(jobs)

        def work(i, job):
            widx, b, res = self._checkout()
            try:
                proof = run(job["project"], job["script"], timeout=timeout,
                            save_as=job.get("save_as"), reaper_bin=b, resource=res,
                            run_root=run_root, state_dir=state_dir)
                if proof.reason_code in ("reaper_crash", "proof_missing"):
                    b, res = self._rebuild(widx)   # 替换 worker 再重试
                    proof = run(job["project"], job["script"], timeout=timeout,
                                save_as=job.get("save_as"), reaper_bin=b, resource=res,
                                run_root=run_root, state_dir=state_dir)
                results[i] = proof
            except Exception as e:  # Report thread failures as fatal proofs.
                results[i] = Proof(run_id="r_unknown", status="error",
                                   reason_code="fatal", duration_ms=0, log=[],
                                   state={}, state_hash=None, result=None,
                                   error={"class": "pool", "message": str(e),
                                          "retriable": False})
            finally:
                self._checkin((widx, b, res))

        threads = [threading.Thread(target=work, args=(i, j))
                   for i, j in enumerate(jobs)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return results
