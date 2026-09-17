# Third-party software and reference data

The [MIT license](LICENSE) covers project-owned code and original documentation
only. It does not relicense the third-party reference text, code or data
described below. Each upstream item remains under its own license and terms.
This notice records scope and provenance; it is not a blanket redistribution grant.

REAPER is a Cockos product. This project is independent, is not endorsed by
Cockos, and includes no REAPER executables, plugins, installers or license keys.
Users obtain [REAPER](https://www.reaper.fm/) under its own terms.

## Bundled reference data — attribution and source conditions

This section covers the data shipped inside the wheels and sdists. For material
that stays in the Git repository only, see
[Repository-only supplemental references](#repository-only-supplemental-references).
`packages/reacli/THIRD_PARTY_NOTICES.md` ships the same notice with the package;
the two are kept aligned.

- `packages/reacli/src/rac/data/knowledge/rpp_schema.json` is now generated from the canonical
  monorepo `schema/rpp/spec.json`, based on **DDDPG/ReaperDoc** commit
  `6416435fdf4cc7e38346fd7875f5d04949b431a2` and recorded adopted evidence.
  The earlier `constants.ts` snapshot at `32047bb` remains historical provenance.
  [DDDPG/ReaperDoc](https://github.com/DDDPG/ReaperDoc) had no explicit license in
  the imported snapshot. On 2026-09-13 the maintainer authorized MIT for original
  ReaperDoc portions; see `apps/reaperdoc/LICENSE` and its scope notice in the
  monorepo. External copied descriptions still require source-specific review and
  are not relicensed by that grant.
- `packages/reacli/src/rac/data/knowledge/api_index.json` was extracted from Cockos's generated
  REAPER v7.77 ReaScript API reference. It includes signatures and descriptions.
  Official reference: [ReaScript API](https://www.reaper.fm/sdk/reascript/reascripthelp.html).
  The reference material is included with its official source link under the
  applicable upstream terms. Retain Cockos attribution and source links with the
  copied descriptions; the project MIT scope does not relicense them.

The project follows each upstream license and term. A project-level license does
not relicense these third-party materials; preserve their source links, notices
and applicable conditions, and re-run the audit if the scope or distribution
context changes.

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

The material under `reference/` and `schema/rpp/evidence/` is excluded from every
wheel, sdist, documentation site and agent bundle. That is a packaging boundary,
not a license boundary: those files are tracked in Git, so cloning or
redistributing this repository distributes them too.

This material is not covered by the project's MIT license. The current repository
delivery carries each item's attribution, source link and applicable conditions
with the notices below. Keep those conditions with every future copy:

- The annotated RPP tree and extraction notes derive from ReaperDoc at the
  historical `32047bb` snapshot. Retain the ReaperDoc and ReaTeam attribution
  recorded in [reference/SOURCES.md](reference/SOURCES.md); the ReaperDoc MIT
  scope does not relicense externally copied descriptions.
- The historical action index derives from the Ultraschall API project's
  REAPER 5.941 / SWS 2.9.7 action list. Retain the
  [Ultraschall API repository citation](https://github.com/Ultraschall/ultraschall-lua-api-for-reaper),
  attribution, version and source link with the index.
- The rendering notes retain attribution to **Meo-Ada Mespotine / Ultraschall**
  and the source's **cc-by-nc** label. The [source file](https://github.com/Ultraschall/ultraschall-lua-api-for-reaper/blob/main-branch/ultraschall_api/Documentation/misc_docs/RENDER_How_RenderCFG-Base64-strings_are_encoded.txt)
  and attribution remain attached to the notes; the **noncommercial condition
  still applies**. The exact license version is not recorded. These notes are
  not relicensed as MIT and are not for commercial redistribution.
- The JSFX handbook and structured reference summarize Cockos documentation.
  Retain the Cockos attribution and official links. The material is included
  under the applicable upstream terms and is not relicensed as MIT.

The current source-gate decision is recorded in
[the publication audit](docs/ecosystem/source-license-audit.md). The current
repository scope is cleared under the recorded source conditions. Preserve
attribution and applicable terms in future releases; the [sources and attribution](reference/SOURCES.md)
and [reference manifest](reference/source-manifest.json) identify the files and
their provenance.
