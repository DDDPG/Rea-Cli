# Invocation and delivery contract

[中文](README.zh-CN.md) · [Handbook](../README.md)

Use this contract when building automation on reacli. It describes the current repository, not every REAPER version. Distribution: `reacli`; Python namespace: `rac`; shell commands: `rac` and `reacli` are aliases. External Python orchestrates REAPER; it does not expose live `reaper.*` objects.

## Choose an execution path

| Task | Preferred path | Required evidence |
|---|---|---|
| Inspect or patch known static fields | `rac.rpp` offline | Reparse, targeted assertions, reviewed diff |
| Use a supported generator operation | `rac.luagen.generate` → `rac.runner.run` | Syntax preflight, proof, saved-state assertions |
| Folder depth, multiple takes, master FX, unsupported operations | Custom Lua in the packaged entry template → runner | Same protocol, explicit object/parameter readback |
| FX state, tempo-aware MIDI, render or host-dependent behavior | REAPER API through Lua | Host readback; audio checks when sound is part of the task |
| Design an audio/MIDI processor | JSFX source plus host loading | DSP and reload tests; Lua compiler is insufficient |

Combining offline and host paths is valid. Choose the host when field semantics are uncertain; do not invent an `op` absent from the generator registry.

## Prepare the environment

From a checkout, install with `python -m pip install -e .`. Run the narrowest relevant check:

```bash
rac doctor --profile offline --json
rac doctor --profile lua --json
rac init --resource ./automation-resource
rac doctor --profile full --resource ./automation-resource --json
```

Python 3.10+ is required; Lua generation needs a compatible Lua 5.3/5.4 compiler. Actual execution needs REAPER and platform dependencies. See [environment setup](../../docs/environment.md), including `RAC_LUAC_BIN`, `RAC_REAPER_BIN` and resource precedence. Linux display/audio configuration differs from macOS.

The runner supplies isolation and startup defaults without changing `run()` calls. A missing VST scan preference defaults to no startup rescan; explicit plugin preferences are retained. On macOS, commands append `-ApplePersistence NO` to suppress Cocoa restoration for the automation process without changing global preferences. This does not guarantee every dialog can be skipped. New plugins may need an intentional scan. Do not replace runner management with `killall`, app-copy recipes or a global “REAPER must be closed” rule.

## Execute and inspect

1. Resolve input, output and media locations. Use distinct outputs and create their parent directories. An input archived by the runner is evidence, not a sandbox: the original project opens so relative media can resolve.
2. Generate or validate Lua before `run`. `run` and `rac exec` do not perform syntax preflight themselves.
3. Supply `save_as` for persistent edits using the packaged entry protocol. A read-only inspection can omit it. Do not rely on dirty flags or exit-time saving.
4. Check `proof.ok`, validate the proof, inspect operation errors in `proof.result`, and reparse the actual output. A successful status alone does not mean all generated operations succeeded.
5. If rendering, check the actual new audio file, format and expected signal. Use fresh output names rather than blindly deleting an existing render.

```python
from rac.luagen import validate
from rac.runner import run
from rac.verify import proof_check

validate("edit.lua")
proof = run("input.rpp", "edit.lua", save_as="output.rpp",
            resource="automation-resource", run_root="runs", timeout=60)
if not proof.ok:
    raise RuntimeError(proof.to_dict())
proof_check(proof)
errors = {k: v for k, v in (proof.result or {}).items() if k.endswith("_error")}
if errors:
    raise RuntimeError(errors)
# Assert the task's saved-project/audio properties next.
```

## Failure, retry and concurrency

`timeout`, `reaper_crash` and `proof_missing` are classified retriable, but `run` does not retry automatically. Inspect the run directory before retrying: missing proof may be caused by a modal dialog, incompatible script, crash or protocol failure. Retry only after addressing the cause or establishing that repetition is safe, with a bounded attempt count.

`Pool` may rebuild and retry once after a crash or missing proof. It assigns distinct resource directories, rejects conflicting output paths, and preserves input order. Resource isolation does not make arbitrary Lua filesystem writes safe. Direct concurrent calls must use different resource directories. Creation, splitting and media insertion are not automatically idempotent; use stable identity or fresh inputs, not names alone when duplicates are possible.

## Deliver evidence proportional to the task

Record input/output paths, REAPER/platform/plugin versions when relevant, script, proof and checked properties. Keep source audio with the project or document synthesis/setup. GUI screenshots show placement, not numerical or audio correctness.

`state_hash` is a bounded summary, not whole-project identity. Semantic diff tolerates selected defaults and GUID differences by default; it does not establish identical sound. Audio verification supports mono/stereo 16/24-bit PCM WAV; sample peaks are not true peaks and approximate LUFS is not a compliance meter.

CLI exit codes: `0` success; `2` validation/data or non-retriable execution failure (also a nonempty semantic diff); `3` retriable `exec` failure; `4` setup/dispatch or doctor failure. See [full API contract](../../docs/api.md) for per-command details and [recorded validation](../../docs/validation.md) for tested platforms.
