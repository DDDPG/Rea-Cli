# REAPER CLI toolkit

本技能支持 Claude Code、Codex、Qwen Code。解压后运行：

```sh
python reaper-agent-cli/scripts/install.py --wheels /absolute/candidate --project ./new-work --harness all
```

源码方式将 --wheels 换为 --source /absolute/Rea-Cli；已有环境可用 --runtime-python。
Python 需要 3.10+。安装器不会覆盖已有技能，也不修改 harness 登录与权限。
进入项目启动 harness，输入“使用 reaper-agent-cli skill 检查环境并完成我的 REAPER 任务”。
REAPER、Lua 和模型登录需另外准备。

[技能入口](SKILL.md)会按需引导读取[环境](reference/setup.md)、[编码](reference/coding.md)、
[验证](reference/verification.md)与[音频](reference/media.md)。Lua 模板从已安装 rac 导出，
不在 bundle 维护另一份运行时。JSFX 示例是 EEL2，需要宿主音频验收。这里不包含 showcase 答案。
