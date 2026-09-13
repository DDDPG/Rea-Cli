# Repository skills / 仓库 Skills

- [reaper-agent-cli](reaper-agent-cli/SKILL.md) — create, inspect, edit and verify REAPER sessions with the installed rac package. [中文说明](reaper-agent-cli/GUIDE.zh-CN.md).
- [Developer handbook / 双语开发规范](../reference/README.md).

Use this skill with a full Rea-Cli checkout and reacli installed from that checkout. Supply the SKILL.md path to your agent, or use your agent's skill-loading mechanism while keeping the checkout references resolvable. The folder is a repository integration, not a standalone vendored CLI. It does not install REAPER or enable embedded Python.

本 skill 依赖完整 Rea-Cli 仓库及从该仓库安装的 reacli。把 SKILL.md 路径提供给 agent，或按 agent 的加载机制使用，同时保留可访问的仓库引用。它不会安装 REAPER，也不要求开启 REAPER 内嵌 Python。

Example / 示例：

> Use the skill at `skills/reaper-agent-cli/SKILL.md` to create a REAPER session with a folder, MIDI items and track FX, then verify the saved project.
>
> 使用 `skills/reaper-agent-cli/SKILL.md`，创建包含 folder、MIDI item 和轨道 FX 的 REAPER 工程，并验证保存结果。

The development prototype supplied for this cleanup was reviewed as source material. Its two-path routing is retained; duplicated `rac_lib`, data indexes and Lua assets are replaced by current package resources. Obsolete direct-process recipes, broad idempotence claims and zero-dependency promises are removed. Both language guides reference the same maintained contracts. `reference/` and `skills/` are Git-only deliverables, excluded from wheel and sdist.

此次整理参考了用户提供的临时版本，保留离线 RPP / 宿主 Lua 两条路径；旧 `rac_lib`、索引和 Lua 副本改用当前包资源，移除过时进程控制、全局幂等及零依赖承诺。两种语言共用当前规范。`reference/` 与 `skills/` 只随 Git 交付，不进入 wheel 或 sdist。
