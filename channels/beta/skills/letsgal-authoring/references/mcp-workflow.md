# Studio 工程的 MCP 执行

本页处理工程读写；字段按任务查[专题](../SKILL.md#按当前任务读取)。扩展源码、Skill 和发行文件使用所属工程的维护流程。

## 连接与目标

首次调用 `studio_get_status`，核完整版本、project.id、权限／工具组、保存／输入及协作状态；读取服务 instructions 和 quickstart，资源不可用时用 `studio_get_reference(topic="quickstart")`。同时完成[静默版本检查](version-compatibility.md#低频静默开工检查)；不匹配或热修复未知时先暂停目标执行并按该页取得本次许可。后续复用有效身份和检查结果，参数以当前 schema 为准。

2.9 多窗口记录“当前端点 → project.id”对应关系。切换工程、重连、冲突、等待确认或长操作后刷新相关状态，再决定写入；以读取确认归属。revision 使用宿主返回的不透明值。

工具缺席或调用掉线时进入[连接恢复](troubleshooting.md#工具消失或断连)，验证成功即继续。尚未配置时可推荐官方接入；任务包含接入才从目标窗口取得实际地址并合并客户端配置，令牌保留在客户端安全配置中。

## 定位与保真

已知 ID 直接读目标；只有名称就限定章／片段搜索，再读邻近上下文。对象仍有关键歧义时集中澄清。

阅读可用 script／lines；修改富文本取 JSON，在原 `content` 数组内改目标 text，保留 styles、非文字项、内联动作和音频绑定。改词后按需重新录音。

整段替换须读完 `nextOffset`，核各页 revision 一致。offset／index 是块序号。旧块缺 ID 时按片段与序号取 JSON；完整片段标为 `textRoundTripSafe=true` 才使用脚本替换，否则选择获准界面或交付草稿。额外属性按 [JSON 保真规则](json.md#序列化与保真)处理。

## 构造与提交

按可审查批次复用有效恢复点；素材另核备份覆盖，限定恢复见[恢复专题](collaboration-git.md)。

| 改动 | 做法 |
| --- | --- |
| 几句文字／参数 | `story_edit_blocks`；content 提交完整内联数组，props 仅提交目标键并浅合并 |
| 同目标多处编辑 | 合并相关 ops，各片段携带自己的 baseRevisions；依赖操作按顺序执行 |
| 整段创作／追加 | `story_write_script`；替换先核往返安全，追加使用 append |
| 批量替词 | `story_replace_text` 预演，读完命中分页，审阅并选择 matchIds |
| 新章／片段 | 结构工具创建后取得正式 ID，再写内容 |
| 扩展设置 | 按[声明](extensions.md)写入；长值用 valueHash 与 expected.isDefault 做冲突检查 |
| UI／数据／舞台 | 按对应专题操作，使用返回的对象名及 ID |

工具提供 dry run 时先看影响和 warnings，修正草案后提交；真实写入继续携带最新 revision。演出 insert／update 的字段位置见[编排](performance.md#编排与写入)。

写后读回 ID、目标内容、非目标字段和 revision。引用／条件变化增加相关 `project_validate`；路线、动画或交互变化按专题运行验证。

## 宿主确认

以 `studio_get_status.confirmations` 及返回类别处理确认。`confirmEveryWrite=false` 时，高影响修改、删除、恢复和主题应用仍可独立要求批准；2.8 开启构建 debug 曾触发 write 类别。

`CONFIRM_PENDING`：说明具体对象和操作，等宿主批准后按提示以相同参数重试；期间目标变化则先重核。拒绝即停止该请求。已有委托继续有效，普通步骤无需额外口头审批。

## 冲突与未知结果

| 返回／现象 | 下一步 |
| --- | --- |
| 参数／格式错误 | 对照 schema 修正草案 |
| REVISION_CONFLICT | 重读并合并局部差异，使用新 revision |
| CHAPTER_LOCKED | 读 details.reason，按[协作范围](collaboration-git.md#多人协作)处理 |
| BUSY／USER_TYPING／RATE_LIMITED | 按提示有限等待；持续失败保留草稿并报告 |
| 超时／断线，写入结果不明 | 读回目标或 `history_get(view="agent-ops")`；已落地就继续，可重试的同一请求沿用 opId |
| PROJECT_MISMATCH | 刷新工程身份及缓存，只写委托内的目标 |
| SESSION_PENDING_APPROVAL | 等连接批准；具体写入再按操作确认处理 |
| 工具缺席／掉线 | 执行[有限恢复](troubleshooting.md#工具消失或断连) |
| 撤销／删除 INTERNAL、EPERM、EBUSY | 读回部分完成结果，按[精确清理](asset-cleanup.md#撤销删除失败与文件占用)处理剩余项 |
| READ_ONLY_SESSION／LICENSE_REQUIRED／HISTORY_DISABLED | 说明所需权限或恢复条件，继续可用读取／草稿 |
| SESSION_REJECTED／CONFIRM_REJECTED／RELAY_LOCKED | 停止该请求，保留原状态 |

## 外部编辑与无 MCP 回退

普通修改优先专用 MCP。确需官方文件会话时先读当前 advanced-file-edit：

1. `studio_file_edit_begin` 声明对象，取得真实会话、有效期及允许路径。保存拟修改前的原文；会话过期、断连或权限变化后重新核状态。
2. 章节只改既有片段 blocks；变量只改指定项同类型 defaultValue／description。结构新增用专用工具；ui／databases／config／extensions 等 unverifiedChanges 不作为可直接提交范围。
3. 写入后立即读实际文件，再执行 `studio_file_edit_end(action="commit", dryRun=true)`，比较预期差异、changedFiles、fragments 和警告。预期有修改却返回空变更、文件回到原文或差异不符时，**停止 commit**，在会话外保留拟写内容，核会话／有效期／保存与编辑状态。
4. 差异符合范围才 commit，再从 Studio 读回正文、ID 和非目标字段。无变化返回成功只表示没有提交变更；写入结果未知先读回，不能反复覆盖文件。需换专用接口时先安全 abandon 并核状态，重新读取对象和 revision，再在已有授权范围内定向写入；只读或拒绝不能绕过。

**2.9 历史现场**：曾出现预期改动没有进入 changedFiles／fragments 的空提交。按当前文件、会话和返回确认实际结果；不把其他宿主的复现细节直接当作本版本原因。

界面操作使用当前任务明确许可。连接故障先走恢复流程；只读、关闭工具组或明确拒绝须保持。获准操作时核窗口、工程、焦点与未保存内容，保留他人连接。

无 MCP 可继续分析与草稿。离线写 JSON 前正常保存关闭目标工程，并核其他实例已释放；活动工程通过官方写入入口修改。阶段完成按需要通知一次。
