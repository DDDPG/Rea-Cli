# REAPER Agent CLI 中文使用说明

[English / Skill 入口](SKILL.md) · [开发规范](../../reference/README.zh-CN.md)

本 skill 通过安装好的 `rac` 操作 REAPER，并依赖同一仓库中的 `reference/`、`examples/` 和包内资源。它随 Git 项目交付，不是把目录单独复制走就能运行的零依赖工具。安装到其他位置时保留完整 checkout，并明确原仓库位置。无需 MCP 服务器。

## 环境与范围

分别明确仓库和任务输出目录，不把生成工程写进 skill。用目标 Python 环境检查 `python -m rac --version`，选择实际需要的 `rac doctor --profile offline`、`lua` 或 `full`，可加 `--json`。需要时从 checkout 安装 `python -m pip install -e /absolute/path/to/Rea-Cli`。宿主执行需要 REAPER，Lua 组合需要[兼容编译器](../../docs/environment.md)。

运行宿主前读[调用规范](../../reference/workflow/README.zh-CN.md)。一次性任务使用 `rac.runner.run` / `rac exec`；仅对独立且可安全重试的任务使用 `Pool`。扫描与 reopen 缺省处理已在 runner 中，不复制临时版本的裸 CLI/kill 循环、不要求关闭用户所有 REAPER，也不带入旧 `rac_lib`。

## 按任务读取

| 任务 | 规范及处理方式 |
|---|---|
| 已知静态字段或只读检查 | [RPP](../../reference/rpp/README.zh-CN.md)：`parse(Path(...))`、定点 patch、保留字节、重新解析并断言 |
| 注册的 intent 操作 | [Lua](../../reference/lua/README.zh-CN.md)：使用 `generate`，不确定时查实际 `OP_REGISTRY` |
| Folder、多 take、master FX、任意宿主操作 | [ReaScript](../../reference/reascript/README.zh-CN.md)：组合 entry 和必要片段，保留保存/proof/退出 |
| 音频/MIDI 处理器 | [JSFX](../../reference/jsfx/README.zh-CN.md)：区分 EEL2 源码与实例状态 |
| 未知 API 或字段 | `rac knowledge api FunctionName` / `rac knowledge rpp section:KEY`；不足时查宿主文档，按需读[资料目录](../../reference/knowledge/README.zh-CN.md) |

## 实现与验证

先定位对象。索引会变化、名称可重复、marker ID 不等于遍历位置，master 有独立 API。检查指针和返回值。创建、切分、插入不自动幂等；重试前检查状态或使用全新输入。

明确单位：RPP 增益是线性值，生成器 `track.set_volume_db` 使用 dB，归一化 FX 参数不等于物理单位。探测插件和参数名，采用有依据的转换并读回格式化值；EQ 检查 band 类型与启用状态。MIDI 使用 tempo map，包络使用实际 scaling mode。不猜测插件 blob 或 region 序列化。

提交前生成或语法检查 Lua，`run` 不会代做。自定义 body 把可序列化结果写入 `RUN.result`，必要操作失败时抛错，保留 entry 协议。同步 entry 不等待 defer，异步 UI 需要另一套生命周期设计。

持久化编辑要传 `save_as` 并创建父目录。归档输入不是文件沙箱，实际打开原工程以保留相对媒体。渲染使用独立新路径与合适尾音，不删除无关输出，不把弹窗被跳过当作媒体/插件加载成功。

检查 `proof.ok`、`proof_check`、操作级错误和保存后的目标属性；涉及声音时检查实际音频及支持格式。摘要哈希、解析通过、截图或退出成功均不能单独证明完成。失败后检查证据、处理原因并限制重试次数，不原样无限重复。

## 示例和交付

[create_project.py](../../examples/create_project.py)提供最小生成操作；[inspector 构建器](../../reference/lua/examples/build_inspector.py)提供自定义只读 body；[show_session.py](../../examples/show_session.py)及其 [Lua](../../examples/show_session.lua)展示现场合成、轨道/folder/item/take/envelope/FX。先读参数，使用任务专属输出。Showcase 插件设置只是示例，不是其他音乐任务的默认值。

交付用户要求的工程/脚本、媒体或合成说明，以及简洁的验证结果和相关宿主/插件版本。明确尚未测试的行为，使用用户语言；任务未涉及的 README 图床链接与远程仓库状态保持原样。
