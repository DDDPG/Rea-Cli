# 发布前置核查（2026-09-17）

当前状态：仓库仍为 private；候选已通过跨平台验收，项目许可证范围已明确，但上游材料
仍需逐项按其许可证/条款核实，TestPyPI 的
`reacli==0.1.0` 与 `reaper-parser==0.1.0a1` 均已完成首次 OIDC 上传并通过隔离安装；
PyPI 当前同时提供两个项目的 `0.1.0`/`0.1.0a1` wheel 和 sdist，四个构件的文件名、
大小、上传时间和 SHA-256 已写入 `publication.json`。`reacli==0.1.0` 的生产上传使用
OIDC；维护者确认 `reaper-parser==0.1.0a1` 是手动上传。两个项目的 owner 和 Trusted
Publishing 配置均已记录为通过；手动上传的 parser 版本不宣称使用 `publish.yml`。

另外，直接下载并读取正式 PyPI wheel 的 `METADATA` 后确认，两个已发布版本仍记录
`License-Expression: MIT`。该元数据随不可变构件不能回写；当前 checkout 已移除单一
许可证表达式，直到发行包中所有上游材料的条款逐项解决或被排除。这个差异已记录在
`publication.json`，下次上传必须使用新版本。

2026-09-15 已完成[来源与再分发授权审计](source-license-audit.md)。当前采用的许可证
范围是：项目自有代码和原创文档按 MIT 发布；ReaTeam、Cockos、Ultraschall、Lua 及
其他上游资料继续遵循各自许可证和条款。维护者口径不等于上游再分发许可，因此
`source_permissions_resolved=false`，并不改变 TestPyPI/PyPI 属于对外再分发这一事实。

2026-09-17 的范围更新进一步明确：Git-only 的 `reference/` 与
`schema/rpp/evidence/` 也不受项目 MIT 覆盖。它们只有在逐项来源条款或另行再分发许可
允许时才能公开；其中 `cc-by-nc` 条目的非商业性条件不因署名而消失，仍需随文件保留。

## 已落实

- `DDDPG/Rea-Cli` 经 GitHub API 确认为 private（核查当日状态）。仓库可见性变更属于
  单独决策，但公开前仍须完成 Git 跟踪上游材料的逐项许可证/许可复核。
- 维护者明确授权其原创 ReaperDoc 代码与文档按 MIT 发布。
  已新增 `apps/reaperdoc/LICENSE`、`schema/rpp/LICENSE` 及范围说明。
  授权不扩展到外来引用或复制的材料。
- 已核查 ReaperDoc README 对 ReaTeam State Chunk Definitions 的致谢；继续保留
  ReaTeam/IXix/Cockos Wiki 来源和适用许可证信息，混合来源的公开条件仍需逐项确认。
- 已核查 Ultraschall 渲染原件的文件级 `cc-by-nc` 标记；继续保留
  Meo-Ada Mespotine/Ultraschall 署名、来源链接和非商业条件，具体版本/许可范围仍需核实。
- 已核查 Cockos ReaScript/JSFX 官方参考页；相关参考资料按适用上游条款使用，保留
  Cockos 署名和官方来源链接，不把上游原文冒充为本项目原创。
- 已记录旧项目来源的 Lua 资源；包内仍须保留原项目/原作者来源信息和可核实的许可证条件。
- 修正 parser 来源说明，移除不属于该包的 Cockos API 索引、rac Lua 和依赖描述。
- 当前 schema 来源更新为 `6416435fdf4cc7e38346fd7875f5d04949b431a2`；
  `32047bb` 仅作为旧快照历史保留。
- PyPI 的 `reacli` 和 `reaper-parser` JSON 均已返回 HTTP 200，版本分别为 `0.1.0` 和
  `0.1.0a1`；两个项目的当前 owner 角色均为 `DDDPG`。四个正式构件均已下载并按
  JSON 中的 SHA-256 核对，且 wheel/sdist 中的 runtime 文件与上传时记录的
  `5ca1f27` 源码 revision 一致。本轮审查随后加入了运行时加固和隐私清理，当前
  checkout 因此不再与这四个不可变构件逐字一致；详情见 `publication.json`，下次上传
  必须提升版本。索引响应证明当前公开记录，不单独证明历史上传渠道。

## 各产物剩余事项

| 产物 | 已确认范围 | 仍需处理 |
| --- | --- | --- |
| parser wheel/sdist | 原创 parser 与 ReaperDoc 原创规格 MIT；generated schema 含混合来源字段说明；包元数据不宣称单一 blanket license | 逐项确认 ReaTeam 等上游条款/许可；保留来源和署名；未完成前不把整个发行物标成无条件 MIT |
| rac wheel/sdist | 原创代码 MIT；runtime 中含按上游条款使用的 Cockos API 描述、schema 和 Lua 资源；包元数据不宣称单一 blanket license | 逐项确认 ReaTeam、旧项目/原作者来源及适用条件；无许可依据的内容须移除或取得许可 |
| 文档站与独立 schema | 原创部分 MIT | 外来说明对账；构建已加入 LICENSE 与范围说明 |
| agent bundle | 原创指南、示例 | 构建已加入许可证；检查引用内容范围 |
| Git 仓库 | 当前仍为 private；项目 MIT 范围已记录，上游逐项许可仍未全部清除 | `reference/` 与 `schema/rpp/evidence/` 的历史 ReaTeam、Ultraschall 及其他未决材料必须按各自条款处理；Cockos API/JSFX 参考资料按上游条款并保留来源链接。clone 或再分发本仓库会分发这些文件。用户工程与媒体仍不进入公开语料 |

这是一份来源记录。当前来源门禁按逐项许可证据保持阻拦；它不替代发行物中保留
许可证文本、署名和来源链接的要求。

## `check_publish` 门禁

| 门禁 | 当前值 | 结果 | 说明 |
| --- | --- | --- | --- |
| `source_permissions_resolved` | `false` | 阻拦（逐项许可未完成） | 项目 MIT 仅覆盖自有代码/原创文档；部分 Ultraschall、混合 schema 和 Lua 来源缺少可核实的统一再分发依据 |
| `package_ownership_verified` | `true` | 通过（当前索引记录） | PyPI JSON 当前服务两个项目，owner 角色均为 `DDDPG`，版本和正式构件均可定位 |
| `trusted_publishing_configured` | `true` | 通过（维护者确认） | 两个项目的 Trusted Publishing 配置按维护者确认记录为完成；`reacli` 的生产上传使用 OIDC，已发布的 parser 版本则是手动上传 |

当前 checkout 的本地实际执行结果：

```text
$ python tools/check_publish.py
Publication prerequisites unresolved: source_permissions_resolved
$ echo $?
1
```

因此普通 `check_publish` 当前仅有 `source_permissions_resolved` 未满足。脚本还包含
一个条件门禁：当 `TARGET=pypi` 时，运行必须来自 `ecosystem-v*` 标签；`reacli` 的
一次性 bootstrap 已在 `ecosystem-v0.1.0` 上通过该条件。已有构件不会自动放开未来的
普通生产模式，也不会替代逐项来源许可审查。

为支持两个项目在两个索引上顺序首次创建，`publish.yml` 现在提供显式的
`mode=testpypi-bootstrap` 和 `mode=pypi-bootstrap`。每个模式只接受 manifest 中已登记的
单个项目；PyPI 模式只允许 `TARGET=pypi` 且必须来自 `ecosystem-v*` 标签，不会放宽普通
模式或 source gate。两个 TestPyPI 项目的首次上传均已验证，PyPI 的 `reacli` bootstrap
已完成；parser 的正式构件由维护者手动上传并按此方式记录。

## 实时索引与 GitHub 环境复核

- `https://pypi.org/pypi/reacli/json` 在 2026-09-17 返回 HTTP 200，项目版本为 `0.1.0`；
  新建隔离环境从正式 PyPI 下载该 wheel 并成功导入 `rac==0.1.0`；再以 parser
  wheel 满足依赖后，两个正式 wheel 的 runtime/archive 校验均通过。
- `https://pypi.org/pypi/reaper-parser/json` 在 2026-09-17 返回 HTTP 200，项目版本为
  `0.1.0a1`，owner 为 `DDDPG`；wheel 和 sdist 均已从正式 PyPI 下载并核对摘要。
- `https://test.pypi.org/pypi/reacli/json` 在 2026-09-17 返回 HTTP 200，项目版本为
  `0.1.0`；`https://test.pypi.org/pypi/reaper-parser/json` 返回 HTTP 200，项目版本为
  `0.1.0a1`。TestPyPI 运行和隔离安装证据仍保留在下方记录的 workflow runs 中。
- `gh api repos/DDDPG/Rea-Cli/environments` 在 2026-09-17 返回 `testpypi` 和 `pypi`
  两个 environment，`protection_rules` 均为空。环境存在本身不等于 PyPI 已登记
  Trusted Publisher；本次 `trusted_publishing_configured=true` 取维护者对两个项目
  配置完成的确认，不能由 environment 对象单独推导。
- GitHub Actions run `35201286656` 的 build 和 publish job 均成功，使用 TestPyPI OIDC
  发布了 `reacli==0.1.0`；这证明了 `reacli` pending publisher 已被消费。
- GitHub Actions run `35202476617` 的 build 和 publish job 均成功，使用 TestPyPI OIDC
  发布了 `reaper-parser==0.1.0a1`；新的隔离虚拟环境已从 TestPyPI 安装并成功导入
  `reaper_parser`。
- GitHub Actions run `35206896709` 的 build 和 publish job 均成功，使用 PyPI OIDC 发布了
  `reacli==0.1.0`；正式 PyPI JSON 和隔离 wheel 安装均已复核。
- `reaper-parser==0.1.0a1` 的生产构件由维护者手动上传；本次不以 GitHub Actions
  记录证明其上传渠道，也不因账号当前 CI 额度耗尽而追加触发 workflow。GitHub `pypi`
  environment 已创建且无保护规则；`reacli` 的 OIDC 记录、parser 的 PyPI 构件和手动
  上传确认分别按其真实来源记录。

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
返回 HTTP 422，提示当前账单方案不支持 required reviewers。维护者随后报告已在 TestPyPI 配置
`reacli` pending publisher，并在首次上传成功后配置 `reaper-parser`；两次 TestPyPI 上传均已验证。
当前已创建无保护规则的 `pypi` environment，且维护者报告已在 PyPI 配置 `reacli` publisher；
生产索引仍需使用 `ecosystem-v` 标签。

[PyPI 官方文档](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
说明 pending publisher 可用于首次创建项目，但登记本身不保留包名。
[Publisher 字段说明](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)
要求仓库、工作流和 environment 与运行身份对应。

## 后续发布顺序

1. 记录维护者已完成的两个账号配置结果，不收集密码、恢复码或 token；邮箱验证和
   双因素状态仍由维护者自行确认。
2. 对每个进入发行物的外来材料确认其来源许可证或明确再分发许可；保持来源、署名和
   适用条件随每个发行物分发。内容变更后重新构建并验收，旧候选不原地替换。
3. TestPyPI 的 `reacli==0.1.0` 与 `reaper-parser==0.1.0a1` 均已完成 action、JSON
   和隔离安装验证；保留 runs `35201286656`、`35202476617` 作为证据。
4. `reacli==0.1.0` 已在 `ecosystem-v0.1.0` 上完成 `target=pypi`、
   `package=reacli`、`mode=pypi-bootstrap`；保留 run `35206896709`、PyPI JSON、归档
   摘要和隔离安装作为证据。
5. 对 `reaper-parser`，保留当前 PyPI JSON/构件摘要和维护者的手动上传确认；不要把这次
   手动发布改写成 `publish.yml` OIDC 证据。未来若恢复 CI 额度并计划改用 workflow，
   再单独验证 publisher/channel，不影响当前 gate 的配置状态记录。

TestPyPI 也是对外上传，不等于私有分发。Git 仓库的可见性不会改变已经上传到索引的构件
的公开状态；两个方向互相独立，需要分别处理。
