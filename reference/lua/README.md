# Lua composition contract

[中文](README.zh-CN.md) · [Handbook](../README.md)

Keep the packaged [entry template](../../src/rac/data/lua/entry.lua) and [stdlib](../../src/rac/data/lua/stdlib/) as the canonical resources. Do not vendor another runtime into an agent skill. Export them with `rac resources --output ./templates` (existing files are not overwritten), or read them through `rac.resources.read_text`.

## Generated operations

```python
from rac.luagen import generate
script = generate({"ops": [
    {"op": "track.create", "args": [0, "Vocal"]},
    {"op": "track.set_volume_db", "args": [0, -6.0]},
    {"op": "marker.add", "args": [1, 0.0, "Start"]},
]}, "edit.lua")
```

The parent directory must exist. `generate` overwrites an explicit output, validates operation names/types and runs a compatible `luac -p`. It supports only [OP_REGISTRY](../../src/rac/luagen/generator.py), not every stdlib function or REAPER API. Check returned operation errors even when the body completed.

## Custom bodies

For arbitrary APIs, replace `body()` in the exported entry, retaining its error, save, proof and exit protocol. Set `RUN.result` to JSON-compatible values; check helper return values and raise an error when a required edit fails. `pcall` catches body runtime errors, not syntax errors or every possible failure outside the body. Validate hand-written scripts with `rac.luagen.validate` before execution.

The snippets define `std_*` tables by text composition; they are not `require()` modules. Compose only the needed snippets before `body`. Lua itself supports modules, but these particular files do not return a module table.

| Snippet | Scope | Boundary |
|---|---|---|
| `track.lua` | create/name/gain/pan/mute/color | Read creation identity rules; no universal idempotence |
| `item.lua` | media/time/fades/split | Media path and target item must be resolved |
| `take.lua` | source/name/rate/offset | Helpers use active take; not all exposed as generator ops |
| `fx.lua` | add/probe/parameter/preset/bypass | Normalized controls are not Hz or dB; ordinary tracks only |
| `env.lua` | envelope lookup/points/scaling | Check envelope existence and domain |
| `midi.lua` | item/notes/CC | Use project-time conversion and sort events |
| `marker.lua` | markers/regions | IDs differ from enumeration indexes |
| `routing.lua` | sends | Direction/category and repeated creation matter |
| `project.lua` | tempo/notes/save | Entry `save_as` is the normal persistence path |
| `render.lua` | render configuration/trigger | Verify command availability and actual new output |
| `snapshot.lua` | bounded state summary | Not full project or sound identity |

Read the relevant file under [stdlib](../../src/rac/data/lua/stdlib/) for exact signatures. Helpers commonly return `{ok=true, value=..., affected=...}` or `{ok=false, reason=...}`; check `ok` before consuming `value`.

## Working inspector and complete examples

From the repository root with reacli installed and a Lua 5.3/5.4 compiler:

```bash
python reference/lua/examples/build_inspector.py ./inspect-project.lua
```

The [builder](examples/build_inspector.py) composes [this body](examples/inspect_project.body.lua), checks its boundary and syntax, and refuses an existing output. It requires no running REAPER to build.

```python
from rac.runner import run
proof = run("/absolute/path/to/project.rpp", "inspect-project.lua")
if not proof.ok:
    raise RuntimeError(proof.to_dict())
print(proof.result)
```

This reads version, OS, resource path and track attributes. No `save_as` means no requested save. The entry exits its one-shot host; do not run it in a user's working editor tab. See [small creation example](../../examples/create_project.py) and [full native-synthesis showcase](../../examples/README.md).

The synchronous template does not await deferred callbacks. Extending it for asynchronous work requires managing completion, proof and exit together. Syntax success only validates Lua grammar, not host API availability, successful saves or plugin behavior.
