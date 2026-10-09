# 章节源 JSON：写入与诊断

本页保留原有磁盘格式工作法与只读检查。已接入官方 MCP 的活动工程优先用 story_read／写入工具，按 [MCP 工作流](mcp-workflow.md) 读取当前块结构；MCP 脚本文本、块 JSON 与磁盘章节不能混用。直接写磁盘仅用于已关闭工程或有效外部编辑会话的明确范围；等自动保存结束不足以避免覆盖。

2026-10-05再次核对[官方 JSON 参考](https://docs.avg-engine.com/reference/script-json)、[调用片段](https://docs.avg-engine.com/manual/writing/blocks/call-fragment)和[章节调度](https://docs.avg-engine.com/advanced/chapter-scheduling)。这些页面未锁定每个宿主版本，不能替代[目标版本证据](version-compatibility.md)。磁盘章节、编译 OP、内置 AI 协议和导入文本是不同格式。

## 先从当前作品取得上下文

仅当结构／字段诊断需要时，读取本次相关章、`project.json` 及需要的角色／场景／变量定义，提取实际 ID、变量 key 和素材引用。典型位置包括 `chapters/*.json`、`characters.json`、`scenes.json`、`project.variables.json`；以该作品实际结构为准。不从显示名字猜 UUID，也不新建整套缺失配置来凑完整工程。

普通章节文件名与顶层 `name` 一致，至少有一个 Fragment，第一项名称是 `main`，`blocks` 按顺序执行。章与片段需要唯一 ID；Block 新建时可省略 ID，修改已有对象保留原 ID。空 `blocks: []` 是合法骨架。

普通新章节登记既有 `chapterOrder`，同时核对 `chapterTreeOrder` 与实际调度；已有目录排序和入口保留，不覆盖整个 `project.json`。2.5.0隔离样例同步两份索引后，原生树与跨章调度均识别新增章节。`kind: "schedule-preprocessing"` 是特殊前处理，不参加普通章节排序；不要因它未列入 `chapterOrder` 就添加进去。普通章节省略 `kind`，不要猜 `normal` 或写 `null`。前处理内容及作用域按调度页和目标样本查证。

## 按字段保存，保留未知结构

| 对象／参数 | 文档中的写法 | 容易弄错的地方 |
| --- | --- | --- |
| `props`、片段 `metadata` | 对象 | 不能整体序列化成字符串；保留已有扩展配置 |
| 纯文本 `content` | 内联项数组，文本项含 `type/text/styles` | 台词不能放进 `props.text`；不要删除未知行内项 |
| `branch.choices`、`if.conditions` | 外层参数为 JSON 字符串 | 先构造数组，再用序列化器写入；不是直接存数组 |
| 场景／声音等布尔数值参数 | 各字段可能是真标量或字符串标量 | 逐项查字段表，禁止全局转成 bool／number |
| `setver`、选项 `varOps` | 同一套赋值字段；`varOps` 本身是数组 | UI 名 Setvar 与磁盘 `setver` 区分；不猜目标变量 key |
| 扩展方法参数 | 查询其参数 schema 和该版保存样本 | 字面量／变量引用、条件参数与剧本方法参数不能混用 |

缺省、空字符串与 `null` 分开判断。只在字段说明或该版原生保存样本允许时使用空值；不能为“补齐默认值”批量写 null。2.4.0-beta.1 原生空白旁白保存时可以省略 `content`；auto 模式对此给出 `native_empty_narration` 警告，保留原文。新生成文本仍显式写内联数组，null／字符串／对象不能代替数组，其他文本指令不据此放宽。2.3 Beta 的超链接、姿势／部位和选项样式见[专页](versions/beta-2.3.md)，2.4 变化见[新版专页](versions/beta-2.4.md)，缺序列化证据就保持 UNKNOWN。

## 章内调用与跨章流程

`branch` 的 `jump` 选项调用片段后回流，空目标按当前文档表示继续；`vars` 选项执行变量操作，不靠片段跳转表达。旧选项省略 `mode` 可兼容为 jump，新生成显式写 mode。`if` 从真实条件数组选择 then／else 目标；`callFragment` 是直接调用。不要给 Fragment 添加猜测的 next 字段，也不要把调用结束当互斥结局。[分支](https://docs.avg-engine.com/manual/writing/blocks/branch)

**官方资料有冲突**：JSON 执行模型将 callFragment 与 branch／if 一起限定为非 main，调用片段手册却允许 main 和自身。2026-09-30在2.3.0-beta.1、2026-10-05在2.5.0正式版原生片段实时预览中，无环A → main均执行目标内容并返回；所以不能将main一律禁止。新制作默认使用无环、非 main 的普通复用片段；明确需要 main 时按实际入口验证。既有引用保留，其他版本、入口与导出仍分别核验，见[本版证据](versions/beta-2.3.md)。branch／if 的 main 目标本轮未测，不从 callFragment 结果推断。

官方手册和编辑器提示声明循环在转换期展开至多 30 层；三个 2.3.0-beta.1 原生循环用例却没有重复输出，自调用 OP 只有两条旁白及对应销毁指令。本轮未确定一般转换算法或深度硬上限，不能把资料声明当作递归保证，也不能推广为所有版本立即剪枝。避免循环与自调用菜单。检查器从存储引用图提示环和超过文档 30 层阈值的无环链；这是复核提示，不能证明转换失败。独立无环链不会因其他片段含环而漏报，循环关联部分的完整最长路未覆盖；不推断禁用块转换或运行可达性。跨章路线使用实际基础／蓝图调度。

2.6.0-beta.1 官方 MCP 脚本资源另外规定 `call` 不以 main 为目标，且部分块不能往返脚本文本；adjustVolume、loadingStrategy、hideFloatingText等仅为该版实例，始终以当前textRoundTripSafe、roundTripIssues及schema判断，不把固定名单当成全部限制。它是该接口约定，不抹去上述原生历史结果；不要用旧样例绕过 MCP 校验，也不要自动改写旧引用。具体适配见 [MCP 工作流](mcp-workflow.md)。

## 修改和验证

加载原对象，定位章／片段／Block，修改必要字段；复杂参数使用两层 JSON 序列化器。参考[原创选择练习](../examples/选择练习.json)，复制前重生成章与片段 ID 并替换引用。示例没有图像或音频依赖，但仍是待加入工程的章节，不是完整游戏或已运行样本。

`scripts/check_project.py` 只读检查 JSON 语法、有限片段结构、索引、对象 ID 和本章引用。0.2.0补查conditions的对象、运算符及左右值形态，setver／varOps的操作数类型、字段和组合约束；不执行表达式，也不证明变量存在、字面量可用于该变量或方法签名正确。未知条件来源保留并标unsupported；未知指令、角色／变量／资产、蓝图、全部标量类型及运行流程仍未覆盖。零错误只表示本次子集未发现错误。

- `auto`：识别已维护的片段布局；旧 mode 缺省按 jump 提示；未知布局／部分指令参数形态返回 unsupported_format。空调用目标按编辑器兼容行为提示，不能当有效生成结果。
- `fragments`：按同一有限约定检查，不对未知布局作 auto 回避；不能保证新建字段完整，也不能证明角色 ID 或全部参数类型正确。
- `json-only`：只解析语法，不施加引擎格式。

main、环、深度和前处理误入普通索引分别提供 `main_call_version_sensitive`、`fragment_cycle`、`fragment_depth`、`preprocessing_in_linear_order` 诊断代码，都是需复核的 warning，不自动改写。同一含If片段被多处存储引用时另提示 `if_reuse_decision_risk`，不据此推断运行可达性。退出码 0 表示此次覆盖范围未发现错误，警告仍须读；1 表示所检查约定中有错误；2 表示无法检查或存在未覆盖格式。结果分别统计未覆盖章节与指令，不能把指令数叫章节数。格式有争议时先比对该版保存样本；不要对未知格式运行自动转换。

静态检查后，在实际入口覆盖选项、条件边界、变量反馈、返回与重入；持久状态另测存读档及全新启动，目标导出另测。不能将 JSON 可解析称为引擎已加载或流程已通过。

## 2.3.0-beta.1 选项赋值的有限原生样本

2026-10-01，原生面板把单项从 jump 切成 vars 后，`choices` 仍是 JSON 字符串。数组中的该项保存 `mode: vars`、`text` 和数组 `varOps`，没有 `fragmentId`。本次操作原文为：

```json
{"key":"BETA_SCORE","op":"=","aKind":"lit","aLit":"42","aVar":"","bKind":"none","bLit":"","bVar":"","binOp":"+"}
```

目标是原生创建的 slot 数值项目变量，默认0、不启用启动重置；调试和新桌面玩家点击均得到42，桌面重启快读／槽位1读档也恢复42。以上只确认这个样本，不能把其空字段或binOp当作其他表达式的默认规范。其他赋值、条件、变量类型与持久方式仍按该版实际样本取证；0.2.0补查varOps内部字段形态，仍不解释表达式或判定变量语义。

## If的回放与正常重入分开

[官方If说明](https://docs.avg-engine.com/manual/writing/blocks/if/)规定回放／历史跳转复用之前的判断结果。2026-10-05在2.5.0正式版合成工程：值为0时调用判断片段走真分支，选择后赋值为1，再调用同一片段仍走真分支；实时面板和正文插值均确认值已为1。紧接着具有独立Block ID、相同条件与目标的新If走假分支。独立Windows玩家选择另一条路线后插值为2，复用If仍为真，独立If为假；本地Web玩家选择首路，插值为1，复用If仍为真，独立If为假。三层各自实际操作，没有用调试结果代替玩家验证。

制作时，把需要在后续位置按新值判断的步骤编排为独立判断区块，并在实际入口验证。新建区块用新ID，已有区块ID保留；不要为了“解锁”批量重写ID或制造循环。这个有限对照支持避免依赖同一If重复求值，尚不证明所有版本、读档路径或内部缓存键。If也不是持续监听器。条件方法以查询为主，副作用另设明确动作；缺失／失败／类型不符按文档与实际警告核对。

## 2.5.0原生赋值与变量反馈

正式版原生项目数值变量保存 `persistence: slot`、默认0；If保存JSON字符串conditions，字面量零仍为字符串；Setvar的磁盘类型仍为 `setver`，字面量一仍为字符串。实际调试赋值后，运行旁白 `CONTROL_VALUE_{SKILL020_SCORE}` 显示 `CONTROL_VALUE_1`，与实时数据面板相符。固定写“值为一”的台词只是说明文字，不能代替变量证据。工程模板仍保存 `version/engineVersion: 1.0.0`，其语义UNKNOWN；实际宿主版本由EXE和官方界面核定。
