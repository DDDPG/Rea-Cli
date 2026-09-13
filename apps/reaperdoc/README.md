# ReaperDoc

The ecosystem specification browser consumes `generated.json`, produced from the only
editable field source at `../../schema/rpp/spec.json`.

From the monorepo root: `python tools/generate_schema.py --check`, then
`npm ci --prefix apps/reaperdoc`, `npm run check --prefix apps/reaperdoc` and
`npm run build --prefix apps/reaperdoc`.

constants.ts, supplementData.ts and rppStructure.ts retain historical provenance; do not
edit them to change the published specification. Saved adopted evidence is under
schema/rpp/evidence; full ignored upstream archives are retained locally, not published.

The original ReaperDoc Git history was imported without squashing. Credit remains with
ReaTeam State Chunk Definitions and the source material recorded in the specification.
Descriptions do not imply every field or every REAPER version has been experimentally verified.
