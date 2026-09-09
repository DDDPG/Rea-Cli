#!/usr/bin/env python3
"""tests/test_platform.py — 跨平台路由单元测试 (标准库, 脚本式)。
用法: python3 tests/test_platform.py"""
import os
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).parent.parent


from rac.runner import platform as P  # noqa: E402

passed = failed = 0


def check(name, fn):
    global passed, failed
    try:
        fn()
        passed += 1
        print(f"✅ {name}")
    except AssertionError as e:
        failed += 1
        print(f"❌ {name}: {e}")


def t_build_command_mac_direct():
    with mock.patch.object(P, "IS_MAC", True), mock.patch.object(P, "IS_LINUX", False):
        cmd = P.build_command("/x/REAPER", "-nosplash", "-ignoreerrors", "p.rpp", "s.lua")
        assert cmd == ["/x/REAPER", "-newinst", "-nosplash", "-ignoreerrors", "p.rpp", "s.lua"], cmd


def t_build_command_linux_headless_xvfb_cfgfile():
    with mock.patch.object(P, "IS_MAC", False), mock.patch.object(P, "IS_LINUX", True), \
         mock.patch.dict(os.environ, {"RAC_NO_XVFB": "0"}, clear=False), \
         mock.patch.object(P.shutil, "which", return_value="/usr/bin/xvfb-run"):
        os.environ.pop("DISPLAY", None)
        cmd = P.build_command("/opt/REAPER/reaper", "-nosplash", "p.rpp",
                              resource="/res")
        assert cmd == ["xvfb-run", "-a", "/opt/REAPER/reaper",
                       "-cfgfile", "/res/reaper.ini", "-nosplash", "p.rpp"], cmd


def t_build_command_linux_with_display_no_xvfb():
    with mock.patch.object(P, "IS_MAC", False), mock.patch.object(P, "IS_LINUX", True), \
         mock.patch.dict(os.environ, {"DISPLAY": ":0"}, clear=False), \
         mock.patch.object(P.shutil, "which", return_value="/usr/bin/xvfb-run"):
        cmd = P.build_command("/opt/REAPER/reaper", "-nosplash", resource="/res")
        assert cmd == ["/opt/REAPER/reaper", "-cfgfile", "/res/reaper.ini", "-nosplash"], cmd


def t_build_command_linux_rac_no_xvfb():
    with mock.patch.object(P, "IS_MAC", False), mock.patch.object(P, "IS_LINUX", True), \
         mock.patch.dict(os.environ, {"RAC_NO_XVFB": "1"}, clear=False), \
         mock.patch.object(P.shutil, "which", return_value="/usr/bin/xvfb-run"):
        os.environ.pop("DISPLAY", None)
        cmd = P.build_command("/opt/REAPER/reaper", "-nosplash", resource="/res")
        assert cmd[0] != "xvfb-run", cmd


def t_build_command_linux_no_resource_omits_cfgfile():
    with mock.patch.object(P, "IS_MAC", False), mock.patch.object(P, "IS_LINUX", True), \
         mock.patch.dict(os.environ, {"RAC_NO_XVFB": "1"}, clear=False), \
         mock.patch.object(P.shutil, "which", return_value="/usr/bin/xvfb-run"):
        os.environ.pop("DISPLAY", None)
        cmd = P.build_command("/opt/REAPER/reaper", "-nosplash", resource=None)
        assert "-cfgfile" not in cmd, cmd


def t_find_reaper_explicit_wins():
    with mock.patch.dict(os.environ, {"RAC_REAPER_BIN": "/env/reaper"}, clear=False):
        assert P.find_reaper("/explicit/reaper") == "/explicit/reaper"


def t_find_reaper_env_over_candidates():
    with mock.patch.dict(os.environ, {"RAC_REAPER_BIN": "/env/reaper"}, clear=False):
        assert P.find_reaper() == "/env/reaper"


def t_resource_dir_priority():
    with mock.patch.dict(os.environ, {"RAC_REAPER_RESOURCE": "/new",
                                      "RAC_RESOURCE_DIR": "/old"}, clear=False):
        assert P.resource_dir() == Path("/new")           # 规范名优先
    with mock.patch.dict(os.environ, {"RAC_RESOURCE_DIR": "/old"}, clear=True):
        assert P.resource_dir() == Path("/old")           # 旧名别名生效
    assert P.resource_dir("/explicit") == Path("/explicit")  # 显式最高


def t_resource_dir_mac_isolated():
    with mock.patch.object(P, "IS_MAC", True), mock.patch.object(P, "IS_LINUX", False), \
         mock.patch.dict(os.environ, {}, clear=True):
        assert P.resource_dir() == Path.home() / "Library/Caches/reacli/reaper"


def t_ensure_resource_seeds_and_idempotent(tmp=None):
    import tempfile
    d = Path(tempfile.mkdtemp(prefix="rac_res_"))
    with mock.patch.object(P, "IS_LINUX", True), mock.patch.object(P, "IS_MAC", False):
        P.ensure_resource(d)
    ini = d / "reaper.ini"
    assert ini.exists(), "reaper.ini 未生成"
    text = ini.read_text()
    assert "audiodev=dummy" in text and "audiocfgopen=0" in text, text
    with mock.patch.object(P, "IS_LINUX", True), mock.patch.object(P, "IS_MAC", False):
        P.ensure_resource(d)  # 幂等: 不报错、内容仍含关键项
    assert "audiodev=dummy" in ini.read_text()


def t_runner_uses_build_command():
    """runner._run_impl 应通过 platform.build_command 构造命令 (Linux 前置 xvfb)。"""
    import rac.runner.runner as R
    captured = {}

    class FakeProc:
        pid = 424242
        def poll(self): return 0
        def wait(self, timeout=None): return 0

    def fake_popen(cmd, **kw):
        captured["cmd"] = cmd
        return FakeProc()

    import tempfile
    proj = Path(tempfile.mktemp(suffix=".rpp")); proj.write_text("<REAPER_PROJECT 0.1>\n")
    scr = Path(tempfile.mktemp(suffix=".lua")); scr.write_text("-- x\n")
    rr = Path(tempfile.mkdtemp()); sd = Path(tempfile.mkdtemp())
    with mock.patch.object(R.platform, "IS_MAC", False), \
         mock.patch.object(R.platform, "IS_LINUX", True), \
         mock.patch.object(R.platform.shutil, "which", return_value="/usr/bin/xvfb-run"), \
         mock.patch("rac.environment.resolve_executable", side_effect=lambda value: value), \
         mock.patch.dict(os.environ, {"RAC_REAPER_BIN": "/opt/REAPER/reaper",
                                      "RAC_NO_XVFB": "0"}, clear=False), \
         mock.patch.object(R.subprocess, "Popen", side_effect=fake_popen):
        os.environ.pop("DISPLAY", None)
        R.run(proj, scr, timeout=1, run_root=str(rr), state_dir=str(sd),
              resource=str(rr / "resource"))
    cmd = captured.get("cmd", [])
    assert cmd and cmd[0] == "xvfb-run", cmd
    assert "/opt/REAPER/reaper" in cmd and "-cfgfile" in cmd, cmd


def t_make_worker_linux_resource_no_wrapper():
    """Linux make_worker 应产出独立资源目录 (含 headless ini), 不再生成 shell 封装。"""
    import tempfile
    import rac.runner.pool as POOL
    wd = Path(tempfile.mkdtemp(prefix="rac_worker_"))
    seed = Path(tempfile.mkdtemp(prefix="rac_seed_"))
    (seed / "reaper.ini").write_text("[audioconfig]\naudiodev=dummy\n[reaper]\naudiocfgopen=0\n")
    with mock.patch.object(POOL.platform, "IS_LINUX", True), \
         mock.patch.object(POOL.platform, "IS_MAC", False):
        res = POOL.make_worker(wd, seed_resource_dir=seed)
    res = Path(res)
    assert res.is_dir() and (res / "reaper.ini").exists(), f"资源目录/ini 缺失: {res}"
    assert "audiodev=dummy" in (res / "reaper.ini").read_text()
    assert not (wd / "reaper").exists(), "不应再生成 shell 封装脚本"


if __name__ == "__main__":
    for name, fn in sorted({k: v for k, v in globals().items()
                            if k.startswith("t_")}.items()):
        check(name, fn)
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
