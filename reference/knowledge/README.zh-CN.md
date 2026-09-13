# 历史证据与原始资料目录

[English](README.md) · [规范首页](../README.zh-CN.md)

本目录保留导入原文与结构化记录，因此部分文件仍为中文或混合语言。日常开发阅读上层双语规范；这里用于核对出处、版本和未解决问题，不能当作当前宿主的完整 API 文档。旧路径保留，方便既有引用继续工作。

| 文件 | 内容与限制 |
|---|---|
| [rpp/annotated_tree.md](rpp/annotated_tree.md) | 带注释的 chunk 树；说明资料，不是工程样本 |
| [rpp/blob_denylist.md](rpp/blob_denylist.md) | 不透明块、对象身份与保留边界 |
| [rpp/semantics_formulas.md](rpp/semantics_formulas.md) | 增益、包络、take 速率和 MIDI 时间证据 |
| [rpp/gap_registry.md](rpp/gap_registry.md) | 未解释字段和版本相关观察 |
| [rpp/extract_report.json](rpp/extract_report.json) | Schema 提取范围与未解决字段 |
| [reascript/api_pitfalls.json](reascript/api_pitfalls.json) | API 陷阱及证据标签 |
| [reascript/actions_index.json](reascript/actions_index.json) | REAPER 5.941 / SWS 2.9.7 历史 action 查询 |
| [reascript/cli_behavior.md](reascript/cli_behavior.md) | CLI 观察：macOS 7.62、Linux 7.77/7.78 |
| [reascript/render_internals.md](reascript/render_internals.md) | 渲染笔记；保留 Ultraschall cc-by-nc 署名与限制 |
| [reascript/jsfx/README.md](reascript/jsfx/README.md) | REAPER 7.78 时期 JSFX 手册快照 |
| [reascript/jsfx/jsfx_reference.json](reascript/jsfx/jsfx_reference.json) | 结构化 JSFX 符号索引 |
| [reascript/jsfx/examples/gain_simple.jsfx](reascript/jsfx/examples/gain_simple.jsfx) | 双声道增益示例 |
| [reascript/jsfx/examples/delay_basic.jsfx](reascript/jsfx/examples/delay_basic.jsfx) | 延迟示例；已知零延迟与尾音限制 |
| [reascript/jsfx/examples/midi_monitor.jsfx](reascript/jsfx/examples/midi_monitor.jsfx) | MIDI monitor 示例 |

包内唯一正本：[API index](../../src/rac/data/knowledge/api_index.json)、[RPP schema](../../src/rac/data/knowledge/rpp_schema.json)、[Lua 资源](../lua/README.zh-CN.md)。当前验证见[记录](../../docs/validation.md)；来源与哈希见[来源说明](../SOURCES.md)及[清单](../source-manifest.json)。翻译后的规范没有把历史观察升级为实测保证。
