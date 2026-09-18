# JSFX 编写与集成规范

[English](README.md) · [规范首页](../README.zh-CN.md)

JSFX 用于 FX 实例内的音频/MIDI 处理，使用 EEL2，既不是 Lua 脚本，也不是 Python 调度层。以[官方文档](https://www.reaper.fm/sdk/js/)为起点。导入手册属于 REAPER 7.78 时期的快照，不代表当前宿主 DSP 验证。

## 区分源码与实例

在专用 REAPER 资源目录的 `Effects` 下以独立名称保存源码，并包含所需 import 和素材。通过宿主加载，检查目标 track/take/master 及实际实例。RPP 中的 `<JS>` 是已保存实例状态，不能只靠源码 slider 声明推断其序列化。未知数据按 [RPP 边界](../rpp/README.zh-CN.md)原样保留。

## 开发检查

区分初始化、参数更新、块处理和逐采样处理；考虑采样率变化、声道范围、内存初始化和状态持久化。MIDI 处理要保留时序及未计划修改的消息。GUI 与音频状态可能相互影响，不能把 GUI 回调当作音频循环。使用不熟悉的功能前，从官方文档确认具体生命周期与语言行为。

在临时宿主工程中加载，测试相关采样率和参数极值，按需要检查静音、旁通、增益变化、削波、延迟和尾音。保存重开后对比预期状态。`luac -p` 不编译 EEL2，RPP 解析成功也不代表 DSP 正确。

## 已有学习资料

- [历史手册](../knowledge/reascript/jsfx/README.md)：生命周期、变量、EEL2 语法、函数分类与算法片段；保留原始混合语言笔记。
- [结构化索引](../knowledge/reascript/jsfx/jsfx_reference.json)：按准确符号检索，保留版本元数据。
- [Gain](../knowledge/reascript/jsfx/examples/gain_simple.jsfx)：仅处理双声道，突然调节增益没有平滑。
- [Delay](../knowledge/reascript/jsfx/examples/delay_basic.jsfx)：零延迟设置会读取旧缓冲槽，声明尾音未覆盖完整反馈衰减；正式使用前应修正并测试。
- [MIDI monitor](../knowledge/reascript/jsfx/examples/midi_monitor.jsfx)：教学源码，需要在目标宿主确认事件流。

手册中的 Chamberlin SVF 片段没有保证全部控制范围内稳定。本次文档整理未对这些示例进行 DSP 实测。署名保留于[来源说明](../SOURCES.md)，进入仓库不改变上游文本许可。
