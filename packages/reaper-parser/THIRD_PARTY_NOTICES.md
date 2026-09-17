# Sources and distribution scope

Project-owned parser code and original documentation are MIT. The distribution
does not claim one blanket license for the generated field specification. It does
not grant rights to third-party descriptions; each upstream item remains under its
own license and terms.

## Bundled specification

`src/reaper_parser/data/rpp_schema.json` is generated from the monorepo canonical
`schema/rpp/spec.json`, based on ReaperDoc commit
`6416435fdf4cc7e38346fd7875f5d04949b431a2` plus recorded adopted evidence.
The previous rac snapshot used `32047bb`; that is historical provenance, not the
current schema revision. The imported ReaperDoc snapshot had no explicit license. On 2026-09-13 the
maintainer authorized MIT for original ReaperDoc portions; the monorepo records
this in apps/reaperdoc/LICENSE and its scope notice. External copied descriptions
retain their source terms and attribution, and the project MIT scope does not
replace any upstream condition.

ReaperDoc's README credits [ReaTeam State Chunk Definitions](https://github.com/ReaTeam/Doc/blob/master/State%20Chunk%20Definitions).
The [ReaTeam/Doc repository](https://github.com/ReaTeam/Doc) is detected as GPL-3.0;
directly copied prose, if any, remains subject to its applicable terms and is not
covered by this package's MIT notice. ReaTeam attribution and applicable terms remain
required; the mixed-source schema is included with those terms and is not relicensed
as MIT.

## Package boundaries

The parser has no runtime dependencies. It does not bundle rac's Cockos ReaScript
API index, Lua assets, REAPER binaries, NumPy, or repository-only references.
Optional development tools are installed separately under their own terms.
REAPER is a Cockos product; this project is independent and not endorsed by Cockos.

See `../../docs/ecosystem/publication-audit.md` and
`../../docs/ecosystem/source-license-audit.md` in the source repository for the current
release checklist and per-source decision log. The current parser package scope is
cleared under the recorded source conditions; this notice still requires source
attribution and applicable license terms.
