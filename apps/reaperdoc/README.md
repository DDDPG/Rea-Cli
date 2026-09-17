# ReaperDoc integration copy

ReaperDoc remains independently maintained at [DDDPG/ReaperDoc](https://github.com/DDDPG/ReaperDoc).
This directory is an ecosystem integration copy, not a replacement for that repository.
The two inputs currently differ and are not automatically synchronized; see the
[maintenance boundary](../../docs/ecosystem/reaperdoc-maintenance.md).

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

For local development, run `npm run dev --prefix apps/reaperdoc` and open
`http://localhost:3000/ReaperDoc/`. The production build retains the historical
`/ReaperDoc/` base; it is not a portable root-path deployment.
The nested deployment workflow is historical upstream configuration, inactive here.
Deployment destinations remain in the [deferred entry-point list](../../docs/ecosystem/public-entrypoints.md).
