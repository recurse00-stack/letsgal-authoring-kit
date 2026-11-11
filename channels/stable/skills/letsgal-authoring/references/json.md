# JSON 与离线检查

先确定目标是磁盘章节、MCP 脚本、编译 OP、内置 AI 协议还是导出文本，再按对应格式处理。活动工程使用 [MCP](mcp-workflow.md)，离线写文件前保存关闭目标工程。

## 目标结构

按任务读取章节及其角色、场景、变量引用。常见文件为 chapters/*.json、characters.json、scenes.json、project.variables.json，实际路径和 UUID 从目标工程获取。

普通章节文件名与顶层 name 一致，至少有一个 Fragment，第一项名为 main，blocks 顺序执行，空数组可作骨架。保留已有章／片段／块 ID；MCP 新结构使用宿主返回 ID。磁盘允许新块省略 ID；MCP 定位仍须使用其支持的真实标识。

新增普通章登记 chapterOrder，核 chapterTreeOrder 和实际调度；前处理 `kind=schedule-preprocessing` 留在普通章顺序外，普通章省略 kind。保留其他索引与入口。[JSON 参考](https://docs.avg-engine.com/reference/script-json) · [章节调度](https://docs.avg-engine.com/advanced/chapter-scheduling)

## 序列化与保真

| 内容 | 写法 |
| --- | --- |
| props／片段 metadata | 保持对象，局部修改目标键 |
| 对白 content | 保持内联数组及 styles、非文字项、控制标记 |
| 旧 branch.choices／if.conditions | 用序列化器生成内部数组，再存为外层 JSON 字符串 |
| 布尔／数字 | 按字段 schema 或当前有效样本保留类型 |
| setver／varOps | UI 名 Setvar 对应磁盘 setver；varOps 是数组，区分赋值与增量 |
| 扩展参数 | 按[真实声明](extensions.md#参数与校验)核字面量、变量及条件 |
| 演出时序 | 存储在块 props；MCP 操作位置及时间单位见[编排](performance.md#编排与写入) |

保留缺省、空字符串与 null 的区别；历史空旁白可没有 content，新文本使用内联数组。

**额外字段**：定向编辑保留非目标原文。新增信息使用当前格式或插件声明的扩展位置。未声明的自定义 props 不具有任意键往返承诺；依赖额外字段时先核支持方式，再安排迁移与读回。正式字段或承诺支持的数据损失才按缺陷排查。

## 引用与控制流

**3.0 新建结构**存于同一 `blocks` 数组：

| 结构 | 平铺顺序与必要字段 |
| --- | --- |
| 选择 | choiceStart → choiceOption(text) → 该项正文 → 后续 option／正文 → choiceEnd |
| 条件 | conditionStart(expression) → 正文 → 可选 conditionElse(kind=elseIf, expression)／正文 → 可选 conditionElse(kind=else)／正文 → conditionEnd |

选项可含 visibleIf，至多一个 isDefault=true；else 放最后且不携 expression 条件。起止按嵌套层配对，菜单开始后紧接首选项。完整演出段放在单条路线内，保持演出内部无控制流。脚本使用缩进结束组，磁盘使用平铺标记。移动／删除整组时包含所有路线和组尾；仅移除结构时明确保留正文并核顺序。

**旧格式**：3.0 只读取和定向维护 branch／if；branch 的 jump 可调用同章或其他启用章节中唯一的片段并回流，vars 执行变量操作。旧 if 的目标仍限同章。空目标按 schema 处理，片段后继使用实际调度。[分支](https://docs.avg-engine.com/manual/writing/blocks/branch)

callFragment 指向同章已存在片段，结束返回；当前契约在转换期最多静态展开 30 层，循环按实际调度设计。旧检查器的 main／环／深度提示用于复核；保留已有合法引用。If 语义见[剧情](story-and-voice.md#剧情变量与流程)。

## check_project.py 的实际覆盖

只读检查 JSON、有限布局／索引／ID／片段引用、conditions 与 setver／varOps 操作数，以及嵌套结构配对、分支字段、else 顺序和演出跨界；接受合法旧格式和未知字段。

- auto 识别已维护布局；fragments 检查相同有限约定；json-only 只解析语法。
- 退出码 0：检查范围无错误，仍读 warning；1：约定错误；2：无法检查或格式未覆盖。
- main_call_version_sensitive、fragment_cycle、fragment_depth、preprocessing_in_linear_order、if_reuse_decision_risk 交给宿主复核。
- native_empty_narration 用于保留历史原文；未知章节／指令分别统计。

表达式、变量存在性、完整方法合同及玩家路线由目标宿主验证。[选择练习](../examples/选择练习.json)用于 3.0 嵌套结构，新建时生成自己的 ID 与引用。交付注明已完成的文件检查和运行范围。
