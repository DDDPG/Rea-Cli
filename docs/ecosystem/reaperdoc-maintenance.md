# ReaperDoc maintenance boundary / 独立维护边界

ReaperDoc remains an independently maintained repository:
[DDDPG/ReaperDoc](https://github.com/DDDPG/ReaperDoc).
The copy under `apps/reaperdoc` is the Rea-Cli ecosystem integration copy;
it does not replace the independent repository or its website.

## Observed state (2026-09-17)

- The inspected independent checkout is at `6416435`. Its `App.tsx` reads
  `constants.ts`, `supplementData.ts` and `rppStructure.ts`.
- The Rea-Cli integration copy reads `generated.json`, generated from
  [`schema/rpp/spec.json`](../../schema/rpp/spec.json). Its original TS data is
  retained as historical provenance, not an active second specification.
- The earlier ecosystem migration imported ReaperDoc history and changed the
  integration copy's data flow. It did **not** add synchronization to the independent
  repository. Therefore, changes in either checkout do not automatically reach the other.
- The nested `.github/workflows/deploy.yml` is an imported deployment configuration
  for the independent repository. It is inactive in this monorepo. The integration
  build still uses the historical `/ReaperDoc/` base path.

## Current maintenance rules

Keep independent ReaperDoc maintenance and deployment in its own repository.
For current Rea-Cli parser/knowledge changes, edit the local versioned specification
and run `python tools/generate_schema.py`; never hand-edit generated consumers.
Treat substantive independent ReaperDoc updates as upstream review input, with commit,
source attribution and field-level evidence recorded before adopting them here.
Do not claim the two sites or repositories are synchronized.

The long-term specification synchronization mechanism remains pending. A proposed
follow-up is to let ReaperDoc own the versioned specification and let Rea-Cli consume
an explicitly pinned export. That requires adapting the independent site's input,
an export/version contract and consumer checks; it is not implemented by this cleanup.
Do not maintain competing accepted field meanings in the interim: record disagreements
for review before regenerating the ecosystem snapshot.

## 中文说明

ReaperDoc 继续作为独立 GitHub 仓库维护。之前的单仓迁移已经改变了本仓库副本的
数据来源：独立仓库读取 TS 数据，本仓库副本读取生成 JSON。两者目前没有自动同步，
因此不能宣称“单仓已经替代独立仓库”或“两边修改会自动一致”。

本轮仅明确边界，未改动独立仓库、发布 workflow 或站点地址。后续建议让独立
ReaperDoc 管理版本化规格，本仓库固定版本消费导出数据；这仍是待实施方案。
分支、站点地址与部署入口统一列在[对外入口待办](public-entrypoints.md)。
