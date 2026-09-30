# 章节源 JSON：写入与诊断

2026-09-30 核对[官方 JSON 参考](https://docs.avg-engine.com/reference/script-json)、[调用片段](https://docs.avg-engine.com/manual/writing/blocks/call-fragment)和[章节调度](https://docs.avg-engine.com/advanced/chapter-scheduling)。这些页面未锁定每个宿主版本，不能替代[目标版本证据](version-compatibility.md)。磁盘章节、编译 OP、内置 AI 协议和导入文本是不同格式。

## 先从当前作品取得上下文

读取本次相关章、`project.json` 及需要的角色／场景／变量定义，提取实际 ID、变量 key 和素材引用。典型位置包括 `chapters/*.json`、`characters.json`、`scenes.json`、`project.variables.json`；以该作品实际结构为准。不从显示名字猜 UUID，也不新建整套缺失配置来凑完整工程。

普通章节文件名与顶层 `name` 一致，至少有一个 Fragment，第一项名称是 `main`，`blocks` 按顺序执行。章与片段需要唯一 ID；Block 新建时可省略 ID，修改已有对象保留原 ID。空 `blocks: []` 是合法骨架。

普通新章节登记既有 `chapterOrder`，同时核对章节树和实际调度，不覆盖整个 `project.json`。`kind: "schedule-preprocessing"` 是特殊前处理，不参加普通章节排序；不要因它未列入 `chapterOrder` 就添加进去。普通章节省略 `kind`，不要猜 `normal` 或写 `null`。前处理内容及作用域按调度页和目标样本查证。

## 按字段保存，保留未知结构

| 对象／参数 | 文档中的写法 | 容易弄错的地方 |
| --- | --- | --- |
| `props`、片段 `metadata` | 对象 | 不能整体序列化成字符串；保留已有扩展配置 |
| 纯文本 `content` | 内联项数组，文本项含 `type/text/styles` | 台词不能放进 `props.text`；不要删除未知行内项 |
| `branch.choices`、`if.conditions` | 外层参数为 JSON 字符串 | 先构造数组，再用序列化器写入；不是直接存数组 |
| 场景／声音等布尔数值参数 | 各字段可能是真标量或字符串标量 | 逐项查字段表，禁止全局转成 bool／number |
| `setver`、选项 `varOps` | 同一套赋值字段；`varOps` 本身是数组 | UI 名 Setvar 与磁盘 `setver` 区分；不猜目标变量 key |
| 扩展方法参数 | 查询其参数 schema 和该版保存样本 | 字面量／变量引用、条件参数与剧本方法参数不能混用 |

缺省、空字符串与 `null` 分开判断。只在字段说明明确允许时使用空值；不能为“补齐默认值”批量写 null。2.3 Beta 的超链接、姿势／部位和选项样式见[专页](versions/beta-2.3.md)，缺序列化证据就保持 UNKNOWN。

## 章内调用与跨章流程

`branch` 的 `jump` 选项调用片段后回流，空目标按当前文档表示继续；`vars` 选项执行变量操作，不靠片段跳转表达。旧选项省略 `mode` 可兼容为 jump，新生成显式写 mode。`if` 从真实条件数组选择 then／else 目标；`callFragment` 是直接调用。不要给 Fragment 添加猜测的 next 字段，也不要把调用结束当互斥结局。[分支](https://docs.avg-engine.com/manual/writing/blocks/branch)

**官方资料有冲突**：JSON 生成规约要求目标为非 main；调用片段手册却说明编辑器可选 main 和当前片段。生成新内容时采用非 main、无环的保守结构；遇到现有 `callFragment → main`，保留并标记待目标宿主核验，不能直接判成损坏。

调用片段手册描述的是转换期静态展开，上限 30 层，循环会截断并可能卡顿，不是可用运行时条件退出的递归。不要用自调用制作无限菜单。检查器的环／深度提示只来自存储引用图，不推断禁用块是否被转换、运行可达性或真实执行结果。跨章路线交给当前基础／蓝图调度，不用章内片段引用冒充跨章跳转。

## 修改和验证

加载原对象，定位章／片段／Block，修改必要字段；复杂参数使用两层 JSON 序列化器。参考[原创选择练习](../examples/选择练习.json)，复制前重生成章与片段 ID 并替换引用。示例没有图像或音频依赖，但仍是待加入工程的章节，不是完整游戏或已运行样本。

`scripts/check_project.py` 只读检查 JSON 语法、有限片段结构、索引、对象 ID 和本章引用；未知指令、复杂参数内部语义、角色／变量／资产、蓝图、全部标量类型及运行流程未覆盖。当前 varOps／conditions 只检查外层数组，不能以零错误认定内部表达式正确。

- `auto`：识别已维护的片段布局；旧 mode 缺省按 jump 提示；未知布局／部分指令参数形态返回 unsupported_format。空调用目标按编辑器兼容行为提示，不能当有效生成结果。
- `fragments`：按同一有限约定检查，不对未知布局作 auto 回避；不能保证新建字段完整，也不能证明角色 ID 或全部参数类型正确。
- `json-only`：只解析语法，不施加引擎格式。

退出码 0 表示此次覆盖范围未发现错误，警告仍须读；1 表示所检查约定中有错误；2 表示无法检查或存在未覆盖格式。结果分别统计未覆盖章节与指令，不能把指令数叫章节数。格式有争议时先比对该版保存样本；不要对未知格式运行自动转换。

静态检查后，在实际入口覆盖选项、条件边界、变量反馈、返回与重入；持久状态另测存读档及全新启动，目标导出另测。不能将 JSON 可解析称为引擎已加载或流程已通过。
