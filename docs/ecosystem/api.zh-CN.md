# 共享解析器与音频接口

[English](api.md) · [API 目录](../api.md) · [完整示范](../../examples/data_roundtrip.py)

## 安装与职责

在完整仓库根目录安装音频工作流所需的两个包：

```sh
python -m pip install ./packages/reaper-parser './packages/reacli[audio]'
```

仅解析工程时，安装 `./packages/reaper-parser` 即可。parser 核心不依赖 rac、NumPy
或 REAPER；导入和解析不会启动宿主。显式渲染、导入需要 REAPER、Lua 和相应的
[环境配置](../environment.md)。

## 文档与对象视图

```python
from pathlib import Path
from reaper_parser import parse, emit

doc = parse('<REAPER_PROJECT\n  <TRACK {EXAMPLE}\n    NAME "Vocal"\n    VOLPAN 1 0\n  >\n>\n')
track = doc.project.tracks[0]
track.name = 'Lead vocal'
assert doc.tracks()[0].find_line('NAME').values == ['Lead vocal']
assert 'Lead vocal' in emit(doc)
# 目标文件不能已存在，父目录需要预先建立。
doc.save(Path('edited.rpp'))
```

`parse(source)` 接受 `Path`、文件名字符串或 RPP 文本。读取文件时推荐使用 `Path`。
返回 `Document`；结构错误抛出 `RPPParseError`，文件访问错误向上传递。
`emit(doc)` 返回文本。`doc.save(path, overwrite=False)` 返回 `Path`，默认拒绝覆盖
（`FileExistsError`），不会创建父目录。读写通过 surrogateescape 保留不可解码字节；
未编辑的文档保留原始文本和换行。文件和文本输入限制为 64 MiB、1,000,000 个逻辑换行
和 256 层嵌套；超过限制的输入会在无界解析前拒绝。

`doc.tracks()` 返回底层 `Element`，`doc.project.tracks` 返回指向同一批节点的 Track
视图。Item、Take、FX、Envelope、Source 也引用共享文档；take/FX 使用父节点中的范围，
不是独立副本。优先用视图 setter 或 `rac.rpp.patch`；直接改节点列表时需正确设置 dirty
并调用 `doc.touch()`。完整成员见[对象实现](../../packages/reaper-parser/src/reaper_parser/model.py)。

## 字段、证据与写入

```python
for field in track.fields():
    print(field.token, field.index, field.raw, field.semantic_status,
          field.write_status, field.value)
assert track.raw('VOLPAN', 0) == '1'
assert track.raw('ABSENT') is None
```

`fields()` 枚举当前对象直接包含的块头和行字段，保留重复行；不会递归枚举子对象，
也不会为缺失字段生成记录。`FieldValue` 包含 token、**1 基** index、raw、location、
可选 metadata、semantic_status、write_status 和 value。location 是结构标签，不是字节偏移。
未知语义的 value 返回原字符串；其他已记载类型可能转换为 int/float，转换成功不代表
语义已验证。必须单独检查状态。无效数值会抛出转换错误。

`raw(key, index=0, default=None)` 使用 **0 基**索引，读取第一条匹配行；缺失时返回
调用者的 default。便捷属性可能有回退值，例如 track volume 为 1、pan 为 0。
这些是 API 回退值，不代表文件包含该字段，也不代表已验证的宿主缺省。
需要区分缺失与存在时，使用 raw 和字段状态。

`set_raw(key, index, value)` 使用 0 基索引，是底层修改入口；可在 index=0 时新增行，
但拒绝凭空补齐前置槽位及多行值。`track.name` 等便捷 setter 使用这一机制。
`set_field(key, index, value)` 使用规范的 **1 基**索引；没有 verified 写入契约时抛出
`ValueError`，通过后执行已有类型检查，不等同于宿主语义验证。原始修改不会提升字段确认状态。
验证持久化结果时，应保存后重新解析。

## 原始音频

```python
from rac.media import read_source

audio = read_source('media/input.wav', project='session.rpp')
assert audio.samples.ndim == 2
print(audio.sample_rate, audio.metadata['level'])  # source
```

`read_source(source, *, project=None, path_map=None)` 接受媒体路径、Take/Source 视图或
`MediaResult`。相对路径以工程目录为基准；视图可使用文档源路径，内存文本工程需要显式提供
project。跨系统路径用前缀映射，例如 `{'D:/session': '/mnt/session'}`；多个前缀同时匹配会
报错，不自动搜索磁盘。

返回 `AudioData(samples, sample_rate, metadata)`，数组为 float32、`(frames, channels)`，
保留声道和采样率，并记录文件散列与版本。不会重采样、下混，也不应用 item 偏移、淡化、
播放速率或 FX。MIDI、SECTION、嵌套工程 source 需要宿主解释。
传入渲染返回的 MediaResult 会保留 `level='rendered'`；只传音频文件名无法恢复这条来源链。
解码后的 float32 音频超过 256 MiB 时会拒绝读取。

## 显式宿主渲染与导入

```python
from pathlib import Path
from rac.media import render, read_source, import_audio

rendered = render('session.rpp', work_dir='new-render',
                  sample_rate=48000, channels=2, time_range=(0, 1),
                  tail_seconds=0, timeout=60)
audio = read_source(rendered)
assert audio.metadata['level'] == 'rendered'
result = import_audio('session.rpp', Path('processed.wav').resolve(),
                      work_dir='new-import', name='Processed audio',
                      position=0, timeout=60)
print(result.path, result.manifest_path)
```

`render(project, *, work_dir, sample_rate=48000, channels=2, time_range=None,
tail_seconds=0, track_guids=None, path_map=None, reaper_bin=None, timeout=60)`
返回指向渲染 WAV 的 MediaResult。时间单位为秒。指定轨道 GUID 时保留相连的 send/folder
依赖，经 master 输出，原来的 mute/solo 状态仍然有效；不承诺严格隔离 stem。

`import_audio(project, audio, *, work_dir, name='Processed audio', position=0,
path_map=None, reaper_bin=None, timeout=60)` 返回的 MediaResult.path 指向**保存后的 RPP**，
不是音频。它新增轨道/item，关闭默认淡化，另存并检查 GUID、路径和时序。
新增 audio 参数使用已存在的绝对路径；这里的 path_map 作用于工程原有媒体准备，
不会为该新增音频参数解析相对路径。

两种操作均要求全新工作目录，在副本上工作并保留诊断。MediaResult 包含 path、
manifest_path、metadata、proof。分别检查 manifest 中的验证项、保存工程与实际音频；
进程退出码不能替代结果验证，原工程也不是输出目标。

`MediaError` 包含 code 和可选 manifest_path，区分依赖缺失、媒体缺失、路径歧义、
不支持的 source、解码及宿主失败。无效数值可能抛出 ValueError，文件系统错误可能直接传递。
早期校验失败时还没有 manifest；应保留已有诊断、修正原因，再换新目录运行。
参见[完整确定性处理示范](../../examples/data_roundtrip.py)与[验收边界](README.md)。
