# 局部编辑、占用与恢复

先读当前服务 instructions／quickstart，需要时用 `studio_get_reference` 查询 errors、not-exposed 和相关对象合同。下面只补多人环境中的决策。

## 在最新内容上修改

用实际章节／片段 ID 读 JSON、revision 和邻近内容；整段读取跟随 nextOffset 并核各页版本一致。富文本从原 content 数组改 text，保留 styles、非文字项、ID、未知字段和非目标参数。

有覆盖本批变化的恢复点后，构造最小 ops，为每个片段带实际 baseRevisions 和可追踪 opId。先 dryRun 审阅范围，再实际提交并读回。**预检不锁定内容，也不保证已检查 revision 冲突**：2.8.0-beta.1 已观察到旧 revision 预检成功、实际提交拒绝。

等待确认、长操作或切换窗口后重新核工程身份，再条件执行写入；不将读取状态与无条件写入排在一起。用户批准当前任务不代表宿主关闭了所有确认类别；按具体 CONFIRM_PENDING 等待该操作确认，不增加逐句口头批准，也不修改宿主设置。

## 遇到变化

| 返回情况 | 处理 |
| --- | --- |
| REVISION_CONFLICT | 读最新内容，重新应用自己的局部差异；不能只换 revision 重发旧整段。影响重要内容时再询问取舍 |
| CHAPTER_LOCKED / BLOCK_CLAIMED | 核 details.reason、details.blocks；等占用结束或转到其他已获准对象，不抢占 |
| CHAPTER_LOCKED / ALIGNING | 有限等待并重读状态与目标版本，不强制解锁 |
| COLLABORATION_STRUCTURE / COLLABORATION | 按具体操作判断；已验证自有章新增片段可行，而外部文件编辑和历史恢复预检受限。不能概括为全部结构不可改，也不换磁盘／UI 绕过拒绝 |
| 超时或连接中断 | 读目标和 history_get(view="agent-ops") 核自己的 opId 是否落地；同请求重试保留 opId，避免重复插入 |
| PROJECT_MISMATCH | 刷新工程和目标；新工程不在委托内就停止写入 |
| 拒绝、只读或工具组关闭 | 停止依赖该权限的操作，继续允许的读取／草稿，不改入口绕过 |

## 只恢复自己的差异

保留改前原文与 opId。`history_undo` 先 dryRun 核目标，再在范围仍成立时撤销并读回原 ID、字段及引用。返回的新 opId 是撤销动作本身，undone 指向被撤销操作。

UNDO_CONFLICT 或撤销未恢复时，重读现状再判断能否局部向前修复；他人已接续的内容不能整段还原。新 ID 重建不等于恢复旧身份。数据行撤销异常属于通用对象恢复缺口，不能仅因发生在房间中归为协作限制。

检查点覆盖工程不授权整工程回退。不能用共享 Ctrl+Z、整工程历史恢复、直接覆盖 JSON 或关闭协作来修复一行；原生工具拒绝的恢复不要另找入口重放。
