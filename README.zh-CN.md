<p align="center"><img src="docs/assets/reacli-icon.png" width="160" alt="Rea-Cli 图标"></p>
<h1 align="center">Rea-Cli</h1>

<p align="center"><strong>REAPER coding. REAPER executing. REAPER verifying.</strong></p>
<p align="center">RPP-as-code · Lua/ReaScript · Agent 接入 · 工程/音频验证</p>
<p align="center">
  <a href="README.md">English</a> · 简体中文 ·
  <a href="docs/README.md">文档</a> ·
  <a href="examples/create_project.py">完整示例</a>
</p>

---

Rea-Cli 是一个可以接入主流 agentic harness 的 Python 库、CLI 和 REAPER 参考环境，
面向 [REAPER](https://www.reaper.fm/) 工程自动化。在这里，RPP 被视为工程源码：
agent 可以编写或修改它，`rac` 负责预检查和检查，REAPER 仍是权威的 parser 和执行环境。
此外，项目还支持 Lua ReaScript 编写、隔离执行，以及保存后工程和渲染音频的验证。

Rea-Cli 本身不是完整的 agent harness，也不是持久化的 REAPER 远程控制服务器。
Python 库用于编程式工作流，CLI 用于检查和隔离执行，仓库内的 skill 则用于向 agent
注入 Rea-Cli 相关的工程知识。

Rea-Cli **只使用 REAPER 原生 ReaScript API**，不需要 **SWS 扩展**、**ReaPack**
或任何其他 REAPER 附加组件，也不会安装它们。仓库内的历史参考资料和示例工程可能
提到 SWS action，那只是查询数据，不是运行依赖。

## 快速开始

如果还没有安装 Rea-Cli，请先按下面的[安装](#安装)选择合适的路线，再运行与你的工作流
对应的命令。

### 不启动 REAPER 的快速体验

检查内置空工程并查询包内知识索引：

```bash
reacli doctor --profile offline --json
reacli resources --output ./quickstart
reacli rpp validate ./quickstart/minimal.rpp
reacli knowledge api GetTrack
```

校验结果应为 `ok: true`、轨道数为 0。资源导出不会覆盖已有文件，重复运行时请使用新目录。
这条路径只需要 Python。

### 从零构建可播放工程（需要 REAPER）

![从空白工程开始，逐步构建 REAPER session 的 52 个中间状态](https://res.cloudinary.com/ybukqfxy/image/upload/v1789647834/showcase_compressed.gif)

这个演示会从空白工程构建一个可直接播放的 REAPER session。请先按路线 B 从源码安装，
并按[环境指南](docs/environment.md)配置 REAPER，再在仓库根目录运行：

```bash
reacli init
reacli doctor --json
python examples/show_session.py ./demo/my-first-session
```

在 REAPER 中打开 **`demo/my-first-session/Show-Session.rpp`**，按播放即可。
工程内嵌 MIDI，并使用 REAPER 自带的 **ReaSynth**，不需要音频素材或第三方乐器。
每次运行请使用新的输出目录；需要 WAV 预览时追加 `--render`。如果找不到 ReaSynth，
请按[环境指南](docs/environment.md#plugin-discovery-and-macos-window-restoration)准备独立资源的 VST 索引。

`examples/show_session.py` 和 `examples/create_project.py` 会把所需资源导出到输出目录，
因此**不需要**先执行上面的 `reacli resources`。两者都需要源码 checkout，因为示例位于
仓库中而不是 wheel 内。

GIF 展示的工程结构、效果器设置、验证边界和 52 个构建中间状态（checkpoint），见[可播放演示指南](examples/README.md#playable-show-demo)。

## 名称速查

项目里有几个相近的名字，对应关系如下：

| 名称 | 类型 | 出现位置 |
|---|---|---|
| `reacli` | PyPI 发行包名，也是主 CLI 命令 | `pip install reacli`、`reacli doctor` |
| `rac` | Python 导入包名**兼** CLI 别名 | `import rac`、`rac doctor` |
| `reaper-parser` | 独立 parser 的 PyPI 发行包名 | `pip install reaper-parser` |
| `reaper_parser` | 该 parser 的 Python 导入包名 | `from reaper_parser import parse` |
| `reacli[audio]` | WAV 检查与渲染所需的可选扩展 | `pip install './packages/reacli[audio]'` |

`reacli` 和 `rac` 是同一个命令行程序的两个入口，发行版同时注册两者。
`reacli` 声明依赖 `reaper-parser`，因此用一条命令成对安装可以让版本保持匹配。

## 安装

需要 **Python 3.10+**。REAPER、Lua 和所有系统库都需要单独安装，见[前置要求](#前置要求)。

### 路线 A —— 安装正式发布版

只想使用 CLI 和 Python API，不需要本仓库源码：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install "reacli==0.1.0" "reaper-parser==0.1.0a1"
reacli --version
```

WAV 和渲染检查需要额外的 audio 扩展：

```bash
python -m pip install "reacli[audio]==0.1.0"
```

参见 [`reacli` PyPI 页面](https://pypi.org/project/reacli/0.1.0/) 和
[`reaper-parser` PyPI 页面](https://pypi.org/project/reaper-parser/0.1.0a1/)。

### 路线 B —— 从源码 checkout 使用

需要运行示例、阅读 `reference/` 手册或参与开发时使用：

```bash
git clone https://github.com/DDDPG/Rea-Cli.git
cd Rea-Cli
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install ./packages/reaper-parser ./packages/reacli
reacli --version
```

### 应该装哪一个？

**当前状态：** 0.1.0 alpha。已发布的 `reacli==0.1.0` 和 `reaper-parser==0.1.0a1`
构件不可变，且上传时间早于本仓库现有的资源、压缩包、parser 和音频安全防护。
因此：从 PyPI 安装得到的是加固前的运行时，从当前 checkout 安装得到的是加固后的版本。
两者的 API 都可能继续调整。上面的路线 B 安装的是较新的代码，下次上传会使用新的版本号
（见[发布流程](docs/releasing.md)）；在那之前两条路线的代码并非逐字节一致，这是预期情况
而不是缺陷。
安装包与 CLI 名称为 `reacli`，Python 导入名为 `rac`。

## 前置要求

安装 `reacli` 不会安装 REAPER、Lua 或系统库。请按实际用途选择所需项：

| 依赖 | 用途 | 说明 |
|---|---|---|
| Python 3.10+ | 全部功能 | 系统解释器若仍为 3.9 则无法运行本包；macOS 请先确认 `python3 --version`。 |
| 官方 REAPER 7.x | 执行、渲染、实机检查 | 未认证最低小版本。请从 [reaper.fm](https://www.reaper.fm/download.php) 下载并单独安装；REAPER 为商业软件，按 [Cockos 条款](https://www.reaper.fm/purchase.php)提供。 |
| 图形会话 | 执行、渲染 | macOS 依赖**已登录的桌面会话**，无桌面服务或无头 CI 不被支持；Linux 需要可用的 `DISPLAY`，或 `xvfb-run`、`Xvfb` 与 `xauth`。 |
| macOS：已完成首次启动 | 执行、渲染 | 需先打开一次 REAPER，并在 **Preferences > Audio > Device** 中选择输出设备。**即使只做离线渲染**也必须先配置好 CoreAudio 输出。 |
| Linux：GTK3、ALSA、Xvfb、xauth | 执行、渲染 | Debian/Ubuntu 与 Fedora 的包名见[环境指南的 Linux 章节](docs/environment.md#linux)。 |
| Lua 5.3 或 5.4 的 `luac` | 通过 CLI 生成 Lua | 仅用于语法预检；宿主执行使用 REAPER 内置 Lua。不支持 Lua 5.5。 |
| SWS、ReaPack、MCP 服务 | — | **不需要。** Rea-Cli 使用 REAPER 原生 ReaScript API，不安装任何附加组件。 |

**操作系统支持：** 执行层支持 macOS 和 Linux。Windows 目前支持离线 parser 和
RPP 检查，**不支持**通过 `rac` 执行 REAPER。

macOS 使用 Homebrew 时可安装新版 Python 与 `lua@5.4`：

```bash
brew install python lua@5.4
```

完整的平台配置、程序路径与排错说明见[环境指南](docs/environment.md)。

## 一个简短的 Python 示例

下面使用前面「不启动 REAPER 的快速体验」导出的 `quickstart` 资源，创建一条 **Vocal**
轨道，将音量设为 **−6 dB**，另存并验证工程：

```python
from pathlib import Path
from rac.luagen import generate
from rac.rpp import parse
from rac.runner import run
from rac.verify import expect

root = Path("quickstart")
script = generate({"ops": [
    {"op": "track.create", "args": [0, "Vocal"]},
    {"op": "track.set_volume_db", "args": [0, -6.0]},
]}, root / "create.lua")

proof = run(
    root / "minimal.rpp", script,
    save_as=root / "created.rpp",
    run_root=root / "runs",
)
assert proof.ok, proof.to_dict()
expect(parse(root / "created.rpp")).track_count(1).track(0) \
    .name("Vocal").volume(10 ** (-6 / 20))
print(proof.run_dir)
```

`generate(...)` 会写出 `quickstart/create.lua`。下面这条 CLI 命令运行的就是同一个
生成的脚本，因此**必须先执行上面的 Python 片段**，否则文件不存在：

```bash
reacli exec --project ./quickstart/minimal.rpp \
  --script ./quickstart/create.lua --save-as ./quickstart/created.rpp \
  --run-root ./quickstart/runs
```

一个自带资源导出、可直接运行的完整示例见 [examples/create_project.py](examples/create_project.py)。

## Harness quick start：让 agent 安装并开始使用

已经在使用 **Claude Code、Codex 或 Qwen Code**？直接把下面这句话交给 agent：

> 请阅读 https://github.com/DDDPG/Rea-Cli 及其中的 `docs/harness/README.zh-CN.md` 安装指南，将 ReaCli CLI toolkit 和 `reaper-agent-cli` skill 安装到新建的 `my-reaper-work` 项目，适配我正在使用的 harness。检查 Python、CLI、Lua 和本机 REAPER 是否可用，并告诉我如何开始使用。

接入组件是项目级的 **CLI toolkit + skill**，通过 harness 已有的 shell 工具执行。
[完整安装指南](docs/harness/README.zh-CN.md)列出了三个 harness 的技能位置、环境要求
以及候选 bundle 的安装方法。

**也可以自己安装：**在本地仓库根目录用 Python 3.10+ 执行：

```sh
python integrations/agents/reaper-agent-cli/scripts/install.py --source . --project ../my-reaper-work --harness all
```

进入新目录打开 Claude Code、Codex 或 Qwen Code，输入：
“使用 reaper-agent-cli skill 检查环境，在 REAPER 中新建工程，保存并验证实际渲染音频。”
项目级技能通过 shell 调用绑定的 CLI/Python，无需 MCP 服务；REAPER、Lua 和 harness 登录
需提前准备。发布 bundle 中的候选 wheel 也支持无 checkout 安装。

详见[三个 harness 的快速接入](docs/harness/README.zh-CN.md)、
[一句指令 showcase 需求](integrations/agents/acceptance/showcase-brief.md)和
[实际验收记录](docs/harness/acceptance.md)。

## 项目亮点

| 重点 | Rea-Cli 的做法 | 与常见替代方案的区别 |
|---|---|---|
| 面向 turn-taking agent | 每一轮都有明确的源码、隔离执行、产物和验证结果 | [`reapy`](https://github.com/RomeoDespres/reapy)、[`reaper-daemon`](https://github.com/wretcher207/reaper-daemon)、OSC 和类似项目更适合连续 live session，但也会带来更多隐式会话状态 |
| REAPER API 接入 | 保留原生 Lua/ReaScript 作为最终扩展路径；agent 可以依据 reference 直接编写宿主侧操作，不必等待每个 API 都被包装成工具 | 高层 wrapper 和 [`reaper-cli`](https://github.com/EmNudge/reaper-cli) 这类 tool catalog 提供现成命令，但工具数量本身也会形成维护面 |
| RPP-as-code | 将 RPP 视为工程源码/声明式工程语言；`rac` 提供 pre-check、查询和 diff，REAPER 负责权威解析和执行 | [`rpp`](https://github.com/Perlence/rpp) 这类 RPP 项目通常专注 parser/emitter，实时控制项目则专注向宿主发送命令 |
| 结果验证 | 将语法检查、保存后工程断言、执行 proof 和渲染音频检查接到同一条流程中 | 很多 live-control 集成把命令发送和验收逻辑分开处理 |
| 接入主流 harness | Python 库、CLI 和仓库 skill 可以接入现有 agent harness；Rea-Cli 不试图替代主 harness | MCP server、daemon 或 standalone agent 通常自带控制面和生命周期管理 |
| 执行方式 | 单次任务不需要为每轮都维护常驻 bridge，同时可用 `Pool` 执行相互独立的任务 | 需要低延迟交互控制时，常驻 bridge 和 OSC 仍然更合适 |

在这个工作流中，大面积 RPP 修改由 agent 或外围 harness 完成。`rac` 是 pre-check
和验证层，不替代 REAPER 的 parser、工程语义或执行环境。

## 可以做什么

- **处理 RPP 源码。** 预检查、查看和比较轨道、媒体项及标记；保留未修改的文本和插件数据，
  由 agent 编写工程变更。
- **编写脚本。** 用已有操作集生成建轨、MIDI 音符、效果器、发送路由和标记等 Lua 操作。
- **执行 REAPER。** 使用独立配置及并发 worker，另存工程，并保留输入快照、日志和执行记录。
- **验证结果。** 断言工程属性，检查 PCM WAV 的时长、静音、削波及测试音的主频。
- **查询知识。** 查询内置 API 和格式索引，或阅读仓库中的[开发规范](reference/README.zh-CN.md)。

基本流程：

```text
Agent / Python / CLI → RPP 或 Lua 源码 → rac pre-check → REAPER → 保存工程 / 渲染音频 → 验证
```

## 默认启动行为

现有 `run()` 和 `Pool.map()` 调用无需增加参数：

- 未明确配置 VST 扫描选项时，默认**不在启动时重新扫描**；macOS 会补充本机已有的 VST 索引。
- 未明确配置 macOS CLAP 路径时，使用独立资源目录内的路径。
- macOS 自动化实例禁用窗口状态恢复，避免强制停止后的 Reopen 弹窗阻塞。

已有明确插件设置会保留。新增插件需要主动扫描，自定义 CLAP 路径仍可能触发发现过程。
这些默认设置不会阻止工程实际使用的插件加载，也无法排除插件自身的弹窗。
详见[插件配置说明](docs/environment.md#plugin-discovery-and-macos-window-restoration)。

## 使用边界

- 进程完成不代表所有操作都成功。应检查 `proof.result` 与日志，再断言所需工程或音频属性。
- 脚本以当前用户权限运行。runner 打开原工程路径以保留相对素材引用，生成脚本支持另存副本；
  尝试修改重要工程时请使用副本。
- 执行层支持 macOS 和 Linux，尚未实现 Windows 执行。不同 REAPER 版本及第三方插件需在目标机器验证。
- 音频检查支持单声道或双声道的 16/24-bit PCM WAV，响度为近似测量；工程结构相同不代表声音完全相同。
- Rea-Cli 调用 REAPER 原生 ReaScript API，不安装、不加载也不要求 SWS、ReaPack
  或其他扩展；依赖第三方扩展的脚本不在已验证范围内。

已测试的环境与验证范围见[验证记录](docs/validation.md)。

## 开发

```bash
python -m pip install -e ./packages/reaper-parser -e './packages/reacli[audio,dev]'
python -m pytest                         # 默认跳过实机测试
RAC_TEST_LIVE=1 python -m pytest -m live  # 需先配置本机 REAPER
npm ci --prefix apps/reaperdoc
python tools/build_release.py --output dist/new-candidate
python -m twine check dist/new-candidate/reacli/* dist/new-candidate/reaper-parser/*
python scripts/check_dist.py dist/new-candidate/reacli
```

仓库按运行代码、示例和参考资料划分：

```text
packages/reacli/src/rac/     Python 库、CLI 及内置运行资源
packages/reaper-parser/     无宿主依赖的保真解析器
apps/reaperdoc/             独立 ReaperDoc 的生态集成副本
schema/rpp/                本仓库版本化规格、证据与生成物
tools/                     跨组件生成与构建工具
examples/    可运行的工作流示例
tests/       离线测试、按需启用的实机测试与合成素材
docs/        环境、API、验证及发布文档
reference/   双语开发规范及历史证据，不进入 wheel 或 sdist
integrations/agents/  可独立安装的 REAPER agent bundle
scripts/     环境引导与发行包检查
.github/     CI、问题模板和手动发布工作流
```

开发约定见 [CONTRIBUTING.md](CONTRIBUTING.md)。
虚拟环境、REAPER 执行产物和本地配置已由 Git 忽略。

## Rea-Cli Agent skill

[Agent bundle 源码](integrations/agents/reaper-agent-cli/SKILL.md)包含自包含的 skill、
精简参考和示例。候选产物中的 `reaper-agent-cli.zip` 可独立解压安装，无需完整 checkout。
需要另外安装匹配版本的 Python 包，并配置 REAPER、Lua；音频示范需要 audio 扩展依赖。

它把 Rea-Cli 接入已有 agent harness，引导 agent 预检查、执行并验证工程，
必要时使用原生 Lua/ReaScript；不要求持久化 MCP 服务。完整开发背景仍可查阅本仓库的
[双语手册](reference/README.zh-CN.md)。

## 文档入口

- [环境配置与前置要求](docs/environment.md)
- [Python API 与 CLI 行为](docs/api.md)
- [验证记录](docs/validation.md)
- [共享 parser 与媒体 API](docs/ecosystem/api.md)
- [自动化开发规范](reference/README.zh-CN.md)：[调用](reference/workflow/README.zh-CN.md) · [RPP](reference/rpp/README.zh-CN.md) · [ReaScript](reference/reascript/README.zh-CN.md) · [Lua](reference/lua/README.zh-CN.md) · [JSFX](reference/jsfx/README.zh-CN.md)
- [Agent skill](integrations/agents/reaper-agent-cli/SKILL.md) · [中文使用说明](integrations/agents/reaper-agent-cli/GUIDE.zh-CN.md)
- [更新记录](CHANGELOG.md) · [发布流程](docs/releasing.md)

## 许可证

项目自有代码和原创文档采用 [MIT 许可证](LICENSE)。导入资料及其他上游内容继续遵循
自身许可证和条款，MIT 不会重新授权这些内容。`reference/` 与
`schema/rpp/evidence/` 虽不进入 wheel、sdist、文档站或 agent bundle，但由 Git 跟踪，
clone 本仓库时会一并取得；保留的上游内容继续带有署名和来源链接。

Cockos API 和 JSFX 参考资料按适用的上游条款使用，并保留来源链接。来自 ReaTeam 的
schema 内容保留 ReaTeam、IXix 和 Cockos Wiki 的适用署名与条款。Ultraschall 渲染笔记
保留 Meo-Ada Mespotine/Ultraschall 署名和来源链接，其中 `cc-by-nc` 条件（包括非商业
使用限制）继续适用。导入的 Lua 资源也保留原始来源署名和条款。详见
[第三方声明](THIRD_PARTY_NOTICES.md) 与[来源和再分发审计](docs/ecosystem/source-license-audit.md)。

已发布 wheel 的元数据仍记录 `License-Expression: MIT`，不可变构件无法回写；当前 checkout
将项目 MIT 范围与上游声明分开记录。REAPER 和第三方插件不包含在项目中，分别遵循自身许可证。
本项目独立维护，与 Cockos 无隶属关系。
