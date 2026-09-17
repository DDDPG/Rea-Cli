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

在完整 checkout 中，参见[生态指南](https://github.com/DDDPG/Rea-Cli/blob/main/docs/ecosystem/README.md)、
[共享解析器与音频 API](https://github.com/DDDPG/Rea-Cli/blob/main/docs/ecosystem/api.zh-CN.md)和[贡献指南](https://github.com/DDDPG/Rea-Cli/blob/main/CONTRIBUTING.md)。
相对链接用于仓库浏览；独立源码包不包含完整仓库文档。

项目自有代码和原创文档采用 MIT。发行包没有把内置参考数据声明为某一个统一许可证；
这些内容继续遵循自身来源条款并保留署名。公开分发 wheel 或源码包前，请先阅读包内声明
并确认对应许可条件。
