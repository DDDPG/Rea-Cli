# REAPER CLI: historical behavior notes

> 来源版本：REAPER 7.62 / macOS、7.77–7.78 / Linux。
> 以下是源项目报告的观察，未逐条为当前版本复验。当前启动方式、实例隔离、
> 配置和超时处理以[环境文档](../../../docs/environment.md)为准。
> 原始文件的 SHA-256 和编辑记录见[来源清单](../../source-manifest.json)。

## 调用形式

```text
reaper [options] [projectfile.rpp | mediafile.wav | scriptfile.lua [...]]
```

- 官方 help 说明位置参数按顺序处理。Linux 7.78 的观察中，工程文件需要放在
  Lua 脚本前，否则脚本执行时工程尚未加载。
- `reaper proj.rpp a.lua b.lua` 在该 Linux 版本按顺序执行两个脚本。
- 此调用方式把脚本作为位置参数，不使用 `-runscript` 或 `-script`。
- `-renderproject <rpp>` 在 Linux 7.77 的测试中渲染后退出。
- `-nonewinst` 的官方说明是转发给已运行实例。隔离运行应使用当前 runner，
  不从旧版本行为推断新版本的实例选择。

## macOS 7.62 的启动观察

- **实例转发：**源项目报告直接再次调用二进制时，请求被交给已经运行的
  实例，包括 help、version 和 Lua 脚本调用。因此脚本可能进入工作中的
  工程。当前 runner 使用的实例参数见环境文档。
- **复制应用：**该测试中的 `.app` 副本需要重新签名才能启动。复制应用
  不是当前推荐的隔离方法，也没有在该记录中证明所有并发情形均可隔离。
- **便携配置：**源测试发现 `.app` 同级的 `reaper.ini` 生效，而放在
  `Contents/MacOS/` 内没有切换资源目录。不要据此修改应用包内文件；
  当前配置路径由 runner 管理。
- **首次启动：**VST 扫描和音频设备设置对话框会阻塞脚本。运行前需完成
  主机初始化并准备适合该平台的配置。
- **窗口：**该 macOS 测试通过图形会话启动 REAPER，窗口会短暂出现。
  Linux 测试通过 Xvfb 提供显示服务；Xvfb 不代表 REAPER 不需要显示服务。

## 脚本执行、保存与输出

下列条目主要来自 macOS 7.62 的源测试。

- 顶层未捕获的 Lua 错误会弹出模态对话框，导致自动化挂起且没有 proof。
  entry 模板以 `pcall` 包裹 `body()`，但这不捕获脚本的语法错误；运行前
  仍需 `luac -p` 预检。模板自身的状态采集和 proof 写出也可能失败。
- `defer` 注册异步工作，不适合当前同步执行并退出的 entry 模板。
- 脚本需明确结束一次性进程。源测试使用 action 40004（退出 REAPER）；
  当前 entry 已包含退出逻辑。
- 部分已测 API 操作（插轨、设值、添加 marker）没有设置项目 dirty 标志。
  这不是所有 API 的保证。显式保存，检查 proof 和输出文件，不依赖退出
  时的隐式保存行为。
- 设置 dirty 后退出可能弹保存确认框。源测试中的
  `Main_SaveProjectEx(0, absolute_path, 4)` 保存副本而不改变 tab 身份；
  目标目录不存在时可能弹框且保存失败。当前 entry 使用临时目标和重命名
  以避免旧文件冒充成功的新输出。
- `print()` / `io.write()` 在 macOS 测试中进入进程 stdout。
  `ShowConsoleMsg` 写入 GUI 控制台，不能代替 proof 输出。
- 位置参数启动的脚本没有 Action List 注册 ID；源记录中的
  `get_action_context()` 返回 cmdID = -1。
- `-ignoreerrors` 在源测试中跳过缺失媒体提示；它不能使缺失媒体可用，
  也不能保证跳过所有类型的模态对话框。
- 已存在的渲染目标可能触发覆盖确认。自动化宜使用新的输出目录或文件名。
- 源测试的默认 WAV 渲染是 24-bit；默认值受配置影响，应用程序应显式
  配置格式并检查实际输出。
- 保存时可能依据项目设置复制媒体并改写 `FILE` 路径。比较媒体身份时
  需要结合内容和工程语义，不能只比较绝对路径或文件名。
- 保存极简工程会补入大量默认字段。源样本从 5 行变为 126 行，见
  [保存后样本](../../../tests/fixtures/minimal_after_reaper_save.rpp)；
  行数和字段默认值不是跨安装保证。
- 源测试中的 UTF-8 中文 marker 名可以直接读写。

## 失败诊断

使用 `rac.runner.run()` 或 `reacli run` 保存完整运行目录。旧版后台启动、
轮询 `/tmp` 和手动 kill 的示例已移除；当前 runner 提供唯一运行目录、
超时处理和结构化 proof，接口见[API 文档](../../../docs/api.md)。

常见现象与检查方向：

- **无 proof、立即退出：**检查 Lua 语法、二进制/脚本路径和进程 stderr。
- **无 proof、持续挂起：**检查首次启动、插件扫描或错误对话框，以及脚本
  是否注册了持续运行的工作。保留日志后使用 runner 的超时结果。
- **`reason_code=lua_error`：**检查 `error.message` 和 `error.lua_traceback`。
- **`reason_code=save_failed`：**检查目标目录、权限、磁盘空间和保存结果。
- **`reason_code=completed_noop`：**这是被采集状态的 hash 与预期值相同；
  不能据此证明整个工程或音频完全未变。

## Linux 7.77 的环境观察

源项目通过 Xvfb 执行过 `-renderproject`。该环境需要 GTK、Xvfb 和 xauth，
并使用 dummy audio 避免依赖声卡。可执行文件旁的 `reaper.ini` 用于便携
配置；JACK 警告在该 dummy 后端环境中没有阻止渲染。这些是特定安装的
记录，安装命令和当前配置模板见环境文档。

## 未由这些历史记录解决的问题

复制应用在已有主实例下的行为、可承受的并发实例数量、不同设备和插件
组合的启动行为，以及 Linux 中各输出通道的表现，均不能由这组有限探针
推导。新结论应记录 REAPER 版本、操作系统、配置和可复现步骤，并与
[当前验证记录](../../../docs/validation.md)区分。
