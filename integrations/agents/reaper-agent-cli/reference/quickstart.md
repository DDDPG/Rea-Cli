# Quickstart

Install the parser wheel and `reacli[audio]` wheel from one ecosystem candidate.
Run `rac resources --output NEW_DIRECTORY` to export the Lua entry, stdlib and RPP fixture.

```python
from rac.rpp import parse, patch
from rac.runner import run
from rac.luagen import generate
from rac.media import read_source, render, import_audio
```

RPP values use their original units: linear gain is not dB. An existing `Line.values`
edit requires dirty marking and document.touch(); prefer patch helpers or views.
`fields()` reports missing semantic knowledge explicitly. `set_raw` bypasses semantic
validation; `set_field` requires an independently verified write contract.

Media arrays have shape `(frames, channels)`, float32, and preserve sample rate.
Raw source audio does not apply project offsets, fades, FX or routing. Render output
has separate lineage. Import adds a new track and uses zero manual/automatic fades.

Use unique output directories. Render and import produce manifest.json and proof.json;
inspect separate structure, field, host and audio checks. Source paths are resolved
relative to their project; foreign or ambiguous paths need explicit path_map entries.

REAPER and plugins are external dependencies with their own terms. Reference descriptions
retain source provenance; publication requires the release prerequisites to be resolved.
