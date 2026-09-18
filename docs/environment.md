# Environment setup and troubleshooting

[Documentation](README.md) · [Quick start](../README.md) · [API guide](api.md)

Installing reacli installs Python code and package data. It does not install
REAPER, system libraries, or Lua, and it does not initialize REAPER preferences.
Choose only the prerequisites needed for your workflow:

- **Offline tools:** Python 3.10+ for RPP parsing/patching, knowledge lookup, and
  PCM WAV checks. REAPER and Lua are unnecessary.
- **Script generation/preflight:** a Lua 5.3 or 5.4 `luac` compiler. REAPER runs
  scripts with its embedded Lua; the external compiler checks syntax only.
- **Execution:** an official REAPER 7.x installation on Linux or macOS, plus the
  platform setup below. REAPER is proprietary and supplied under
  [Cockos's terms](https://www.reaper.fm/purchase.php).

The minimum REAPER minor version has not been certified. Use doctor and the
smoke test to check your installed version; see [validation coverage and limits](validation.md).

Install reacli in an isolated virtual environment using the
[source installation instructions](../README.md#installation). On Python
3.13+, `audioop-lts` is installed automatically. A system Python reporting 3.9
cannot run this package.

## macOS

1. Install the official app from [reaper.fm](https://www.reaper.fm/download.php)
   in `/Applications/REAPER.app` or `~/Applications/REAPER.app`.
2. Open REAPER once to complete any first-launch prompts. In
   **Preferences > Audio > Device**, select an output, then close REAPER to save
   the choice. A configured CoreAudio output is needed even for offline rendering.
3. Install the compatible Lua compiler. Homebrew Python is useful if the system
   interpreter is too old:

```bash
brew install python lua@5.4
python3 --version
```

After activating the virtual environment and installing reacli, initialize and
check the dedicated automation configuration:

```bash
reacli init
reacli doctor --json
reacli doctor --render --work-dir ./smoke-artifacts --json
```

`lua@5.4` is keg-only. Discovery checks compatible compilers on `PATH`, then
`/opt/homebrew/opt/lua@5.4/bin/luac` and
`/usr/local/opt/lua@5.4/bin/luac`; no forced linking is needed. The unversioned
Homebrew `lua` formula can install Lua 5.5, which is outside the supported target.

For another app location, select the actual executable, not the bundle directory:

```bash
export RAC_REAPER_BIN="/path/to/REAPER.app/Contents/MacOS/REAPER"
```

The runner uses the logged-in macOS desktop session. It starts a separate
REAPER process with `-newinst` and an absolute `-cfgfile` path; it does not use
Xvfb. Execution in a desktop-less macOS service is not covered by the recorded
validation.

### Plugin discovery and macOS window restoration

When a dedicated resource has no explicit `vst_scan` preference, initialization
sets `vst_scan=2` to disable startup scanning for new/updated VSTs. On macOS,
missing VST indexes (`reaper-vstplugins_arm64.ini` and `reaper-vstplugins64.ini`)
are copied from the native REAPER resource, without overwriting worker indexes.
This permits cached plugins, including ReaEQ, to be resolved without rescanning.
If no index exists, initialize and scan a dedicated resource once before using
VSTs. New or updated plugins require an explicit rescan; disabling discovery
does not prevent a plugin used by a project from loading or showing its own UI.

On macOS, missing CLAP path preferences default to `<resource>/UserPlugins/CLAP`,
rather than the system-wide directories. Existing explicit paths and `vst_scan`
values are preserved. To prepare plugins, open the **dedicated** configuration
in REAPER, set the desired paths, and rescan in Preferences > Plug-ins. Disable
“Scan new/updated plug-ins on startup” again after preparing the VST index.
Use `Pool(seed_resource_dir=...)` to distribute that prepared resource. Explicit
CLAP paths can still cause CLAP startup scans; the default isolated path avoids
system CLAP discovery and does not make system CLAP plugins available.

macOS commands append `-ApplePersistence NO` after all REAPER arguments to
disable Cocoa state restoration for the automation process. Putting this option
first can prevent REAPER 7.48 from parsing `-cfgfile`; `ApplePersistenceIgnoreState`
alone did not prevent the crash/reopen dialog on the tested machine. No global
`defaults` setting or native saved-window state is deleted. This covers runner,
pool and render commands. Verified on macOS 26.6.1 / REAPER 7.48 arm64; other
macOS/REAPER combinations still need live validation.

### CoreAudio settings

The default resource directory is `~/Library/Caches/reacli/reaper`.
Initialization requires `[reaper] audiocfgopen=0` and a nonempty
`coreaudiooutdevnew`. The packaged macOS INI deliberately contains no device
names and must be completed locally.

If the target has no output selection, `reacli init` and the runner read
`~/Library/Application Support/REAPER/reaper.ini` and fill only missing values
from these eight keys:

```text
coreaudioindevnew    coreaudiooutdevnew
coreaudiosrate      coreaudiosrateuse
coreaudiobs         coreaudiobsuse
coreaudioignorereset coreaudioignprojsr
```

Audio seeding never modifies the native INI or copies scripts or general
preferences. VST index seeding is described above. Existing target settings are preserved. An already
initialized target does not need the native INI. If neither has an output
selection, initialization reports an error with device-setup instructions.
Linux dummy-audio settings are not added on macOS.

The default macOS `Pool` shares the installed executable and gives each worker
its own resource directory and `-newinst` process. A custom app requires the
Python `source_app` argument. The legacy `copy_app=True` option timed out in
recorded validation; use the default mode. Full resource seeding and its
difference from legacy configuration seeding are described in the
[pool API](api.md#concurrent-workers).

## Linux

REAPER needs GTK3 and ALSA libraries even for CLI-driven jobs. It also needs an
X display: a reachable `DISPLAY`, or `xvfb-run`, `Xvfb`, and `xauth` for headless
execution. The dedicated dummy-audio configuration needs no physical audio
device or sound server for the built-in smoke test.

For Debian/Ubuntu before the `t64` library transition:

```bash
sudo apt-get update
sudo apt-get install libgtk-3-0 libasound2 xvfb xauth lua5.4
```

On Ubuntu 24.04, use the updated library package names:

```bash
sudo apt-get update
sudo apt-get install libgtk-3-0t64 libasound2t64 xvfb xauth lua5.4
```

On Fedora/RHEL-family distributions, the corresponding packages are `gtk3`,
`alsa-lib`, `xorg-x11-server-Xvfb`, `xorg-x11-xauth`, and `lua`. Verify that the
available compiler is 5.3/5.4; some distributions ship another version. Optional
packages are `libmp3lame0` (Debian/Ubuntu) or `lame-libs` (RPM) for MP3 encoding,
and `x11-utils` or `xorg-x11-utils` for an `xdpyinfo` display check.

Download and install the correct official REAPER archive for your CPU from
[reaper.fm](https://www.reaper.fm/download.php). Point reacli to the actual
binary next to `libSwell.so`, then initialize the environment:

```bash
export RAC_REAPER_BIN="/opt/REAPER/reaper"  # adjust for your installation
reacli init
reacli doctor --json
reacli doctor --render --work-dir ./smoke-artifacts --json
```

Doctor checks shared-library linkage for both REAPER and `libSwell.so`.
Successful linkage does not rule out plugin-loading problems or startup dialogs;
the smoke test verifies actual execution and saving.

### Bootstrap helper

[`scripts/bootstrap-reaper.sh`](../scripts/bootstrap-reaper.sh) can install
dependencies, install an already-extracted official archive, initialize
configuration, and verify a render. It does not download REAPER.

Run from the repository root with the reacli virtual environment activated:

```bash
export REAPER_SRC="/path/to/extracted/reaper_linux_x86_64"
export REACLI_PREFIX="$HOME/.local/opt/reacli"
export REACLI_PYTHON="$(command -v python)"
bash scripts/bootstrap-reaper.sh deps
bash scripts/bootstrap-reaper.sh install
export PATH="$REACLI_PREFIX/bin:$PATH"
export RAC_REAPER_BIN="$REACLI_PREFIX/REAPER/reaper"
bash scripts/bootstrap-reaper.sh env
bash scripts/bootstrap-reaper.sh verify
```

Adjust `REAPER_SRC` for the archive's architecture and extraction path. `deps`
needs root or sudo; other stages support a user-owned prefix. `install` delegates
to the archive's official installer, whose overwrite behavior applies. `all`
runs every stage. `REACLI_PYTHON` selects the interpreter containing reacli.

Some RPM distributions provide Xvfb without the Debian-style `xvfb-run` wrapper.
The helper supplies [`scripts/xvfb-run`](../scripts/xvfb-run) under the selected
prefix's `bin/` when needed. It uses `-displayfd` for display allocation,
Xauthority cookies, and disables TCP listening. Keep that directory on `PATH`.

### Display selection

If `DISPLAY` is set, the runner uses it. A stale value can hang startup; unset
it to use Xvfb:

```bash
unset DISPLAY
reacli doctor --smoke --json
```

`RAC_NO_XVFB=1` skips the wrapper for externally managed displays/backends. It
does not make REAPER a native headless application. Verify such a setup with
`doctor --smoke` before submitting jobs.

## Configuration

The REAPER executable is selected by explicit `--reaper-bin`/Python
`reaper_bin=`, then `RAC_REAPER_BIN`, then platform discovery. macOS pool
execution separately uses `source_app`; see [the pool API](api.md#concurrent-workers).

Resource selection follows this order:

1. Explicit `--resource` or Python `resource=`.
2. `RAC_REAPER_RESOURCE`.
3. The compatibility alias `RAC_RESOURCE_DIR`.
4. Platform default: `$XDG_CACHE_HOME/reacli/reaper` or
   `~/.cache/reacli/reaper` on Linux, `~/Library/Caches/reacli/reaper` on macOS.

For example, use a dedicated resource alongside an automation project:

```bash
reacli init --resource ./automation-resource
reacli doctor --resource ./automation-resource --render --json
```

`init` and execution initialize or repair required INI keys, while retaining
unrelated settings. Linux enforces `[audioconfig] audiodev=dummy`, `mode=0`, and
`[reaper] audiocfgopen=0`. macOS follows the CoreAudio rules above. Always select
a resource dedicated to automation. Use separate resources for concurrent
processes; `Pool` creates them per worker.

`RAC_LUAC_BIN` selects a Lua compiler. Explicit compiler overrides are
authoritative: an invalid override causes an error instead of fallback. REAPER
and Lua version discovery do not establish third-party plugin availability.

## Diagnostics and smoke tests

```bash
reacli doctor --profile offline --json
reacli doctor --profile lua --json
reacli doctor --profile runner --json
reacli doctor --json
```

`offline` checks Python and bundled data; `lua` adds compiler checks; `runner`
adds REAPER execution prerequisites; default `full` includes both Lua and
runner checks. Plain doctor reads configuration and probes dependencies without
creating or repairing resource files. Warnings alone return success; errors
return exit code `4`.

`--smoke` explicitly launches REAPER, executes generated Lua, validates the
proof, saves an isolated project, and reparses it. `--render` adds a generated
440 Hz signal, a render, and WAV checks for duration, non-silence, clipping, and
frequency. These flags need a compatible compiler as well as execution
prerequisites. Use the default full profile for them.

```bash
reacli doctor --render --work-dir ./smoke-artifacts --timeout 60 --json
```

Smoke tests use generated projects and dedicated temporary resources. With
`--work-dir`, each run's artifacts remain in a unique subdirectory for inspection;
otherwise temporary artifacts are cleaned up. The test uses no third-party
plugins. Your projects are not opened by these probes.

## Troubleshooting

### Python imports the wrong package

Activate the intended environment and inspect the import path:

```bash
python -c 'import rac; print(rac.__file__)'
python -m pip show reacli
```

A local `rac.py` or `rac/` directory can shadow the installed library. Move to
an unrelated working directory and retry. Avoid installing another distribution
that provides `rac` into the same environment.

### REAPER is found but cannot start

On Linux, inspect doctor linkage results for missing GTK/ALSA dependencies.
Select the real REAPER binary rather than a shell wrapper so `libSwell.so` can
be located. Check `DISPLAY`, or unset it and ensure all three Xvfb tools exist.

On macOS, finish first-launch prompts and initialize an audio output. A bare
`audiocfgopen=0` setting alone is insufficient. Check the dedicated resource
with doctor, then run `reacli init` to fill missing CoreAudio values. Plugin or
license dialogs can also block startup; inspect the retained run logs and app.

Official macOS REAPER 7.62 prints valid `-help` output with exit status 1.
Doctor accepts that specific convention only when the expected usage header
and CLI capabilities are present.

### Lua compiler is missing or incompatible

Install Lua 5.3/5.4 (`brew install lua@5.4` on macOS), or set `RAC_LUAC_BIN` to
its compiler. Lua 5.5 is unsupported. Clear an obsolete explicit override if
you want automatic discovery. A syntax pass does not guarantee the script's
ReaScript APIs exist on your installed REAPER version.

### Execution returns proof_missing

Use generated Lua or retain the exported `entry.lua` result-writing protocol.
A plain ReaScript can finish without emitting the proof required by the runner.
Inspect `stdout.log`, `stderr.log`, and any startup dialogs before retrying.

### Audio or plugin checks fail

The audio reader accepts mono/stereo 16/24-bit PCM WAV, not floating-point WAV,
MP3, or multichannel output. MP3 encoding also needs LAME on Linux. Third-party
plugins must be installed and licensed separately, with needed resources made
available to the automation configuration. A passing stock smoke test does not
certify those plugins.

For the exact platforms and workflows exercised, see the
[validation record](validation.md).
