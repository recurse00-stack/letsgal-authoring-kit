# 章节数据与局部修改

本页用于字段、序列化与离线检查；进入写入前先按本通道执行流程确认目标状态与权限。磁盘章节、MCP脚本、编译OP、内置AI协议和导入文本不是同一种格式。MCP的富文本读写与分页规则以其执行专题为准，不把显示文本当作原始序列化。

## 定位与结构

按目标读取相关章／片段／块及实际用到的角色、场景和变量；典型文件为chapters/*.json、characters.json、scenes.json、project.variables.json，以当前作品为准。已知目标不重扫整个目录，不用显示名猜UUID。

普通章节文件名与顶层name一致，至少有一个Fragment，第一项名为main，blocks按序执行，空blocks数组可作骨架。保留已有章／片段／Block ID；新结构通过当前执行方式取得合法ID。新磁盘Block按该格式可省略ID，缺ID不允许拿序号冒充MCP块ID。

新增普通章登记既有chapterOrder并核chapterTreeOrder及真实调度，保留目录和原入口，不覆盖整个project.json。kind为schedule-preprocessing的前处理不加入普通章顺序；普通章省略kind，不猜normal或补null。[JSON参考](https://docs.avg-engine.com/reference/script-json) · [章节调度](https://docs.avg-engine.com/advanced/chapter-scheduling)

## 字段保真

| 内容 | 保留／生成方式 |
| --- | --- |
| props、片段metadata | 对象，保留未知配置，不整体转字符串 |
| 对白content | 内联项数组；从原项修改目标text，保留styles、非文字项、格式／停顿／变量／动作标记，不改成props.text |
| branch.choices、if.conditions | 外层参数是JSON字符串；用序列化器编码内部数组，不直接存数组 |
| 布尔／数字参数 | 按各字段类型或目标样本处理，不能全局转换字符串标量 |
| setver、varOps | UI名Setvar与磁盘setver区分；varOps自身为数组，按实际运算符保留赋值／增量语义 |
| 扩展方法参数 | 核真实schema，区分字面量、变量引用、条件与普通调用 |

缺省、空字符串和null不同，不批量补默认值或清空未知字段。已存在的空旁白可有缺content的历史保存形态，先保留；新生成文本按当前规范写内联数组，不把这一例外推广到所有指令。配音绑定保留不表示旧录音已随新台词更新。

## 选项、调用与条件

branch的jump选项调用片段后回流，vars选项执行变量操作；新生成时显式mode。不能把卡片变量模式和跳转模式随意叠加，或给Fragment猜加next。空目标是否继续按当前样本处理，不作为生成缺失引用的捷径。[分支](https://docs.avg-engine.com/manual/writing/blocks/branch)

callFragment的main目标在官方执行模型与调用片段手册间存在描述冲突；既有引用不一律判错。新内容默认普通非main、无环复用片段；明确需要main时核当前入口证据。branch／if不能套用callFragment的观察。文档“最多30层”不保证递归循环行为，避免用自调用实现循环菜单。[调用片段](https://docs.avg-engine.com/manual/writing/blocks/call-fragment)

If不是持续监听，历史回放可复用先前判断；需要后续按新值判断时设置独立判断点，不批量重写已有ID“解锁”。条件方法尽量只查询，状态副作用另设动作；缺失、失败和类型不符按实际警告处理。当前正式版与Beta的证据范围见[当前能力](current-capabilities.md)。

## 离线只读检查的范围

scripts/check_project.py检查JSON语法、有限章节布局、索引、ID、本章引用、conditions和setver／varOps操作数形态；不执行表达式，不证明变量存在、方法签名或玩家行为正确。[选择练习](../examples/选择练习.json)使用前需按加入方式创建新ID和引用，不直接覆盖已有章。

- auto：识别已维护布局，未覆盖格式明确报告；fragments：检查相同有限约定；json-only：只解析语法。
- 退出码0：覆盖范围未发现错误，仍需读warning；1：已检查约定中有错误；2：无法检查或含未覆盖格式。
- main_call_version_sensitive、fragment_cycle、fragment_depth、preprocessing_in_linear_order、if_reuse_decision_risk为复核提示，不自动改写，不证明真实可达性或转换失败。
- native_empty_narration等兼容提示用于保留历史原文，不授予生成未知格式的依据。未知章节与未知指令分别统计。

本次改字读回文本及保留字段，引用变化再核相关结构；路线、保存读取与导出只按实际影响另验。没有宿主运行证据时，交付应明确只是文件或静态结果。
