# Lua 组合与执行规范

[English](README.md) · [规范首页](../README.zh-CN.md)

以包内 [entry 模板](../../src/rac/data/lua/entry.lua)和 [stdlib](../../src/rac/data/lua/stdlib/)为唯一正本，不在 agent skill 中再复制一套运行时。通过 `rac resources --output ./templates` 导出（不覆盖已有文件），或用 `rac.resources.read_text` 读取。

## 生成操作

```python
from rac.luagen import generate
script = generate({"ops": [
    {"op": "track.create", "args": [0, "Vocal"]},
    {"op": "track.set_volume_db", "args": [0, -6.0]},
    {"op": "marker.add", "args": [1, 0.0, "Start"]},
]}, "edit.lua")
```

输出父目录需存在。`generate` 会覆盖显式输出文件，验证操作名称与参数类型并运行兼容的 `luac -p`。它只支持 [OP_REGISTRY](../../src/rac/luagen/generator.py)，不覆盖所有 stdlib 函数或 REAPER API。即使 body 完成，也需检查操作返回错误。

## 自定义 body

使用任意 API 时，替换导出 entry 的 `body()`，保留异常处理、保存、proof 和退出协议。`RUN.result` 仅放 JSON 可表达的数据；检查 helper 返回值，必要操作失败时抛错。`pcall` 捕获 body 运行时异常，不捕获语法错误或 body 外的所有故障。手写脚本执行前使用 `rac.luagen.validate`。

片段通过文本组合定义 `std_*` 表，不是 `require()` 模块。把需要的片段放在 body 前。Lua 语言本身支持模块，只是这些文件不返回模块表。

| 片段 | 范围 | 边界 |
|---|---|---|
| `track.lua` | 新建/名称/增益/声像/静音/颜色 | 读取新建对象的匹配规则，不默认所有操作幂等 |
| `item.lua` | 媒体/时间/淡变/切分 | 明确媒体路径和目标 item |
| `take.lua` | 源信息/名称/速率/偏移 | helper 使用 active take；并非全部注册为 op |
| `fx.lua` | 添加/探测/参数/预设/旁通 | 归一化值不等于 Hz 或 dB；封装面向普通轨道 |
| `env.lua` | 包络查找/点/scaling | 检查包络是否存在及数值域 |
| `midi.lua` | item/音符/CC | 使用工程时间换算并排序事件 |
| `marker.lua` | marker/region | ID 不等于遍历索引 |
| `routing.lua` | send | 注意方向、类别和重复创建 |
| `project.lua` | tempo/notes/save | 通常由 entry 的 `save_as` 完成持久化 |
| `render.lua` | 配置/触发渲染 | 确认命令可用并检查实际新输出 |
| `snapshot.lua` | 有限状态摘要 | 不代表整个工程或声音身份 |

精确签名从 [stdlib](../../src/rac/data/lua/stdlib/)对应文件读取。常见返回为 `{ok=true, value=..., affected=...}` 或 `{ok=false, reason=...}`；使用 `value` 前先检查 `ok`。

## 可运行 inspector 与完整示例

安装 reacli 和 Lua 5.3/5.4 编译器后，在仓库根目录运行：

```bash
python reference/lua/examples/build_inspector.py ./inspect-project.lua
```

[构建器](examples/build_inspector.py)组合[检查 body](examples/inspect_project.body.lua)，验证替换边界和语法，并拒绝覆盖已有输出。构建阶段不需要运行 REAPER。

```python
from rac.runner import run
proof = run("/absolute/path/to/project.rpp", "inspect-project.lua")
if not proof.ok:
    raise RuntimeError(proof.to_dict())
print(proof.result)
```

它读取版本、OS、资源路径和轨道属性。不传 `save_as` 就不请求保存。Entry 会退出一次性宿主，不应直接在用户正在工作的编辑器 tab 中执行。另见[最小新建示例](../../examples/create_project.py)和[现场合成 showcase](../../examples/README.md)。

同步模板不等待 defer 回调。若扩展为异步任务，需要一起管理完成条件、proof 和退出。语法通过只能证明 Lua 语法有效，不能证明宿主 API 可用、保存成功或插件行为正确。
