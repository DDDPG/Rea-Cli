# RPP editing contract

[中文](README.zh-CN.md) · [Handbook](../README.md)

RPP is a nested text document with context-dependent fields and opaque state. Use the [parser and patch helpers](../../docs/api.md#read-edit-and-compare-rpp-files); do not apply global string replacements across tracks, items and takes.

## Read, patch, preserve

```python
from pathlib import Path
from rac.rpp import parse, emit, patch
from rac.verify import expect

doc = parse(Path("input.rpp"))  # input must contain a track
track = doc.tracks()[0]
patch.set_track_name(doc, track, "Bass")
patch.set_track_volume(doc, track, 10 ** (-6 / 20))
Path("output.rpp").write_bytes(emit(doc).encode("utf-8"))
expect(parse(Path("output.rpp"))).track(0).name("Bass").volume(10 ** (-6 / 20))
```

Use `Path` for filenames: a missing string path can otherwise be interpreted as RPP text. Preserve untouched nodes, unknown fields, line endings and opaque bytes. Writing bytes avoids newline conversion. The illustrative [annotated tree](../knowledge/rpp/annotated_tree.md) contains annotations, not runnable fixture data.

```bash
rac knowledge rpp track:VOLPAN
rac rpp validate output.rpp
rac rpp get output.rpp track:0:VOLPAN
rac rpp diff input.rpp output.rpp
```

A deliberate edit normally produces a diff (exit 2); inspect it instead of treating any difference as a crash. For stricter comparisons use `semantic_diff(..., strict_guid=True, use_defaults=False)`; even that is not a byte comparator or an audio test.

## Units and context

| Property | RPP context | Host API or rule |
|---|---|---|
| Track gain | `track:VOLPAN`, field 1 | `D_VOL`, linear amplitude |
| Track pan | `track:VOLPAN`, field 2 | `D_PAN`, -1 to 1 |
| Track name | track `NAME` | `P_NAME` on a track |
| Item time | item `POSITION`, `LENGTH` | `D_POSITION`, `D_LENGTH`, seconds |
| Take source offset/rate | appropriate take's `SOFFS`, `PLAYRATE` | `D_STARTOFFS`, `D_PLAYRATE` |
| Track mute | `MUTESOLO`, field 1 | `B_MUTE` |

Schema field numbers are one-based; Python track/item indexes are zero-based. `NAME` and `VOLPAN` do not have one global meaning. Multiple takes require distinguishing their own records; do not rename every `NAME` inside an item. Marker IDs are not enumeration indexes; region serialization must not be guessed from one MARKER row.

`linear = 10 ** (dB / 20)`; for positive gain, `dB = 20 * log10(linear)`. Zero represents negative infinity dB. In the simple constant-rate case, source consumption equals item length × take rate; looping, stretch markers and tempo changes need separate treatment.

Volume-envelope API values can require `ScaleToEnvelopeMode` / `ScaleFromEnvelopeMode` using the actual scaling mode. Do not write those fader-domain values into RPP `PT` rows merely because the API accepts them. See [formula evidence](../knowledge/rpp/semantics_formulas.md); its file-domain findings are historical, not a rule for every envelope type. MIDI PPQ resolution is source-dependent: do not assume 960 or convert project seconds without the tempo map.

## Opaque data and object identity

Preserve VST/AU/CLAP state, JSFX instance serialization, render/record format blocks, encoded metronome data, SysEx, extensions and unknown sources. A host-generated validated whole block can be reused when identity and references remain consistent. Changing `PRESETNAME` does not apply a preset. Arbitrary FXID/GUID replacement can break envelope links. Use host APIs for plugin changes, complex routing/folders or uncertain data.

See [full boundaries](../knowledge/rpp/blob_denylist.md), [known gaps](../knowledge/rpp/gap_registry.md), [schema](../../packages/reacli/src/rac/data/knowledge/rpp_schema.json) and [extraction report](../knowledge/rpp/extract_report.json). Defaults in saved fixtures are host/configuration observations. A clean parse does not establish media availability, routing correctness or valid plugin state.
