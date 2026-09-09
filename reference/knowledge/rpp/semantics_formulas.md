# RPP volume, envelope and timing formulas

> 来源：ReaperDoc 字段说明及源项目在 REAPER 7.62 / macOS 中报告的观察。
> `live` 指历史源测试，当前整理没有逐条复验。新的 API 行为应在目标宿主
> 验证，来源见[清单](../../source-manifest.json)。

## 音量：dB 与线性幅度

```text
linear = 10^(dB / 20)
dB = 20 * log10(linear)      # linear > 0
-6 dB ≈ 0.501187
 0 dB = 1.0
-12 dB ≈ 0.251189
```

零幅度对应负无穷 dB。该幅度换算适用于 `track:VOLPAN` field 1（轨道
音量）及 `item:VOLPAN` field 1（item trim）。源测试报告
`VOLPAN 0.501187` 与 `std_track.set_volume_db(-6)` 一致。

## 音量包络：文件域与 API 域

```text
API 写入: raw = ScaleToEnvelopeMode(scaling, linear)
API 读出: linear = ScaleFromEnvelopeMode(scaling, raw)
源测试对照: DB2SLIDER(-6) ≈ ScaleToEnvelopeMode(1, 0.501187) ≈ 592.848336
```

原记录在 2026-08-02 修正了文件域与 API 域混用的问题：源测试中的音量
包络，RPP/StateChunk 的 `PT` 行保存线性幅度，例如 unity 为 `PT 0 1 0`，
-10 dB 约为 `PT 2 0.31623 0`。API 层则根据 `GetEnvelopeScalingMode`
使用上述转换。此处讨论音量包络，不能推广到声像、静音或插件参数包络。

源测试还观察到：

- 手写 `VOLENV2` 未设置 `VOLTYPE` 时，scaling mode 为 0；设置
  `VOLTYPE 1` 时为 fader mode 1。使用 API 时读取实际 mode。
- mode 0 的转换是恒等操作，因此只测 mode 0 会掩盖读写方向用反的问题。
  测试应包含 mode 1 和预期绝对幅度。
- 没有点的包络可能未被实例化，`GetTrackEnvelopeByName` 返回 nil。
  需要宿主读取的 fixture 应至少包含一个有效种子点。

## Take 源偏移与播放速率

```text
SOFFS = 源内起始偏移（秒）
源消费时长 = item LENGTH × take PLAYRATE
```

上述时长关系用于恒定播放速率、未引入循环或额外时间变换的简单情形。
如果改变播放速率后需要保持相同的源片段范围，应按比例调整 item 长度。
如果要保持相同的工程时间长度，则保留 LENGTH，消耗的源片段长度会变化。

`SOFFS` 等 KEY 在 item 和 take 上下文中的位置需要结合
[schema](../../../src/rac/data/knowledge/rpp_schema.json)理解，不能只按
字段名字匹配。源记录依据 ReaperDoc 整理；复杂 take、循环、拉伸标记和
tempo 变化的行为需要另行验证。

## Item 淡入淡出

```text
FADEIN <shape> <len_s> <other_fields...>
FADEOUT <shape> <len_s> <other_fields...>
```

field 2 是时长（秒）。shape 编号的含义与有效边界需结合目标版本核实；
上游提取的 `enum_candidates` 是候选描述，不代表所有组合经过实测。
未知尾部字段应保留，见[知识缺口](gap_registry.md)。

## MIDI 时间

MIDI source 的 `HASDATA` 行记录其 PPQ 分辨率；源样本常用每四分音符
960 PPQ，不能把该值硬编码为所有 source 的常量。工程秒与 MIDI PPQ 的
转换还依赖 tempo map，使用宿主的 `MIDI_GetPPQPosFromProjTime` 和
`MIDI_GetProjTimeFromPPQPos`。

源项目报告用这些 API 的 MIDI note 插入测试通过。`IGNTEMPO` 等 source
设置会影响时间解释；直接编辑 MIDI 数据前，检查源节拍设置并在目标
工程读回验证。
