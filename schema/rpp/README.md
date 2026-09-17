# RPP specification source

[Documentation](../../docs/README.md) · [Ecosystem guide](../../docs/ecosystem/README.md) · [Third-party notices](THIRD_PARTY_NOTICES.md)

`schema/rpp/` is the single reviewed source for every RPP consumer in this
repository. Edit `spec.json`, then regenerate the consumers — never edit the
generated JSON by hand.

```bash
python tools/generate_schema.py          # write every generated consumer
python tools/generate_schema.py --check  # verify they are current; writes nothing
python -m pytest tests/conformance -q
```

## Layout

| Path | Role |
|---|---|
| `spec.json` | Reviewed source: sections, entries, fields, corrections and provenance |
| `generated/runtime.json` | Generated consumer shipped as `reaper_parser/data/rpp_schema.json` |
| `generated/docdata.json` | Generated consumer shipped as `apps/reaperdoc/generated.json` |
| `generated/coverage.json` | Generated coverage summary |
| `evidence/` | Recorded live-host evidence behind adopted corrections |
| `LICENSE`, `THIRD_PARTY_NOTICES.md` | License scope for the original and imported parts |

`spec.json` is generated into four tracked files:

```text
schema/rpp/generated/runtime.json
packages/reaper-parser/src/reaper_parser/data/rpp_schema.json
packages/reacli/src/rac/data/knowledge/rpp_schema.json
apps/reaperdoc/generated.json  (via schema/rpp/generated/docdata.json)
```

They are byte-identical per consumer and covered by
`tests/conformance/test_schema.py` and the `--check` gate.

## Reading the provenance fields

Two different upstreams are recorded here, and the field names do not say which
is which. None of the paths below exists in a clone of this repository, and none
of them is a broken link:

- `source_commit` — a commit in the independent
  [DDDPG/ReaperDoc](https://github.com/DDDPG/ReaperDoc) repository, the origin of
  the field descriptions. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
  It is not a commit of this monorepo.
- `source_files` — the ReaperDoc-side inputs (`constants.ts`,
  `supplementData.ts`, `rppStructure.ts`, …) and the hashes recorded at import.
- `sourceFile` (per entry) — a path relative to the **`reaper_agent_cli` source
  workspace** named in
  [`reference/source-manifest.json`](../../reference/source-manifest.json), for
  example `reaper_parser/project.py`. That workspace is the project this
  collection was imported from; it is not shipped and is unrelated to ReaperDoc.
  An empty `sourceFile` means no specific source file was recorded.

`sourceFile` values are retained verbatim as provenance rather than rewritten to
local paths. Removing or remapping them would discard the audit trail; read them
as "where this description came from", not as a navigable path in a clone.

The `reaper_parser` name invites a specific mistake: this repository also has a
`packages/reaper-parser` distribution that imports as `reaper_parser`, but its
modules are `model.py`, `parser.py` and `schema.py`. The workspace-relative
`reaper_parser/envelope.py`, `fx.py`, `item.py`, `project.py`, `take.py`,
`track.py` and `extras.py` refer to the source workspace, not to that package.

Because `rpp_schema.json` ships inside the wheel, where this README is absent,
the same explanation is carried in the data: every generated consumer's `meta`
block has `source_file_base` and `source_file_note`.

## Evidence

`evidence/` records the live-host observations behind adopted corrections,
including paired before/after RPP captures under `evidence/live/` and
`evidence/live-shapes/`. These are audit records: they document what was verified
on a real host and are not executable fixtures. See
[APPLIED.md](evidence/APPLIED.md) and
[behavior-review/RESULTS.md](evidence/behavior-review/RESULTS.md).

Like `reference/`, this directory is excluded from every wheel, sdist,
documentation site and agent bundle, but it **is** tracked in Git, so cloning the
repository clones it too. It is not covered by the project MIT license and may be
published only when each source's terms or separate redistribution permission
allow it; see the
[root README's License section](../../README.md#license).
