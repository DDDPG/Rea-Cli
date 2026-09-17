# ReaScript object and FX contract

[中文](README.zh-CN.md) · [Handbook](../README.md)

ReaScript is the host API; Lua is the language used by this library's execution template. External `import rac` is not an embedded `reaper_python` session. Lua uses `reaper.FunctionName(...)`; Python host bindings have different arguments and return tuples. Consult the target host's generated API documentation or [official API](https://www.reaper.fm/sdk/reascript/reascripthelp.html), rather than mechanically translating signatures.

## Resolve objects before edits

Use `rac knowledge api GetTrack` for a packaged signature, then check availability in the target REAPER (for example `reaper.APIExists`). Indexes can shift after insertion or deletion. Keep stable identity where possible, resolve again after structural edits, and check nil pointers and API return values. Duplicate names are not unique IDs.

| Object | Scope and verification |
|---|---|
| Track / folder | Track indexes are zero-based. Folder depth is a relationship across tracks; verify the closing depth and routing, not just a name containing “Bus”. |
| Item / take | Select the intended item and take. Several helpers address the active take only. Multi-take operations need explicit take enumeration. |
| Envelope | Resolve the specific owner and envelope; absence can return nil. Read scaling mode, sort changed points, and verify time/value pairs. |
| MIDI | Resolve a MIDI take, convert project time through MIDI time-conversion APIs, insert events and sort. Check pitch, channel, velocity and event positions. |
| Marker / region | Enumeration position differs from marker ID. Include both markers and regions when iterating. |
| Send / master | Distinguish send/receive categories and destination. Get master via `GetMasterTrack`, not `GetTrack(0, -1)`. |

The generator only covers its [registered operations](../../packages/reacli/src/rac/luagen/generator.py). Folder management, arbitrary takes and master FX require custom Lua in the entry template. The [showcase](../../examples/show_session.lua) demonstrates that path; its Python builder verifies the resulting session.

## FX: identify, set, read back

1. Resolve the intended track, master or take, and correct FX chain. Match the installed plugin and inspect its returned name. A failed add returns an invalid index; don't continue on that index.
2. Enumerate parameter names and ranges on that instance. Record plugin/version, chain position and parameter identity. Avoid portable claims for a numeric parameter index discovered on one machine.
3. Distinguish normalized control values from physical units. `TrackFX_SetParamNormalized` takes 0–1; a target of 100 Hz or -15 dB is not that number divided by an arbitrary maximum. Plugin mappings can be nonlinear.
4. Read back formatted values, enabled/bypass/offline state and, for EQ, band type and enabled state. Verify after saving and reopening when persistence matters.

The packaged `std_fx.probe` exposes parameters and range information; it does not determine every plugin's physical-unit mapping. For ReaEQ prefer its specialized EQ API where appropriate. For other plugins use documented mapping or a bounded, validated conversion with formatted-value checks. Do not binary-search a non-monotonic or discrete control without checking its behavior.

Examples of acceptance criteria: Melody ReaEQ high-pass at 100 Hz with the band enabled; Chords long reverb with stated room/damping/wet values; Bass compressor threshold -15 dB and makeup +3 dB with auto makeup accounted for; master limiter threshold -4.5 dB. These are showcase targets, not universal defaults or portable parameter indexes. See [showcase builder](../../examples/show_session.py) and [Lua implementation](../../examples/show_session.lua).

## Actions and state persistence

Prefer direct APIs when available. For an action, verify the command, section and required extension in the target Action List. `NamedCommandLookup` resolves named commands; it is not a validator for arbitrary numeric IDs. The bundled action index is historical (REAPER 5.941 / SWS 2.9.7).

Do not assume an API marks the project dirty. The entry protocol handles an explicit `save_as`; check proof and fresh output. ReaScript permits deferred scripts, but this library's synchronous entry template is not an asynchronous lifecycle manager. Use a deliberately separate lifecycle if deferred UI work is required.

## Rendering

Use a fresh render directory and explicit range, sample rate, channels and output format. RPP blocks and API property names differ: API `RENDER_FORMAT` is not a literal RPP `RENDER_CFG` line. Confirm format configuration with the target host rather than fabricating encoded bytes. Include an appropriate tail for reverb/delay and inspect actual output files.

A suppressed dialog or successful process exit does not prove media and FX loaded. Reopen/read back relevant state and verify audio against the task. Details: [runner contract](../workflow/README.md), [render notes](../knowledge/reascript/render_internals.md), [API pitfalls](../knowledge/reascript/api_pitfalls.json), [historical actions](../knowledge/reascript/actions_index.json). These last three are source evidence, not current-host certification.
