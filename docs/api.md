# API and CLI guide

[Documentation](README.md) · [Quick start](../README.md) ·
[Environment setup](environment.md)

The distribution is `reacli`; Python code imports `rac`. This is an alpha API.
The examples below describe the current implementation and its boundaries.

## Bundled resources

Resources are located through `importlib.resources`, independently of the
working directory. Use the resource API instead of constructing source-tree
paths:

```python
from rac.resources import asset, read_text, export_resources

schema_json = read_text("knowledge/rpp_schema.json")
entry = asset("lua/entry.lua")  # read-only Traversable, not necessarily a Path
output = export_resources("templates")
```

`asset(name)` accepts a relative POSIX path within package data and rejects
parent traversal. `export_resources(destination)` returns the absolute output
`Path` and exports `entry.lua`, `minimal.rpp`, and 11 files under `stdlib/`.
It refuses to overwrite any destination file. It does not export the JSON
knowledge indexes; access those with `read_text` or the knowledge CLI.

The two indexes and 12 Lua files ship with the package. The extended
[`reference/`](../reference/README.md) library is repository-only and is excluded
from both wheels and sdists.

## Read, edit, and compare RPP files

`parse(source)` accepts a `Path`, an existing filename string, or RPP text. Prefer
`Path` when reading files so a missing filename cannot be interpreted as text.
`emit(doc)` and `doc.text()` return serialized text.

```python
from pathlib import Path
from rac.rpp import parse, emit, patch
from rac.verify import expect

# This example expects a project with at least one track.
doc = parse(Path("project.rpp"))
track = doc.tracks()[0]
patch.set_track_name(doc, track, "Vocal")
patch.set_track_volume(doc, track, 10 ** (-6 / 20))
Path("edited.rpp").write_bytes(emit(doc).encode("utf-8"))

saved = parse(Path("edited.rpp"))
expect(saved).track(0).name("Vocal").volume(10 ** (-6 / 20))
```

Track volume is linear amplitude in the RPP helpers; `track.set_volume_db` in
the Lua generator uses decibels. Track and item indices are zero-based. Marker
IDs are explicit project IDs, rather than a position in a Python list.
Schema field positions (`field_meta`, `validate_value`) and `expect.line_value`
use one-based field indices.

The parser preserves untouched text, line endings, unknown fields, and opaque
plugin chunks. Patch helpers mark only the edited nodes for serialization.
Write the encoded result as bytes when preserving line endings matters.
Structural validation does not check missing media, plugin compatibility, or
whether every field has the intended meaning in REAPER.

Useful helpers in `rac.rpp.patch` include `set_track_name`, `set_track_volume`,
`set_track_pan`, `set_track_mute`, `set_item_position`, `set_item_length`,
`set_marker`, and `delete_marker`. Lower-level helpers provide line/value edits.
`rac.rpp.schema` exposes `load`, `key_meta`, `field_meta`, and `validate_value`
for the bundled schema.

```python
from rac.verify.semantics import semantic_diff

differences = semantic_diff(parse(Path("before.rpp")), parse(Path("after.rpp")))
for difference in differences:
    print(difference)
```

An empty diff means no difference under this comparator's rules. By default it
uses `float_tol=1e-4`, ignores GUID differences, and tolerates selected root
defaults from a REAPER 7.62 fixture. Use `strict_guid=True` to compare GUIDs and
`use_defaults=False` to disable default completion. This is a structural check,
not proof that two projects will sound identical. Schema facts and API
signatures are versioned reference data, not live queries of the installed host.

Optional independent parser checks are in `rac.rpp.oracle`. Install the extra
from this checkout with `python -m pip install '.[oracle]'`; it uses the upstream
`rpp` dependency without a vendored copy or `sys.path` changes.

## Generate or write Lua

```python
from rac.luagen import generate, validate

script = generate({"ops": [
    {"op": "track.create", "args": [0, "Vocal"]},
    {"op": "track.set_volume_db", "args": [0, -6.0]},
    {"op": "marker.add", "args": [1, 0.0, "Start"]},
]}, "edit.lua")

validate(script)  # useful separately for hand-written or later-edited scripts
```

`generate(intent, out_path=None)` returns the written `Path` and immediately
runs `luac -p`. It accepts only operations in
[`OP_REGISTRY`](../src/rac/luagen/generator.py), validates their argument types,
and includes the required library snippets in the generated script. The
operation set covers selected track, item, marker, envelope, FX, MIDI, render,
project, and routing edits; it is not the entire ReaScript API.

The output file's parent directory must exist. An explicit output file is
overwritten; an omitted output path creates a unique temporary file owned by
the caller. Compiler discovery accepts Lua 5.3/5.4. An incompatible explicit
`luac_bin` or `RAC_LUAC_BIN` fails rather than silently selecting another version.
Syntax failures raise `SyntaxError`; invalid intent raises `ValueError` or
`TypeError`; unavailable compilers raise `rac.environment.EnvironmentError`.

For custom ReaScript, export the templates and edit `body()` in `entry.lua`.
Keep the skeleton's synchronous execution, result writing, save, and exit
protocol. Store custom output in `RUN.result`. The runner expects this protocol;
an arbitrary script that writes no proof produces `proof_missing`.

Generated operations record rejected edits as `op_N_error` entries in
`RUN.result` and error logs. These do not necessarily cause the Lua body to
raise an exception. Inspect the result and verify the saved project even when
`proof.ok` is true. Syntax checking also cannot confirm API or plugin
availability at runtime.

## Run a script

```python
from rac.runner import run
from rac.verify import proof_check

proof = run(
    "project.rpp",
    "edit.lua",
    save_as="edited.rpp",
    run_root="runs",
    timeout=60,
)
if not proof.ok:
    raise RuntimeError(proof.to_dict())
proof_check(proof)
print(proof.result)
print(proof.run_dir)
```

`run` starts REAPER through the official CLI with the project and Lua script as
positional arguments. It does not perform Lua preflight itself: use `generate`
or `validate` before submitting a script. `reacli exec` calls the same runner.

The original project path is opened so relative media paths continue to resolve.
An archived input is evidence of the invocation, not a sandboxed working copy.
Scripts run with the current user's permissions and can save or modify arbitrary
files. `save_as` tells the bundled skeleton to save a separate project after
successful body execution; create its parent directory first. Use distinct
output paths for independent jobs.

Each invocation allocates a unique directory under `run_root` (default `runs`).
It records `input.rpp`, `script.lua`, stdout/stderr logs, and the script's
`proof.json` when available. Fresh saves also produce an archived
`output.rpp`. Early setup failures can return a proof without a run directory;
crashes and timeouts can leave logs without a script-written proof.

`timeout` defaults to 60 seconds and must be positive and finite. `kill_grace`
defaults to 5 seconds: additional time allowed for process exit after a proof
arrives. A process that exceeds its deadline is terminated with its process
group, including Xvfb children. Abrupt external termination of Python can prevent
cleanup. `state_dir` is retained for compatibility; run IDs are allocated by
creating unique directories under `run_root`.

`resource=` selects a dedicated REAPER resource directory; setup and precedence
are documented in [environment configuration](environment.md#configuration).
Concurrent direct `run` calls must use different resource directories. `Pool`
handles that allocation for you.

### Read a Proof

`Proof.to_dict()` converts the result into JSON-compatible data. The main fields
are:

- `status`, `reason_code`, and `error`: execution outcome and failure detail.
- `run_id`, `run_dir`, and `duration_ms`: record location and reported duration.
- `log` and `result`: script events and operation-specific return data.
- `state` and `state_hash`: a bounded project summary and its change-detection hash.
- `save`: requested-save outcome, or `null` when no save was requested.
- `teardown_killed`: whether the runner had to terminate a process after it wrote
  its proof.

`proof.ok` means `status == "ok"`. It does not assert musical correctness or
that every generated operation succeeded. `proof_check` checks the proof schema
and log timestamp order, and also accepts a proof dictionary or `proof.json`
path. Assert the required RPP or audio properties separately.

Common reasons are `completed`, `completed_noop`, `lua_error`, `save_failed`,
`timeout`, `reaper_crash`, `proof_missing`, `proof_invalid`, `validation_failed`,
and `fatal`. Environment/filesystem failures inside `run` become error proofs
with `reason_code="fatal"`. `proof.retriable` is true for `timeout`,
`reaper_crash`, and `proof_missing`; direct `run` does not retry automatically.

The summary records at most 50 tracks and 50 markers/regions and does not cover
all project content. Its FNV-1a hash is a change-detection hint, not a
cryptographic digest or whole-project identity. `expect_state_hash=` can produce
`completed_noop` when the summary hash matches. `state_delta` compares summaries;
`is_noop_sequence` detects repeated successful summary hashes. Neither replaces
checking the full saved project.

## Concurrent workers

```python
from rac.runner.pool import Pool

# Input projects and scripts must already exist.
pool = Pool("workers", n_workers=2)
proofs = pool.map([
    {"project": "a.rpp", "script": "a.lua", "save_as": "a-out.rpp"},
    {"project": "b.rpp", "script": "b.lua", "save_as": "b-out.rpp"},
], timeout=60, run_root="runs")

for proof in proofs:
    if not proof.ok:
        raise RuntimeError(proof.to_dict())
```

`Pool` prepares one resource directory per worker and starts a fresh REAPER
process for each job. `map` returns proofs in input order, rejects duplicate
`save_as` paths with `PoolBlocked("blocked:output_conflict")`, and rebuilds and
retries once after `reaper_crash` or `proof_missing`. Jobs must tolerate that
possible retry; resource isolation does not isolate arbitrary script writes.
Use one pool instance per worker root, and a positive integer worker count.

Linux workers share the installed REAPER binary. macOS workers share the
executable in `source_app` (default `/Applications/REAPER.app`), each with a
separate `-newinst` process and explicit configuration. For a custom macOS
installation, pass `source_app` to `Pool`; `RAC_REAPER_BIN` does not override
this pool parameter. The default mode needs no app copies or signing tools.

Optional resource seeding has two forms:

- `seed_resource_dir` supplies a complete initialized resource tree, including
  `Effects`, `Scripts`, `Data`, and plugin caches. On macOS, a seed `REAPER.app`
  is skipped and the executable comes from `source_app`; seed and worker paths
  must not overlap.
- Legacy `seed_config_dir` copies only the selected INI/plugin-cache files in
  `PLUGIN_CACHE_FILES` on macOS. On Linux, it supplies a complete resource tree.
  `seed_resource_dir` takes precedence if both are passed.

For example, `Pool("workers", n_workers=2,
seed_resource_dir="automation-seed")` creates workers from an initialized seed.
The CLI exposes the legacy form as `--seed-config`; full resource seeding is
available through Python. `make_worker` is a lower-level helper returning the
executable path on macOS and the resource directory on Linux.

The Python-only option `copy_app=True` retains legacy macOS app copying and
ad-hoc signing with `codesign --force --deep --sign -`. It timed out during
recorded validation and is not a validated execution mode. Use the default
shared executable; see the [validation record](validation.md).

## Audio checks

```python
from rac.verify import expect_audio

expect_audio("tone.wav").duration(1.0, tol=0.05).not_silent().no_clipping()
expect_audio("tone.wav").dominant_freq(440, tol=5)
```

Audio checks accept mono/stereo 16/24-bit PCM WAV. Stereo analysis uses the
louder channel to avoid phase cancellation; it does not independently validate
both channels. The frequency estimator is intended for tonal test signals.
`no_clipping` applies a sample-peak threshold, not true-peak measurement.

`lufs` is approximate: K weighting and absolute gating, without a relative gate,
using at most the first 30 seconds. Use a standards-compliant meter for mastering
or compliance measurements. MP3, floating-point WAV, and multichannel checks
are outside the current audio reader's scope.

## CLI commands and exit codes

Use `reacli --help` for the command inventory. Individual execution, pool,
initialization, resource-export, and doctor commands accept `--help`.

```bash
reacli rpp validate project.rpp
reacli rpp get project.rpp tracks
reacli rpp get project.rpp track:0:VOLPAN
reacli rpp diff before.rpp after.rpp
reacli knowledge rpp track:VOLPAN
reacli knowledge api GetTrack
reacli verify audio tone.wav --expect duration=1 not_silent=1 no_clipping=1
reacli exec --project project.rpp --script edit.lua --save-as edited.rpp
reacli pool exec --jobs jobs.json --workers 2 --workers-root ./workers
```

The pool jobs file is a JSON array of objects with `project`, `script`, and
optional `save_as` fields, matching the Python example above. CLI pool output is
a summary per job; use the Python API when full `Proof` objects are needed.

Data and execution commands write JSON to stdout. Help, version, and the
doctor's default display are text; use `doctor --json` for structured output.

- `0`: successful command; for RPP diff, no semantic differences found.
- `2`: validation/data failure, a non-retriable `exec` error, or at least one
  failed pool job. Argument-parser usage errors also use `2`.
- `3`: retriable `exec` failure.
- `4`: dispatch/setup errors or a failed doctor check. Runner setup failures
  captured in an `exec` proof instead follow the `exec` exit-code rule above.

Doctor warnings alone do not fail. Inspect each job's `reason_code` for pool
failures; the pool command itself does not distinguish retriable errors by exit
code. A successful `exec` code has the same limits as `proof.ok`.
