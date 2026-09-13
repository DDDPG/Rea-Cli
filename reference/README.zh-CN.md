# REAPER 自动化开发规范

[English](README.md) · [项目首页](../README.zh-CN.md) · [API 签名](../docs/api.md) · [Agent skill](../skills/reaper-agent-cli/SKILL.md)

本规范说明如何使用 reacli 选择操作路径、实现修改并验证结果，在 API 参考之外补充单位、对象身份、执行生命周期和证据要求。先按主题阅读，精确签名以实现和包内索引为准。

## 主题导航

| 规范 | 检查内容 | English |
|---|---|---|
| [调用与交付](workflow/README.zh-CN.md) | 环境、路径选择、proof、重试、并发 | [Invocation](workflow/README.md) |
| [RPP](rpp/README.zh-CN.md) | 上下文、单位、字段修改、不透明数据、语义 diff | [RPP](rpp/README.md) |
| [ReaScript](reascript/README.zh-CN.md) | Track/folder/item/take/envelope/MIDI、FX、action、渲染 | [ReaScript](reascript/README.md) |
| [Lua](lua/README.zh-CN.md) | 生成器注册表、自定义 body、片段组合与执行 | [Lua](lua/README.md) |
| [JSFX](jsfx/README.zh-CN.md) | EEL2 源码、实例状态、DSP 检查与示例 | [JSFX](jsfx/README.md) |
| [历史证据资料](knowledge/README.zh-CN.md) | 全部导入笔记/索引、版本与知识缺口 | [Evidence archive](knowledge/README.md) |

直接构建工程可从 [quick start](../README.zh-CN.md) 或[现场合成 showcase](../examples/README.md)开始。Agent 使用仓库中的 [reaper-agent-cli skill](../skills/reaper-agent-cli/SKILL.md)，通过同一套规范工作，不复制另一套运行时。

## 信息优先级

- **当前调用约定：**[环境](../docs/environment.md)、[API 指南](../docs/api.md)、`src/rac/` 实现及本目录双语规范。中英文范围一致，维护时同步更新。
- **当前测试证据：**[验证记录](../docs/validation.md)。新增说明不意味着新增实机测试。
- **历史证据：**`knowledge/` 保留来源语言、日期、限制和署名。`live` / `verified-live` 是源项目报告的实验；`doc` / `human` 表示文档或人工审阅依据，都不等于当前宿主认证。
- **尚不明确：**查询 gap registry，并在目标宿主确认。Schema 覆盖率或旧 action 索引不能证明功能可用。

## 唯一正本与分发范围

`rac knowledge api GetTrack` 查询 [API 索引](../src/rac/data/knowledge/api_index.json)；`rac knowledge rpp track:VOLPAN` 查询 [RPP schema](../src/rac/data/knowledge/rpp_schema.json)。`rac resources --output ./templates` 导出 [entry](../src/rac/data/lua/entry.lua)、极简工程和 11 个 [Lua 片段](../src/rac/data/lua/stdlib/)。Skill 不再维护重复副本。

`reference/` 和 `skills/` 随 Git 仓库交付，不进入 wheel 或 sdist。运行时索引和模板仍随包安装。Skill 依赖本仓库及安装好的 reacli，不是零依赖独立运行时。

## 维护方式

[来源清单](source-manifest.json)中的原始哈希保持不变；编辑导入内容时更新目标哈希和编辑记录。新增双语指南是持续维护的规范，不对全部历史数据集逐字翻译。保留原始标识和来源路径，方便外部审阅者回查证据。

来源和再分发限制见[来源说明](SOURCES.md)及[第三方声明](../THIRD_PARTY_NOTICES.md)。文档和 skill 中不放个人 REAPER 配置、许可文件、插件缓存或机器专属媒体。
