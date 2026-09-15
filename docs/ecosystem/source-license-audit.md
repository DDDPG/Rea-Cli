# 来源与再分发授权审计

审计日期：2026-09-15

审计对象：Rea-Cli 单仓中的 `reacli`、`reaper-parser`、ReaperDoc 规格、文档参考和 Lua 资源。
审计目的：判断哪些内容可以随源码、wheel/sdist、文档站或 agent bundle 再分发。

## 结论

本次审计先记录了公开来源的许可证缺口；2026-09-15 维护者进一步明确确认
ReaTeam、Cockos 公开资料、Ultraschall 资料以及 GitHub 开源 Lua 资源均可在本项目中
使用，并按来源署名。基于这一维护者授权声明，**来源授权门禁已清除**；它仍然是
维护者声明而非外部机构对本项目发行物的独立背书，来源许可证和署名义务继续保留。
当前候选仍不能公开发布，原因只剩包名所有权和 Trusted Publisher 配置尚未核实：

- 用户已确认其原创 ReaperDoc 代码和文档按 MIT 发布；该授权不覆盖外来引用、复制描述、第三方数据或来源项目中不属于用户的内容。
- “网页公开可访问”不等于允许复制和再分发。GitHub 的官方说明明确指出，未附许可证时仍适用默认版权，其他人没有自动的复制、分发或改作权。[GitHub licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
- 用户说明目前没有商业盈利，且本次明确确认可以使用相关来源；项目仍须保留署名、来源链接和适用许可证条件，不能把外来内容改称 MIT。TestPyPI/PyPI 上传仍是对外再分发。
- `source_permissions_resolved` 已按维护者声明更新为 `true`。`package_ownership_verified` 和
  `trusted_publishing_configured` 仍为 `false`，在这两个门禁通过前不运行公开发布流程。

## 证据和判定

状态含义：

- **已清除（原创新作）**：有维护者授权，且范围可以明确划出。
- **有条件**：发现了许可证或来源线索，但还必须满足许可证条件、确认版本/范围，或与发行物的许可证相容。
- **未解决**：只找到公开页面、来源记录或复制痕迹，没有可依赖的再分发授权。
- **排除**：当前不进入发行物；保留在私有研究区不等于获得公开授权。
- **维护者已确认**：维护者明确承担当前来源使用授权；仍须按来源保留署名、链接和其他适用条件。

| 内容/位置 | 本地证据 | 上游证据（本次核查） | 判定 | 发行处置 |
| --- | --- | --- | --- | --- |
| ReaperDoc 原创代码、原创说明和由此产生的原创规格文字 | `apps/reaperdoc/LICENSE`、范围说明；维护者于 2026-09-13 明确授权其原创部分按 MIT | [DDDPG/ReaperDoc](https://github.com/DDDPG/ReaperDoc) 当前仓库元数据没有识别到 LICENSE；授权来自维护者本人而不是 GitHub 自动推定 | **已清除（限原创部分）** | 可按 MIT 发布，但必须继续排除外来文字和数据 |
| ReaperDoc/`schema/rpp/spec.json` 中可能直接来自 ReaTeam 或其他来源的字段说明 | README 明确致谢 ReaTeam；规格是混合来源，未逐字段标出复制边界 | [ReaTeam/Doc LICENSE](https://github.com/ReaTeam/Doc/blob/master/LICENSE) 当前仓库识别为 GPL-3.0；[State Chunk Definitions](https://github.com/ReaTeam/Doc/blob/master/State%20Chunk%20Definitions) 文件还保留 IXix/Cockos Wiki 等上游署名 | **维护者已确认** | 保留 ReaTeam/IXix/Cockos Wiki 署名和适用许可证；不把上游文本冒充为本项目原创 |
| `packages/reacli/src/rac/data/knowledge/api_index.json` | 当前文件含 865 个 API 函数的签名、参数和英文描述；SHA-256 `bce7d856221555d036d37e68d923357008c3602770c0e7da6286f78c6e25fcc4` | [Cockos ReaScript](https://www.reaper.fm/sdk/reascript/reascript.php) 说明文档可在线查看并可由 REAPER 生成；本次没有找到页面级许可，但维护者确认可整理使用 | **维护者已确认** | 保留 Cockos 来源链接和署名；继续避免把 Cockos 原文声明为本项目原创 |
| `reference/knowledge/reascript/jsfx/*` 及 JSFX handbook | `reference/source-manifest.json` 记录来自 Cockos JSFX Programming Reference；示例 `.jsfx` 字节未改写 | [Cockos JSFX Programming](https://www.reaper.fm/sdk/js/js.php)；官方用户指南示例版本仍写有保留权利：[User Guide PDF](https://www.reaper.fm/userguide/ReaperUserGuide735cc.pdf)；维护者确认可整理使用 | **维护者已确认** | 保留 Cockos attribution、官方链接和适用限制；不把上游原文标为 MIT |
| `reference/knowledge/reascript/render_internals.md` | 当前文件 SHA-256 `282c766019d738626e239374d5662f6d8ed61cebc801c8d4725696efec6d0936`，保留 Meo-Ada Mespotine/Ultraschall 署名及 `cc-by-nc` 标签 | 上游文件 [RENDER_How_RenderCFG-Base64-strings_are_encoded.txt](https://github.com/Ultraschall/ultraschall-lua-api-for-reaper/blob/main-branch/ultraschall_api/Documentation/misc_docs/RENDER_How_RenderCFG-Base64-strings_are_encoded.txt) 明写 `licensed creative commons cc-by-nc`；维护者确认可使用 | **维护者已确认** | 保留 Meo-Ada Mespotine/Ultraschall 署名、来源链接和 `cc-by-nc` 标签；具体版本未知时不补写版本号 |
| `reference/knowledge/reascript/actions_index.json` | 来源清单记录来自 Ultraschall 的历史 action list；当前 SHA-256 `bf570b0c62b85436f4065acf16d8e9a4261dcfc8f6fb1ac015913b41f1ab42f6` | Ultraschall API 仓库没有识别到顶层 LICENSE；维护者确认 GitHub 开源来源可使用 | **维护者已确认** | 保留 Ultraschall 来源、版本和 attribution；不把历史索引声明为本项目原创 |
| `packages/reacli/src/rac/data/lua/entry.lua` 与 11 个 `stdlib/*.lua` | 文件头写有 `(reaper_agent_cli)`、`粘贴片段`；来源清单记录与旧项目字节一致，entry SHA-256 `b2c74e382efa0fc7a86bdf13d3629796848ea39c691f244c506eb4ffd693c9fc` | 维护者确认这些来自 GitHub 开源社区的 Lua 资源可使用 | **维护者已确认** | 保留原项目/原作者链接和适用许可证；不要用根 MIT 文件覆盖原来源条件 |
| `schema/rpp/evidence`、`reference/` 中研究原件、工程备份、插件状态和媒体 | 文件清单与来源 manifest 已记录，部分内容源于本地实验或第三方文档 | 不属于运行时所需的最小发行内容；第三方来源各自的许可没有统一解决 | **排除** | 保持私有；不进入 wheel、sdist、文档站或 agent bundle。Git 仓库若公开也会分发这些文件，因此当前仓库继续 private |

## 许可证含义的适用边界

对渲染笔记，`cc-by-nc` 只能作为上游文件写下的线索，不能自行补成某个具体版本。若最终确认是 CC BY-NC 4.0，其官方条款允许在遵守条件时复制和改编，但要求署名、许可证链接和修改声明，并禁止商业用途；官方说明还提醒，其他权利可能继续限制使用。[CC BY-NC 4.0 deed](https://creativecommons.org/licenses/by-nc/4.0/)

因此，来源门禁现在依据你的维护者声明清除，但发行物仍需按来源保留署名和链接。若未来改变用途或进入商业分发，应重新检查 `cc-by-nc` 等限制和所有适用许可证。

## 已完成的仓库动作

- 新增本审计文件，固定了来源、散列、上游 URL 和每项发行处置。
- 更新 `docs/ecosystem/publication.json`，记录来源授权为维护者确认并将 `source_permissions_resolved` 设为 `true`；包所有权和 Trusted Publisher 仍为 `false`。
- 更新两个 Python 包的第三方声明和 `reference/SOURCES.md`，使 ReaTeam GPL、Ultraschall `cc-by-nc`、Cockos 和 Lua 的署名条件可见。
- 没有上传 PyPI/TestPyPI，没有改包名所有权，也没有把任何未解决项标成已授权。

## 清除路径

接下来只需完成发布身份门禁，并保持来源署名：

1. 在 PyPI 和 TestPyPI 分别确认 `reacli`、`reaper-parser` 的项目归属或首次创建权限。
2. 在两个索引分别配置 `publish.yml` 对应的 Trusted Publisher；GitHub environment 名称按工作流要求填写。
3. 重新构建并扫描 wheel/sdist、文档站和 bundle，确认每个来源链接和署名仍随发行物保留。
4. 先运行 TestPyPI 验证安装，再按发布门禁运行正式流程。

这是一份工程发布门禁记录，不是针对具体司法辖区的法律意见；若要在不清理内容的情况下发行，应该让熟悉版权和开源许可证的律师逐项审阅。
