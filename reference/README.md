# REAPER knowledge and Lua examples

Supplemental material for writing ReaScript, understanding `.rpp` projects and
authoring JSFX. The technical notes are primarily in Chinese. They accompany
the Git repository and are excluded from both wheel and source distributions;
`pip install` and the `reacli` runtime do not require this directory.

Start with the maintained [environment guide](../docs/environment.md) and
[API reference](../docs/api.md) to run reacli. Use this collection when you need
background on REAPER's file formats or scripting behavior.

## Explore the collection

- **RPP structure:** [annotated project tree](knowledge/rpp/annotated_tree.md),
  [opaque-block editing boundaries](knowledge/rpp/blob_denylist.md),
  [volume, envelope and timing formulas](knowledge/rpp/semantics_formulas.md),
  [known gaps](knowledge/rpp/gap_registry.md) and the
  [schema extraction report](knowledge/rpp/extract_report.json).
- **ReaScript:** [API pitfalls](knowledge/reascript/api_pitfalls.json),
  [historical action index](knowledge/reascript/actions_index.json),
  [version-specific CLI observations](knowledge/reascript/cli_behavior.md) and
  [rendering notes](knowledge/reascript/render_internals.md).
- **JSFX:** [handbook](knowledge/reascript/jsfx/README.md),
  [structured reference](knowledge/reascript/jsfx/jsfx_reference.json) and
  [gain](knowledge/reascript/jsfx/examples/gain_simple.jsfx),
  [delay](knowledge/reascript/jsfx/examples/delay_basic.jsfx) and
  [MIDI monitor](knowledge/reascript/jsfx/examples/midi_monitor.jsfx) examples.
- **Lua composition:** [template index and project inspector](lua/README.md).
- **Provenance:** [sources and attribution](SOURCES.md) and
  [source and destination hashes](source-manifest.json).

## Resources already included in the package

These have one canonical copy under `src/rac/data/`:

- [ReaScript API index](../src/rac/data/knowledge/api_index.json):
  `reacli knowledge api GetTrack`.
- [RPP schema](../src/rac/data/knowledge/rpp_schema.json):
  `reacli knowledge rpp track:VOLPAN`.
- [Lua entry template](../src/rac/data/lua/entry.lua) and
  [11 standard-library snippets](../src/rac/data/lua/stdlib/):
  `reacli resources --output ./reaper-templates`.

The source collection contained identical copies of these files at import.
The manifest records that baseline; it does not require future maintenance to
keep the files identical to their source.

## Versions and evidence

This is a curated knowledge snapshot, not a complete or current REAPER
specification. `live` and `verified-live` identify observations reported in the
source notes; `doc` refers to documentation and `human` to an author's review.
They do not mean every entry has been retested for this release. Current
project checks are listed separately in [validation](../docs/validation.md).

CLI observations cover REAPER 7.62 on macOS and 7.77/7.78 on Linux. Platform
behavior, startup flags and configuration locations must be checked against
the environment guide and the installed host. Old probes are retained as
observations; the obsolete process-control recipe has been removed.

The action index covers REAPER 5.941 with SWS 2.9.7 and contains 5,188 records.
Check the target host's Action List, action section and installed extensions
before using an ID. `NamedCommandLookup` resolves named extension or custom
commands; it does not validate arbitrary numeric action IDs. An absent ID
does not establish that a newer host lacks that action.

The JSFX reference reflects documentation captured for REAPER 7.78. Its
examples demonstrate concepts and have not undergone current-host DSP
validation. Check the [official reference](https://www.reaper.fm/sdk/js/) for
new features and use the limitations noted in the handbook.

## Maintaining this collection

Keep source hashes immutable. When editing an imported file, update its
`destination_sha256` and `edits` entry in `source-manifest.json`. Use paths
relative to the source project for provenance; do not add private server names,
machine paths, user settings or media. Newly authored examples are identified
separately from imported files.

The original collection's raw HTML, complete SDK copies, duplicate indexes,
extraction intermediates and internal progress documents were not imported.
See the manifest for the exact scope. Attribution and redistribution limits
are documented in [SOURCES.md](SOURCES.md) and
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).
