# REAPER ecosystem

Two independent Python distributions share one lossless RPP document
implementation. `reaper_parser` has no runtime dependencies. `rac` provides the
CLI, patch, runner and proof interfaces. The ReaperDoc integration copy renders
generated data from `schema/rpp/spec.json`; the independent ReaperDoc repository
remains separately maintained. See the
[maintenance boundary](reaperdoc-maintenance.md).

## Install from the monorepo

```sh
python -m pip install ./packages/reaper-parser './packages/reacli[audio,dev]'
python -m pytest -m 'not live'
python tools/generate_schema.py --check
reacli doctor --profile offline --json
```

## Published packages

```sh
python -m pip install "reacli==0.1.0" "reaper-parser==0.1.0a1"
```

See the [reacli release](https://pypi.org/project/reacli/0.1.0/) and the
[reaper-parser release](https://pypi.org/project/reaper-parser/0.1.0a1/).
For a candidate, install both wheels from an unrelated directory:

```sh
python -m pip install /path/to/candidate/reaper-parser/*.whl /path/to/candidate/reacli/*.whl numpy soundfile
```

Lua and REAPER are external prerequisites for host operations. See
[validation](../validation.md) for coverage and limits.

## Document contract

```python
from rac.rpp import parse, patch, emit
p = parse('input.rpp')
patch.set_track_name(p, p.tracks()[0], 'Vocal')
assert p.project.tracks[0].name == 'Vocal'
p.save('copy.rpp')  # FileExistsError unless overwrite=True is explicit
```

`Document`, `Element`, `Line`, parse and emit are the same objects through rac
and reaper_parser. Models are views into this one document, including take and
FX ranges. `fields()` enumerates direct values with raw text, 1-based schema
indexes and semantic status. Type conversion errors are errors, not substituted
zeros. `set_raw` and convenience setters are low-level patches with no
semantic-verification claim; `set_field` refuses unverified contracts.

The old rppxml `raw_node` interface is not retained. All runtime documents are
backed by the shared tree.

## Audio interfaces

```python
from rac.media import read_source, render, import_audio
raw = read_source('audio.wav', project='session.rpp')
result = render('session.rpp', work_dir='new-render', time_range=(0, 1))
samples = read_source(result)  # metadata retains level='rendered'
updated = import_audio('session.rpp', 'processed.wav', work_dir='new-import')
```

Arrays are float32 `(frames, channels)`; sample rates and channels are
preserved. Source reading does not apply item transforms, fades or FX.
SECTION/MIDI source interpretation requires the host. Foreign paths need an
explicit prefix `path_map`; overlapping matches are an error.

Rendering uses a copied project with absolute media references in a fresh
output directory. `import_audio` adds a new track and item, explicitly disables
default fades, saves a new project, and verifies GUID, path and timing. It does
not embed audio inside RPP. Each host operation retains `manifest.json`,
`proof.json`, project snapshots and logs.

## Reproducible demonstration

```sh
python examples/data_roundtrip.py /absolute/new-directory
```

The example creates stereo 440/660 Hz audio, reads its samples, renders the
master, applies NumPy gain 0.5, imports the result on a new track, and renders
that track again. See [examples/README.md](../../examples/README.md).

## Specification

`schema/rpp/spec.json` is the only editable field source. Generate all consumers
with `python tools/generate_schema.py`. Coverage distinguishes confirmed,
documented and unknown semantics; entry count is not a claim of full REAPER
support. See [schema/rpp/README.md](../../schema/rpp/README.md).

## Build candidates

```sh
npm ci --prefix apps/reaperdoc
npm run check --prefix apps/reaperdoc
npm run build --prefix apps/reaperdoc
python tools/build_release.py --output dist/new-candidate
```

The output contains two wheel/sdist pairs, a static website ZIP, a standalone
agent ZIP, an examples ZIP, runtime schema and a SHA-256 manifest. Candidate
builds do not upload packages. See [releasing](../releasing.md).
