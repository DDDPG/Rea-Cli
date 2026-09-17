# REAPER rendering: formats, settings and historical observations

> 来源：Meo-Ada Mespotine / Ultraschall 的 `misc_docs` 渲染文档。
> 原始来源标记为 **cc-by-nc**；完整许可证版本未记录，见
> [来源和许可说明](../../SOURCES.md)。这里保留该署名及限制，不适用项目 MIT 许可。
> 源项目的实机观察主要来自 REAPER 7.62 / macOS 与 7.77 / Linux，
> 未逐条为当前版本复验。当前运行方式见[环境文档](../../../docs/environment.md)。

## RENDER_CFG 是格式配置数据

RPP 的 `<RENDER_CFG` 块保存经过 base64 编码的二进制配置；源文档记录
`reaper.ini` 中使用 HEX 表达。前 4 字节用于识别格式，例如 `evaw` 表示
WAVE。后续字节含位深、BWF/marker/tempo 等选项，以及 WAV、Wave64、RF64
等大文件策略。AIFF、FLAC、WAVPACK 等格式具有各自的布局。

这些偏移是理解旧资料的线索，不是可以跨格式写入的通用 schema。格式
选项、codec 可用性和 REAPER 版本都可能影响数据。按
[opaque-block 规则](../rpp/blob_denylist.md)保留整个块；需要替换时，使用
目标安装中由宿主生成并验证过的配置。

API 属性名与 RPP 块名不是通用的一一映射。修改渲染格式时查询目标版本的
[ReaScript API](https://www.reaper.fm/sdk/reascript/reascripthelp.html)，
不要直接把 RPP 的 `RENDER_CFG` 当作 API 字符串属性名。2026-09-09 核对的
官方 API 文档使用 `GetSetProjectInfo_String` 的 `RENDER_FORMAT` 表示
base64 格式配置，`RENDER_FORMAT2` 表示第二输出格式；这是文档核对，
不是对所有格式的实机验证。

## RPP 明文字段与 API 属性

[保存后工程样本](../../../tests/fixtures/minimal_after_reaper_save.rpp)
展示了宿主写出的字段，例如：

```text
RENDER_FILE ""
RENDER_PATTERN ""
RENDER_FMT 0 2 0
RENDER_1X 0
RENDER_RANGE 1 0 0 0 1000
RENDER_RESAMPLE 3 0 1
RENDER_ADDTOPROJ 0
RENDER_STEMS 0
RENDER_DITHER 0
RENDER_TRIM 0.000001 0.000001 0 0
```

这里的具体值是样本数据，不是新工程默认值的承诺。明文层中可以看见输出
目录、文件名模式、范围等设置，但字段含义需要对应版本的文档和保存读回
验证。

- `GetSetProjectInfo_String` 的 `RENDER_FILE` 表示渲染目录；
  `RENDER_PATTERN` 表示文件名模式，可包含 `$project` 等变量。
- 采样率使用 `GetSetProjectInfo` 的 `RENDER_SRATE`；范围使用
  `RENDER_BOUNDSFLAG`、`RENDER_STARTPOS` 和 `RENDER_ENDPOS` 等 API 属性。
  这些 API 名称不能直接作为 RPP 行名使用。
- 旧记录中某些工作流会重置输出模式，因此渲染完成后应检查实际输出位置。
  修改设置成功和预期音频已经生成是两个不同的验证步骤。

[render.lua](../../../packages/reacli/src/rac/data/lua/stdlib/render.lua)展示了通过宿主 API
设置渲染参数的方式。所选格式的完整配置仍需由目标宿主确认。

## Render presets 与默认配置

源文档描述 REAPER 6+ 的 `reaper-render.ini` 使用下列记录：

- `<RENDERPRESET ...>`：采样率、声道等选项及格式配置数据。
- `<RENDERPRESET2 ...>`：第二格式的配置数据。
- `RENDERPRESET_EXT ...`：normalize、fade、silence-trim 和 pad 等参数。
- `RENDERPRESET_OUTPUT ...`：范围、时间、source、tail、目录与文件名模式。

这些记录适合理解和检查宿主生成的预设。不要假定预设文件的字段可以原样
写入 `.rpp`；它们是不同文件格式。自动化优先通过已支持的 API 设置工程，
保留已验证的预设或格式数据，并检查宿主保存后的结果。

`reaper.ini` 还保存新工程继承的渲染默认值。可为隔离资源目录准备配置，
但音频设备和平台设置应使用当前环境指南；不要把 Linux 配置直接用于 macOS。

## 触发渲染

源项目在 Linux 7.77 用 `-renderproject` 验证过整工程渲染。当前 CLI 和
runner 的使用方法以维护中的 API/环境文档为准。

脚本中的 action 41824 在旧索引中是使用最近渲染设置的命令。索引来自
REAPER 5.941 / SWS 2.9.7，不能代替当前宿主的 Action List。旧记录未能
确认 41829、42230 等编号；缺失编号不说明新版不存在对应 action，
`NamedCommandLookup` 也不能校验任意数字 action 的语义。执行前确认
目标版本、section 和命令含义，并使用新的渲染目标避免覆盖确认对话框。
