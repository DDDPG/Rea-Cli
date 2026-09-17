# REAPER ecosystem alpha

Two independent Python distributions share one lossless RPP document implementation.
`reaper_parser` has no runtime dependencies. `rac` retains its CLI, patch, runner and proof
interfaces. The ReaperDoc integration copy renders generated data from `schema/rpp/spec.json`.
The independent ReaperDoc repository remains separately maintained; see the
[maintenance boundary and synchronization gap](reaperdoc-maintenance.md).

## Install from the monorepo

```sh
python -m pip install ./packages/reaper-parser './packages/reacli[audio,dev]'
python -m pytest -m 'not live'
python tools/generate_schema.py --check
rac doctor --profile offline --json
```

## Published packages

The current PyPI pair is:

```sh
python -m pip install "reacli==0.1.0" "reaper-parser==0.1.0a1"
```

Both projects currently expose the matching wheel and source distribution on
PyPI. See the [reacli release](https://pypi.org/project/reacli/0.1.0/), the
[reaper-parser release](https://pypi.org/project/reaper-parser/0.1.0a1/) and
the [machine-readable publication index](publication.json) for the observed
files and hashes. The `reacli` production upload has a successful OIDC workflow
record; the maintainer confirms that `reaper-parser==0.1.0a1` was uploaded
manually. The parser release is therefore recorded as a live manual upload, not
as a `publish.yml` OIDC upload.

For a candidate release, install BOTH wheels in one command from an unrelated directory:

```sh
python -m pip install /path/to/candidate/reaper-parser/*.whl /path/to/candidate/reacli/*.whl numpy soundfile
```

Lua and REAPER are external prerequisites for host operations. The tested host is
REAPER 7.48/macOS-arm64. [The historical cross-platform CI run](https://github.com/DDDPG/Rea-Cli/actions/runs/34756655368)
passed all 22 jobs: parser on Linux/macOS/Windows (Python 3.10–3.14), rac offline on
Linux/macOS (3.10/3.12/3.14), and Linux candidate wheel installation. These offline
results do not establish Linux or Windows REAPER host acceptance, and do not assert that
the latest post-upload hardening run completed. See [validation.json](validation.json).

## Document contract

```python
from rac.rpp import parse, patch, emit
p = parse('input.rpp')
patch.set_track_name(p, p.tracks()[0], 'Vocal')
assert p.project.tracks[0].name == 'Vocal'
p.save('copy.rpp')  # FileExistsError unless overwrite=True is explicit
```

`Document`, `Element`, `Line`, parse and emit are the same objects through rac and
reaper_parser. Models are views into this one document, including take and FX ranges.
`fields()` enumerates direct values with raw text, 1-based schema indexes and semantic
status. Children and plugin payload remain available in the raw tree. Type conversion
errors are errors, not substituted zeros. `set_raw` and convenience setters are low-level
patches with no semantic-verification claim; `set_field` refuses unverified contracts.

The old rppxml raw_node interface is not retained. All runtime documents are backed by
the shared tree. Legacy parser source and user media remain in their original directory
and in the local baseline archive; they are not copied into wheels.

## Audio interfaces

```python
from rac.media import read_source, render, import_audio
raw = read_source('audio.wav', project='session.rpp')
result = render('session.rpp', work_dir='new-render', time_range=(0, 1))
samples = read_source(result)  # metadata retains level='rendered'
updated = import_audio('session.rpp', 'processed.wav', work_dir='new-import')
```

Arrays are float32 `(frames, channels)`; sample rates and channels are preserved. Source
reading does not apply item transforms, fades or FX. SECTION/MIDI source interpretation
requires the host. Foreign paths need an explicit prefix path_map; overlapping matches
are an error. Paths are never guessed through a search of the user's disk.

Rendering uses a copied project with absolute media references in a fresh output directory,
explicit render settings, isolated resources, bounded execution and checked WAV output.
Track GUID selection includes the connected send/folder dependency component and passes
through the master; it is not an isolated stem. Existing mute/solo state remains meaningful.
`import_audio` adds a new track and item, explicitly disables default fades, saves a new
project, and verifies its GUID, path and timing. It does not embed audio inside RPP.

Each host operation retains manifest.json, proof.json, project snapshots and logs.
Failures carry a reason code and manifest_path. Check structure/fields/host/audio separately.
Rendered silence can be intentional; the demo separately asserts its known signal.

## Reproducible demonstration

```sh
python examples/data_roundtrip.py /absolute/new-directory
```

The example creates stereo 440/660 Hz audio, reads its samples exactly, renders the master,
applies NumPy gain 0.5, imports the result on a new track, and renders that track again.
The final comparison allows two 16-bit PCM steps; the numerical gain check is exact.
The original project hash must remain unchanged. See roundtrip.json and the three manifests.

## Specification and provenance

`schema/rpp/spec.json` is the only editable field source. Field layouts, defaults and unknown
meanings remain explicit. Generate all consumers with `python tools/generate_schema.py`.
The site, parser and rac snapshots share a version/hash. The 23 adopted field mappings are
checked against saved two-value RPP evidence. Historical corrections are retained without
blanket promotion of an entire row to confirmed semantics. Historical TS files in ReaperDoc
are provenance snapshots and are not the site's input.

181 document entries are not 181 fully supported parameters. Use the generated coverage
report; it distinguishes confirmed, documented and unknown semantics. No percentage of all
REAPER internals is claimed. The 68-file local corpus contains related backups.

## Build candidates

```sh
npm ci --prefix apps/reaperdoc
npm run check --prefix apps/reaperdoc
npm run build --prefix apps/reaperdoc
python tools/build_release.py --output dist/new-candidate
```

The output contains two wheel/sdist pairs, static website ZIP, standalone agent ZIP,
examples ZIP, runtime schema and SHA-256 manifest. The builder refuses existing output
folders, checks schema freshness, compares archive runtime bytes to source, and runs twine.
Candidate builds do not upload or change visibility. The current package artifacts are
already live on PyPI but are immutable; because this checkout includes post-upload runtime
hardening, a same-version candidate is for review only and the next upload must use a new
version. The normal future-publication gate remains blocked by the unresolved
source-specific license/permission review. Package ownership and Trusted
Publishing configuration are recorded as cleared; `publication.json` records
MIT only for project-owned code, keeps upstream terms separate, and records that
the existing published wheel metadata cannot be rewritten. The manually
uploaded parser version is not represented as a workflow-channel proof.

## Migration and recovery

`main` is the default branch. It was pushed on 2026-09-17 as a fast-forward of
`codex/reaper-ecosystem-alpha`, which remains as a non-default branch. That branch
preserves pre-existing ReaCli work in a separate snapshot commit, specification work
in a subsequent commit, and directory migration in a separate commit. ReaperDoc
history was imported without squashing. Original sibling folders
were not deleted. Full baseline archives and binary diffs are held only in a
local, Git-ignored `.state/ecosystem-baseline-20260913` directory. They are
**not** in this repository and cannot be downloaded from it; only the summaries
beside this guide are public. The recorded evidence JSON keeps its original
`.state/` paths, which mark evidence that stays on the machine that produced it.

Known scope limits: macOS-only new live evidence; no Windows runner, all-plugin state
interpretation, offline time-stretch reconstruction, live control server or training system.
Performance records are instrumented baselines, not comparative speed claims.
