# 调用与交付规范

[English](README.md) · [规范首页](../README.zh-CN.md)

本规范面向使用 reacli 构建自动化的开发者，描述当前仓库的调用约定，不代表所有 REAPER 版本。发行包名为 `reacli`，Python 导入名为 `rac`；`rac` 与 `reacli` 是同一 CLI 的别名。外部 Python 负责调度，不直接提供宿主内的 `reaper.*` 对象。

## 选择执行路径

| 任务 | 建议路径 | 应提供的证据 |
|---|---|---|
| 查询或修改语义明确的静态字段 | 离线 `rac.rpp` | 重新解析、目标属性断言、审阅 diff |
| 生成器已支持的操作 | `rac.luagen.generate` → `rac.runner.run` | 语法预检、proof、保存后属性断言 |
| folder 深度、多 take、总线 FX、未封装操作 | 在包内 entry 模板中编写 Lua → runner | 相同协议，显式读回对象及参数 |
| 插件状态、随 tempo 变化的 MIDI、渲染、宿主相关行为 | Lua 调用 REAPER API | 宿主读回；涉及声音时检查音频 |
| 编写音频或 MIDI 处理器 | JSFX 源码及宿主加载 | DSP 和重新加载测试；Lua 编译器不能代替 |

可组合离线与宿主路径。字段语义不明确时交给宿主；不要杜撰生成器注册表中不存在的 `op`。

## 准备环境

在仓库中用 `python -m pip install -e .` 安装，根据任务选择检查范围：

```bash
rac doctor --profile offline --json
rac doctor --profile lua --json
rac init --resource ./automation-resource
rac doctor --profile full --resource ./automation-resource --json
```

需要 Python 3.10+；生成 Lua 需要兼容的 Lua 5.3/5.4 编译器；执行需要 REAPER 及平台依赖。配置方法、`RAC_LUAC_BIN`、`RAC_REAPER_BIN` 和资源目录优先级见[环境指南](../../docs/environment.md)。Linux 的显示与音频配置不能直接套用到 macOS。

runner 默认处理实例隔离和启动设置，调用者不用改变 `run()` 的用法。缺少 VST 扫描偏好时默认关闭启动重扫，已有显式插件偏好保留。macOS 命令末尾添加 `-ApplePersistence NO`，针对自动化进程抑制 Cocoa 恢复，不修改全局偏好。这不保证能跳过所有弹窗，新插件可能需要主动扫描。不要用 `killall`、复制 app 的旧配方或“必须关闭所有 REAPER”的全局规则替代 runner。

## 执行和检查

1. 明确输入、输出及媒体位置，使用独立输出并先创建父目录。runner 归档的输入是调用证据，不是沙箱副本；实际打开原工程以保留相对媒体路径。
2. 调用 `run` 前生成或验证 Lua；`run` 和 `rac exec` 本身不做语法预检。
3. 使用包内 entry 协议时，通过 `save_as` 持久化修改；只读检查可省略。不要依赖 dirty 标志或退出时自动保存。
4. 检查 `proof.ok`、proof 格式、`proof.result` 内的操作错误，并重新解析实际输出。成功状态不代表每条生成操作都成功。
5. 渲染后检查实际生成的新音频、格式和信号，优先使用新文件名，不盲目删除已有渲染。

```python
from rac.luagen import validate
from rac.runner import run
from rac.verify import proof_check

validate("edit.lua")
proof = run("input.rpp", "edit.lua", save_as="output.rpp",
            resource="automation-resource", run_root="runs", timeout=60)
if not proof.ok:
    raise RuntimeError(proof.to_dict())
proof_check(proof)
errors = {k: v for k, v in (proof.result or {}).items() if k.endswith("_error")}
if errors:
    raise RuntimeError(errors)
# 接着断言任务要求的工程或音频属性。
```

## 失败、重试与并发

`timeout`、`reaper_crash`、`proof_missing` 被分类为可重试，但 `run` 不会自动重试。先检查运行目录：缺少 proof 可能由弹窗、脚本不兼容、崩溃或协议失败引起。解决原因或确认重复执行安全后，再进行次数有上限的重试。

`Pool` 在崩溃或缺少 proof 后可能重建并重试一次。它为 worker 分配独立资源目录、拒绝输出冲突并保留输入顺序。资源隔离不约束 Lua 的任意文件写入。直接并发调用必须使用不同资源目录。新建、切分和插入媒体不自动幂等；使用稳定标识或全新输入，存在重名对象时不能只凭名称判断。

## 按任务提供交付证据

记录输入输出、相关的 REAPER/平台/插件版本、脚本、proof 及检查过的属性。媒体随工程保存，或说明合成和环境准备方式。GUI 截图能展示位置，不能证明数值或音频正确。

`state_hash` 只是有限状态摘要，不是全工程身份。语义 diff 默认容忍部分默认字段和 GUID 差异，不证明声音相同。音频检查支持单/双声道 16/24-bit PCM WAV；采样峰值不是 true peak，近似 LUFS 不是合规响度计。

CLI 退出码：`0` 成功；`2` 数据/验证或不可重试执行失败（也包括非空语义 diff）；`3` 可重试的 `exec` 失败；`4` 初始化/分派或 doctor 失败。各命令细节见[完整 API 约定](../../docs/api.md)，平台实测范围见[验证记录](../../docs/validation.md)。
