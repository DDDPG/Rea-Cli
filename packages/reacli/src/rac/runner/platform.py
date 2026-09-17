"""rac/runner/platform.py — REAPER 调用的跨平台路由 (单一真相源)。

macOS 直调独立 REAPER.app 实例; 两平台用 -cfgfile 隔离资源目录。
runner / pool / score 共用。环境变量:
  RAC_REAPER_BIN       REAPER 可执行文件 (覆盖平台自动发现)
  RAC_REAPER_RESOURCE  资源/配置目录; 旧名 RAC_RESOURCE_DIR 亦读
  RAC_NO_XVFB=1        跳过 xvfb (有真实 DISPLAY 时也自动跳)
"""
from __future__ import annotations

import os
import shutil
import sys
import configparser
from pathlib import Path
from rac.environment import EnvironmentError

IS_MAC = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")

_MAC_CANDIDATES = ["/Applications/REAPER.app/Contents/MacOS/REAPER",
                   str(Path.home() / "Applications/REAPER.app/Contents/MacOS/REAPER")]
_LINUX_CANDIDATES = ["reaper", "/opt/REAPER/reaper", "/usr/local/bin/reaper",
                     str(Path.home() / "opt/REAPER/reaper")]

_HEADLESS_INI = Path(__file__).resolve().parent / "assets" / "reaper_headless.ini"
_HEADLESS_FALLBACK = ("[audioconfig]\naudiodev=dummy\nmode=0\n\n"
                      "[reaper]\naudiocfgopen=0\n")
_MAC_INI = _HEADLESS_INI.with_name("reaper_macos.ini")
_MAC_FALLBACK = "[reaper]\naudiocfgopen=0\n"
_MAC_AUDIO_KEYS = (
    "coreaudioindevnew", "coreaudiooutdevnew", "coreaudiosrate", "coreaudiosrateuse",
    "coreaudiobs", "coreaudiobsuse", "coreaudioignorereset", "coreaudioignprojsr",
)


def _mac_audio_configured(config: configparser.ConfigParser) -> bool:
    return bool(config.get("reaper", "coreaudiooutdevnew", fallback="").strip())


def _mac_audio_seed(config: configparser.ConfigParser) -> dict[str, str]:
    """Read only initialized CoreAudio choices, never user startup scripts/caches."""
    if _mac_audio_configured(config):
        return {}
    source = Path.home() / "Library/Application Support/REAPER/reaper.ini"
    native = configparser.ConfigParser(interpolation=None, strict=False)
    try:
        native.read(source, encoding="utf-8")
    except (configparser.Error, OSError, UnicodeError) as exc:
        raise EnvironmentError(f"Cannot read CoreAudio configuration from {source}: {exc}") from exc
    if not _mac_audio_configured(native):
        raise EnvironmentError(
            "macOS REAPER needs an initialized CoreAudio output selection. "
            "Launch REAPER once, choose an output in Preferences > Audio > Device, "
            "then run reacli init again; or supply --resource with an initialized reaper.ini. "
            "Only CoreAudio options are copied into the dedicated automation resource.")
    return {key: native.get("reaper", key) for key in _MAC_AUDIO_KEYS
            if native.has_option("reaper", key)
            and not config.get("reaper", key, fallback="").strip()}


def _resource_settings() -> dict[str, dict[str, str]]:
    if IS_LINUX:
        return {"audioconfig": {"audiodev": "dummy", "mode": "0"},
                "reaper": {"audiocfgopen": "0"}}
    if IS_MAC:
        # macOS uses CoreAudio settings, not Linux's [audioconfig] section.
        # REAPER also needs an initialized CoreAudio output choice at startup.
        return {"reaper": {"audiocfgopen": "0"}}
    raise EnvironmentError("REAPER execution currently supports Linux and macOS")


def find_reaper(reaper_bin: str | None = None) -> str:
    """显式参数 > RAC_REAPER_BIN > 平台候选表首个存在者。"""
    if reaper_bin:
        return reaper_bin
    env = os.environ.get("RAC_REAPER_BIN")
    if env:
        return env
    for c in (_MAC_CANDIDATES if IS_MAC else _LINUX_CANDIDATES):
        if Path(c).exists() or shutil.which(c):
            return c
    raise FileNotFoundError("REAPER binary not found; set RAC_REAPER_BIN")


def resource_dir(explicit: str | os.PathLike | None = None) -> Path | None:
    """显式 > RAC_REAPER_RESOURCE > RAC_RESOURCE_DIR(旧名) > 平台默认。
    macOS 默认 ~/Library/Caches/reacli/reaper; Linux 默认 ~/.cache/reacli/reaper。"""
    if explicit:
        return Path(explicit).expanduser().resolve()
    env = os.environ.get("RAC_REAPER_RESOURCE") or os.environ.get("RAC_RESOURCE_DIR")
    if env:
        return Path(env).expanduser().resolve()
    if IS_LINUX:
        cache = Path(os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache")))
        return cache.expanduser().resolve() / "reacli" / "reaper"
    if IS_MAC:
        return Path.home() / "Library" / "Caches" / "reacli" / "reaper"
    return None


def resource_ready(resource: str | os.PathLike) -> bool:
    requested = Path(resource).expanduser()
    if requested.is_symlink() or (requested / "reaper.ini").is_symlink():
        return False
    config = configparser.ConfigParser(interpolation=None, strict=False)
    try:
        config.read(Path(resource) / "reaper.ini", encoding="utf-8")
        settings_ready = all(config.get(section, key, fallback=None) == value
                             for section, settings in _resource_settings().items()
                             for key, value in settings.items())
        return settings_ready and (not IS_MAC or IS_LINUX or _mac_audio_configured(config))
    except (configparser.Error, OSError, UnicodeError):
        return False


def ensure_resource(resource: str | os.PathLike) -> Path:
    """幂等初始化专用自动化配置 (Linux dummy 音频; macOS 保留设备设置)。
    空/缺则从平台模板 seed (模板缺失退化写内置最小 ini);
    已有配置但缺关键项则追加补段。"""
    wanted = _resource_settings()
    requested = Path(resource).expanduser()
    if requested.is_symlink():
        raise EnvironmentError(f"REAPER resource directory must not be a symlink: {requested}")
    resource = requested.resolve()
    resource.mkdir(parents=True, exist_ok=True)
    ini = resource / "reaper.ini"
    if ini.is_symlink():
        raise EnvironmentError(f"REAPER resource configuration must not be a symlink: {ini}")
    text = ini.read_text(encoding="utf-8", errors="ignore") if ini.exists() else ""
    config = configparser.ConfigParser(interpolation=None, strict=False)
    if text.strip():
        try:
            config.read_string(text)
        except configparser.Error as exc:
            raise EnvironmentError(f"Invalid {ini}: {exc}; repair it or select a fresh resource directory") from exc
    if IS_MAC and not IS_LINUX:
        # Cached VST discovery is needed even for bundled ReaEQ when scanning is
        # disabled. Copy indexes only; never overwrite a worker's own cache.
        native = Path.home() / "Library/Application Support/REAPER"
        for name in ("reaper-vstplugins_arm64.ini", "reaper-vstplugins64.ini"):
            source, target = native / name, resource / name
            if source.is_file() and not target.exists():
                shutil.copyfile(source, target)
    # Explicit plugin preferences belong to the caller. Missing preferences
    # must not trigger a machine-wide third-party scan in a fresh worker.
    wanted.setdefault("reaper", {})
    if not config.has_option("reaper", "vst_scan"):
        wanted["reaper"]["vst_scan"] = "2"
    if IS_MAC and not IS_LINUX:
        for key in ("clap_path_macos-aarch64", "clap_path_macos-x86_64"):
            if not config.has_option("reaper", key):
                wanted["reaper"][key] = str(resource / "UserPlugins" / "CLAP")
    if resource_ready(resource) and all(
        config.get(section, key, fallback=None) == value
        for section, values in wanted.items() for key, value in values.items()
    ):
        return resource
    if IS_MAC and not IS_LINUX:
        wanted["reaper"].update(_mac_audio_seed(config))
    if not text.strip():
        template = _HEADLESS_INI if IS_LINUX else _MAC_INI
        fallback = _HEADLESS_FALLBACK if IS_LINUX else _MAC_FALLBACK
        seed = template.read_text(encoding="utf-8") if template.exists() else fallback
        if IS_MAC and not IS_LINUX:
            seed = seed.rstrip() + "\n" + "".join(
                f"{key}={value}\n" for key, value in wanted["reaper"].items()
                if key != "audiocfgopen")
        else:
            seed = seed.rstrip() + "\nvst_scan=2\n"
        ini.write_text(seed, encoding="utf-8")
    else:
        # Preserve comments, unknown keys and plugin settings. Replace required
        # keys in every repeated section instead of appending conflicting values.
        output, seen_sections = [], set()
        section, seen_keys = "", set()

        def flush():
            for key, value in wanted.get(section, {}).items():
                if key not in seen_keys:
                    output.append(f"{key}={value}")

        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                flush()
                section, seen_keys = stripped[1:-1].strip().lower(), set()
                seen_sections.add(section)
            elif "=" in stripped and not stripped.startswith((";", "#")):
                key = stripped.split("=", 1)[0].strip().lower()
                if key in wanted.get(section, {}):
                    line = f"{key}={wanted[section][key]}"
                    seen_keys.add(key)
            output.append(line)
        flush()
        for section, values in wanted.items():
            if section not in seen_sections:
                output.append(f"[{section}]")
                output.extend(f"{key}={value}" for key, value in values.items())
        ini.write_text("\n".join(output) + "\n", encoding="utf-8")
    return resource


def build_command(reaper_bin: str, *reaper_args: str,
                  resource: str | os.PathLike | None = None) -> list[str]:
    """构造平台正确的 argv。变参 reaper_args 原样透传 (支持
    `proj script` 与 `-renderproject proj` 等各种形态)。
    macOS: [bin, -newinst, -cfgfile ...?, *args]，不向已有桌面实例转发。
    Linux: [xvfb-run -a]? bin [-cfgfile <res>/reaper.ini]? *args。"""
    args = [str(a) for a in reaper_args]
    if IS_MAC:
        # Cocoa consumes this through NSArgumentDomain. It must come LAST:
        # REAPER 7.48 stops parsing its own options at an unknown Cocoa option.
        # IgnoreState alone still permits the crash/reopen dialog on macOS 26.
        args += ["-ApplePersistence", "NO"]
        if resource is not None:
            return [reaper_bin, "-newinst", "-cfgfile", str(Path(resource).expanduser().resolve() / "reaper.ini"), *args]
        return [reaper_bin, "-newinst", *args]
    if not IS_LINUX:
        raise EnvironmentError("REAPER execution currently supports Linux and macOS")
    cmd = [reaper_bin]
    if resource is not None:
        cmd += ["-cfgfile", str(Path(resource) / "reaper.ini")]
    cmd += args
    headless = (not os.environ.get("DISPLAY")
                and os.environ.get("RAC_NO_XVFB", "0") != "1")
    if headless:
        missing = [name for name in ("xvfb-run", "Xvfb", "xauth") if not shutil.which(name)]
        if missing:
            raise EnvironmentError("Headless REAPER requires " + ", ".join(missing)
                                   + "; install xvfb and xauth, then run reacli doctor")
        return ["xvfb-run", "-a", *cmd]
    return cmd
