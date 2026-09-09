# reacli

**Script REAPER, preserve project files, and verify what changed.**

[中文文档](README.zh-CN.md) · [Environment setup](docs/environment.md) ·
[API guide](docs/api.md) · [Knowledge and Lua examples](reference/README.md)

reacli is a Python library and command-line toolkit for automating the
[REAPER](https://www.reaper.fm/) digital audio workstation. It connects project
editing, standalone Lua ReaScripts, REAPER's official CLI, and checks on the
resulting project and audio. Use it in scripts, agent workflows, and integration
tests where an exit code alone is not enough to establish success.

The current version is **0.1.0, an unreleased alpha**. Install from a checkout;
the commands below do not assume a published PyPI package. APIs may change.

## What it does

- **Inspect and edit `.rpp` files offline.** Parse the project tree, patch track,
  item, and marker values, preserve untouched text and opaque plugin data, and
  compare project structure.
- **Prepare Lua scripts.** Generate self-contained ReaScripts from a bounded set
  of operations, or write your own using the bundled skeleton and snippets.
  Generated scripts receive a Lua syntax check before execution.
- **Run and record jobs.** Launch REAPER with dedicated configuration, save a
  separate project, and collect JSON results, logs, and input snapshots. A worker
  pool supports concurrent jobs on Linux and macOS.
- **Check the outcome.** Assert project state and PCM WAV properties such as
  duration, non-silence, clipping, and a test tone's frequency.
- **Look up REAPER knowledge.** Query bundled RPP/API indexes and browse the
  repository's extended workflow notes and Lua examples.

REAPER is installed separately. reacli uses its official CLI and embedded Lua;
it does not bundle REAPER or third-party plugins. Linux and macOS execution are
supported. Windows execution is not implemented; the offline Python tools do
not require a REAPER host.

## Install from source

Download or clone this repository, open its root directory, and use Python 3.10
or newer:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
reacli --version
```

On macOS, `python3` can still be the system Python 3.9. In that case, follow
[Python setup](docs/environment.md) first and create the environment with the
newer interpreter (for example, `python3.14 -m venv .venv`).

The distribution and preferred command are named **`reacli`**; the Python import
is **`rac`**. `rac` is also installed as a compatibility command, and
`python -m rac` is equivalent. Use an isolated environment to avoid collisions
with other packages named `rac`. Python 3.13+ installs `audioop-lts` automatically.

## Quick start without REAPER

This exports a tiny empty project and the Lua templates, validates the project,
and queries the bundled knowledge. Neither REAPER nor Lua is needed:

```bash
reacli doctor --profile offline --json
reacli resources --output ./quickstart
reacli rpp validate ./quickstart/minimal.rpp
reacli rpp get ./quickstart/minimal.rpp tracks
reacli knowledge rpp track:VOLPAN
reacli knowledge api GetTrack
```

Validation returns `{"ok": true, "tracks": 0, "markers": 0}`. Resource export
refuses to overwrite existing files; choose a new output directory when repeating
the example.

You can also patch and verify this project entirely in Python:

```python
from pathlib import Path
from rac.rpp import parse, emit, patch
from rac.verify import expect

doc = parse(Path("quickstart/minimal.rpp"))
patch.set_marker(doc, index=1, pos=0.0, name="Start")
Path("quickstart/marked.rpp").write_bytes(emit(doc).encode("utf-8"))

saved = parse(Path("quickstart/marked.rpp"))
expect(saved).track_count(0).has_marker(name="Start", pos=0.0)
```

## Create and save a project in REAPER

First follow the [Linux or macOS setup guide](docs/environment.md). Execution
needs REAPER 7.x; script generation also needs a **Lua 5.3 or 5.4 `luac` compiler**.
On macOS, initialize a CoreAudio output in REAPER's preferences before the first
run. Then check the environment:

```bash
reacli init
reacli doctor --json
reacli doctor --render --work-dir ./smoke-artifacts --json
```

`doctor --render` executes an isolated Lua/save/render test and checks a 440 Hz
WAV. Plain `doctor` only checks prerequisites. It does not install software.

Using the `quickstart` directory exported above, generate a script that creates
a track named **Vocal** at **−6 dB**, then run it and save a new project:

```bash
python - <<'PY'
from rac.luagen import generate

generate({"ops": [
    {"op": "track.create", "args": [0, "Vocal"]},
    {"op": "track.set_volume_db", "args": [0, -6.0]},
]}, "quickstart/create.lua")
PY

reacli exec \
  --project ./quickstart/minimal.rpp \
  --script ./quickstart/create.lua \
  --save-as ./quickstart/created.rpp \
  --run-root ./quickstart/runs

reacli rpp get ./quickstart/created.rpp tracks
```

Confirm the saved result, including the conversion from decibels to linear
amplitude:

```bash
python - <<'PY'
from pathlib import Path
from rac.rpp import parse
from rac.verify import expect

doc = parse(Path("quickstart/created.rpp"))
expect(doc).track_count(1).track(0).name("Vocal").volume(10 ** (-6 / 20))
print("Saved project verified")
PY
```

The execution response identifies its `run_dir`, which contains the input
snapshot, script, stdout/stderr logs, and `proof.json`. The saved project remains
at the requested `--save-as` path. For an all-Python version, see
[examples/create_project.py](examples/create_project.py) and the
[runner API](docs/api.md#run-a-script).

## Behavior to understand

- **A successful process is only one check.** Generated operations can report a
  blocked edit in `result` and logs while the script itself completes. Inspect
  those fields and assert the saved project or audio you actually need.
- **Scripts execute with your user permissions.** The runner opens the original
  project path so relative media references work. `save_as` requests a separate
  save through the bundled skeleton; arbitrary scripts can still write files.
  Work on copies when testing edits to valuable projects.
- **Configuration is separate from project data.** Linux uses a dedicated
  dummy-audio configuration. macOS starts separate `-newinst` processes and
  initializes missing CoreAudio settings from a narrow, read-only selection of
  the user's REAPER preferences. Concurrent jobs need separate resources;
  `Pool` prepares them automatically.
- **Checks have explicit limits.** Semantic RPP comparison is not a proof of
  identical sound. Audio checks accept mono/stereo 16/24-bit PCM WAV; loudness
  is an approximation. See [API behavior and limits](docs/api.md).

Live validation has covered macOS 15.5 / Apple Silicon / REAPER 7.62 with Python
3.10 and 3.14, and Linux / REAPER 7.77 with Python 3.13. The
[validation record](docs/validation.md) describes tested workflows and evidence.
Other REAPER versions and third-party plugins need local checks. The default
macOS pool has been validated; legacy `copy_app=True` timed out and remains
unverified.

## Knowledge in the package and repository

The installed package contains two JSON knowledge indexes and 12 Lua files
(one entry skeleton and 11 snippets), plus project fixtures and platform INIs.
They work independently of the checkout and can be accessed through
[`rac.resources`](docs/api.md#bundled-resources).

The broader [reference library](reference/README.md) includes CLI/API notes,
RPP explanations, and workflow examples. **`reference/` stays in the Git
repository and is excluded from both wheels and source distributions.** Knowledge
indexes and Lua templates have one canonical copy under `src/rac/data/`; the
reference library links to them.

## Documentation and development

- [Environment setup and troubleshooting](docs/environment.md)
- [Python API, CLI contracts, and concurrent workers](docs/api.md)
- [Reference knowledge and Lua examples](reference/README.md)
- [Validation evidence and limitations](docs/validation.md)
- [Contributing and local checks](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md) and [release procedure](docs/releasing.md)

For development, activate the virtual environment above and run:

```bash
python -m pip install -e '.[dev]'
python -m pytest
```

The default suite requires no REAPER; Lua-dependent cases need a compatible
compiler. Live integration tests are opt-in. See [CONTRIBUTING.md](CONTRIBUTING.md)
for the build and live-test commands.

## License and project status

The project's own code uses the [MIT license](LICENSE). Third-party reference
descriptions and data retain their own provenance; redistribution permission
for the bundled indexes still needs to be established before public release.
See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the outstanding items.
REAPER is a Cockos product, provided under its own terms. This project is
independent of and not endorsed by Cockos.
