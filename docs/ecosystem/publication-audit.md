# 发布前置核查（2026-09-17）

当前状态：私有仓库候选已通过跨平台验收；来源授权已由维护者确认，TestPyPI 的
`reacli` 已完成首次 OIDC 上传，`reaper-parser` 的 pending publisher 已由维护者报告配置，
尚待首次上传；PyPI 生产发布仍未配置。

2026-09-15 已完成[来源与再分发授权审计](source-license-audit.md)。维护者确认
ReaTeam、Cockos、Ultraschall 及 GitHub 开源 Lua 资料可以使用并按来源署名；该声明
已记录为 `source_permissions_resolved=true`。它不替代发行物中的署名和适用许可证
条件，也不改变 TestPyPI/PyPI 属于对外再分发这一事实。

## 已落实

- `DDDPG/Rea-Cli` 经 GitHub API 确认为 private；保持该可见性。
- 维护者明确授权其原创 ReaperDoc 代码与文档按 MIT 发布。
  已新增 `apps/reaperdoc/LICENSE`、`schema/rpp/LICENSE` 及范围说明。
  授权不扩展到外来引用或复制的材料。
- 已核查 ReaperDoc README 对 ReaTeam State Chunk Definitions 的致谢；维护者确认
  可以使用，仍保留 ReaTeam/IXix/Cockos Wiki 来源和适用许可证信息。
- 已核查 Ultraschall 渲染原件的文件级 `cc-by-nc` 标记；维护者确认可以使用，仍
  保留 Meo-Ada Mespotine/Ultraschall 署名与来源链接。
- 已核查 Cockos ReaScript/JSFX 官方参考页；维护者确认可以在署名和来源链接完整
  的前提下整理使用，项目不把 Cockos 原文冒充为本项目原创。
- 维护者确认旧项目来源的 Lua 资源可使用；包内仍保留原项目/原作者来源信息。
- 修正 parser 来源说明，移除不属于该包的 Cockos API 索引、rac Lua 和依赖描述。
- 当前 schema 来源更新为 `6416435fdf4cc7e38346fd7875f5d04949b431a2`；
  `32047bb` 仅作为旧快照历史保留。
- PyPI 上 `reacli` 和 `reaper-parser` 的 JSON 接口仍返回 404；TestPyPI 的 `reacli`
  JSON 已返回版本 `0.1.0`，`reaper-parser` 尚待首次上传。索引响应不证明全部包名的
  账号控制权。

## 各产物剩余事项

| 产物 | 已确认范围 | 仍需处理 |
| --- | --- | --- |
| parser wheel/sdist | 原创 parser 与 ReaperDoc 原创规格 MIT；外来资料有维护者授权声明 | 保留 ReaTeam 来源、许可证和署名；不把上游文本冒充为 MIT 原创 |
| rac wheel/sdist | 原创代码 MIT；Cockos API 与 Lua 资源有维护者授权声明 | 保留 Cockos、旧项目/原作者来源及适用条件 |
| 文档站与独立 schema | 原创部分 MIT | 外来说明对账；构建已加入 LICENSE 与范围说明 |
| agent bundle | 原创指南、示例 | 构建已加入许可证；检查引用内容范围 |
| Git 仓库 | 保持 private | `reference/` 的历史 ReaTeam、Ultraschall、Cockos 等材料按维护者声明保留来源；继续排除用户工程、媒体和研究原件 |

这是一份来源记录。当前来源门禁依据维护者声明通过，但并不替代逐项保留
许可证文本、署名和来源链接的发行要求。

## `check_publish` 门禁

| 门禁 | 当前值 | 结果 | 说明 |
| --- | --- | --- | --- |
| `source_permissions_resolved` | `true` | 通过（维护者声明） | 已记录 ReaTeam、Cockos、Ultraschall 和 Lua 来源使用确认 |
| `package_ownership_verified` | `false` | 阻拦 | TestPyPI/reacli 已返回项目 JSON，但 PyPI 两项及生产项目归属仍未核实 |
| `trusted_publishing_configured` | `false` | 阻拦 | TestPyPI/reacli 的 OIDC 上传已验证，`reaper-parser` pending publisher 仅有维护者报告，PyPI 两项尚未核实 |

2026-09-15 本地实际执行结果：

```text
$ python tools/check_publish.py
Publication prerequisites unresolved: package_ownership_verified, trusted_publishing_configured
$ echo $?
1
```

因此当前 `check_publish` 的未满足项只有后两项。脚本还包含一个条件门禁：当
`TARGET=pypi` 时，运行必须来自 `ecosystem-v*` 标签；由于前置布尔门禁尚未通过，
本次运行尚未进入该条件检查。

为支持两个项目在 TestPyPI 上顺序首次创建，`publish.yml` 现在提供显式的
`mode=testpypi-bootstrap`。该模式只接受 manifest 中已登记的单个项目、只允许
`TARGET=testpypi`，不会放宽普通模式或正式 PyPI 的三个全局门禁；当前 `reacli` 的首次上传
已验证，`reaper-parser` 已登记为待首次上传。

## 实时索引与 GitHub 环境复核

- `https://test.pypi.org/pypi/reacli/json` 在 2026-09-17 返回 HTTP 200，项目版本为
  `0.1.0`；`https://pypi.org/pypi/reacli/json`、`https://pypi.org/pypi/reaper-parser/json`
  和 `https://test.pypi.org/pypi/reaper-parser/json` 尚未提供生产或 parser 项目证据。
  索引响应本身不能证明全部包名的账号所有权，因此 `package_ownership_verified` 继续保持
  `false`。
- `gh api repos/DDDPG/Rea-Cli/environments` 在 2026-09-15 返回一个 `testpypi`
  环境，`protection_rules` 为空；响应中没有 `pypi` 环境。GitHub 环境存在本身不等于
  PyPI/TestPyPI 已登记 Trusted Publisher，故 `trusted_publishing_configured` 继续为
  `false`。
- 维护者报告 TestPyPI 已接受 `reacli` 的 pending publisher；为同一仓库、工作流和
  environment 注册 `reaper-parser` 时返回：`A pending trusted publisher matching this
  configuration has already been registered for a different project name.` 这表示当前
  应先使用 `reacli` 完成一次上传，让 pending publisher 转为该项目的普通 publisher，
  再注册 `reaper-parser`。
- GitHub Actions run `35201286656` 的 build 和 publish job 均成功，使用 TestPyPI OIDC
  发布了 `reacli==0.1.0`；这证明了 `reacli` pending publisher 已被消费。
- 维护者随后报告已为同一仓库、工作流和 environment 配置 `reaper-parser` pending
  publisher；尚未运行 parser 的首次上传。生产运行仍需使用 `ecosystem-v*` 标签。

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

GitHub API 初次核查 environments 数量为 0；随后复查发现 GitHub 已创建
`testpypi` 空环境，但未添加保护规则。创建带 DDDPG required reviewer 的保护规则时
返回 HTTP 422，提示当前账单方案不支持 required reviewers。维护者随后报告已在 TestPyPI
配置 `reacli` pending publisher，并在首次上传成功后配置 `reaper-parser`；当前复核仍未
观察到 `pypi` 环境。后续应完成 TestPyPI 的 `reaper-parser` 首次上传，安装验证后再补建
`pypi` environment 并登记正式 publisher；当前工作流仅允许人工触发，生产索引另外要求
`ecosystem-v` 标签。

[PyPI 官方文档](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
说明 pending publisher 可用于首次创建项目，但登记本身不保留包名。
[Publisher 字段说明](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)
要求仓库、工作流和 environment 与运行身份对应。

## 下一次执行顺序

1. 记录维护者已完成的两个账号配置结果，不收集密码、恢复码或 token；邮箱验证和
   双因素状态仍由维护者自行确认。
2. 保持外来材料的来源、署名和适用许可证条件随每个发行物分发；内容变更后重新构建
   并验收，旧候选不原地替换。
3. `reacli` 的 TestPyPI action 已完成；保留 run `35201286656`、项目页和 JSON 作为证据。
4. 维护者已注册 `reaper-parser` 的 pending publisher；当前仓库 manifest 已将其
   bootstrap 许可更新为 `allowed=true`。下一步选择 `package=reaper-parser` 单独运行
   TestPyPI action，验证项目页、JSON 和隔离安装。两个项目都验证后，再补建 `pypi`
   environment、登记正式 publisher，并将对应全局布尔门禁改为 `true`。

TestPyPI 也是对外上传，不等于私有分发。保持 Git 仓库 private 不会使索引包私有。
