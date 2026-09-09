# Opaque RPP blocks: editing boundaries

> 本文整理自源项目 2026-07-31 的 RPP 编辑约束。它是保守的编辑策略，
> 不是对 REAPER 所有内部格式的完整说明。来源与哈希见
> [来源清单](../../source-manifest.json)。

插件状态、格式配置和扩展数据中存在不可由当前 schema 解释的内容。
编辑工程时应原样保留这些数据；删除对象时可连同其完整状态块删除；
需要替换时使用来源明确、在目标宿主中验证过的整块数据。不要依据可见
base64、十六进制或数字序列推测内部字段。

## 需要整体处理的内容

- `<VST ...>`、`<AU ...>`、`<CLAP ...>` 中的插件私有状态。
- `<JS ...>` 内的参数序列和扩展状态；JSFX 源代码与 RPP 中的实例状态是
  两个不同层面，源码参考见 [JSFX 手册](../reascript/jsfx/README.md)。
- `<RENDER_CFG`、`<RECORD_CFG`、`<APPLYFX_CFG` 等格式配置，见
  [渲染笔记](../reascript/render_internals.md)。
- `<METRONOME` 内的编码数据。
- MIDI SysEx `<X>` / `<x>` 事件的数据和时序。
- `<EXTENSIONS>` 中 SWS 等扩展的私有块。
- 当前 schema 未解释的 `<PROJBAY>`、视频/分段 source 及其他未知块。

## 相邻明文字段

下面是示意片段，省略号和行内注释不能作为实际 RPP 数据使用：

```text
<FXCHAIN
  BYPASS 0 0 0         # 明文旁通字段
  <VST "VST: Example" ...
    ... private data ...
  >
  WET 1 0.5           # 明文 wet/dry 字段
  PRESETNAME "example"
  FXID {GUID}
>
```

编辑有文档定义的 `BYPASS`、`WET` 等明文字段时，保留相邻状态块。
仅更改 `PRESETNAME` 不会应用对应预设；使用宿主 API 操作预设。
已有 `FXID` 可能被参数包络或其他对象引用，不能任意替换。

## 整块替换与复制

适用来源包括目标 REAPER 安装中通过 GUI/API 导出的状态，或已在相同
环境中验证过的 fixture。跨轨道复制状态还需要处理对象标识与引用：
生成新的 FXID 后，相关包络或链接也必须保持一致。只替换 GUID 不能
保证一条复杂 FX 链仍然正确，宜交给宿主操作并保存读回。

## 检查修改结果

- `reacli rpp validate before.rpp` 检查结构，不解释或验证插件状态字节。
- `reacli rpp diff before.rpp after.rpp` 可辅助检查哪些明文字段和不透明
  数据行变化。审阅中应确认只发生了预期的块保留、删除或替换。
- 需要严格字节保留时，再比较被保留块的原始字节或哈希。语义 diff 并不
  等价于整个文件的字节相等，也不证明插件能够加载或音频行为相同。
- 在目标宿主加载、保存或渲染适当的工程副本，验证实际行为。
