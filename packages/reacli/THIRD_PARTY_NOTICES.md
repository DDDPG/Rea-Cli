# Third-party software and reference data

The [MIT license](LICENSE) covers project-owned code and original documentation
only. It does not relicense the third-party reference text, code or data described
below. Each upstream item remains under its own license and terms; this notice is
not a blanket redistribution grant.

REAPER is a Cockos product. This project is independent, is not endorsed by
Cockos, and includes no REAPER executables, plugins, installers or license keys.
Users obtain [REAPER](https://www.reaper.fm/) under its own terms.

## Bundled reference data — attribution and source conditions

This notice ships with the package. The repository's
[`THIRD_PARTY_NOTICES.md`](https://github.com/DDDPG/Rea-Cli/blob/main/THIRD_PARTY_NOTICES.md) carries the same wording
plus the Git-only redistribution boundary; keep the two aligned.

- `src/rac/data/knowledge/rpp_schema.json` is now generated from the canonical
  monorepo `schema/rpp/spec.json`, based on **DDDPG/ReaperDoc** commit
  `6416435fdf4cc7e38346fd7875f5d04949b431a2` and recorded adopted evidence.
  The earlier `constants.ts` snapshot at `32047bb` remains historical provenance.
  [DDDPG/ReaperDoc](https://github.com/DDDPG/ReaperDoc) had no explicit license in
  the imported snapshot. On 2026-09-13 the maintainer authorized MIT for original
  ReaperDoc portions; see `apps/reaperdoc/LICENSE` and its scope notice in the
  monorepo. External copied descriptions remain subject to their source terms and
  require source-specific redistribution permission where those terms do not grant
  it. The project MIT scope does not change that boundary.
- ReaperDoc's upstream README credits [ReaTeam State Chunk Definitions](https://github.com/ReaTeam/Doc/blob/master/State%20Chunk%20Definitions).
  The [ReaTeam/Doc repository license](https://github.com/ReaTeam/Doc/blob/master/LICENSE)
  is detected as GPL-3.0, while the file also preserves IXix/Cockos Wiki attribution.
  Any directly copied prose must retain its applicable terms. The ReaperDoc and
  project MIT scopes do not turn this upstream material into MIT or grant rights
  beyond the GPL/source conditions.
- `src/rac/data/knowledge/api_index.json` was extracted from Cockos's generated
  REAPER v7.77 ReaScript API reference. It includes signatures and descriptions.
  Official references: [ReaScript overview](https://www.reaper.fm/sdk/reascript/reascript.php)
  and [generated API help](https://www.reaper.fm/sdk/reascript/reascripthelp.html).
  The reference material is included with its official source links under the
  applicable upstream terms. Retain Cockos attribution and source links with the
  copied descriptions; the project MIT scope does not relicense them.

Before public distribution, preserve the recorded source attribution and applicable
terms. The source gate remains conditional until every bundled upstream item has a
clear source basis or is removed from the artifact; the project MIT license does
not replace the terms of these third-party materials.

## Python dependencies

- Optional `rpp` (Perlence/rpp) uses BSD-3-Clause and is installed as a dependency
  with `reacli[oracle]`. No vendored copy is included in reacli.
- `audioop-lts` supplies Python's removed audioop implementation on Python 3.13+;
  it is installed as a dependency, with its own Python Software Foundation terms.

Lua skeleton/snippets and synthetic test fixtures were copied from the source
project. Their original bytes and source-project-relative paths are recorded in
[the source baseline](https://github.com/DDDPG/Rea-Cli/blob/main/docs/source-baseline.json); changes in the standalone
copy are described in the [changelog](https://github.com/DDDPG/Rea-Cli/blob/main/CHANGELOG.md). The source README mentioned
external composition patterns, but no separate third-party Lua source tree is
included in the Python build.

## Repository-only supplemental references

The material under `reference/` is excluded from both wheel and sdist. That is a
packaging boundary, not a license boundary: the files are tracked in Git, so
publishing the repository publishes them. They are not covered by the project MIT
license and remain subject to each source's terms. The notices below are required
conditions, not a blanket permission to publish.

- The annotated RPP tree and extraction notes derive from ReaperDoc at the
  historical `32047bb` snapshot. Keep the recorded ReaperDoc/ReaTeam attribution
  and include the material only if the applicable source terms allow it.
- The historical action index derives from the Ultraschall API project's
  REAPER 5.941 / SWS 2.9.7 action list. Keep the Ultraschall attribution; the
  upstream repository's license metadata remains recorded as absent, so this item
  needs permission or exclusion before public distribution.
- The rendering notes retain attribution to **Meo-Ada Mespotine / Ultraschall**
  and the source's **cc-by-nc** label. The exact license version is not recorded;
  retain the source label and attribution. These notes must not be presented as
  MIT-licensed material or as permitting commercial redistribution.
- The upstream render file explicitly says `licensed creative commons cc-by-nc`,
  but the version is not stated and the Ultraschall API repository has no detected
  top-level LICENSE. Retain the source link, attribution and any applicable
  noncommercial condition; confirm the exact permission before public distribution.
- The JSFX handbook and structured reference summarize Cockos documentation.
  Retain Cockos attribution and the official links. The material is included under
  the applicable upstream terms and is not relicensed as MIT. The official [JSFX
  programming reference](https://www.reaper.fm/sdk/js/js.php) remains the canonical
  source.

Before public release, preserve these source terms and attribution in every affected
artifact. The detailed decision log is
[source-license-audit.md](https://github.com/DDDPG/Rea-Cli/blob/main/docs/ecosystem/source-license-audit.md).
[Sources and attribution](https://github.com/DDDPG/Rea-Cli/blob/main/reference/SOURCES.md) and the [reference manifest](https://github.com/DDDPG/Rea-Cli/blob/main/reference/source-manifest.json)
identify the files and their provenance.
