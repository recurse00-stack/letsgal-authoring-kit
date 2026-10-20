# JSON 与离线检查

先区分磁盘章节、MCP 脚本、编译 OP、内置 AI 协议和导出文本，它们不能直接互换。活动工程按[MCP 流程](mcp-workflow.md)修改；离线写文件须先保存并关闭目标工程。显示文本与富文本原序列化的区别也见该流程。

## 目标结构

只读相关章／片段／块和用到的角色、场景、变量。典型文件为 chapters/*.json、characters.json、scenes.json、project.variables.json，真实结构以目标工程为准；不按显示名猜 UUID。

普通章节文件名与顶层 name 一致，至少有一个 Fragment，第一项名为 main，blocks 按序执行，空数组可作骨架。已有章／片段／块 ID 保留；MCP 新结构用返回的真实 ID。磁盘格式允许新块省略 ID，不表示可以拿序号充当 MCP 块 ID。

新增普通章登记已有 chapterOrder，并核 chapterTreeOrder 与真实调度，保留其他索引及入口。kind 为 schedule-preprocessing 的前处理不加入普通章顺序；普通章省略 kind，不猜 normal 或补 null。[JSON 参考](https://docs.avg-engine.com/reference/script-json) · [章节调度](https://docs.avg-engine.com/advanced/chapter-scheduling)

## 序列化与保真

| 内容 | 规则 |
| --- | --- |
| props、片段 metadata | 对象；保留未知配置，不整体转字符串 |
| 对白 content | 内联数组，改目标 text 并保留 styles／非文字项／控制标记，不移到 props.text |
| branch.choices、if.conditions | 磁盘外层参数为 JSON 字符串，用序列化器编码内部数组，不直接存数组 |
| 布尔／数字 | 按具体字段或当前样本判断，不全局转换字符串标量 |
| setver、varOps | UI 名 Setvar 与磁盘 setver 区分；varOps 自身为数组，保留赋值／增量运算语义 |
| 扩展参数 | 按真实声明区分字面量、变量与条件；[校验缺口](extensions.md#参数与校验)不能由 JSON 语法检查弥补 |
| 演出时序 | MCP update 操作层的 segmentStart／segmentHold 写到块 props；insert 的块顶层不沿用操作层字段，写后核实际 props。毫秒数与脚本秒数区分 |

缺省、空字符串和 null 不同，不批量补默认值。历史空旁白可能没有 content，先保留；新文本仍按规范写内联数组，不把历史例外推广到所有指令。

## 引用与控制流

branch 的 jump 选项调用同章片段并回流，vars 执行变量操作；新生成显式 mode，不随意叠加两种模式或给 Fragment 猜 next。空目标按当前 schema／样本处理，不能作为生成缺失引用的捷径。[分支](https://docs.avg-engine.com/manual/writing/blocks/branch)

当前 callFragment 字段要求同章已存在片段 ID，子流程结束后返回。自调用在转换期最多静态展开 30 层，不支持按运行时条件退出的真递归；这是当前宿主契约，不是运行兼容测试。不要将旧检查器对 main／环／深度的提示直接判成现有内容无效，也不要自动改写这些引用。If 的复用与变量语义见[制作能力](story-and-voice.md#剧情变量与流程)。

## check_project.py 的实际覆盖

只读检查 JSON 语法、有限章节布局、索引、ID、本章引用、conditions 与 setver／varOps 操作数形态。不执行表达式，不证明变量存在、方法签名或玩家行为正确。

- auto 识别已维护布局，未覆盖格式明确报告；fragments 检查相同有限约定；json-only 只解析语法。
- 退出码 0 表示已检查范围未发现错误，仍需读 warning；1 表示约定错误；2 表示无法检查或存在未覆盖格式。
- main_call_version_sensitive、fragment_cycle、fragment_depth、preprocessing_in_linear_order、if_reuse_decision_risk 是复核提示，不证明真实可达性或转换失败，不触发自动修复。
- native_empty_narration 等兼容提示用于保留旧原文，不授予生成未知格式的依据；未知章节与未知指令分别统计。

[选择练习](../examples/选择练习.json)须按加入方式创建新 ID 与引用，不直接覆盖原章。静态通过之后，按本次影响验证宿主读回、路线和持久化；不能运行时明确交付仅到文件／静态层。
