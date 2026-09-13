# RPP 编辑规范

[English](README.md) · [规范首页](../README.zh-CN.md)

RPP 是带上下文语义和不透明状态的嵌套文本。使用[解析器与 patch 工具](../../docs/api.md#read-edit-and-compare-rpp-files)，不要跨 track、item、take 全局替换同名字符串。

## 读取、修改、保留

```python
from pathlib import Path
from rac.rpp import parse, emit, patch
from rac.verify import expect

doc = parse(Path("input.rpp"))  # 输入需要至少一条轨道
track = doc.tracks()[0]
patch.set_track_name(doc, track, "Bass")
patch.set_track_volume(doc, track, 10 ** (-6 / 20))
Path("output.rpp").write_bytes(emit(doc).encode("utf-8"))
expect(parse(Path("output.rpp"))).track(0).name("Bass").volume(10 ** (-6 / 20))
```

文件名使用 `Path`：不存在的字符串路径可能被当作 RPP 文本解析。保留未修改节点、未知字段、换行风格和不透明字节；按 bytes 写出可避免换行转换。[带注释的结构树](../knowledge/rpp/annotated_tree.md)是说明资料，不是可运行工程。

```bash
rac knowledge rpp track:VOLPAN
rac rpp validate output.rpp
rac rpp get output.rpp track:0:VOLPAN
rac rpp diff input.rpp output.rpp
```

有意修改通常会产生 diff（退出码 2），应审阅差异，不应把有差异当成程序崩溃。更严格的比较可用 `semantic_diff(..., strict_guid=True, use_defaults=False)`；它仍不是字节比较或音频测试。

## 单位与上下文

| 属性 | RPP 上下文 | 宿主 API 或约定 |
|---|---|---|
| 轨道增益 | `track:VOLPAN` field 1 | `D_VOL`，线性幅度 |
| 轨道声像 | `track:VOLPAN` field 2 | `D_PAN`，-1 到 1 |
| 轨道名 | track 的 `NAME` | track 的 `P_NAME` |
| Item 时间 | item 的 `POSITION`、`LENGTH` | `D_POSITION`、`D_LENGTH`，秒 |
| Take 源偏移/速率 | 对应 take 的 `SOFFS`、`PLAYRATE` | `D_STARTOFFS`、`D_PLAYRATE` |
| 轨道静音 | `MUTESOLO` field 1 | `B_MUTE` |

schema 字段位置从 1 开始，Python track/item 索引从 0 开始。`NAME` 和 `VOLPAN` 不能脱离上下文解释。多个 take 必须区分各自记录，不能修改 item 内所有 `NAME`。Marker ID 不等于遍历索引；不要根据一行 MARKER 样本猜测 region 序列化。

`linear = 10 ** (dB / 20)`；正幅度时 `dB = 20 * log10(linear)`，零幅度对应负无穷 dB。简单恒速情况下，源消费时长 = item 长度 × take 速率；循环、拉伸标记和 tempo 变化需单独处理。

音量包络 API 可能需要根据实际 scaling mode 使用 `ScaleToEnvelopeMode` / `ScaleFromEnvelopeMode`。不能把 API 接受的推子域值直接写进 RPP 的 `PT` 行。见[公式证据](../knowledge/rpp/semantics_formulas.md)：文件域结论属于历史观察，不能推广到全部包络。MIDI PPQ 分辨率由 source 决定，不固定为 960；秒数换算需要 tempo map。

## 不透明数据与对象身份

保留 VST/AU/CLAP 状态、JSFX 实例序列化、渲染/录制格式块、编码节拍器数据、SysEx、扩展和未知 source。可复用宿主生成并验证过的完整块，但必须保持标识和引用一致。修改 `PRESETNAME` 不等于应用预设；任意替换 FXID/GUID 可能破坏包络链接。插件修改、复杂路由/folder 和含义不明的数据交给宿主 API。

详细资料：[编辑边界](../knowledge/rpp/blob_denylist.md)、[知识缺口](../knowledge/rpp/gap_registry.md)、[schema](../../src/rac/data/knowledge/rpp_schema.json)、[提取报告](../knowledge/rpp/extract_report.json)。保存样本中的默认值仅反映特定宿主与配置。解析通过不证明媒体可用、路由正确或插件状态有效。
