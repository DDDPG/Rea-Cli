# ReaCli

基于 reaper-parser 的 REAPER 执行、工程检查与结果验证工具。

正式版本可以直接从 PyPI 安装两个 Python 包：

```sh
python -m pip install "reacli==0.1.0" "reaper-parser==0.1.0a1"
```

音频接口可追加 `python -m pip install "reacli[audio]==0.1.0"`。
源码开发时，请在 monorepo 根目录安装 `./packages/reaper-parser` 和
`./packages/reacli`，不要把 checkout 与已经发布的包混用。
本次审查后的 checkout 增加了发布后运行时加固；这些改动不在不可变的
`0.1.0` 构件中，下次上传前需要提升版本。
CLI 的 `rac`、`reacli` 等价，Python 导入名为 `rac`。
`rac doctor --profile offline --json` 无需 REAPER；宿主操作需要另外配置 REAPER。

在完整 checkout 中，参见[生态指南](../../docs/ecosystem/README.md)、
[共享解析器与音频 API](../../docs/ecosystem/api.zh-CN.md)和[贡献指南](../../CONTRIBUTING.md)。
相对链接用于仓库浏览；独立源码包不包含完整仓库文档。

内置参考数据保留原来源条款；公开分发仍需遵循对应的来源与许可要求。
