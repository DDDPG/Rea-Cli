# reacli

**用脚本操作 REAPER，保留工程内容，并验证每次修改。**

[English](README.md) · [环境配置](docs/environment.md) ·
[API 指南](docs/api.md) · [知识库与 Lua 示例](reference/README.md)

reacli 是面向 [REAPER](https://www.reaper.fm/) 数字音频工作站的 Python 库和
命令行工具。它把 RPP 工程编辑、独立 Lua ReaScript、REAPER 官方 CLI 和产物检查
连接起来，适合自动化脚本、agent 工作流及集成测试：除了进程是否成功退出，还能
检查工程究竟改了什么、渲染结果是否符合预期。

当前版本为 **0.1.0，尚未发布的 alpha 版本**。请从源码目录安装；本文不假设
PyPI 已有可用发行包。API 后续可能调整。

## 可以做什么

- **离线读取和编辑 `.rpp`。** 解析工程结构，修改轨道、媒体项和标记，保留未改动的
  文本及不透明插件数据，并比较工程结构差异。
- **准备 Lua 脚本。** 用限定的操作集生成独立 ReaScript，或基于内置骨架和片段
  编写脚本。生成时自动检查 Lua 语法。
- **执行并留存记录。** 使用专用配置启动 REAPER，另存工程，收集 JSON 结果、日志
  及输入快照。Linux 和 macOS 均支持 worker 并发。
- **验证产物。** 断言工程状态，检查 PCM WAV 的时长、非静音、削波情况和测试音频率。
- **查询知识。** 查询内置 RPP/API 索引，查阅仓库中的工作流说明和 Lua 示例。

REAPER 需要单独安装。reacli 使用官方 CLI 和内嵌 Lua，不包含 REAPER 本体或第三方
插件。执行层支持 Linux 与 macOS；Windows 执行尚未实现，离线 Python 工具不需要
REAPER 环境。

## 从源码安装

下载或克隆仓库后，进入仓库根目录，使用 Python 3.10 或更新版本：

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
reacli --version
```

macOS 的 `python3` 仍可能指向系统 Python 3.9。遇到这种情况，请先按
[环境指南](docs/environment.md)安装新版 Python，再用对应解释器创建环境，
例如 `python3.14 -m venv .venv`。

发行包与推荐命令名为 **`reacli`**，Python 导入名为 **`rac`**。安装后也可使用
兼容命令 `rac` 或 `python -m rac`。请使用独立虚拟环境，避免其他同名 `rac` 包
冲突。Python 3.13+ 会自动安装 `audioop-lts`。

## 无需 REAPER 的快速开始

先导出一个空工程和 Lua 模板，检查工程结构，再查询内置知识。以下命令不需要
REAPER，也不需要 Lua：

```bash
reacli doctor --profile offline --json
reacli resources --output ./quickstart
reacli rpp validate ./quickstart/minimal.rpp
reacli rpp get ./quickstart/minimal.rpp tracks
reacli knowledge rpp track:VOLPAN
reacli knowledge api GetTrack
```

工程校验应返回 `{"ok": true, "tracks": 0, "markers": 0}`。资源导出不会覆盖已有
文件；重复运行时，请换一个输出目录。

也可以完全通过 Python 修改并验证这个工程：

```python
from pathlib import Path
from rac.rpp import parse, emit, patch
from rac.verify import expect

doc = parse(Path("quickstart/minimal.rpp"))
patch.set_marker(doc, index=1, pos=0.0, name="Start")
Path("quickstart/marked.rpp").write_bytes(emit(doc).encode("utf-8"))

saved = parse(Path("quickstart/marked.rpp"))
expect(saved).track_count(0).has_marker(name="Start", pos=0.0)
```

## 在 REAPER 中创建并保存工程

先完成 [Linux 或 macOS 环境配置](docs/environment.md)。执行需要 REAPER 7.x；
生成脚本还需要 **Lua 5.3 或 5.4 的 `luac` 编译器**。macOS 首次运行前，需要在
REAPER 偏好设置中选定 CoreAudio 输出设备。随后初始化并检查环境：

```bash
reacli init
reacli doctor --json
reacli doctor --render --work-dir ./smoke-artifacts --json
```

`doctor --render` 会用独立工程执行 Lua、保存、渲染，并检查 440 Hz WAV。
普通 `doctor` 只检查前置条件，不安装软件。

接着使用上一步导出的 `quickstart` 目录，生成一个创建 **Vocal** 轨道并将音量设为
**−6 dB** 的脚本，再执行并另存工程：

```bash
python - <<'PY'
from rac.luagen import generate

generate({"ops": [
    {"op": "track.create", "args": [0, "Vocal"]},
    {"op": "track.set_volume_db", "args": [0, -6.0]},
]}, "quickstart/create.lua")
PY

reacli exec \
  --project ./quickstart/minimal.rpp \
  --script ./quickstart/create.lua \
  --save-as ./quickstart/created.rpp \
  --run-root ./quickstart/runs

reacli rpp get ./quickstart/created.rpp tracks
```

最后检查已保存的工程。RPP 中的轨道音量为线性幅度，因此需要将分贝换算后断言：

```bash
python - <<'PY'
from pathlib import Path
from rac.rpp import parse
from rac.verify import expect

doc = parse(Path("quickstart/created.rpp"))
expect(doc).track_count(1).track(0).name("Vocal").volume(10 ** (-6 / 20))
print("Saved project verified")
PY
```

执行结果中的 `run_dir` 指向本次记录目录，包含输入快照、脚本、stdout/stderr 日志
和 `proof.json`。工程保存在 `--save-as` 指定的位置。完整 Python 示例见
[examples/create_project.py](examples/create_project.py)，更多说明见
[runner API](docs/api.md#run-a-script)。

## 使用前需要了解的行为

- **进程成功只是其中一项检查。** 生成脚本中的某个操作可能被拒绝，并写入 `result`
  和日志，而脚本整体仍正常完成。应检查这些字段，并断言实际需要的工程或音频结果。
- **脚本以当前用户权限运行。** runner 打开原始工程路径，以保留相对素材引用。
  `save_as` 通过内置骨架请求另存副本；自定义脚本仍可自行写文件。尝试修改重要工程时，
  应先使用副本。
- **配置与工程数据分别管理。** Linux 使用专用 dummy 音频配置。macOS 通过
  `-newinst` 启动独立实例，仅从用户 REAPER 偏好中读取白名单内的 CoreAudio 设置来
  补齐专用配置。并发任务需要不同的资源目录，`Pool` 会自动准备。
- **验证有明确边界。** RPP 语义比较不能证明声音完全相同。音频检查支持单声道或
  双声道的 16/24-bit PCM WAV，响度测量为近似值。详见 [API 行为与限制](docs/api.md)。

实机验证覆盖 macOS 15.5 / Apple Silicon / REAPER 7.62 / Python 3.10、3.14，
以及 Linux / REAPER 7.77 / Python 3.13。测试范围与证据见[验证记录](docs/validation.md)。
其他 REAPER 版本和第三方插件需要在目标环境自行检查。macOS 默认并发方式已验证；
旧 `copy_app=True` 模式曾超时，尚未验证通过。

## 安装包与仓库知识库

安装包包含 2 个 JSON 知识索引、12 个 Lua 文件（1 个入口骨架及 11 个片段），以及
工程样例、比较基准和平台 INI。它们不依赖源码目录，可通过
[`rac.resources`](docs/api.md#bundled-resources) 访问。

[reference 知识库](reference/README.md) 另外整理了 CLI/API 说明、RPP 知识和工作流
示例。**`reference/` 只保留在 Git 仓库，不进入 wheel 或源码发行包 sdist。**
知识索引和 Lua 模板只在 `src/rac/data/` 保留一份，知识库通过链接引用，避免重复维护。

## 文档与开发

- [环境配置与排错](docs/environment.md)
- [Python API、CLI 约定和并发执行](docs/api.md)
- [知识库与 Lua 示例](reference/README.md)
- [验证证据与已知限制](docs/validation.md)
- [贡献指南与本地检查](CONTRIBUTING.md)
- [更新记录](CHANGELOG.md)及[发布流程](docs/releasing.md)

开发时，在前面创建的虚拟环境中运行：

```bash
python -m pip install -e '.[dev]'
python -m pytest
```

默认测试不需要 REAPER；涉及 Lua 的测试需要兼容编译器。实机集成测试需显式启用，
构建与实机测试命令见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证与项目状态

项目自有代码采用 [MIT 许可证](LICENSE)。第三方描述及数据保留原始来源；内置
索引的再分发权限仍需在公开发布前确认，详见
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。REAPER 属于 Cockos，按其自身
条款提供。本项目独立维护，未获 Cockos 背书。
