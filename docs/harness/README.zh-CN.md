# 在 Claude Code、Codex、Qwen Code 中使用 ReaCli

[English](README.md) · [接口说明](../ecosystem/api.zh-CN.md)

这是一套 CLI toolkit：harness 中的 agent 编写代码，通过本地 shell 调用 ReaCli，
再验证 REAPER 保存工程和音频。不安装 MCP 服务、常驻 daemon 或新的模型账户。

## 一条命令安装到项目

需要 Python 3.10+（包含 venv/pip）及已安装、已登录的 harness。
宿主执行还需 REAPER 7.x、Lua 5.3/5.4；macOS 需要桌面会话及已配置的 CoreAudio。
Linux 依赖见[环境指南](../environment.md)。Windows 当前只支持离线解析，不支持 rac 宿主执行。

从本地 checkout 安装：

```sh
# 将 --source 指向你的 checkout，源码获取不会向 GitHub 发起请求。
REACLI_SOURCE=/absolute/path/to/Rea-Cli
python "$REACLI_SOURCE/integrations/agents/reaper-agent-cli/scripts/install.py" \
  --source "$REACLI_SOURCE" --project ./my-reaper-work --harness all
```

安装器建立项目内 venv，安装两个包及音频依赖，检查 CLI，并注册三个项目级技能。
只装一个可选 `--harness claude`、`codex` 或 `qwen`。Python 依赖仍可能联网下载。
安装结果不依赖原 checkout 的 editable 路径，也不会修改全局 harness 权限、登录信息或 MCP 配置。

候选包解压后也可使用：

```sh
python reaper-agent-cli/scripts/install.py --wheels /absolute/candidate \
  --project ./my-reaper-work --harness all
```

每个 Python 包只允许一个 wheel。已有运行环境可用
`--runtime-python /absolute/venv/bin/python` 替代 `--source`/`--wheels`，会检查 rac、parser
及音频依赖。重复安装不会覆盖已有 toolkit 或同名技能；升级请使用新目录。
迁移目录后重新安装，不要搬动 venv。移除旧安装前先保留工作产物。

安装报告在 `.reacli-toolkit/installation.json`；harness 是否在 PATH 单独报告。
安装通过不等于模型登录、REAPER 启动或音频输出验证通过。失败时查看 install.log 和 FAILED。
安装报告可能含本机路径，不应直接作为公开证据上传。

## 打开 harness，说一句指令

```sh
cd my-reaper-work
claude  # 或 codex、qwen
```

| Harness | 技能位置 | 输入示例 |
| --- | --- | --- |
| Claude Code | `.claude/skills/reaper-agent-cli` | `/reaper-agent-cli 检查环境，在 REAPER 中生成八小节 MIDI 工程，另存并验证渲染音频。` |
| Codex | `.agents/skills/reaper-agent-cli` | `$reaper-agent-cli 检查环境，在 REAPER 中生成八小节 MIDI 工程，另存并验证渲染音频。` |
| Qwen Code | `.qwen/skills/reaper-agent-cli` | `使用 reaper-agent-cli skill 检查环境，在 REAPER 中生成八小节 MIDI 工程，另存并验证渲染音频。` |

授权 harness 执行当前任务需要的本地 shell/宿主操作；受限容器或沙箱可能无法启动桌面
REAPER。安装器不会自动关闭沙箱或改写审批策略；技能也不是操作系统级沙箱。
执行使用隔离 REAPER 实例和工程副本，不会接管正在编辑的桌面工程。

无交互入口分别为 `claude -p '使用 reaper-agent-cli skill …'`、
`codex exec '使用 reaper-agent-cli skill …'`、`qwen '使用 reaper-agent-cli skill …'`。
先完成登录，并为该次运行配置必要工具权限；headless 无法回答交互审批。
无交互模式优先直接写技能名，不依赖斜杠命令展开。

## 环境、执行和 coding

以 Codex 技能路径为例；另两个 harness 将 `.agents` 换成 `.claude` 或 `.qwen`：

```sh
python .agents/skills/reaper-agent-cli/scripts/toolkit.py doctor --profile offline --json
python .agents/skills/reaper-agent-cli/scripts/toolkit.py doctor --profile full --json
python .agents/skills/reaper-agent-cli/scripts/toolkit.py rac init
python .agents/skills/reaper-agent-cli/scripts/toolkit.py templates ./new-starters
python .agents/skills/reaper-agent-cli/scripts/toolkit.py compose authored.body.lua authored.lua
python .agents/skills/reaper-agent-cli/scripts/toolkit.py python authored.py
```

helper 根据 runtime.json 使用绑定的 Python，避免系统中多个 CLI/Python 相互覆盖。
默认使用项目专属 REAPER resource；显式设置 RAC_REAPER_RESOURCE 时尊重该配置。
doctor 只检查，init 才初始化资源。

支持 RPP 解析/patch/diff、API 查询、Lua 生成/原生脚本组合、run/Pool/proof、工程断言、
NumPy 原始读取/宿主渲染/处理回写。模板包含通用 Lua inspector 和 JSFX 增益示例，
文档说明 MIDI、插件参数单位、包络及 DSP 验证。JSFX 是 EEL2，不能用 luac 验证，
必须通过宿主及实际音频检查。

## 一句指令重新构造 showcase

将[纯需求描述](../../integrations/agents/acceptance/showcase-brief.md)复制到新工作区的
`requirements.md`，然后输入：

> 使用 reaper-agent-cli skill 独立实现 requirements.md，通过本机 CLI toolkit 操作 REAPER，交付保存工程、实际音频预览和保存后重读验证证据。

只提供编曲结构和效果目标，不提供原 showcase 的代码、完成工程或其他 harness 的答案。
音符由 agent 自主创作；验收功能等价，不要求与原音乐逐样本一致，也不包含 52 帧 GIF 截图。
不能把 CLI 已安装当成端到端通过。覆盖范围见[验证记录](../validation.md)。

适配依据见[英文页的官方资料链接](README.md#adapter-references)。
