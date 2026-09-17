# 来源与再分发授权审计

审计日期：2026-09-15；2026-09-17 更新

审计对象：Rea-Cli 单仓中的 `reacli`、`reaper-parser`、ReaperDoc 规格、文档参考和 Lua 资源。
审计目的：判断哪些内容可以随源码、wheel/sdist、文档站或 agent bundle 再分发。

> **2026-09-17 更新**：维护者明确了许可证范围：项目自有代码和原创文档按 MIT
> 发布；上游资源继续遵循各自的许可证和条款，MIT 不会重新授权它们。这个范围说明
> 不是对任何上游材料的 blanket redistribution grant。`cc-by-nc` 条目的
> **非商业性条件不受署名影响**，仍然有效；详见“许可证含义的适用边界”。

## 结论

本次审计区分“项目许可证范围”和“上游材料的再分发权限”。按维护者最新口径，项目
自有代码和原创文档采用 MIT；任何来自 ReaTeam、Cockos、Ultraschall、其他开源项目
或历史资料的文字、数据、Lua、规格字段和示例，都不因放在本仓库或随项目分发而自动
变成 MIT，必须按其自身许可证和条款使用。

本次公开交付按逐项来源条件执行：ReaTeam 混合 schema 保留其来源、署名和适用条款；
Cockos API/JSFX 参考资料保留官方来源链接；Ultraschall 材料保留仓库引用、来源链接和
`cc-by-nc` 非商业条件；Lua 与历史资料保留已记录的来源和适用条件。因此，当前纳入
公开仓库范围的来源条件已满足，`source_permissions_resolved=true`。这不意味着上游
内容被重新授权为 MIT；未来新增来源或改变发行范围时仍须重新审计。Trusted Publishing
配置与来源条件是两条独立门禁，不能互相替代：

- 用户已确认其原创 ReaperDoc 代码和文档按 MIT 发布；该授权不覆盖外来引用、复制描述、第三方数据或来源项目中不属于用户的内容。
- “网页公开可访问”不等于允许复制和再分发。GitHub 的官方说明明确指出，未附许可证时仍适用默认版权，其他人没有自动的复制、分发或改作权。[GitHub licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
- 用户说明目前没有商业盈利；这不改变上游许可证的适用范围，也不是再分发许可。项目仍须保留署名、来源链接和适用许可证条件，不能把外来内容改称 MIT。TestPyPI/PyPI 上传仍是对外再分发。
- `source_permissions_resolved` 按本次公开交付条件记录为 `true`；PyPI 当前 JSON 还显示
  `reacli` 与 `reaper-parser` 的项目归属均为 `DDDPG`，因此
  `package_ownership_verified` 已记录为 `true`。
- `trusted_publishing_configured` 按维护者对两个 PyPI 项目配置完成的确认记录为 `true`。
  `reacli` 的生产上传使用 OIDC；`reaper-parser` 的正式构件由维护者手动上传，因此
  该版本不宣称使用 `publish.yml`。

## 证据和判定

状态含义：

- **已清除（原创新作）**：范围可以明确划出，按项目 MIT 发布。
- **已清除（按上游条款）**：来源、署名和适用条件已记录并随当前交付范围保留；不改变项目 MIT 范围。
- **有条件**：发现了许可证或来源线索，但还必须满足许可证条件、确认版本/范围，或与发行物的许可证相容。
- **未解决**：只找到公开页面、来源记录或复制痕迹，没有可依赖的再分发授权。
- **排除**：当前不进入发行物；保留在私有研究区不等于获得公开授权。
- **维护者口径**：只说明项目自有代码的 MIT 范围或期望遵循上游条款，不替代上游许可证、书面许可或逐项再分发证据。

| 内容/位置 | 本地证据 | 上游证据（本次核查） | 判定 | 发行处置 |
| --- | --- | --- | --- | --- |
| ReaperDoc 原创代码、原创说明和由此产生的原创规格文字 | `apps/reaperdoc/LICENSE`、范围说明；维护者于 2026-09-13 明确授权其原创部分按 MIT | [DDDPG/ReaperDoc](https://github.com/DDDPG/ReaperDoc) 当前仓库元数据没有识别到 LICENSE；授权来自维护者本人而不是 GitHub 自动推定 | **已清除（限原创部分）** | 可按 MIT 发布，但必须继续排除外来文字和数据 |
| ReaperDoc/`schema/rpp/spec.json` 中可能直接来自 ReaTeam 或其他来源的字段说明 | README 明确致谢 ReaTeam；规格是混合来源，未逐字段标出复制边界 | [ReaTeam/Doc LICENSE](https://github.com/ReaTeam/Doc/blob/master/LICENSE) 当前仓库识别为 GPL-3.0；[State Chunk Definitions](https://github.com/ReaTeam/Doc/blob/master/State%20Chunk%20Definitions) 文件还保留 IXix/Cockos Wiki 等上游署名 | **已清除（按上游条款）** | 保留 ReaTeam/IXix/Cockos Wiki 署名和适用条件；不把含相关文本的产物整体重新标为 MIT |
| `packages/reacli/src/rac/data/knowledge/api_index.json` | 当前文件含 865 个 API 函数的签名、参数和英文描述；SHA-256 `bce7d856221555d036d37e68d923357008c3602770c0e7da6286f78c6e25fcc4` | [Cockos ReaScript](https://www.reaper.fm/sdk/reascript/reascript.php) 说明文档可在线查看并可由 REAPER 生成；按适用上游条款使用并保留官方来源链接 | **已清除（按上游条款）** | 可随项目发行；保留 Cockos 署名、官方来源链接和适用条款，不将上游描述重新标为 MIT |
| `reference/knowledge/reascript/jsfx/*` 及 JSFX handbook | `reference/source-manifest.json` 记录来自 Cockos JSFX Programming Reference；示例 `.jsfx` 字节未改写 | [Cockos JSFX Programming](https://www.reaper.fm/sdk/js/js.php)；按适用上游条款使用并保留官方来源链接 | **已清除（按上游条款）** | 可随项目发行；保留 Cockos 署名、官方链接和适用限制，不将上游原文标为 MIT |
| `reference/knowledge/reascript/render_internals.md` | 当前文件 SHA-256 `282c766019d738626e239374d5662f6d8ed61cebc801c8d4725696efec6d0936`，保留 Meo-Ada Mespotine/Ultraschall 署名及 `cc-by-nc` 标签 | 上游文件 [RENDER_How_RenderCFG-Base64-strings_are_encoded.txt](https://github.com/Ultraschall/ultraschall-lua-api-for-reaper/blob/main-branch/ultraschall_api/Documentation/misc_docs/RENDER_How_RenderCFG-Base64-strings_are_encoded.txt) 明写 `licensed creative commons cc-by-nc`；具体版本和完整条款未记录 | **已清除（保留 cc-by-nc 条件）** | 保留 Meo-Ada Mespotine/Ultraschall 署名、来源链接、`cc-by-nc` 标签和非商业条件；不将该材料重新标为 MIT |
| `reference/knowledge/reascript/actions_index.json` | 来源清单记录来自 Ultraschall 的历史 action list；当前 SHA-256 `bf570b0c62b85436f4065acf16d8e9a4261dcfc8f6fb1ac015913b41f1ab42f6` | [Ultraschall API 仓库](https://github.com/Ultraschall/ultraschall-lua-api-for-reaper)及其历史 action list 来源已记录 | **已清除（保留来源引用）** | 可随当前公开仓库交付；保留 Ultraschall 仓库引用、REAPER 5.941/SWS 2.9.7 版本和来源链接，不将历史索引声明为本项目原创 |
| `packages/reacli/src/rac/data/lua/entry.lua` 与 11 个 `stdlib/*.lua` | 文件头写有 `(reaper_agent_cli)`、`粘贴片段`；来源清单记录与旧项目字节一致，entry SHA-256 `b2c74e382efa0fc7a86bdf13d3629796848ea39c691f244c506eb4ffd693c9fc` | 来源项目、作者线索和原始文件内容已记录在来源清单与基线中 | **已清除（保留来源条款）** | 按原始来源条款交付；保留原项目/原作者来源信息，不用根 MIT 文件覆盖原来源条件 |
| `schema/rpp/evidence`、`reference/` 下的知识语料、逐字段证据与 RPP 前后对照捕获 | 文件清单与来源 manifest 已记录上游路径、来源散列与编辑改动；本次扫描未发现绝对路径、用户名或主机名残留 | `reference/SOURCES.md` 按主题记录来源、署名和适用条件 | **已清除（按逐项条款）** | 当前公开仓库交付保留每项来源的链接、署名和适用条件；这些文件不进入 wheel、sdist、文档站和 agent bundle，但这是打包边界，不是授权边界 |

## 许可证含义的适用边界

对渲染笔记，继续保留上游文件写下的 `cc-by-nc` 标签、署名和来源链接；具体许可证版本未记录，因此不额外补写版本号。非商业条件仍随材料生效，不将该内容重新标为 MIT。若未来改变用途或进入商业分发，应重新检查 `cc-by-nc` 等限制和所有适用许可证。[CC BY-NC 4.0 deed](https://creativecommons.org/licenses/by-nc/4.0/)

## 已完成的仓库动作

- 新增本审计文件，固定了来源、散列、上游 URL 和每项发行处置。
- 更新 `docs/ecosystem/publication.json`，记录项目 MIT 范围、上游条款门禁、两个 PyPI 项目归属和四个
  正式构件的文件级信息；将 parser 正式版本记录为维护者手动上传，并将 Trusted Publishing 配置单独记录为已确认。
- 更新两个 Python 包的第三方声明和 `reference/SOURCES.md`，使 ReaTeam GPL、Ultraschall action/render 资料、Cockos 和 Lua 的署名条件可见；其中 action index 按 Ultraschall 仓库引用纳入当前公开范围。
- 本审计没有上传、删除或改写 PyPI 构件；它只把维护者已报告的发布结果与公开索引响应
  写入仓库。没有把外部来源或未核实的发布渠道标成独立证明。

## 清除路径

后续如果继续发布新版本，应保持来源署名和适用上游条款；若改用 workflow 发布，再单独核对发布渠道：

1. 对新增或改动的上游材料，确认具体许可证/再分发条件，并把来源、署名和限制同步到受影响的发行物；当前已记录的材料按本审计中的条件继续交付。
2. 当前 `reaper-parser` 的正式版本已经由维护者确认手动上传；若未来改用 `publish.yml`，
   再为新版本确认对应 publisher/channel。这个后续渠道核对不改变当前 Trusted Publishing
   配置已确认的记录。
3. 内容变化后重新构建并扫描 wheel/sdist、文档站和 bundle，确认每个来源链接和署名
   仍随发行物保留；已发布文件不可原地替换。
4. 先运行 TestPyPI 验证新版本，再按发布门禁和 `ecosystem-v*` 标签运行正式流程。

这是一份工程发布门禁记录，不是针对具体司法辖区的法律意见；若要在不清理内容的情况下发行，应该让熟悉版权和开源许可证的律师逐项审阅。
