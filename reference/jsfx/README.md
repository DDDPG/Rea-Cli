# JSFX authoring and integration

[中文](README.zh-CN.md) · [Handbook](../README.md)

Use JSFX for audio/MIDI processing inside an FX instance. JSFX uses EEL2; it is neither a Lua script nor the Python orchestration layer. Start from the [official reference](https://www.reaper.fm/sdk/js/). The imported handbook is a REAPER 7.78-era snapshot, not current-host DSP validation.

## Source and instance are separate

Keep authored source under a distinct name in the dedicated REAPER resource directory's `Effects` tree; include required imports/assets. Load it through the host and verify the intended track/take/master and active instance. RPP `<JS>` data is saved instance state; do not infer its serialization from the source slider declarations alone. Preserve unknown state as described in [RPP boundaries](../rpp/README.md).

## Development checks

Separate initialization, parameter updates, block processing and sample processing. Account for sample-rate changes, channel scope, memory initialization and state persistence. MIDI processing must preserve timing and any messages not intentionally transformed. GUI state and audio state can interact; do not assume GUI callbacks run like the audio loop. Consult the exact lifecycle and language behavior in the official documentation before using unfamiliar facilities.

Load in a disposable host project; verify signal behavior at relevant sample rates and parameter extremes. Check silence, bypass, gain changes, clipping, latency and tails as appropriate. Save/reopen and compare expected state. `luac -p` does not compile EEL2, and successful RPP parsing does not test DSP.

## Existing learning material

- [Historical handbook](../knowledge/reascript/jsfx/README.md): lifecycle, variables, EEL2 syntax, function groups and illustrative algorithms; original mixed-language notes.
- [Structured reference](../knowledge/reascript/jsfx/jsfx_reference.json): search by exact symbol; preserve version metadata.
- [Gain](../knowledge/reascript/jsfx/examples/gain_simple.jsfx): stereo only; no smoothing for abrupt gain changes.
- [Delay](../knowledge/reascript/jsfx/examples/delay_basic.jsfx): zero-delay setting reads the old buffer slot, and the declared tail does not model full feedback decay. Correct and test before production use.
- [MIDI monitor](../knowledge/reascript/jsfx/examples/midi_monitor.jsfx): illustrative source; verify event flow on the target host.

The handbook's Chamberlin SVF fragment is not guaranteed stable over its exposed controls. These examples were not DSP-tested as part of the documentation reorganization. Attribution is retained in [sources](../SOURCES.md); repo inclusion does not relicense upstream text.
