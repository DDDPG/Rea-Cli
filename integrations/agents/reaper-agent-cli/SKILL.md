---
name: reaper-agent-cli
description: Build, inspect, edit and verify REAPER projects using the reacli Python library and CLI, offline RPP patches, and Lua ReaScript. Use for tracks, folders, items, takes, envelopes, MIDI, FX, routing and rendering; includes JSFX integration guidance.
---

# REAPER Agent CLI

[中文说明](GUIDE.zh-CN.md) · [Developer handbook](../../reference/README.md)

Use the installed `rac` library with this Rea-Cli checkout. This skill is repository-delivered and depends on the sibling `reference/`, `examples/` and package resources. Keep the checkout available if installing the skill elsewhere; resolve all relative links against this file's original directory, or explicitly locate the checkout. Do not claim this directory alone is a standalone runtime. No MCP server is required.

## Establish scope and environment

Locate the checkout and task output directory independently; do not put generated projects in the skill directory. Check `python -m rac --version` in the intended environment and `rac doctor --profile offline --json` (choose `lua` or `full` when needed). Install from the checkout if needed (`python -m pip install -e /absolute/path/to/Rea-Cli`). Actual host work needs REAPER; Lua composition needs the compatible compiler described in the [environment guide](../../docs/environment.md).

Read [invocation and delivery](../../reference/workflow/README.md) before host execution. Use `rac.runner.run` / `rac exec` for isolated one-shot jobs, and `Pool` only for independent retry-safe jobs. Current runner defaults already handle missing scan preferences and process-local macOS restoration suppression. Do not revive the prototype's raw launch/kill loop, vendored `rac_lib`, blanket app-closing rule or “zero external dependencies” claim.

## Route by task

- **Known static fields or inspection:** [RPP contract](../../reference/rpp/README.md). Use `parse(Path(...))`, targeted patch helpers, byte-preserving output, reparse and assertions. Preserve unknown state.
- **Supported intent operations:** [Lua contract](../../reference/lua/README.md). Use `generate`; inspect the actual `OP_REGISTRY` when unsure. Helpers and native APIs are not automatically registered operations.
- **Folders, multi-take edits, master FX or other native operations:** [ReaScript contract](../../reference/reascript/README.md), then compose custom Lua with the packaged entry and only needed snippets. Keep save/proof/exit handling.
- **Audio/MIDI processor authoring:** [JSFX contract](../../reference/jsfx/README.md). Treat EEL2 source and RPP instance state separately.
- **Unknown signature or format field:** query `rac knowledge api FunctionName` or `rac knowledge rpp section:KEY`, then check target-host documentation where the snapshot is insufficient. Use the [evidence catalog](../../reference/knowledge/README.md) only for the relevant topic.

## Implement and verify

Resolve the intended objects and preserve their identity. Indexes shift, names can repeat, marker IDs differ from enumeration positions, and the master requires its own API. Check pointers and return values. Creation, splitting and insertion may repeat destructively; inspect state or start from a fresh input before a retry.

Keep units explicit: RPP gain is linear, generator `track.set_volume_db` takes dB; normalized FX values are not physical units. Probe plugin/parameter names, map using a supported API or validated conversion, and read back formatted values. For EQ verify band type and enabled state. Use the tempo map for MIDI time and the actual envelope scaling mode. Do not guess plugin blobs or region serialization.

Generate or syntax-check Lua **before** submitting it: `run` does not do this. For custom bodies, put serializable results in `RUN.result`, propagate failed required helper calls as errors, and retain the entry protocol. This synchronous entry does not wait for deferred work; a different lifecycle is needed for asynchronous UI tasks.

For edits, supply `save_as` and create the output parent. Input archival is not a filesystem sandbox; the original project opens to preserve relative media paths. Use distinct new render paths and appropriate tails. Do not delete unrelated output or assume a suppressed dialog means media/FX loaded.

Check `proof.ok`, `proof_check`, result-level operation errors and the saved project's target properties. For sound-producing requests, validate the actual audio in supported formats. A summary hash, successful parse, screenshot or process exit is insufficient alone. On failure, inspect run evidence, address the cause and bound any retry. Do not repeatedly launch the same failing job unchanged.

## Starting examples

Use [create_project.py](../../examples/create_project.py) for a small generated edit, the [inspector builder](../../reference/lua/examples/build_inspector.py) for a custom read-only body, or [show_session.py](../../examples/show_session.py) and [its Lua body](../../examples/show_session.lua) for a native-synthesis session with tracks, folders, items, takes, envelopes and FX. Read their arguments before running; create task-specific outputs. The showcase's plugin settings are examples, not defaults for unrelated music tasks.

Deliver the requested project/script, required media or synthesis instructions, and concise verification results with relevant host/plugin versions. Report untested behavior explicitly. Use the user's language. Keep hosted README images and remote repository state unless the task calls for changing them.
