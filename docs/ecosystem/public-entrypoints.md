# Deferred public entry points / 对外入口待办

Status: **reviewed and deferred by maintainer, 2026-09-17**. This is an inventory,
not a claim that every external publication or deployment control is complete.
The two current PyPI package records are indexed in `publication.json`; no
branch, visibility, publisher or deployment change is authorized by this list.
Account-side publisher administration remains external to this repository cleanup.

| Entry | Current state | Deferred action |
| --- | --- | --- |
| Rea-Cli default branch | **Done 2026-09-17:** `main` is pushed and is the remote default branch. `codex/reaper-ecosystem-alpha` remains as a non-default branch holding the pre-migration history | None. No branch change is blocking a public release |
| Package Documentation / Changelog URLs | `packages/reacli/pyproject.toml` points to `blob/main`; `main` now exists, so the paths resolve | Confirm the rendered links on the project pages after the next upload; the URLs themselves need no change |
| Repository visibility | Private at inspection | The current tracked upstream items have recorded source links, attribution and applicable conditions. The project MIT scope does not relicense `reference/` or `schema/rpp/evidence/`; carry each item's conditions, including the `cc-by-nc` noncommercial condition. See [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md). Changing visibility remains the maintainer's decision |
| Repository About | Description exists; homepage and topics unset | Add the final documentation URL and accurate discovery topics |
| ReaperDoc repository | Independently maintained `DDDPG/ReaperDoc` | Preserve independent ownership; agree on versioned specification exchange |
| Integrated ReaperDoc site | Vite base `/ReaperDoc/`; nested historical deployment workflow | Decide integration preview vs independent site destination before changing base or deployment |
| Site assets | Tailwind CSS is generated locally; no Tailwind runtime CDN or Google Fonts are loaded | Keep the dependency lockfile and local build check current |
| README and changelog publication status | Records `reacli==0.1.0` and `reaper-parser==0.1.0a1` on PyPI | Keep immutable release facts and the next-version process synchronized |
| Security reporting entry | SECURITY.md describes GitHub private reporting with fallback | Verify the enabled reporting channel before public exposure |
| Agent bundle distribution link | Built as a candidate ZIP | Add stable download/version links after the release location is selected |

Local source navigation must work now; external branch-dependent links remain listed
here instead of being silently redirected to a temporary branch. See the
[ReaperDoc maintenance boundary](reaperdoc-maintenance.md).

本轮已把两个 PyPI 正式版本和构件索引写入仓库；长期分支、可见性、正式站点
和稳定下载地址仍需维护者另行确认。此清单不会解除发布门禁，也不把暂定地址
描述为正式入口。
