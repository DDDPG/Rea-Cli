# 本地差异行为验证

> 发布更新：用户已授权应用已验证字段，见 [应用记录](../APPLIED.md)。本文保留实验时的判断与边界。

环境：REAPER 7.48/macOS-arm64。隔离工程、独立 resource；没有覆盖原始字段定义。原始差异编号沿用 REVIEW.md。

方法：通过原生 API 或明确动作改参数、立即读回、保存 RPP 并比较 token。这里验证的是状态到序列化字段的对应，不等同于重载持久性、声音效果或 7.61 Windows 的验证。API 枚举名称参照[官方 ReaScript 文档](https://www.reaper.fm/sdk/reascript/reascripthelp.html)。

实验排除项：run1 的 PT 实验误操作初始 shape=0 点，虽 API tension 读回成功但文件未变化，已排除；run2 定位 time=1.5 的 shape=5 点重新验证。run1 fx_wet 负值案例失败（-.5读回0），保留失败记录，不算全通过。master hardware automation API 成功而文件不变，也不算持久字段证据。

机器证据：[results.json](results.json)、`run1/runs/r_000001/proof.json`、`run2/runs/r_000001/proof.json`（完整运行 proof 仅保留在本地归档，不随仓库分发）。scripts/report.mjs 校验关键保存行，保留原始快照供复核。e/E 沿用上一轮独立实验。

## D001：部分支持新来源；root 待验证

Track/master 的 I_PANMODE=0/3/5/6 已设置、读回并保存。枚举名称由官方 API 支持：0 classic、3 balance、5 stereo、6 dual。未单独验证 root PANMODE 和 -1 回退，不能把 track 实验直接当 root 的完整行为验证。

证据：track_I_PANMODE_*; master_I_PANMODE_*。未标 run2 的快照位于 run1。

## D002：本地模块证据支持保留原文；未做编辑器行为实验

上一轮 reaper_midi.dylib 含编辑器字段 writer；足以否定只扫主 EXE 的推理方法，不能直接裁定 7.61 Windows 模块。

证据：../evidence/binary-formats.json。未标 run2 的快照位于 run1。

## D003：原文正确；新来源 K.2 正确、C.8.2 错

此前四状态实测 E 未选、e 选中，m 后缀静音。

证据：../evidence/live-validation.json。未标 run2 的快照位于 run1。

## D004：新来源第7参 tension 正确

普通 JSFX 参数包络，shape=5；改变 tension 只改变 PT t7，选中改变 t5。原文 t4=tension 错。tempo 包络及 t4 精细语义未验证。

证据：run2/pt_tension_1.rpp; run2/pt_tension_2.rpp; run2/pt_selected.rpp。未标 run2 的快照位于 run1。

## D005：仍待本地行为验证

pitch range/snap 有独立文档支持，本轮未操纵 DEFSHAPE。不能列为实机定论。

证据：尚无本轮单变量证据。未标 run2 的快照位于 run1。

## D006：原文低两位正确；新来源非位域结论错误

关闭两选项128；只开 crossfade129；再开 trim131；动作状态分别读回。支持 +1/+2 独立位。其它位含 -64 与 bit7 尚未验证。

证据：run2/action_41119.rpp; run2/action_41118.rpp; run2/action_41120.rpp。未标 run2 的快照位于 run1。

## D007：原文正确

解除联动，时间选区1.25..2.5、loop4..7；分别保存 SELECTION 与 SELECTION2，后者不是副本。

证据：run2/selection.rpp。未标 run2 的快照位于 run1。

## D008：待对应版本验证

本机7.48不能直接验证7.61新增根头第4参。

证据：尚无本轮单变量证据。未标 run2 的快照位于 run1。

## D009：未新增实机结论

TEMPO t4 / RIPPLE t2 保留基准，未做逐项实验。

证据：尚无本轮单变量证据。未标 run2 的快照位于 run1。

## D010：原文部分细节正确

B_TCPPIN 对应 SHOWINMIX t9；I_NUMFIXEDLANES 对应 ITEMLANES；C_LANESETTINGS=0/2/8/32 对应 FIXEDLANES t1。未验证其余位及 LANEREC。

证据：track_B_TCPPIN_*; track_I_NUMFIXEDLANES_*; track_C_LANESETTINGS_*。未标 run2 的快照位于 run1。

## D011：双方各有正确部分

REC t3=I_RECMON、t4=I_RECMODE、t5=I_RECMONITEMS，支持原文；新增 t8 对应 I_RECMODE_FLAGS，0/1/2已读回保存。t6 PDC 未本轮切换。

证据：track_I_RECMON_*; track_I_RECMODE_*; track_I_RECMONITEMS_*; track_I_RECMODE_FLAGS_*。未标 run2 的快照位于 run1。

## D012：原文已知字段获支持；新增位置只确认结构

TRACKHEIGHT t1高度/t3锁高、BUSCOMP t1折叠均验证；保存分别7/5参，未解释所有其它位置。

证据：track_I_HEIGHTOVERRIDE_*; track_B_HEIGHTLOCK_*; track_I_FOLDERCOMPACT_*。未标 run2 的快照位于 run1。

## D013：普通 HWOUT 原文t9正确；新来源t8获支持；master另论

HWOUT t8=panlaw含:U，t9=I_AUTOMODE；MASTERHWOUT本机只写8参，t8颜色无关、为panlaw。master I_AUTOMODE虽API读回成功，RPP无变化，不能认定存在持久化t9。

证据：hw_I_AUTOMODE_*; hw_D_PANLAW_*; masterhw_I_AUTOMODE_*; masterhw_D_PANLAW_*。未标 run2 的快照位于 run1。

## D014：双方各有正确部分

AUXRECV t10=panlaw含:U；t11对应 I_MIDIFLAGS（0/31/1/33）；t12=I_AUTOMODE，支持原文自动化解释，不能降成未知flags。API定义0=全部，31=禁用源MIDI，所以原文0=None不成立；未做MIDI音频渲染，t13 GUID未验证。

证据：send_I_MIDIFLAGS_*; send_I_AUTOMODE_*; send_D_PANLAW_*。未标 run2 的快照位于 run1。

## D015：原文单位有误；新来源无条件秒也不完整

flag0，D_PLAY_OFFSET=.125/.25原值写出，即秒而非毫秒；flag2写128/256采样；flags可为3，按位解释，不能只用互斥枚举。

证据：seconds_D_PLAY_OFFSET_*; samples_D_PLAY_OFFSET_*; track_I_PLAY_OFFSET_FLAG_*。未标 run2 的快照位于 run1。

## D016：128声道说法获支持；通用64上限错误

普通轨与master设置128读回成功并保存128，同时出现>64标记。本轮不验证128路实际音频路由。

证据：track_I_NCHAN_2.rpp; master_I_NCHAN_2.rpp。未标 run2 的快照位于 run1。

## D017：原文MUTE两字段正确；其余待验证

更正先前清单措辞：原文本来就有MUTE t2。B_MUTE_ACTUAL改变t1；C_MUTE_SOLO=-1/0/1改变t2。这不是新增arg。POSITION/LENGTH/SNAPOFFS的QN尾参仍待验证。

证据：item_B_MUTE_ACTUAL_*; item_C_MUTE_SOLO_*。未标 run2 的快照位于 run1。

## D018：原文已知字段及部分新位置获支持

FADEIN/OUT t2手动时长、t3自动时长、t6曲率有API设置与保存证据。形状设置可能同时改变t1/t4及曲率；不能据此完整裁定小数形状枚举及t5/t7。

证据：item_D_FADEINLEN_*; item_D_FADEINLEN_AUTO_*; item_D_FADEINDIR_*; item_D_FADEOUT*。未标 run2 的快照位于 run1。

## D019：新来源t3正确、t6错误；t5需精确措辞

PLAYRATE t3=D_PITCH半音，t5=I_STRETCHFLAGS，t6=F_STRETCHFADESIZE（秒），不是quality。原文未列t6；两份文档都不足以完整说明。

证据：take_D_PITCH_*; take_I_STRETCHFLAGS_*; take_F_STRETCHFADESIZE_*。未标 run2 的快照位于 run1。

## D020：原文第3参颜色正确

改变 take marker color，TKM t3跟随；macOS颜色保存数值与API颜色整数可能存在通道布局转换，不能直接泛化跨平台编码。t4用途未验证。

证据：take_marker_color_*。未标 run2 的快照位于 run1。

## D021：原文WET t2正确；其它部分仍待验证

切换 :delta 后 WET 1 1，t2是delta solo；wet=.25/.75写t1。API设置-.5被钳为0，此路径不支持负值，但没有测试RPP reader是否另支持负值。BYPASS t1旁路/t2offline已验证；t3及窗口坐标未验证。

证据：fx_delta_*; fx_wet_*; fx_bypass_*; fx_offline_*。未标 run2 的快照位于 run1。

## D022：待本地行为验证

ACT/VIS/LANEHEIGHT尾参、ARM缺省未做单变量测试。

证据：尚无本轮单变量证据。未标 run2 的快照位于 run1。

## D023：待本地行为验证

本轮未切换trim/pitch等包络类型，不把PROGRAMENV内部矛盾当作实机证明。

证据：尚无本轮单变量证据。未标 run2 的快照位于 run1。

## D024：未验证全称；不采信全称保证

未进行未知token重载回写实验。来源自身缺乏无条件无损保证的充分证据。

证据：尚无本轮单变量证据。未标 run2 的快照位于 run1。

## D025：待reader级验证

未穷尽引号/注释/省略尾参；WDL源码只能证明对应解析器实现，不能替代REAPER所有调用点。

证据：尚无本轮单变量证据。未标 run2 的快照位于 run1。

## D026：新来源CURSOR与MASTERPEAKCOL解释正确

编辑光标1.25/3.75秒对应CURSOR；master I_CUSTOMCOLOR改变MASTERPEAKCOL。VZOOMEX未测试，颜色跨平台位布局未推定。

证据：cursor_*; master_I_CUSTOMCOLOR_*。未标 run2 的快照位于 run1。

## D027：部分结构确认，flags未裁定

新增marker和region真实保存；可见region结束短行，但未逐项切换选择/渲染/颜色位，不能裁定全部字段。

证据：project_markers.rpp。未标 run2 的快照位于 run1。

## D028：新来源四项API映射正确

MASTERTRACKVIEW t2=F_MCP_FXSEND_SCALE、t3=F_MCP_SENDRGN_SCALE、t4=F_MCP_FXPARM_SCALE、t13=F_TCP_FXPARM_SCALE，各自两值设置/读回/保存。原文t13未知可补；参照区域应依API精确定义。原文t15 pin也验证。

证据：master_F_MCP_*; master_F_TCP_FXPARM_SCALE_*; master_B_TCPPIN_*。未标 run2 的快照位于 run1。
