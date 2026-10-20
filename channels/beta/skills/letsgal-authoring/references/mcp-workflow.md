# Studio 工程的 MCP 执行

本页负责目标、读写、确认和异常。制作字段按任务查[能力索引](current-capabilities.md)；独立扩展源码、Skill 与发行材料沿所属工程的文件流程维护。

## 连接与目标

首次用 `studio_get_status` 核完整宿主版本、工程 ID、权限／工具组、保存／输入及协作状态；读取服务 instructions 和 quickstart。无法读取资源时用 `studio_get_reference(topic="quickstart")`；专题按需读取，当前工具列表与 schema 决定可用接口。

复用有效 ID 和已读指导。等待确认、长耗时操作、换工程、重连或冲突后刷新相关状态，再根据结果决定是否写入。不能将“读状态”和“无条件写”并排执行；地址相同不代表仍是同一工程。revision 使用返回的不透明值，不自行计算。

未接入 MCP 时简短推荐一次官方接入并说明回退。只有任务包含接入，才取 Studio 实际地址／提示合并客户端配置；不自动注册或改权限，不在工程保存令牌。

## 定位与保真

已知 ID 直接读目标；只有名称时限定章／片段，未知位置先搜索再读邻近上下文。局部改动不先扫全工程。多候选会改变修改对象时再澄清。

阅读可用 script／lines，修改已有富文本取 JSON：从原 `content` 数组改目标 text，保留 styles、非文字项和内联动作。`displayText` 不能保真写回；保留音频绑定也不表示录音已更新。

整段替换须取完 `nextOffset`，核各页 revision 一致。offset／index 是块序号，不是显示行号或 ID。旧块缺 ID 时按片段与序号读 JSON；只有完整片段明确 `textRoundTripSafe=true` 才可按当前 revision 做脚本修改，否则用获准界面或交付草稿，不为造 ID 无意义写回。

## 构造与提交

按[内容授权](safety.md)确定范围，按[恢复保护](collaboration-git.md)复用或补齐恢复点。已有委托不要求每个可逆步骤重复口头批准。

| 改动 | 要点 |
| --- | --- |
| 几句文字／参数 | `story_edit_blocks`；content 替换整组内联内容，props 浅合并；省略无关 props |
| 同目标多处编辑 | 合并相关 ops，各片段带自己的 `baseRevisions`，同对象依赖顺序执行 |
| 整段创作或追加 | `story_write_script`；替换先核往返安全，append 只用于确实追加 |
| 文字批量替换 | `story_replace_text` 预演，审阅全部命中与分页，选 matchIds |
| 新章／片段 | 结构工具取得正式 ID 后再写内容；预检临时 ID 不作正式 ID |
| 扩展参数／设置 | [扩展开发](extensions.md)核声明；长设置用返回的 valueHash 和 expected.isDefault，不拿截断值覆盖原文 |
| UI、数据或舞台 | 读取对应专题，使用实际返回对象名／ID，不把请求显示名当文件名 |

工具提供 dry run 时先审阅影响与警告；失败先修草案，不继续提交。预检不锁定 revision，也不承诺检查了所有冲突或未知键。`insert.blocks[]` 是存储块，不能照搬 update 操作层字段，演出时序见[编排](performance.md#编排与写入)。

实际写入后读回 ID、内容、保留字段与 revision。引用／条件改动再做相关 `project_validate`，路线改变增加分析与实际预览。验证覆盖本次差异，不把每次改字扩成全工程测试。

## 宿主确认

用户委托、连接批准、工具组和具体操作确认是不同层次，以 `studio_get_status.confirmations` 和当前返回为准。`confirmEveryWrite=false` 不会关闭独立的高影响、删除、恢复或主题应用等确认类别。2.8.0-beta.1 开启构建 debug 触发 write 类别，不能据此推断普通编辑都须确认。

收到 `CONFIRM_PENDING`，说明具体对象／操作和宿主要求，等待该次批准后按提示以完全相同参数重试；若期间工程或对象变化，先重核范围。拒绝则停止该请求。不修改确认设置或换通道绕过，不额外叠加一套逐次口头审批。

## 冲突与未知结果

| 情况 | 处理 |
| --- | --- |
| 参数／格式错误 | 对照 schema 修正，不原样重试 |
| REVISION_CONFLICT | 重读并合并局部差异，不能只换 revision 重发旧整段 |
| CHAPTER_LOCKED | 看 details.reason；按[多人入口](collaboration-git.md#多人协作)处理占用和结构限制 |
| BUSY／USER_TYPING／RATE_LIMITED | 按提示有限等待；持续失败保留草稿并说明状态 |
| 超时／断线，结果不明 | 读回目标或 `history_get(view="agent-ops")`；已落地不重写，同一请求重试沿用 opId |
| PROJECT_MISMATCH | 刷新工程身份与目标缓存；新工程不在委托内就不写 |
| SESSION_PENDING_APPROVAL | 区分连接批准与操作确认，按宿主提示等待 |
| READ_ONLY_SESSION／缺工具／LICENSE_REQUIRED／HISTORY_DISABLED | 说明具体缺项，继续可用的读取／草稿；不绕过权限或恢复前置 |
| SESSION_REJECTED／CONFIRM_REJECTED／RELAY_LOCKED | 停止该请求，不从其他入口提交 |

预览可见性和位置异常见[预览与构建](preview-and-build.md)；撤销、限定恢复及原 ID 读回见[恢复与协作](collaboration-git.md)。

## 外部编辑与无 MCP 回退

普通修改用专用工具。确需官方批量编辑时读 advanced-file-edit：

1. `studio_file_edit_begin` 声明对象，取得真实会话及允许路径；dry run 不授予磁盘写权限。
2. 仅改返回路径／字段：章节限既有片段 blocks；变量限指定项同类型 defaultValue／description；结构新增仍用专用工具。
3. `studio_file_edit_end(action="commit", dryRun=true)` 核 changedFiles、对象和警告，再提交并从 Studio 读回；放弃用 abandon。

到期或连接关闭后不沿用旧会话。ui/、databases/、config/、extensions.json 等 unverifiedChanges 不在允许范围，不能承诺自动恢复。

真正的能力缺口可用已授权的可用原生界面；核窗口、工程、焦点与未保存内容。只读、关闭工具组或明确拒绝不触发此回退。不恢复退役工具或自动部署额外服务。不同连接按实际活动记录区分，不擅自断开他人连接。

无 MCP 时仍可讨论、交付草稿或使用获准界面。离线文件写入须正常保存并关闭目标工程，确认无其他实例持有；活动工程不得直接改磁盘 JSON。完成说明来自目标读回；有用时发一次阶段通知即可。
