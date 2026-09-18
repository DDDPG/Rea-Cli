> **历史知识快照 / Source snapshot**（整理于 2026-09-09）。下文保留原作者的版本、日期和验证标记，
> 不代表本次已在当前 macOS 或 Linux 上复验。运行环境与启动方法请以
> [当前环境文档](../../../../docs/environment.md) 为准；来源和证据边界见[知识库索引](../../../README.md)。

# JSFX 速查手册

> 来源: reaper.fm 官方 JSFX Programming Reference(2026-07-31 抓取, 对应 REAPER 7.78)
> 范围: **编写与修改 JSFX 效果器**(EEL2 源码层); RPP 内 `<JS>` chunk 的编辑边界见第 6 节
> 未覆盖: gfx_* / 用户自定义函数 / 预处理器(官方 gfx.html / userfunc.html / preproc.html 不在抓取范围)

## 1. JSFX 是什么

- REAPER 内嵌的音频/MIDI 插件格式, 用 **EEL2** 编写 —— 官方: "a scripting language that is compiled on the fly", 可修改/生成音频与 MIDI, 也可绘制自定义矢量 UI。
- 本体是纯文本文件(.jsfx), 载入 REAPER 即成完整插件。源码分发可直接编辑(官方建议另存新名, 防升级覆盖)。
- 存放于 JS effect directory(REAPER 资源目录/Effects); 仅供 import 的库命名 `xyz.jsfx-inc`, 不进 FX 列表。JSFX 实例在 RPP 中以 `<JS>` chunk 存于 `<FXCHAIN>` 内(见 §6)。

## 2. 文件结构与 lifecycle

文件 = 描述行 + 若干代码段。每个代码段只能定义一次, 全部可选。

### 2.1 描述行

| 行 | 语义 |
|---|---|
| `desc:名称` | 插件显示名。只出现一次, 建议首行 |
| `tags:...` | 空格分隔标签; 含 `instrument` 进 Instruments 列表(6.74+) |
| `sliderN:默认<最小,最大,步进>描述` | 第 N 个参数, **最多 256 个**; 用户可调、可自动化 |
| `in_pin:名` / `out_pin:名` | pin 命名; 唯一命名为 `none` 表示无音频 I/O(host 可优化)。**MIDI-only FX 应写 `in_pin:none` + `out_pin:none`** |
| `filename:idx,文件` | 数据文件(REAPER\Data, `file_open(idx)` 读)或 .png(gfx_blit); 索引从 0 连续 |
| `options:...` | `gmem=命名空间` / `maxmem=` / `prealloc=` / `no_meter` / `want_all_kb` / `gfx_idle` / `gfx_idle_only` / `gfx_hz=` |
| `import 文件` | 导入库(4.25+); 其 @init 函数可用; 本效果未实现的段用被导入版本 |

slider 扩展写法: `varname=` 前缀命名访问(5.0+); `{a,b,c}` 枚举(须 0 起步、步进 1); `/path:def.wav:` 文件选择器(配 `file_open(slider1)`); 描述名前加 `-` 隐藏(仍生效可自动化); 步进后接 `:log` / `:sqr` shaping(6.74+, `:log=X` 定中点, `:sqr=X` 定指数, 加 `!` 不影响已有自动化)。

### 2.2 代码段 lifecycle

| 段 | 何时执行 | 要点 |
|---|---|---|
| `@init` | 加载、采样率变化、播放开始 | 调用前变量/内存**重新清零**; 定义非空 `@serialize` 可阻止清零; `ext_noinit=1` 禁止播放开始时重跑 |
| `@slider` | `@init` 之后、slider 变化时 | 在此做参数换算; 官方: "adapt to the new parameters (ideally avoiding clicks or glitches)" |
| `@block` | 每个采样块之前 | `samplesblock` 在此有效; 典型块长 128–2048。**MIDI 处理推荐在这里** |
| `@sample` | 每个 PCM 采样一次 | 读写 `spl0..spl63`; 不修改的 splX 原样直通 |
| `@serialize` | 加载/保存扩展状态时 | slider 值宿主自动存; 内部状态用 `file_var(0,x)` / `file_mem(0,offs,len)`; `file_avail(0)<0` 表示写模式 |
| `@gfx [w] [h]` | GUI 打开时约 30 次/秒 | **独立线程**, 与音频并发; 实际尺寸用 `gfx_w/gfx_h`; 不绘制则不刷新 |

## 3. 关键变量表

| 变量 | 上下文 | 读写 | 语义 |
|---|---|---|---|
| `spl0..spl63` | @sample | RW | 各声道当前采样; +0dB = ±1.0, 允许 overs; 不改即直通 |
| `spl(i)` | @sample | RW | 可编程下标版(略慢) |
| `slider1..N` | 所有段 | RW | 用户参数; @slider 之外改写须 `sliderchange()` |
| `slider(i)` | 所有段 | RW | 可编程下标版(3.11+) |
| `slider_next_chg(i,nextval)` | @block/@sample | — | 采样级自动化: 返回变化点块内偏移, 无变化返回非正值 |
| `trigger` | @block/@sample | RW | 位掩码触发器(UI 出 10 按钮); 建议只在 @block 用 |
| `srate` | 所有段 | RO | 采样率(通常 44100–192000) |
| `num_ch` | 多数段 | RO | 声道数(通常 2); splXX 始终可写, 超出的被忽略 |
| `samplesblock` | @block 有效 | RO | 即将处理的块长(他段需容错) |
| `tempo` | @block/@sample | RO | 工程 BPM |
| `play_state` | @block/@sample | RO | 0=stopped 1=playing 2=paused 5=recording 6=rec paused <0=error |
| `play_position` / `beat_position` | @block/@sample | RO | 播放位置(秒/拍, 以上次 @block 计) |
| `ts_num` / `ts_denom` | @block/@sample | RO | 拍号分子/分母 |
| `ext_noinit` | @init only | W | 置 1 禁止播放开始时重跑 @init; 代价: srate 在 @init 可能不准 |
| `ext_nodenorm` | @init only | W | 置 1 不加抗 denormal 噪声 |
| `ext_tail_size` | @init/@slider | W | 尾音采样数; -1=自动检测, -2=无尾音无状态(6.71+) |
| `ext_gr_meter` | @init/@block | W | @init 置 0, @block 写负值上报增益衰减(7.0+) |
| `reg00..reg99` | 所有段 | RW | 跨效果共享(`_global.regXX` 别名); 用法须在 desc 文档化 |
| `_global.*` | 所有段 | RW | 跨全部实例共享命名变量(4.5+) |
| `pdc_delay` | @block/@slider | RW | 插件延迟采样数; 不宜频繁改 |
| `pdc_bot_ch` / `pdc_top_ch` | @block/@slider | RW | 被补偿声道区间(如 0..2 补偿 spl0/spl1) |
| `pdc_midi` | @block/@slider | RW | 置 1 则 MIDI 也做延迟补偿 |
| `ext_midi_bus` | @init | W | 置 1 启用 16 条 MIDI bus(4.16+, 默认非 0 bus 直通) |
| `midi_bus` | — | RW | 事件所属 bus 0..15(启用后 midirecv 写 / midisend 读) |

## 4. 语言与内置函数要点

EEL2 与 C 相似但有关键差异:
- 变量无需声明、默认全局于本效果、**全是 double**; 名字**不区分大小写**; 最长 127 字符
- 常量 `$pi $phi $e`; hex `$x90`(4.25+ 也可 `0x90`); 字符 `$'c'`; 位掩码 `$~7`=127
- 注释 `//` 与 `/* */`; **块用圆括号不用花括号**: `z = ( a=5; b=3; a+b; )` → z=8(取末语句值)
- 分支用 `cond ? a : b`, 无 if/else; `?:` 可作 lvalue: `(a<5 ? b : c) = 8;`
- 位运算 `| & ~`(**异或是 `~`**); `| & ~` 及 `|| &&` 各同优先级左结合 —— 混用**必须加括号**
- `==` 带 epsilon(|差| < 0.00001); 精确比较用 `===`(4.53+)
- 本地内存约 8M slots, `buf[i]` 寻址(左值+括号值); 下标按 value+0.00001 截断 → 小数下标写 `x[y|0]`
- `gmem[]` 默认约 1M slots 全实例共享; `options:gmem=name` 换私有 8M 命名空间
- `loop(n,code)` / `while(code)` / `while(cond)(code)`(4.59+); 上限约 100 万次防挂死
- 字符串(4.59+): 字面量不可变; 可变串用命名串 `#name`(支持 `#name = / +=`)或槽位 0–1023; 软上限约 16KB

函数速查（签名与语义见 [jsfx_reference.json](jsfx_reference.json)）：
- 数学: `sin cos tan asin acos atan atan2 sqr sqrt pow exp log log10 abs min max sign rand floor ceil invsqrt`; 时间: `time() time_precise()`
- 内存: `memcpy memset mem_set_values mem_get_values mem_multiply_sum mem_insert_shuffle freembuf __memtop()`
- FFT/MDCT: `fft ifft fft_real ifft_real fft_permute fft_ipermute mdct imdct convolve_c`(尺寸须 2 的幂, **不得跨 65536 边界**)
- 宿主: `sliderchange slider_automate slider_show export_buffer_to_project get_host_placement` 及 pin mapper 族
- 栈/原子: `stack_push/pop/peek/exch`; `atomic_set/get/add/exch/setifequal`

## 5. 教学示例

这些示例保留源项目的逻辑，没有在本次整理中进行实机 DSP 验证。
三个独立文件可放入测试用 REAPER 资源目录的 `Effects` 子目录，再通过
FX 浏览器加载；资源目录可在 REAPER 的“Show REAPER resource path”菜单项
查看。使用独立文件名，以免与已安装的效果器冲突。它们不随 pip 安装。

使用时注意源示例的边界：

- Gain 只修改 `spl0` 和 `spl1`，其他声道原样输出；突然调整增益没有平滑。
- Delay 的 0 ms 设置会在写入前读取当前缓冲槽，实际不等于零延迟。
  `ext_tail_size=bufsize` 也没有按反馈量计算完整衰减尾音，反馈较高时
  可能提前截断。用于正式处理前应修正这些边界并测试不同采样率。
- 下方 Chamberlin SVF 是算法片段。较高频率和部分 Q 值可能导致不稳定，
  当前 slider 范围没有保证数值稳定性，不应作为生产滤波器直接使用。

### 5.1 Gain（[完整注释版](examples/gain_simple.jsfx)）

```jsfx
desc:Simple Gain (dB)
slider1:0<-60,12,0.1>Gain (dB)

@slider
gain = 10 ^ (slider1 / 20);   // dB→线性只在参数变化时换算

@sample
spl0 *= gain;
spl1 *= gain;
```

### 5.2 立体声 Delay（[完整注释版](examples/delay_basic.jsfx)）

```jsfx
desc:Basic Stereo Delay
slider1:250<0,2000,1>Delay (ms)
slider2:0.35<0,0.95,0.01>Feedback
slider3:0.5<0,1,0.01>Wet

@init
bufsize = 400000; bufL = 0; bufR = bufsize; pos = 0;
ext_tail_size = bufsize;   // 告诉宿主有尾音

@slider
delay_spl = min(slider1 * 0.001 * srate, bufsize - 1) | 0;

@sample
rpos = pos - delay_spl; rpos < 0 ? rpos += bufsize;
dl = bufL[rpos]; dr = bufR[rpos];
bufL[pos] = spl0 + dl * slider2;
bufR[pos] = spl1 + dr * slider2;
spl0 = spl0 * (1-slider3) + dl * slider3;
spl1 = spl1 * (1-slider3) + dr * slider3;
pos += 1; pos >= bufsize ? pos = 0;
```

### 5.3 立体声 Band-pass(Chamberlin SVF)

```jsfx
desc:Minimal Stereo Bandpass (SVF)
slider1:1000<20,20000,1:log>Center (Hz)
slider2:1<0.1,10,0.1>Q

@slider
f = 2 * sin($pi * slider1 / srate);  // SVF 系数; 中心频率不宜超 srate/6
d = 1 / slider2;                     // 阻尼 = 1/Q

@sample
// 每声道独立状态 —— 共享状态会让 L/R 串扰
low0 += f * band0; high0 = spl0 - low0 - d*band0; band0 += f * high0; spl0 = band0;
low1 += f * band1; high1 = spl1 - low1 - d*band1; band1 += f * high1; spl1 = band1;
```

## 6. RPP 中的 `<JS>` chunk 与禁区规则

实例形态(实机 RPP 取证, `synthesis/tonegenerator`):

```
<JS synthesis/tonegenerator ""
  6 -120 1000 0 0 0 0 - - - - ...(共 64 个槽位)
>
```

- 首行: `<JS <相对 Effects 目录的路径> "<预设名, 可空>"`
- 该样本次行有 64 个滑参槽位，数字为 slider 值，`-` 为未用槽。样本行宽不能推广为所有版本和效果器的保证。slider 参数由宿主自动保存。
- 若效果定义了 `@serialize`, 滑参行后可能有扩展状态行 —— **该行族语义未验证**(ReaperDoc 未覆盖, blob_denylist 明列)

**编辑边界见 [不透明块规则](../../rpp/blob_denylist.md)：**
- `<JS>` 内部整体属禁区: 只可**整块保留 / 整块删除 / 整块替换**, 绝不编辑内部字节 —— 即使滑参行是明文数字也不手改
- 合法替换来源: 同机同版本宿主(GUI/ReaScript)配好后导出的整块; 或同工程已有块(FXID 需重新生成)
- 本知识包覆盖 **JSFX 源码层**(.jsfx 编写); 改已挂载实例的参数走宿主路径, 而非改 RPP 文本
- 验证: `reacli rpp validate` 检查结构；`reacli rpp diff` 辅助审阅预期块变化。严格保留要求还需比较原始字节或哈希，并在宿主中验证加载行为。

## 7. 常见坑

1. **slider 换算放 @slider**: @sample 每采样跑一遍, 系数换算(exp/sin 等)放 @slider; 采样级自动化用 `slider_next_chg()`
2. **@slider 之外改 sliderX 必须 sliderchange()**, 否则 UI 不刷新; 录自动化用 `slider_automate()`
3. **ext_noinit 的代价**: srate 在 @init 可能不准 —— 在 @block/@slider 监测 srate 变化
4. **buffer 下标**: 小数下标写 `x[y|0]`; FFT/MDCT/convolve 不得跨 65536 边界
5. **双声道状态独立**: 滤波器/delay 状态变量必须 L/R 各一套, 共享状态会串声道
6. **MIDI 必须 drain**: 调了 midirecv* 就必须收完所有事件并把不消费的原样 midisend 透传; SysEx 被 midirecv 自动透传, 要处理用 midirecv_buf
7. **@serialize 精度**: 32-bit 紧凑格式有精度损失; @init 可能在 @serialize 之后被调用 —— 别在 @init 里清 @serialize 恢复的变量
8. **运算符陷阱**: 异或是 `~` 不是 `^`; `==` 带 epsilon —— 位运算混用加括号, 精确比较用 `===`
9. **不修改即直通**: 不写的 splX 原样输出; 想静音必须显式写 0

## 8. MIDI 处理要点

- 官方强烈推荐 @block 做 MIDI 处理; 发送也可在 @sample; offset 参数是块内采样偏移
- `midisend/midirecv` 四参形式为 4.60+; 三参形式第三参打包 `msg2 + msg3*256`
- 变长消息/SysEx 用 `midirecv_buf` / `midisend_buf`(自动补 F0/F7); `midisyx` 已废弃; drain+透传范式见 [MIDI monitor 示例](examples/midi_monitor.jsfx)
