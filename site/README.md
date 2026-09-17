# Rea-Cli 落地页（GitHub Pages 原型）

纯静态 HTML/CSS/JS，无构建步骤、无运行时依赖。直接以静态站点方式部署即可。
它是仓库内的落地页原型，不属于 `tools/build_release.py` 生成的
`reaperdoc-site.zip`；在配置独立 Pages workflow 前，不应把它描述为已发布站点。

## 结构

- `index.html` — 简体中文（默认）
- `en/index.html` — English（导航栏 `EN` / `中文` 互切）
- `styles.css` / `main.js` — 两版共用；英文版通过 `window.SITE_I18N` 注入英文交互文案（复制提示、菜单标签、工作流状态文本）
- `assets/reacli-icon.png` — 仓库 README 图标的本地拷贝

## 本地预览

```bash
python3 -m http.server 8080 --directory site
# 打开 http://localhost:8080 （中文）或 http://localhost:8080/en/ （English）
```

## 部署到 GitHub Pages

任选其一（本轮不执行发布）：

1. **GitHub Actions（推荐）**：用 `actions/upload-pages-artifact` + `actions/deploy-pages`，将 `site/` 作为 artifact 发布。
2. **分支目录**：把 `site/` 内容放到 `gh-pages` 分支根目录，或重命名为 `docs/` 后在仓库设置中选择该目录（注意与现有文档目录冲突，需先迁移现有 `docs/`）。

## 设计参考与取舍

- **Raycast（DESIGN.md 样例）**：借鉴其精密工具感——面板顶缘 1px inset 高光、细发丝边框、多层柔和黑阴影、克制的状态语义色。未照搬其品牌色与排版。
- **Resend（DESIGN.md 样例）**：借鉴其代码展示的组织方式（窗口头 + 文件名 + 复制按钮）与内容节奏（短句标题 + 代码主体）。未照搬其配色与字体。
- **按需求重新配色**：背景纯色石墨灰 `#181a1c`，面板 `#202326` / `#272a2e`，文字 `#f3f4f5` / `#aeb3b8`，1px 白色低透明高光，柔和黑阴影。全站仅一个青绿语义色（`#55b7a1`），用于流程激活与验证通过状态。无渐变、无彩色光团、无霓虹、无玻璃模糊、无粒子。
- **字体**：系统中文字体栈（PingFang SC / 微软雅黑 / Noto Sans CJK）+ 系统等宽字体（SF Mono / Menlo / Consolas），零网络字体请求。
- **性能与动效**：无框架、无 WebGL；动画仅使用 `transform` / `opacity`，微交互 160–220ms；`prefers-reduced-motion` 下全部禁用；无持续装饰运动、无滚动劫持。

## 事实边界（写作依据）

所有产品描述均取自仓库 `README.md`、`docs/api.md`、`docs/environment.md`，未虚构用户数、性能指标、评价或实测结果：

- 定位：Python 库、CLI 与参考环境，接入 Claude Code / Codex / Qwen Code 等现有 harness；**不是**完整 harness，**不是**常驻 REAPER 控制服务。
- 安装命令 `python -m pip install "reacli==0.1.0" "reaper-parser==0.1.0a1"`、离线三命令（`doctor --profile offline --json` / `resources --output` / `rpp validate`）、`reacli exec` 参数形式、`expect` / `expect_audio` API 均与文档一致。
- 环境要求：Python 3.10+；离线检查仅需 Python；Lua 5.3/5.4 `luac`；实时执行需 REAPER 7.x（macOS / Linux）；Windows 执行尚未实现；0.1.0 alpha。
- 首屏工作台与三步流程中的面板内容均为**流程示意**（演示数据），页面上已明确标注；未伪装成真实启动 REAPER 或真实验证结果。
- 页面不包含外部图片资源；图标为仓库自有 `docs/assets/reacli-icon.png` 的本地拷贝。
- 文档链接使用 `https://github.com/DDDPG/Rea-Cli/blob/HEAD/...` 指向真实路径：`docs/environment.md`、`docs/api.md`、`docs/validation.md`、`docs/harness/README.zh-CN.md`。
## 无障碍与交互自查清单

- 选项卡遵循 `tablist` 模式（方向键 / Home / End 可切换）；复制结果经 `aria-live` 区域播报。
- 全部可交互元素触控区 ≥ 44px；代码块局部横向滚动；360 / 390 / 768 / 1440 宽度无页面级横向溢出。
- 移动端为纵向流程标签与抽屉菜单（Esc 可关闭）；提供跳转主内容的 skip link。

## 许可证

页面中的项目自有内容采用 [MIT 许可证](../LICENSE)。上游内容继续遵循各自许可证和条款；
Cockos API 和 JSFX 参考资料保留来源链接并按适用的上游条款使用。Ultraschall 渲染笔记
保留 Meo-Ada Mespotine/Ultraschall 署名、来源链接和 `cc-by-nc` 非商业条件。详见
[第三方声明](../THIRD_PARTY_NOTICES.md) 与[来源和再分发审计](../docs/ecosystem/source-license-audit.md)。
