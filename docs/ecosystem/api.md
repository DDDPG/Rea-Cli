# Shared parser and media API

[中文](api.zh-CN.md) · [API index](../api.md) · [Working demonstration](../../examples/data_roundtrip.py)

## Install and choose a layer

From a complete checkout, install both packages for audio workflows:

```sh
python -m pip install ./packages/reaper-parser './packages/reacli[audio]'
```

For document-only work, `python -m pip install ./packages/reaper-parser` is enough.
The parser has no runtime dependency on rac, NumPy or REAPER. Importing/parsing a
project never starts REAPER. Only explicit host operations require REAPER and Lua;
see [environment setup](../environment.md).

## Documents and views

```python
from pathlib import Path
from reaper_parser import parse, emit

doc = parse('<REAPER_PROJECT\n  <TRACK {EXAMPLE}\n    NAME "Vocal"\n    VOLPAN 1 0\n  >\n>\n')
track = doc.project.tracks[0]
track.name = 'Lead vocal'
assert doc.tracks()[0].find_line('NAME').values == ['Lead vocal']
assert 'Lead vocal' in emit(doc)
# Use a fresh destination whose parent directory already exists.
doc.save(Path('edited.rpp'))
```

`parse(source)` accepts a `Path`, a filename string, or RPP text. Prefer `Path` for
files. It returns `Document`; malformed structure raises `RPPParseError` and file
access errors propagate. `emit(doc)` returns text. `doc.save(path, overwrite=False)`
returns a `Path`, refuses existing files with `FileExistsError`, and does not create
parent directories. File decoding/encoding preserves undecodable bytes through
surrogateescape. Unedited documents preserve original text and line endings. File
and text inputs are bounded to 64 MiB, 1,000,000 logical line breaks and 256 nested
chunks; larger or deeper documents are rejected before unbounded parsing work.

`doc.tracks()` returns low-level `Element` objects; `doc.project.tracks` returns
`Track` views of those same nodes. Track items, item takes, FX chains, envelopes,
and sources also reference the shared document. First and later takes/FX use ranges
inside the actual parent. Use view setters or `rac.rpp.patch` for edits; mutating
raw node lists directly requires correct dirty marking and `doc.touch()`.
See [model implementation](../../packages/reaper-parser/src/reaper_parser/model.py).

## Raw fields, evidence and writes

```python
for field in track.fields():
    print(field.token, field.index, field.raw, field.semantic_status,
          field.write_status, field.value)

assert track.raw('VOLPAN', 0) == '1'
assert track.raw('ABSENT') is None
```

`fields()` enumerates direct header/line values, including repeated rows. Each
`FieldValue` has `token`, **1-based** `index`, `raw`, `location`, optional `metadata`,
`semantic_status`, `write_status` and `value`. It does not recursively enumerate
children and is not an inventory of absent fields. `location` is a structural label,
not a byte offset. Unknown semantics return raw strings. Other documented types
may convert to int/float; conversion alone does not mean the semantics are confirmed.
Malformed numeric values raise conversion errors. Inspect status explicitly.

`raw(key, index=0, default=None)` returns a value from the first matching row, using
**0-based** indexing; absent fields return the caller's default. Some convenience
properties have fallback values (for example track volume 1 and pan 0). These are
API fallbacks, not evidence that the field was present or that its default was verified.
Use raw fields/status when missing versus present matters.

`set_raw(key, index, value)` is a low-level write with 0-based indexing. It can add
a missing row at index 0 but rejects invented preceding slots and multiline values.
Convenience setters such as `track.name` use this low-level mechanism.
`set_field(key, index, value)` uses the specification's **1-based** index and rejects
fields without a verified write contract (`ValueError`). It performs the implemented
type validation; do not infer broader host validation. Raw edits do not upgrade field
verification status. Always save and reparse when checking persistent changes.

## Source audio

```python
from rac.media import read_source

# Relative media is resolved against the project's directory.
audio = read_source('media/input.wav', project='session.rpp')
assert audio.samples.ndim == 2
print(audio.sample_rate, audio.metadata['level'])  # level: source
```

`read_source(source, *, project=None, path_map=None)` accepts a media path, a
Take/Source view or a `MediaResult`. Relative paths require a project (views can use
the document's source path). Foreign paths require an explicit prefix mapping such
as `path_map={'D:/session': '/mnt/session'}`. Multiple matching prefixes are an
error; no disk search is performed. In-memory documents need an explicit project
path for relative media.

Returns `AudioData(samples, sample_rate, metadata)`: float32 `(frames, channels)`,
with original channel count/sample rate, source hash and version metadata. No
resampling, downmixing, item offset, fade, playback-rate or FX processing is applied.
MIDI, SECTION and nested project sources require host interpretation. Passing a
render `MediaResult` preserves `level='rendered'`; passing only its filename cannot
recover that lineage. `read_source` rejects audio whose decoded float32 payload
would exceed 256 MiB.

## Explicit host rendering and import

```python
from pathlib import Path
from rac.media import render, read_source, import_audio

rendered = render('session.rpp', work_dir='new-render',
                  sample_rate=48000, channels=2, time_range=(0, 1),
                  tail_seconds=0, timeout=60)
audio = read_source(rendered)
assert audio.metadata['level'] == 'rendered'

# Supply an existing absolute path for the audio being imported.
result = import_audio('session.rpp', Path('processed.wav').resolve(),
                      work_dir='new-import', name='Processed audio',
                      position=0, timeout=60)
print(result.path, result.manifest_path)
```

`render(project, *, work_dir, sample_rate=48000, channels=2, time_range=None,
tail_seconds=0, track_guids=None, path_map=None, reaper_bin=None, timeout=60)`
returns a `MediaResult` pointing to the rendered WAV. Time values are seconds.
With selected track GUIDs it retains connected send/folder dependencies and renders
through master, retaining mute/solo state. This is not isolated stem extraction.

`import_audio(project, audio, *, work_dir, name='Processed audio', position=0,
path_map=None, reaper_bin=None, timeout=60)` returns a `MediaResult` whose `path` is
the **saved RPP**, not an audio file. It creates a new track/item with zero fades,
saves a copy, and checks GUID/path/timing. Use an absolute audio path: `path_map`
applies to project media preparation, not to this new audio argument.

Both operations require a fresh work directory, retain diagnostic manifests and
operate on project copies. `MediaResult` exposes `path`, `manifest_path`, `metadata`
and `proof`; inspect manifest checks and actual saved/audio results, not only process
exit. The original project is not the output destination.

`MediaError` exposes `code` and optional `manifest_path`. Codes distinguish missing
dependencies/media, ambiguous mapping, unsupported source, decoding and host failures.
Invalid numeric options can raise `ValueError`; filesystem errors can propagate.
Early validation may fail before a manifest exists. Keep diagnostics and correct the
cause before rerunning in a new directory. See the [complete deterministic workflow](../../examples/data_roundtrip.py)
and [acceptance boundaries](README.md).
