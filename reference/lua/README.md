# Lua templates and composition examples

The package includes one [entry template](../../src/rac/data/lua/entry.lua) and
[11 standard-library snippets](../../src/rac/data/lua/stdlib/). These matched
the original project's `lua/` tree byte for byte at import. This directory
provides navigation and a runnable composition example, without maintaining a
second template tree.

## Export the package resources

After installing reacli, export the templates to a new directory:

```bash
reacli resources --output ./reaper-templates
```

The export includes `entry.lua`, `minimal.rpp` and all 11 snippets. It refuses
to overwrite existing files. The entry template catches errors in `body()`,
collects project state, writes `proof.json` and exits the one-shot REAPER
process. Use it with the runner and an isolated instance configured as described
in the [environment guide](../../docs/environment.md).

## Standard-library snippets

- [track.lua](../../src/rac/data/lua/stdlib/track.lua): track creation, names, volume, pan and color.
- [item.lua](../../src/rac/data/lua/stdlib/item.lua): media insertion, position, length, fades and splits.
- [take.lua](../../src/rac/data/lua/stdlib/take.lua): playback rate, source offset and pitch.
- [fx.lua](../../src/rac/data/lua/stdlib/fx.lua): lookup, insertion, parameters and bypass.
- [env.lua](../../src/rac/data/lua/stdlib/env.lua): envelope lookup, points and scaling conversions.
- [midi.lua](../../src/rac/data/lua/stdlib/midi.lua): MIDI items, notes and controller events.
- [marker.lua](../../src/rac/data/lua/stdlib/marker.lua): markers and regions.
- [routing.lua](../../src/rac/data/lua/stdlib/routing.lua): sends and routing parameters.
- [project.lua](../../src/rac/data/lua/stdlib/project.lua): tempo, project notes and saving.
- [render.lua](../../src/rac/data/lua/stdlib/render.lua): render configuration and triggering.
- [snapshot.lua](../../src/rac/data/lua/stdlib/snapshot.lua): project state inspection.

These snippets define `std_*` tables through text composition. They are not
`require()` modules and do not return a module table. Operations commonly
return `{ok=true, value=..., affected=...}` or `{ok=false, reason=...}`; check
`ok` before using a result. Track indexes generally start at zero. Read the
specific function before relying on repeatability: finding a named track can
be repeatable, while unconditional creation and media insertion are not.

For supported operations, use `rac.luagen.generate()` to validate parameters
and select the required snippets. See the
[project creation example](../../examples/create_project.py). The inspector
below shows how to compose arbitrary ReaScript logic with the same entry
template.

## Build a project inspector

Prerequisites: a repository checkout, reacli installed in the active Python
environment, and a **Lua 5.3 or 5.4** compiler. On macOS, use `brew install
lua@5.4`; set `RAC_LUAC_BIN` if discovery needs an explicit compiler path.
REAPER is not needed for this build step.

Run from the repository root:

```bash
python reference/lua/examples/build_inspector.py ./inspect-project.lua
```

[build_inspector.py](examples/build_inspector.py) inserts
[inspect_project.body.lua](examples/inspect_project.body.lua) into the installed
entry template, runs syntax validation, then writes the requested output.
The output's parent directory must exist; an existing output is never
replaced. The builder exits with an error if the compiler is unavailable,
validation fails, or the entry template's composition boundary has changed.

The body reads the REAPER version, OS, resource path, track names, linear
volumes and pan values into `RUN.result`. It does not change the project.

After following the environment guide, run it on a disposable project copy:

```python
from rac.runner import run

proof = run("/absolute/path/to/project-copy.rpp", "inspect-project.lua")
if proof.status != "ok":
    raise RuntimeError(proof.to_dict())
print(proof.result)
```

No `save_as` is supplied, so this invocation does not save the project. The
complete entry template exits its REAPER host after inspection; it is intended
for the runner's one-shot process, not for direct use in a working editor
session. Lua syntax validation does not validate host APIs or replace a live
REAPER run. For an operation that should save changes, set `save_as` explicitly
and check both the proof and the resulting file.
