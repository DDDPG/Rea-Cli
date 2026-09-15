# 发布前置核查（2026-09-15）

当前状态：私有仓库候选已通过跨平台验收；尚不满足公开上传条件。
本次没有创建账号、占用包名、配置 PyPI publisher 或上传发行包。

2026-09-15 已完成独立的[来源与再分发授权审计](source-license-audit.md)。结论是
“部分清除”：维护者授权覆盖原创 ReaperDoc 部分，但 ReaTeam、Cockos、Ultraschall
和旧项目 Lua 资源仍有逐项范围或许可缺口。用户声明当前没有商业盈利已记录为
非商业条件的背景信息，不改变 `source_permissions_resolved=false`，也不改变
TestPyPI/PyPI 属于对外再分发这一事实。

## 已落实

- `DDDPG/Rea-Cli` 经 GitHub API 确认为 private；保持该可见性。
- 维护者明确授权其原创 ReaperDoc 代码与文档按 MIT 发布。
  已新增 `apps/reaperdoc/LICENSE`、`schema/rpp/LICENSE` 及范围说明。
  授权不扩展到外来引用或复制的材料。
- 已核查 ReaperDoc README 对 ReaTeam State Chunk Definitions 的致谢；ReaTeam/Doc
  当前仓库标注 GPL-3.0，故不能把混合来源规格整体静默标成 MIT。
- 已核查 Ultraschall 渲染原件的文件级 `cc-by-nc` 标记；由于许可证版本和完整
  法律文本未记录，当前只保留署名和限制，不宣称授权已清除。
- 已核查 Cockos ReaScript/JSFX 官方参考页；本次页面核查没有找到可直接套用的
  文档再分发许可。REAPER 用户指南的官方 PDF 版本还明确保留全部权利并要求
  取得许可后再发布，不能由“公开可访问”推出自由复制。
- 修正 parser 来源说明，移除不属于该包的 Cockos API 索引、rac Lua 和依赖描述。
- 当前 schema 来源更新为 `6416435fdf4cc7e38346fd7875f5d04949b431a2`；
  `32047bb` 仅作为旧快照历史保留。
- PyPI、TestPyPI 上 `reacli` 和 `reaper-parser` 的 JSON 接口均返回 404。
  这仅说明未找到公开项目，不证明名称可注册、被保留情况或账号控制权。

## 各产物剩余事项

| 产物 | 已确认范围 | 仍需处理 |
| --- | --- | --- |
| parser wheel/sdist | 原创 parser 与 ReaperDoc 原创规格 MIT | 将 schema 中外来原文与原创说明逐项区分；ReaTeam 等外来部分取得授权或独立重写 |
| rac wheel/sdist | 原创代码 MIT | Cockos API 索引复制描述、旧项目 Lua 资源尚无独立授权记录；需移除、重写或取得许可 |
| 文档站与独立 schema | 原创部分 MIT | 外来说明对账；构建已加入 LICENSE 与范围说明 |
| agent bundle | 原创指南、示例 | 构建已加入许可证；检查引用内容范围 |
| Git 仓库 | 保持 private | `reference/` 的历史 ReaTeam、Ultraschall、Cockos 等材料不因排除于 wheel 而获得公开授权 |

这是一份来源记录，不将无法找到授权等同于确认禁止分发。未知项继续保持未决。
全局 `source_permissions_resolved` 不能因原创部分授权而直接改为 true。

## 账号与发布身份

维护者已报告完成 PyPI/TestPyPI 注册，两个用户名均为 `DDDPG`。
邮箱验证与双因素认证尚未独立核实；浏览器读取连续超时。
不要在对话或仓库中保存密码、恢复码或 token。

- [PyPI 注册](https://pypi.org/account/register/)
- [TestPyPI 注册](https://test.pypi.org/account/register/)
- [PyPI pending publisher 配置](https://pypi.org/manage/account/publishing/)
- [TestPyPI pending publisher 配置](https://test.pypi.org/manage/account/publishing/)

两个索引独立配置，每个索引各添加两个项目：

| 字段 | TestPyPI | PyPI |
| --- | --- | --- |
| Project name | 分别为 `reacli`、`reaper-parser` | 分别为 `reacli`、`reaper-parser` |
| Owner | `DDDPG` | `DDDPG` |
| Repository | `Rea-Cli` | `Rea-Cli` |
| Workflow | `publish.yml` | `publish.yml` |
| Environment | `testpypi` | `pypi` |

GitHub API 初次核查 environments 数量为 0；上表是待配置值，不是完成声明。
创建带 DDDPG required reviewer 的 TestPyPI environment 时返回 HTTP 422，
提示当前账单方案不支持 required reviewers。复查发现 GitHub 已先创建
`testpypi` 空环境，但未添加保护规则；尚未配置 publisher，也没有触发发布。
后续创建对应 environment，并验证保护规则与 OIDC 配置。当前工作流仅允许人工触发，
生产索引另外要求 `ecosystem-v` 标签；保留这些门禁。

[PyPI 官方文档](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
说明 pending publisher 可用于首次创建项目，但登记本身不保留包名。
[Publisher 字段说明](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)
要求仓库、工作流和 environment 与运行身份对应。

## 下一次执行顺序

1. 维护者注册两个账号；记录账号名及配置结果，不收集凭证。
2. 完成外来文本逐项对账，保留事实字段及来源，对未获授权的复制描述独立重写或剔除。
3. 独立产物许可证已补齐；继续在内容调整后重建并验收，旧候选不原地替换。
4. 核实四个 publisher 与 GitHub environment，按实际证据更新发布门禁。
5. 经明确发布授权后手动运行 TestPyPI；验证索引安装后再处理正式 PyPI。

TestPyPI 也是对外上传，不等于私有分发。保持 Git 仓库 private 不会使索引包私有。
