# ReaperDoc maintenance boundary / 独立维护边界

ReaperDoc remains an independently maintained repository:
[DDDPG/ReaperDoc](https://github.com/DDDPG/ReaperDoc).
The copy under `apps/reaperdoc` is the Rea-Cli ecosystem integration copy; it
does not replace the independent repository or its website.

The integration copy reads `generated.json`, produced from
[`schema/rpp/spec.json`](../../schema/rpp/spec.json). Historical TypeScript
parameter files in the copy are provenance snapshots, not a second editable
specification. Changes in either repository do not automatically reach the other.

For parser and knowledge changes in this repository, edit `schema/rpp/spec.json`
and run `python tools/generate_schema.py`. Do not hand-edit generated consumers.
The nested `.github/workflows/deploy.yml` under `apps/reaperdoc` is imported
upstream configuration and is inactive here. The integration build still uses
the `/ReaperDoc/` base path.

## 中文说明

ReaperDoc 继续作为独立 GitHub 仓库维护。本仓库副本读取由 `schema/rpp/spec.json`
生成的 JSON；独立仓库读取其自身的 TS 数据。两边没有自动同步，不能宣称单仓已经
替代独立仓库。
