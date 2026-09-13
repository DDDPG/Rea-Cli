# ReaScript 对象与 FX 规范

[English](README.md) · [规范首页](../README.zh-CN.md)

ReaScript 是宿主 API，Lua 是本库执行模板使用的语言。外部 `import rac` 不等于宿主内的 `reaper_python` 会话。Lua 使用 `reaper.FunctionName(...)`，Python 宿主绑定的参数与返回元组不同；查询目标宿主生成的 API 文档或[官方 API](https://www.reaper.fm/sdk/reascript/reascripthelp.html)，不要机械转换签名。

## 先定位对象再修改

用 `rac knowledge api GetTrack` 查询包内签名，再检查目标 REAPER 是否提供该 API（例如 `reaper.APIExists`）。插入或删除会改变索引；尽量保留稳定标识，结构修改后重新定位，并检查 nil 指针和 API 返回值。重名对象不能靠名称唯一识别。

| 对象 | 操作范围与验证 |
|---|---|
| Track / folder | 轨道索引从 0 开始。Folder 深度描述跨轨道关系，要检查闭合深度和路由，不是名称中有 Bus 就成立。 |
| Item / take | 定位目标 item 和 take；部分 helper 只处理 active take，多 take 需要显式枚举。 |
| Envelope | 明确所属对象和具体包络；不存在时可能返回 nil。读取 scaling mode，编辑后排序并检查时间/值。 |
| MIDI | 确认 MIDI take，用宿主 API 换算工程时间，插入后排序；检查音高、通道、力度和位置。 |
| Marker / region | 遍历位置不等于 marker ID，遍历时同时考虑 marker 和 region。 |
| Send / master | 区分 send/receive 类别及目标；用 `GetMasterTrack` 获取 master，不用 `GetTrack(0, -1)`。 |

生成器仅覆盖[注册表中的操作](../../src/rac/luagen/generator.py)。Folder、任意 take 和 master FX 需在 entry 模板中编写自定义 Lua。[Showcase](../../examples/show_session.lua)展示了该路径，Python 构建器负责验证输出工程。

## FX：识别、设置、读回

1. 定位目标 track、master 或 take 及正确 FX 链，匹配已安装插件并检查返回名称。添加失败会返回无效索引，不应继续设置。
2. 在该实例枚举参数名称和值域，记录插件/版本、链位置和参数身份。不要把单机发现的数值索引写成跨平台约定。
3. 区分归一化控制值与物理单位。`TrackFX_SetParamNormalized` 使用 0–1；100 Hz 或 -15 dB 不能简单除以某个最大值，插件映射可能非线性。
4. 读回格式化参数、enabled/bypass/offline 状态；EQ 还要检查 band 类型与启用状态。需要持久化时，保存重开后再检查。

包内 `std_fx.probe` 提供参数和值域信息，但不解决所有插件的物理单位映射。ReaEQ 在适用时优先使用专门 EQ API。其他插件使用有文档的映射，或经过验证且有范围限制的转换，并检查格式化值。未确认单调性或离散行为前，不要直接二分搜索参数。

可验证目标示例：Melody 上启用的 ReaEQ 100 Hz 高通；Chords 长尾混响及明确的 room/damping/wet 值；Bass 压缩器 threshold -15 dB、makeup +3 dB，同时确认 auto makeup；master limiter threshold -4.5 dB。这些是 showcase 目标，不是通用默认值，也不提供可跨版本硬编码的参数索引。见[构建器](../../examples/show_session.py)和 [Lua 实现](../../examples/show_session.lua)。

## Action 与持久化

有直接 API 时优先使用。调用 action 前，在目标 Action List 确认命令、section 和所需扩展。`NamedCommandLookup` 用于命名命令，不用于验证任意数字 ID。包内 action 索引来自历史版本 REAPER 5.941 / SWS 2.9.7。

不要假定 API 会设置 dirty。Entry 协议处理显式 `save_as`，仍需检查 proof 和新输出。ReaScript 支持 defer，但本库同步 entry 模板不管理异步生命周期；需要异步 UI 时应明确采用另一套生命周期设计。

## 渲染

使用新渲染目录，明确范围、采样率、声道和格式。RPP 块与 API 属性名不同，例如 API `RENDER_FORMAT` 不等于 RPP 中直接写一行 `RENDER_CFG`。格式配置应由目标宿主确认，不凭猜测编造编码字节。为混响/延迟保留适当尾音，并检查实际文件。

弹窗被抑制或进程正常退出，不证明媒体和 FX 已加载。重开并读回相关状态，按任务检查音频。详见[调用规范](../workflow/README.zh-CN.md)、[渲染笔记](../knowledge/reascript/render_internals.md)、[API 陷阱](../knowledge/reascript/api_pitfalls.json)、[历史 action](../knowledge/reascript/actions_index.json)。后三项属于来源资料，不是当前宿主认证。
