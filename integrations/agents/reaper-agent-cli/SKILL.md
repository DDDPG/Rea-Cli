---
name: reaper-agent-cli
description: Inspect RPP, execute isolated REAPER jobs, verify saved projects and audio, and use explicit NumPy media workflows through rac.
---
# REAPER agent workflow

This bundle is self-contained. Install the two Python distributions identified by
`compatibility.json`; add the reacli audio extra for the data example. REAPER and Lua
are installed separately. Read `reference/quickstart.md` from this bundle.

1. Run `rac doctor --profile offline --json`; use `full` for host work. Record the
   reported parser/schema/host versions. Write outputs in a new task directory.
2. Inspect with `rac.rpp.parse` and `document.project`. Query `rac knowledge rpp`
   for field semantics. Unknown fields remain raw; do not infer verified meanings.
3. Use rac patch helpers for supported offline changes; use `generate` or validated
   native Lua plus `run(..., save_as=...)` for host edits. Never guess plugin blobs.
4. Check proof, saved state and actual audio separately. A parse or exit code alone
   does not demonstrate audible correctness. Preserve failure manifests; do not
   retry unchanged failing jobs in a loop.
5. Use `rac.media.read_source` for unprocessed media. `render` is an explicit host
   operation. Selected-track rendering retains its send/folder dependency component
   through the master and is not an isolated stem. `import_audio` adds a new track
   with explicit zero fades and saves a new project.
6. Deliver project/media paths and concise results, including unchecked behavior.

Run `examples/data_roundtrip.py NEW_DIRECTORY` for the deterministic NumPy example.
No source checkout, persistent server or MCP server is required.
