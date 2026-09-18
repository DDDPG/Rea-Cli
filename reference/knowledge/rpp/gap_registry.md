# RPP knowledge gaps

> 主源：[ReaperDoc](https://github.com/DDDPG/ReaperDoc) @ `32047bb`；
> 源项目记录日期：2026-07-30，后续 JSFX 补充：2026-07-31。
> 本文保留尚未解决的格式问题和有限的历史观察，不代表当前版本已完成验证。

## 未完整描述的领域

- **渲染格式数据 `RENDER_CFG`：**Ultraschall 文档解释过部分编码，
  但当前 schema 没有可跨格式、跨安装使用的写入契约。按
  [不透明块规则](blob_denylist.md)保留或整体替换，设置参数时优先使用
  宿主 API，见[渲染笔记](../reascript/render_internals.md)。
- **JSFX 实例 `<JS>`：**[JSFX 手册](../reascript/jsfx/README.md)覆盖效果器
  源码；它不完整描述 RPP 中的参数/扩展状态序列。官方文档整理属于文档
  证据，不能视为每种序列化格式都已通过实机验证。
- **`<SOURCE VIDEO>` / `<SOURCE SECTION>`：**当前提取的 schema 覆盖不足，
  未识别数据应保留。
- **插件状态：**VST、AU、CLAP 私有块依赖插件自己的格式；按不透明数据处理。
- **`<EXTENSIONS>` / `<PROJBAY>`：**扩展私有内容和部分 project bay 字段
  没有完整解释；不能据通用 schema 推断其内部结构。

## 字段缺失和含义不明

`project:MARKER` 的 ReaperDoc 字段说明在 field 4 后跳到 field 8（GUID）。
源项目曾观察到下面这类行：

```text
MARKER 1 30 example-marker 0 0 1 B {GUID} 0 2
```

中间各值不能仅靠这条样例推断语义。写入前应参照目标宿主样本并做逐字段
保存读回测试；未知尾部字段原样保留。

[extract_report.json](extract_report.json)记录了这次 schema 提取的
5 个 TODO key 和 6 个 NOT CLEAR key，包括 `MASTER_NCH`、`MASTERPEAKCOL`、
`SMPTESYNC`、`MIXERUIFLAGS`、`MASTERTRACKVIEW` 和 `PROJBAY` 的部分字段。
这些列表是一次提取结果，当前没有自动同步到上游。新的解释应附来源或
可复现的宿主实验，并更新对应 schema/文档的证据状态。

## 源项目报告的补充观察

- **默认字段补全：**REAPER 7.62 / macOS 把一个 5 行极简工程保存为
  126 行，补入 grid、metronome 和 render 等设置。可查看
  [保存后 fixture](../../../tests/fixtures/minimal_after_reaper_save.rpp)。
  该样本的 `AUTOXFADE=129` 与 ReaperDoc 的 `192` 不同；默认值随配置
  变化，不能直接作为所有安装的标准值。
- **上下文敏感的 KEY：**`VOLPAN`、`SOFFS`、`NAME`、`PLAYRATE`、`LOOP`、
  `COMP`、`SEL`、`GUID`、`BEAT`、`PANMODE`、`<SOURCE>` 和 `<NOTES>` 在
  不同 section 中含义不同。查询
  [schema](../../../packages/reacli/src/rac/data/knowledge/rpp_schema.json)时使用
  `<section>:<KEY>`，例如 `track:VOLPAN`。
- **UTF-8 marker 名称：**源测试中的中文名称可以直接写入、读回。
- **缺失媒体提示：**REAPER 7.62 / macOS 在使用 `-ignoreerrors` 的源测试中
  跳过了缺失媒体提示。它不证明媒体已经可用，也不涵盖所有错误对话框。

## 可复现的后续验证方向

- 在目标版本中构造不同 FADEIN/FADEOUT shape，保存读回并确认枚举边界。
- 用不同精度的 envelope `PT` 点保存读回，观察数值格式和精度变化。
- 对尚未解释的尾部字段逐个变异，记录 REAPER 版本、平台、原始样本、
  读回结果和实际播放行为，避免只凭文本 diff 判断语义。
