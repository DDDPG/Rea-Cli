---
name: reaper-agent-cli
description: Operate local REAPER through the ReaCli CLI toolkit. Use for RPP editing, MIDI arrangement, native Lua/ReaScript or JSFX coding, isolated host execution, rendering, audio processing and saved-project verification.
---
# REAPER CLI toolkit

Use the installed `scripts/toolkit.py` relative to this SKILL.md; call it with Python
3.10+ (the installer interpreter works). It binds a tested Python/CLI environment
through runtime.json, so do not rely on whichever `rac` or `python` is on PATH.
Let TOOL denote the absolute path to that script; substitute it in shell commands.
The user's harness provides shell/file tools. No server or transport service is needed.

1. Inspect the request and run `python3 TOOL doctor --profile offline --json`.
   For host work also run `python3 TOOL doctor --profile full --json`. Missing
   resource configuration is repaired with `python3 TOOL rac init`; then recheck.
   A missing REAPER/Lua executable or audio device requires the environment guidance
   in [setup](reference/setup.md). Do not overwrite the user's native REAPER preferences.
   Query the host version with `reaper.GetAppVersion()` in an isolated script;
   invoking the REAPER executable with `--version` can launch a GUI and hang.
2. Use a new output directory and copies of user projects. Existing projects retain
   relative-media context. Never terminate unrelated REAPER processes.
3. Choose the route in [coding](reference/coding.md): RPP views/patch for static edits,
   registered generation for supported operations, native Lua for the rest, JSFX for
   sample processing. `python3 TOOL rac resources --output NEW_DIR` exports canonical
   runtime assets. `python3 TOOL templates NEW_DIR` adds small coding starters.
   Look up APIs via `python3 TOOL rac knowledge api NAME` rather than guessing.
4. Execute authored Python with `python3 TOOL python SCRIPT.py`; it can import rac and
   reaper_parser. Compose custom Lua with `python3 TOOL compose BODY.lua SCRIPT.lua`.
   Use `run(..., save_as=..., run_root=..., timeout=...)` or `rac exec`; inspect operation
   errors and saved RPP. Syntax validation must precede execution. Match units to API
   metadata; do not mistake normalized plugin parameters for dB or Hz.
5. Use explicit `rac.media.render` for audible acceptance. Source audio arrays are not
   project playback. Inspect manifests, proof, saved readback and WAV separately. See
   [verification](reference/verification.md) and [media](reference/media.md).
6. Report output paths and proven checks, including skipped/failed checks. If an operation
   fails, preserve evidence and fix the cause; do not repeatedly retry unchanged host jobs.

These are generic tools, not a prebuilt song. For new compositions author the musical
material and scripts from the user's requirements; installed starters contain no showcase
solution. Do not copy repository demos or existing finished projects as newly generated work.
