# Third-party software and reference data

The [MIT license](LICENSE) covers project-owned code and documentation. It does
not relicense the third-party reference text and data described below.

REAPER is a Cockos product. This project is independent, is not endorsed by
Cockos, and includes no REAPER executables, plugins, installers or license keys.
Users obtain [REAPER](https://www.reaper.fm/) under its own terms.

## Bundled reference data — attribution and source conditions

- `src/rac/data/knowledge/rpp_schema.json` is now generated from the canonical
  monorepo `schema/rpp/spec.json`, based on **DDDPG/ReaperDoc** commit
  `6416435fdf4cc7e38346fd7875f5d04949b431a2` and recorded adopted evidence.
  The earlier `constants.ts` snapshot at `32047bb` remains historical provenance.
  [DDDPG/ReaperDoc](https://github.com/DDDPG/ReaperDoc) had no explicit license in
  the imported snapshot. On 2026-09-13 the maintainer authorized MIT for original
  ReaperDoc portions; see `apps/reaperdoc/LICENSE` and its scope notice in the
  monorepo. On 2026-09-15 the maintainer confirmed that the acknowledged external
  material may also be used with source attribution; the applicable source terms
  remain in force.
- ReaperDoc's upstream README credits [ReaTeam State Chunk Definitions](https://github.com/ReaTeam/Doc/blob/master/State%20Chunk%20Definitions).
  The [ReaTeam/Doc repository license](https://github.com/ReaTeam/Doc/blob/master/LICENSE)
  is detected as GPL-3.0, while the file also preserves IXix/Cockos Wiki attribution.
  The maintainer confirmed use of this material; any directly copied prose must retain
  its applicable terms and the ReaperDoc MIT scope does not turn it into MIT.
- `src/rac/data/knowledge/api_index.json` was extracted from Cockos's generated
  REAPER v7.77 ReaScript API reference. It includes signatures and descriptions.
  Official references: [ReaScript overview](https://www.reaper.fm/sdk/reascript/reascript.php)
  and [generated API help](https://www.reaper.fm/sdk/reascript/reascripthelp.html).
  The inspected pages provide access to the reference but no separate redistribution
  grant for copying the descriptions into a package was found; the maintainer confirms
  that the reference can be curated and used with Cockos attribution and source links.

Before public distribution, preserve the recorded source attribution and applicable
terms. The source gate is marked resolved by the maintainer's 2026-09-15 attestation;
the project MIT license does not replace the terms of these third-party materials.

## Python dependencies

- Optional `rpp` (Perlence/rpp) uses BSD-3-Clause and is installed as a dependency
  with `reacli[oracle]`. No vendored copy is included in reacli.
- `audioop-lts` supplies Python's removed audioop implementation on Python 3.13+;
  it is installed as a dependency, with its own Python Software Foundation terms.

Lua skeleton/snippets and synthetic test fixtures were copied from the source
project. Their original bytes and source-project-relative paths are recorded in
[the source baseline](../../docs/source-baseline.json); changes in the standalone
copy are described in the [changelog](../../CHANGELOG.md). The source README mentioned
external composition patterns, but no separate third-party Lua source tree is
included in the Python build.

## Repository-only supplemental references

The material under `reference/` is excluded from both wheel and sdist. Publishing
the Git repository still distributes these files; exclusion from `pip install`
is not a license grant.

- The annotated RPP tree and extraction notes derive from ReaperDoc at the
  historical `32047bb` snapshot. The maintainer confirms use with the recorded
  ReaperDoc/ReaTeam attribution.
- The historical action index derives from the Ultraschall API project's
  REAPER 5.941 / SWS 2.9.7 action list. The maintainer confirms use with Ultraschall
  attribution; the upstream repository's license metadata remains recorded as absent.
- The rendering notes retain attribution to **Meo-Ada Mespotine / Ultraschall**
  and the source's **cc-by-nc** label. The exact license version is not recorded;
  retain the source label and attribution. These notes must not be presented as
  MIT-licensed material or as permitting commercial redistribution.
- The upstream render file explicitly says `licensed creative commons cc-by-nc`,
  but the version is not stated and the Ultraschall API repository has no detected
  top-level LICENSE. The maintainer confirms use; retain the source link, attribution
  and any applicable noncommercial condition.
- The JSFX handbook and structured reference summarize Cockos documentation.
  No page-level redistribution grant was located during inspection. The maintainer
  confirms use with Cockos attribution and source links. The official [JSFX programming
  reference](https://www.reaper.fm/sdk/js/js.php) is a public reference page, and one
  official user-guide PDF version states that reproduction requires permission:
  [REAPER User Guide](https://www.reaper.fm/userguide/ReaperUserGuide735cc.pdf).

Before public release, preserve these source terms and attribution in every affected
artifact. The detailed decision log is
[source-license-audit.md](../../docs/ecosystem/source-license-audit.md).
[Sources and attribution](../../reference/SOURCES.md) and the [reference manifest](../../reference/source-manifest.json)
identify the files and their provenance.
