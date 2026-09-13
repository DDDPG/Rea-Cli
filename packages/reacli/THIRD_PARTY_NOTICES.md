# Third-party software and reference data

The [MIT license](LICENSE) covers project-owned code and documentation. It does
not relicense the third-party reference text and data described below.

REAPER is a Cockos product. This project is independent, is not endorsed by
Cockos, and includes no REAPER executables, plugins, installers or license keys.
Users obtain [REAPER](https://www.reaper.fm/) under its own terms.

## Bundled reference data — redistribution review required

- `src/rac/data/knowledge/rpp_schema.json` is now generated from the canonical
  monorepo `schema/rpp/spec.json`, based on **DDDPG/ReaperDoc** commit
  `6416435fdf4cc7e38346fd7875f5d04949b431a2` and recorded adopted evidence.
  The earlier `constants.ts` snapshot at `32047bb` remains historical provenance.
  [DDDPG/ReaperDoc](https://github.com/DDDPG/ReaperDoc) had no explicit license in
  the imported snapshot. On 2026-09-13 the maintainer authorized MIT for original
  ReaperDoc portions; see `apps/reaperdoc/LICENSE` and its scope notice in the
  monorepo. External copied descriptions still require source-specific review.
- `src/rac/data/knowledge/api_index.json` was extracted from Cockos's generated
  REAPER v7.77 ReaScript API reference. It includes signatures and descriptions.
  Official reference: [ReaScript API](https://www.reaper.fm/sdk/reascript/reascripthelp.html).
  No separate redistribution grant was established from the local source files.

Before public distribution, the maintainer must establish permission for these
bundled descriptions/data, or replace them with independently authored data and
re-run schema/API compatibility tests. A project-level license does not grant
rights to these third-party materials. This is the outstanding provenance item
from extracting the internal library; it does not prevent local build/testing.

## Python dependencies

- Optional `rpp` (Perlence/rpp) uses BSD-3-Clause and is installed as a dependency
  with `reacli[oracle]`. No vendored copy is included in reacli.
- `audioop-lts` supplies Python's removed audioop implementation on Python 3.13+;
  it is installed as a dependency, with its own Python Software Foundation terms.

Lua skeleton/snippets and synthetic test fixtures were copied from the source
project. Their original bytes and source-project-relative paths are recorded in
[the source baseline](docs/source-baseline.json); changes in the standalone
copy are described in the [changelog](CHANGELOG.md). The source README mentioned
external composition patterns, but no separate third-party Lua source tree is
included in the Python build.

## Repository-only supplemental references

The material under `reference/` is excluded from both wheel and sdist. Publishing
the Git repository still distributes these files; exclusion from `pip install`
is not a license grant.

- The annotated RPP tree and extraction notes derive from ReaperDoc at the
  historical `32047bb` snapshot, with unresolved source-license status.
- The historical action index derives from the Ultraschall API project's
  REAPER 5.941 / SWS 2.9.7 action list. The import record does not establish a
  separate redistribution grant for the extracted descriptions.
- The rendering notes retain attribution to **Meo-Ada Mespotine / Ultraschall**
  and the source's **cc-by-nc** label. The exact license version and applicable
  source document terms need verification. These notes must not be presented
  as MIT-licensed material or as permitting commercial redistribution.
- The JSFX handbook and structured reference summarize Cockos documentation.
  No independent redistribution grant for upstream descriptions was recorded.

Before public release, resolve these source terms or replace the affected
material with independently authored references. Preserve attribution and
record the resolution. [Sources and attribution](reference/SOURCES.md) and the
[reference manifest](reference/source-manifest.json) identify the files and
their provenance.
