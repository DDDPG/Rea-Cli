"""Environment discovery and diagnostics; no package or software installation."""
from __future__ import annotations

import configparser
import ctypes.util
import math
import os
import re
import shutil
import signal
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


class EnvironmentError(RuntimeError):
    """An external prerequisite is missing or unusable."""


def resolve_executable(value: str) -> str:
    expanded = os.path.expanduser(value)
    found = shutil.which(expanded)
    if not found:
        raise EnvironmentError(f"Executable not found or not executable: {value}")
    return str(Path(found).resolve())


def find_luac(explicit: str | None = None) -> str:
    """Find a Lua 5.3/5.4 compiler (the bundled scripts use native bitwise ops)."""
    override = explicit or os.environ.get("RAC_LUAC_BIN")
    candidates = [override] if override else ["luac5.4", "luac54", "luac5.3", "luac53", "luac"]
    if not override and sys.platform == "darwin":
        # Homebrew's unversioned lua may be newer than REAPER's embedded Lua.
        # lua@5.4 is keg-only, so it need not appear on PATH after installation.
        candidates += ["/opt/homebrew/opt/lua@5.4/bin/luac",
                       "/usr/local/opt/lua@5.4/bin/luac"]
    failures = []
    for candidate in candidates:
        try:
            binary = resolve_executable(candidate)
            proc = subprocess.run([binary, "-v"], capture_output=True, text=True, timeout=5)
            version = proc.stdout + proc.stderr
            if proc.returncode == 0 and re.search(r"Lua 5\.[34](?:\D|$)", version):
                return binary
            failures.append(f"{candidate}: requires Lua 5.3 or 5.4, got {version.strip()}")
        except (EnvironmentError, OSError, subprocess.TimeoutExpired) as exc:
            failures.append(str(exc))
    raise EnvironmentError("Install Lua 5.4 (macOS: brew install lua@5.4), or set RAC_LUAC_BIN. "
                           + "; ".join(failures))


def run_bounded(command: list[str], *, timeout: float = 15, env=None):
    """Run a probe, killing its process group on timeout (including Xvfb)."""
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be positive and finite")
    with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True, env=env, start_new_session=(os.name == "posix")) as proc:
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except BaseException:
            if os.name == "posix":
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                proc.kill()
            proc.communicate()
            raise
        return subprocess.CompletedProcess(command, proc.returncode, stdout, stderr)


@dataclass
class Check:
    name: str
    status: str
    detail: str
    hint: str = ""


def doctor(*, profile: str = "full", reaper_bin: str | None = None,
           resource: str | Path | None = None) -> dict:
    """Read-only checks. Profiles: offline, lua, runner, full. Warnings don't fail."""
    from rac import __version__
    from rac.resources import asset
    from rac.runner import platform

    if profile not in {"offline", "lua", "runner", "full"}:
        raise ValueError(f"unknown profile: {profile}")
    checks = []

    def add(name, status, detail, hint=""):
        checks.append(Check(name, status, str(detail), hint))

    add("python", "ok", sys.version.split()[0])
    try:
        import json
        from rac.rpp import parse
        json.loads(asset("knowledge/rpp_schema.json").read_text(encoding="utf-8"))
        json.loads(asset("knowledge/api_index.json").read_text(encoding="utf-8"))
        parse(asset("defaults/minimal_after_reaper_save.rpp").read_text(encoding="utf-8"))
        assert asset("lua/entry.lua").is_file()
        required = {"env", "fx", "item", "marker", "midi", "project", "render",
                    "routing", "snapshot", "take", "track"}
        assert all(asset(f"lua/stdlib/{name}.lua").is_file() for name in required)
        from importlib.resources import files
        for ini_name in ("reaper_headless.ini", "reaper_macos.ini"):
            assert files("rac.runner").joinpath(f"assets/{ini_name}").is_file(), ini_name
        add("package_data", "ok", "Lua templates, schema, API index, defaults and platform INIs present")
    except (OSError, ValueError, AssertionError) as exc:
        add("package_data", "error", f"Missing or invalid packaged assets: {exc}", "Reinstall reacli")
    try:
        import audioop
        audioop.rms(b"\x00\x00", 2)
        add("audio", "ok", "PCM checks available")
    except ImportError as exc:
        add("audio", "error", exc, "Python 3.13+ requires audioop-lts; reinstall reacli with dependencies")

    if profile in {"lua", "full"}:
        try:
            add("luac", "ok", find_luac())
        except EnvironmentError as exc:
            add("luac", "error", exc, "Debian/Ubuntu: apt-get install lua5.4; macOS: brew install lua@5.4")
    if profile in {"runner", "full"}:
        if not (platform.IS_LINUX or platform.IS_MAC):
            add("platform", "error", sys.platform, "REAPER execution supports Linux and macOS; offline tools work on Windows")
        else:
            add("platform", "ok", sys.platform)
        binary = None
        try:
            binary = resolve_executable(platform.find_reaper(reaper_bin))
            add("reaper", "ok", binary)
            try:
                help_result = run_bounded([binary, "-help"], timeout=10)
                usage = help_result.stdout + help_result.stderr
                expected = ("-cfgfile", "-renderproject", "scriptfile.lua")
                absent = [flag for flag in expected if flag not in usage]
                # The official macOS 7.62 binary prints full usage and exits 1.
                # Accept that convention only when the REAPER usage header and
                # every capability are present; failed wrappers still fail.
                mac_help = (platform.IS_MAC and help_result.returncode == 1 and not absent
                            and re.search(r"^\s*Usage:\s*reaper\s+\[options\]", usage,
                                          re.IGNORECASE | re.MULTILINE))
                help_ok = not absent and (help_result.returncode == 0 or bool(mac_help))
                add("reaper_cli", "ok" if help_ok else "error",
                    "Missing CLI capabilities: " + ", ".join(absent) if absent else
                    ("Official positional Lua, -cfgfile and -renderproject supported"
                     + (" (macOS help exits 1)" if mac_help else "") if help_ok else
                     f"Help exited {help_result.returncode}"),
                    "Use a current official REAPER 7.x executable; run doctor --smoke")
            except (OSError, subprocess.TimeoutExpired) as exc:
                add("reaper_cli", "error", exc, "Check shared libraries and use the real REAPER executable")
        except (EnvironmentError, FileNotFoundError) as exc:
            add("reaper", "error", exc, "Install REAPER from https://www.reaper.fm/download.php; set RAC_REAPER_BIN to the real executable")
        if platform.IS_LINUX:
            for lib in ("gtk-3", "asound"):
                located = ctypes.util.find_library(lib)
                add(lib, "ok" if located else "error", located or "shared library missing",
                    "Install GTK3 and ALSA; see docs/environment.md")
            lame = ctypes.util.find_library("mp3lame")
            add("mp3", "ok" if lame else "warning", lame or "MP3 encoder missing (WAV works without it)")
            if os.environ.get("DISPLAY"):
                if shutil.which("xdpyinfo"):
                    try:
                        display = run_bounded(["xdpyinfo"], timeout=5)
                        add("display", "ok" if display.returncode == 0 else "error",
                            os.environ["DISPLAY"], "DISPLAY must point to a reachable X server")
                    except (OSError, subprocess.TimeoutExpired) as exc:
                        add("display", "error", exc)
                else:
                    add("display", "warning", "DISPLAY set, connectivity unverified; run doctor --smoke")
            elif os.environ.get("RAC_NO_XVFB") == "1":
                add("display", "warning", "RAC_NO_XVFB=1 with no DISPLAY; run doctor --smoke to verify your backend")
            else:
                for name in ("xvfb-run", "Xvfb", "xauth"):
                    located = shutil.which(name)
                    add(name, "ok" if located else "error", located or "missing",
                        "Install xvfb + xauth. RPM distributions may also need an xvfb-run wrapper; see docs/environment.md")
            if binary:
                paths = [Path(binary), Path(binary).with_name("libSwell.so")]
                for path in paths:
                    if not path.is_file():
                        add(path.name + "_linkage", "error", f"Missing {path}", "Point RAC_REAPER_BIN at the actual REAPER binary, not a shell wrapper")
                        continue
                    if shutil.which("ldd"):
                        try:
                            result = run_bounded(["ldd", str(path)], timeout=10)
                            output = result.stdout + result.stderr
                            missing = [line.strip() for line in output.splitlines() if "not found" in line]
                            add(path.name + "_linkage", "error" if missing or result.returncode else "ok",
                                "\n".join(missing) or (output.strip() if result.returncode else "All linked libraries resolved"))
                        except (OSError, subprocess.TimeoutExpired) as exc:
                            add(path.name + "_linkage", "error", exc)
                    else:
                        add("ldd", "warning", "ldd unavailable; use doctor --smoke")
        res = platform.resource_dir(resource)
        if res is not None:
            res = res.expanduser().resolve()
            parent = res
            while not parent.exists() and parent != parent.parent:
                parent = parent.parent
            writable = parent.is_dir() and os.access(parent, os.W_OK | os.X_OK)
            ini = res / "reaper.ini"
            if ini.exists() and not os.access(ini, os.W_OK):
                writable = False
            add("resource_writable", "ok" if writable else "error", res)
            platform_name = "macOS" if platform.IS_MAC else "Linux" if platform.IS_LINUX else "REAPER"
            if platform.IS_MAC and not platform.IS_LINUX:
                # Inspect the same narrow native-audio seed as init, but never
                # create a directory, write an INI or initialize REAPER here.
                config = configparser.ConfigParser(interpolation=None, strict=False)
                try:
                    config.read(ini, encoding="utf-8")
                    audio_seed = platform._mac_audio_seed(config)
                    ready = platform.resource_ready(res)
                    hint = "Run reacli init --resource PATH to " + (
                        "copy missing CoreAudio options from the initialized local REAPER INI"
                        if audio_seed else "repair startup settings while preserving the selected CoreAudio output")
                    add("resource_config", "ok" if ready else "warning",
                        ini if ready else f"macOS resource needs initialization: {ini}",
                        "" if ready else hint)
                except (configparser.Error, OSError, UnicodeError, EnvironmentError) as exc:
                    add("resource_config", "error", exc,
                        "Initialize an output in REAPER Preferences > Audio > Device, then run reacli init; "
                        "or pass --resource PATH with an initialized reaper.ini. Repair invalid INI files first")
            elif not ini.exists():
                add("resource_config", "warning", f"reaper.ini will be initialized on first {platform_name} run",
                    "Run reacli init --resource PATH to initialize it now")
            else:
                ready = platform.resource_ready(res)
                add("resource_config", "ok" if ready else "warning", ini,
                    "" if ready else f"{platform_name} runner repairs required dummy-audio settings before execution")
        else:
            add("resource_config", "warning", "No isolated REAPER resource directory selected",
                "Pass --resource PATH or set RAC_REAPER_RESOURCE")
    return {"ok": all(c.status != "error" for c in checks), "version": __version__,
            "profile": profile, "checks": [asdict(c) for c in checks]}
