# 已应用的字段修正

用户已授权修复并发布。此轮修改16条现有定义；34条增补继续独立展示。原始基准快照不变，审阅文档中的“保留/待决定”属于初次审阅历史，下面的应用记录优先。

完整前后值：[applied-corrections.json](applied-corrections.json)。实验证据：[behavior-review/RESULTS.md](behavior-review/RESULTS.md)。验证主机7.48/macOS；状态读回和保存实验不等同于音频效果或所有版本兼容性测试。

- **project/CURSOR** — D026；已应用经审阅的字段修正，详情见前后值记录。
- **project/MASTERPEAKCOL** — D026；已应用经审阅的字段修正，详情见前后值记录。
- **project/MASTERTRACKVIEW** — D028；已应用经审阅的字段修正，详情见前后值记录。
- **project/MASTERHWOUT** — D013；已应用经审阅的字段修正，详情见前后值记录。
- **project/MASTER_NCH** — D016；已应用经审阅的字段修正，详情见前后值记录。
- **track/NCHAN** — D016；已应用经审阅的字段修正，详情见前后值记录。
- **project/MASTER_PANMODE** — D001；已应用经审阅的字段修正，详情见前后值记录。
- **track/PANMODE** — D001；已应用经审阅的字段修正，详情见前后值记录。
- **track/PLAYOFFS** — D015；已应用经审阅的字段修正，详情见前后值记录。
- **track/REC** — D011；已应用经审阅的字段修正，详情见前后值记录。
- **track/AUXRECV** — D014；已应用经审阅的字段修正，详情见前后值记录。
- **track/HWOUT** — D013；已应用经审阅的字段修正，详情见前后值记录。
- **item/FADEIN** — D018；已应用经审阅的字段修正，详情见前后值记录。
- **item/FADEOUT** — D018；已应用经审阅的字段修正，详情见前后值记录。
- **item/PLAYRATE** — D019；已应用经审阅的字段修正，详情见前后值记录。
- **envelope/PT** — D004；已应用经审阅的字段修正，详情见前后值记录。

保留正确的原定义：E/e、SELECTION2、AUTOXFADE低两位、TKM颜色、WET delta solo、MUTE两字段，以及普通HWOUT/AUXRECV自动化位置等。

未应用的争议：root PANMODE及-1回退、DEFSHAPE、FX窗口坐标、未验证尾参/默认值、7.61专属布局、未知token无损保证。原始RPP树是保存样例，不为凑齐参数而补写未出现的可选值。

复现：`npm ci && npm run check && npm run build`。`node supplements/reaper-7z/behavior-review/scripts/report.mjs` 可重新核验保存行及生成行为报告；完整原始语料审计需本地归档和原语料。
