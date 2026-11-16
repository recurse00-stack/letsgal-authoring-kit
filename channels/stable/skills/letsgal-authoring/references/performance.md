# 演出段

本页处理时间轴；角色／媒体见[舞台](stage-and-assets.md)，运行入口见[预览](preview-and-build.md)。

## 编排与写入

同一片段的平铺块用 performanceStart／performanceEnd 成对围住，脚本写 performance begin／performance end。起止同批增删，保持单层演出；字段查当前 stage、script 指导及标记 schema。

| 项目 | 操作规则 |
| --- | --- |
| 时间单位 | JSON segmentStart／segmentHold 用毫秒，脚本 at／hold 用秒 |
| 普通轨排序 | 块顺序同时决定时间顺序；较早时刻会抬到前块开始，未指定开始则接上一条占时长指令。背景声音、粒子、变量等不推进后续时刻；r7 并行循环轨有独立时钟 |
| 文字轨道 | 对白、旁白、段落及关闭对话框共用轨道，保持区间不重叠 |
| 自动时长 | 显式 hold 转手动；恢复自动按 schema 用 null 清除手动时序，读回自动字段和语音跟随，并检查相邻文字 |
| 段尾 | segmentEndBehavior=continue 自动继续，waitForClick 等一次点击；segmentForceWatch=true 要求观看，验证所需输入行为 |
| 轨道配置 | 保留 segmentTrack、名称、禁用和锁定；普通轨禁用仍占时间，锁定仅影响编辑。并行循环轨另由 segmentLoopGroups 与成员归属管理 |

段内按当前允许清单使用舞台／媒体／对白指令。分支、If、片段调用、章末／返回、玩家输入、系统消息、wait、自动播放切换、加载策略、旧 stageAnimation 及模态 UI 打开指令放在段外。停顿通过下一条开始时刻安排。扩展运行时弹出的模态 UI 会暂停时间轴，关闭后恢复。

精确运镜用独立 camera 块，默认持续 1 秒，瞬变明确 0；多条镜头操作互相接管。对白内联镜头受打字速度影响。旧镜头动画按明确迁移范围处理。

普通轨段长取其有效指令的最晚结束；并行循环轨不延长前台等待。媒体文件长度、异步扩展方法各按实际占时规则安排。声音／视频／粒子／蒙层淡出参数查各自 schema。

**MCP 时序位置**：先成对插入并取得块 ID，再用最新 revision 的 story_edit_blocks **update 操作层**设置 segmentStart／segmentHold；读回块 props 中的时序及自动标志。insert.blocks[] 使用存储块格式。2.8 样本将操作层字段放到插入块顶层会被忽略。

提交前 dry run，提交后查 performance-segments 及相关编译／引用。处理短 hold、portrait-pose-interrupted 等 warnings；后者表示后续立绘动作可能接管尚未结束的姿态变化，按预期调整时序；自动时长引发重叠时同批调整相关文字。

## 并行循环轨与控制（3.0 r7）

r6 引入并行循环轨，r7 调整其运行语义：**普通轨播完后按段尾设置继续剧情，各循环轨按自己的周期和次数在后台运行**。维护 r6 内容时先核实际补丁与当前参考；r6 公告中“前台无限循环阻塞剧情”的说明不适用于 r7。

普通轨的 `segmentBackgroundLoop=true` 使普通轨也在后台重复，剧情立即继续，`segmentEndBehavior` 和 `segmentForceWatch` 对这部分不生效。它与并行循环轨分别配置。普通后台轨限画面、音效等可循环指令；并行循环轨另支持幕布、BGM 和语音，文字与剧情控制留在普通轨或段外。

先读目标段的 JSON。r7 的开始标记 `props.segmentLoopGroups` 为 JSON 数组字符串；每项使用段内唯一 `id`、非负整数 `start`、正整数总轮数 `count`，无限为 JSON `null`；可保留 `name`、`disabled`、`locked`。成员块用 `props.segmentLoopGroup` 指向该 ID，`segmentLoopOffset` 记录轨内毫秒位置。新建最小组可用：

```json
{"segmentLoopGroups":"[{\"id\":\"loop-a\",\"start\":0,\"count\":2,\"name\":\"环境动作\"}]"}
```

成员示例为 `{"segmentLoopGroup":"loop-a","segmentLoopOffset":0}`，与该指令自身的合法参数合并。这里的组 ID 属于新建段内部；修改现有内容使用真实组 ID。周期由轨内指令计算，不自行添加 duration 字段。`segmentTrack` 是编辑器行号，不能代替循环组归属。

通过 `story_edit_blocks` 局部更新 props，保留其他组和成员；新增时同批包含成对标记。当前 performanceStart 字段表尚未完整列出上述存储字段，需结合目标 r7 JSON 和 dry-run 核对，写后逐项读回。脚本可保留这些属性，但已有复杂段的局部改动优先块编辑。

“演出段控制”继续使用块类型 `stopBackgroundPerformance`：

| action | 目标与效果 |
| --- | --- |
| `stop`，或省略 | segmentId 填开始标记的真实块 ID，停止该段后台轨道；留空停止全部后台演出 |
| `pauseTrack` | segmentId 和 trackId 都必填；trackId 来自该段 segmentLoopGroups，暂停并保持当前位置 |
| `resumeTrack` | 同一组标识，从暂停位置继续 |

换章停止后台演出；读档或跳转会从循环轮次起点重建，轮内位置不保留。为无限循环安排停止路径；并行轨和剧情争用同一镜头／场景／角色时，按任务意图处理接管告警。

## 连续播放验证

核普通轨结束、段后剧情继续、各循环轨实际变化，以及暂停保持／继续／有限轮次结束／显式停止。持续视频／粒子另按 ID 核停止范围。需要显示轮次时可由人工展开该循环轨；当前 preview_get_state 未提供完整循环轮次列表，使用它实际返回的对象状态与连续播放核对。

从 fresh 状态 run_to 到段前可等待台词，再 advance 连续进入；观察换句、配置的 PerformanceEndWait、段后 Dialogue 及正文。没有段前台词时加载包含段后正文的范围，再从当前状态映射取队列索引定位段首。原生“重播”用于检查时间轴，段尾仍须实际推进。

要看中间帧，让 advance.timeoutMs 短于演出时长。收到 stoppedBecause=timeout 后读 position、waitingFor 和画面；处于 PerformanceSegment／busy 时继续观察至段尾。默认调用可能等待整段结束才返回。

seek／run_to 是定位路径，可能重放方法和订阅；副作用异常用 fresh 后连续路线复核。历史包含旧重播条目时核本次位置。位置跳到 following／别章则重核目标再有限重定位；窗口隐藏按[预览处理](preview-and-build.md#选择与交互)。

## 存档与副作用

段内读档从段首重播，槽位变量回到段首值；共享和启动重置变量保留各自语义。共享累加、Steam stat.add 及外部动作实现防重复结算，按实际存档落点验证。扩展恢复方法见[运行状态与恢复](extensions.md#运行状态与恢复)。
