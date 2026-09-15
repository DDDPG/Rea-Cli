# 来源与再分发授权审计

审计日期：2026-09-15

审计对象：Rea-Cli 单仓中的 `reacli`、`reaper-parser`、ReaperDoc 规格、文档参考和 Lua 资源。
审计目的：判断哪些内容可以随源码、wheel/sdist、文档站或 agent bundle 再分发。

## 结论

本次审计只清除了维护者明确拥有并授权的原创部分。当前候选仍然是**部分清除、不得公开发布**：

- 用户已确认其原创 ReaperDoc 代码和文档按 MIT 发布；该授权不覆盖外来引用、复制描述、第三方数据或来源项目中不属于用户的内容。
- “网页公开可访问”不等于允许复制和再分发。GitHub 的官方说明明确指出，未附许可证时仍适用默认版权，其他人没有自动的复制、分发或改作权。[GitHub licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
- 用户说明目前没有商业盈利，这只可能满足某些非商业许可证的一个条件；它不能替代授权、署名、许可证链接、修改声明，也不能把内容改成 MIT。TestPyPI/PyPI 上传仍是对外再分发。
- `source_permissions_resolved` 必须继续为 `false`。在外来内容取得书面许可、逐项重写或从发行物移除前，不运行任何公开发布流程。

## 证据和判定

状态含义：

- **已清除（原创新作）**：有维护者授权，且范围可以明确划出。
- **有条件**：发现了许可证或来源线索，但还必须满足许可证条件、确认版本/范围，或与发行物的许可证相容。
- **未解决**：只找到公开页面、来源记录或复制痕迹，没有可依赖的再分发授权。
- **排除**：当前不进入发行物；保留在私有研究区不等于获得公开授权。

| 内容/位置 | 本地证据 | 上游证据（本次核查） | 判定 | 发行处置 |
| --- | --- | --- | --- | --- |
| ReaperDoc 原创代码、原创说明和由此产生的原创规格文字 | `apps/reaperdoc/LICENSE`、范围说明；维护者于 2026-09-13 明确授权其原创部分按 MIT | [DDDPG/ReaperDoc](https://github.com/DDDPG/ReaperDoc) 当前仓库元数据没有识别到 LICENSE；授权来自维护者本人而不是 GitHub 自动推定 | **已清除（限原创部分）** | 可按 MIT 发布，但必须继续排除外来文字和数据 |
| ReaperDoc/`schema/rpp/spec.json` 中可能直接来自 ReaTeam 或其他来源的字段说明 | README 明确致谢 ReaTeam；规格是混合来源，未逐字段标出复制边界 | [ReaTeam/Doc LICENSE](https://github.com/ReaTeam/Doc/blob/master/LICENSE) 当前仓库识别为 GPL-3.0；[State Chunk Definitions](https://github.com/ReaTeam/Doc/blob/master/State%20Chunk%20Definitions) 文件还保留 IXix/Cockos Wiki 等上游署名 | **有条件/未解决** | 逐字段确认原创或来源；直接复制内容不能静默放进 MIT 发行物，未确认项应独立重写或移除 |
| `packages/reacli/src/rac/data/knowledge/api_index.json` | 当前文件含 865 个 API 函数的签名、参数和英文描述；SHA-256 `bce7d856221555d036d37e68d923357008c3602770c0e7da6286f78c6e25fcc4` | [Cockos ReaScript](https://www.reaper.fm/sdk/reascript/reascript.php) 说明文档可在线查看并可由 REAPER 生成，但核查页面没有给出将页面文字整体复制到第三方包的再分发许可 | **未解决** | 发行包删除复制的描述，或改成独立撰写/事实字段并保留兼容性测试；取得 Cockos 许可后再恢复 |
| `reference/knowledge/reascript/jsfx/*` 及 JSFX handbook | `reference/source-manifest.json` 记录来自 Cockos JSFX Programming Reference；示例 `.jsfx` 字节未改写 | [Cockos JSFX Programming](https://www.reaper.fm/sdk/js/js.php) 是公开参考页，但本次核查未找到页面级再分发许可；REAPER 用户指南的一个官方 PDF 版本明确写有保留所有权利及未经许可不得整篇或部分再发布：[User Guide PDF](https://www.reaper.fm/userguide/ReaperUserGuide735cc.pdf) | **未解决** | 仓库可继续保持 private；公开文档只保留链接和独立撰写内容，示例/原文需逐项确认许可 |
| `reference/knowledge/reascript/render_internals.md` | 当前文件 SHA-256 `282c766019d738626e239374d5662f6d8ed61cebc801c8d4725696efec6d0936`，保留 Meo-Ada Mespotine/Ultraschall 署名及 `cc-by-nc` 标签 | 上游文件 [RENDER_How_RenderCFG-Base64-strings_are_encoded.txt](https://github.com/Ultraschall/ultraschall-lua-api-for-reaper/blob/main-branch/ultraschall_api/Documentation/misc_docs/RENDER_How_RenderCFG-Base64-strings_are_encoded.txt) 明写 `licensed creative commons cc-by-nc`；[Ultraschall API repository](https://github.com/Ultraschall/ultraschall-lua-api-for-reaper) 顶层没有识别到统一 LICENSE，源文件也没有写出版本号 | **有条件** | 只有在确认具体 CC 版本和完整法律文本后，保留署名、许可证链接、修改说明，并限制为非商业；不得标为 MIT，也不得承诺商业再分发 |
| `reference/knowledge/reascript/actions_index.json` | 来源清单记录来自 Ultraschall 的历史 action list；当前 SHA-256 `bf570b0c62b85436f4065acf16d8e9a4261dcfc8f6fb1ac015913b41f1ab42f6` | Ultraschall API 仓库没有识别到顶层 LICENSE，文件级授权未找到 | **未解决** | 从公开仓库/发行包移除，或取得作者许可并保留完整 attribution |
| `packages/reacli/src/rac/data/lua/entry.lua` 与 11 个 `stdlib/*.lua` | 文件头写有 `(reaper_agent_cli)`、`粘贴片段`；来源清单记录与旧项目字节一致，entry SHA-256 `b2c74e382efa0fc7a86bdf13d3629796848ea39c691f244c506eb4ffd693c9fc` | 当前仓库只记录了源项目相对路径和散列，没有该项目的公开许可证或版权授权凭证 | **未解决** | 证明旧项目权利归属/取得许可，或重新实现并替换；在此之前不得把该 Lua 资源按 MIT 发行 |
| `schema/rpp/evidence`、`reference/` 中研究原件、工程备份、插件状态和媒体 | 文件清单与来源 manifest 已记录，部分内容源于本地实验或第三方文档 | 不属于运行时所需的最小发行内容；第三方来源各自的许可没有统一解决 | **排除** | 保持私有；不进入 wheel、sdist、文档站或 agent bundle。Git 仓库若公开也会分发这些文件，因此当前仓库继续 private |

## 许可证含义的适用边界

对渲染笔记，`cc-by-nc` 只能作为上游文件写下的线索，不能自行补成某个具体版本。若最终确认是 CC BY-NC 4.0，其官方条款允许在遵守条件时复制和改编，但要求署名、许可证链接和修改声明，并禁止商业用途；官方说明还提醒，其他权利可能继续限制使用。[CC BY-NC 4.0 deed](https://creativecommons.org/licenses/by-nc/4.0/)

因此，“没有商业行为盈利”不足以清除当前门禁：它没有解决 ReaTeam/Cockos/旧项目材料的授权来源，也没有解决 CC 版本和署名记录，更不能覆盖未来把包用于商业场景的变化。

## 已完成的仓库动作

- 新增本审计文件，固定了来源、散列、上游 URL 和每项发行处置。
- 更新 `docs/ecosystem/publication.json`，记录本次审计为 `partial_clearance_only`，保留三个发布门禁为 `false`。
- 更新两个 Python 包的第三方声明和 `reference/SOURCES.md`，使 ReaTeam GPL、Ultraschall `cc-by-nc`、Cockos 未发现页面级再分发许可、旧 Lua 来源未解决等事实可见。
- 没有上传 PyPI/TestPyPI，没有改包名所有权，也没有把任何未解决项标成已授权。

## 清除路径

推荐先做发行物清理，再申请外部许可：

1. 保留 RPP 结构事实、token、位置和由用户独立撰写的解释；逐字段把直接复制的 ReaTeam/其他来源文字替换为独立表述。
2. 从 `reacli` wheel/sdist 移除 Cockos API 的复制描述；若需要完整帮助，运行时从官方 URL 或用户本地生成文档读取。
3. 证明 `reaper_agent_cli` Lua 的版权归属，或以本仓库重新实现的代码替换它们。
4. 将 Ultraschall 渲染笔记作为单独、带完整署名和明确 CC 版本的非商业参考，或从公开发行物移除。
5. 对 ReaTeam/Doc、Cockos 和 Ultraschall 的每个仍保留文件保存书面许可或完整许可证文本；之后重新构建并扫描 wheel/sdist、文档站和 bundle，最后才有资格把 `source_permissions_resolved` 改为 `true`。

这是一份工程发布门禁记录，不是针对具体司法辖区的法律意见；若要在不清理内容的情况下发行，应该让熟悉版权和开源许可证的律师逐项审阅。
