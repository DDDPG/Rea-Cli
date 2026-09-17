# RPP, Lua/ReaScript and JSFX coding

## Python and RPP

Run Python via `python3 TOOL python authored.py` to use the bound environment.
`from rac.rpp import parse, emit, patch`; `doc.project` is the typed view over the
same document. `doc.tracks()` returns raw Elements. Save copies with `doc.save(path)`.
Fields use original RPP units (volume is linear). Unknown fields/plugin blobs remain
opaque. `fields()` indexes are 1-based; raw access/set_raw use 0-based indexes.
`set_field` rejects unverified semantic writes. Direct tree edits need dirty marking.

## Generated and native Lua

```python
from rac.luagen import generate, validate
from rac.runner import run
script = generate({'ops': [{'op': 'track.create', 'args': [0, 'Voice']}]}, 'create.lua')
proof = run('input.rpp', script, save_as='copy.rpp', run_root='runs', timeout=60)
assert proof.ok, proof.to_dict()
```

Discover supported operations with `from rac.luagen.generator import OP_REGISTRY`.
Generate checks argument types and Lua syntax; it does not wrap the entire REAPER API.
Use native ReaScript for folder depth, alternate takes, master FX and plugin parameters.
Write `local function body() ... RUN.result = {...} end` in a separate file and run
`python3 TOOL compose authored.body.lua authored.lua`. This uses the installed entry
skeleton, preserves proof/save/exit behavior and validates Lua. `assets/inspect.body.lua`
is a minimal read-only body, not a standalone script. Add assertions for every native
API operation whose failure matters. Return JSON-friendly scalars/tables in RUN.result.

Look up signatures with `python3 TOOL rac knowledge api CreateNewMIDIItemInProj`, etc.
MIDI API times may be PPQ: convert using MIDI_GetPPQPosFromProjTime for each take.
Set tempo before building time-dependent data. Use MIDI_Sort after bulk note insertion.
For folder routing, set I_FOLDERDEPTH deliberately and check closing child depth.
For alternate takes, do not assume AddTakeToMediaItem gives a valid MIDI source.
Inspect an actual MIDI source/take and use host APIs to create/copy it appropriately.

FX AddByName failures return negative indexes; assert success. Check actual plugin
parameter names and formatted values before choosing values: normalized 0..1 does not
mean dB/Hz. For EQ use TrackFX_SetEQParam when suitable. ReaComp Wet output is distinct
from the host Wet mix; read both. Save/reopen and verify settings. Avoid guessed plugin
state blobs. For volume envelopes check scaling mode and use ScaleToEnvelopeMode;
pan envelopes have a different domain. Native REAPER help is authoritative.

## JSFX/EEL2

`assets/gain_simple.jsfx` is a stereo dB-gain starter. JSFX is EEL2, not Lua.
Use @init for state, @slider for coefficient changes and @sample for per-sample DSP.
Define desc/slider metadata; explicitly decide channel handling and reset behavior.
Install new effects only into a dedicated REAPER resource's Effects directory, then
load through a JS: effect name and verify actual audio. `luac` cannot validate JSFX.
A parsed RPP or successful script proof is not a DSP test. Use deterministic tones,
check sample rate/channels/duration, gain or spectral behavior, and clipping.
