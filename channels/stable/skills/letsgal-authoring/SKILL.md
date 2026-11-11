---
name: letsgal-authoring
description: 制作和修改 LetsGal Studio 的剧情、分支、演出、UI 与扩展，处理工程格式及运行排错；一般创作讨论不自动写入工程。
metadata:
  version: 3.0.0
  channel: stable
  revision: 20261111-series300
---

# LetsGal Studio 创作

适用 **3.0 系列正式版**。2.9／2.8 工程选 Beta 载荷；2.5 资料从[历史发行](https://github.com/recurse00-stack/letsgal-authoring-kit/releases)取得。优先官方 MCP；连接异常按[恢复流程](references/troubleshooting.md#工具消失或断连)处理，界面托底须有当前任务的明确许可。

## 按当前任务读取

本会话首次执行工程或扩展操作前，先检查实际 AI 用户主目录的 `~/.letsgal-authoring/preferences/user.md`；存在就读取并应用与当前任务相关的约定，不能只读主 Skill 后跳过。已读且仍有效的信息可复用；用户告知偏好更新或相关上下文缺失时重读。旧路径兼容、缺失与冲突处理见[个人定制](references/customization.md)。

涉及已有插件的使用或维护时，先按[插件知识](references/plugin-skills.md)核对 ID／版本并读取用户区对应指南；不必等用户再次点名子包，也不因它未单独列在 Agent 技能列表中而跳过。

讨论使用已有创作上下文；操作工程时读项目规则、简短当前状态及目标原文。只读取下表中与任务相关的专题或章节，复用仍有效的上下文。

| 当前任务 | 入口 |
| --- | --- |
| 查询能力、选择实现方式 | [选型](references/research.md#先确认能力再选择做法) |
| 讨论、改写、整合反馈 | [创作协作](references/production.md) |
| 工程读写、批量编辑 | [MCP 执行](references/mcp-workflow.md)；字段问题查 [JSON](references/json.md) |
| 分支、变量、语言、配音 | [剧情与配音](references/story-and-voice.md) |
| 立绘、口型、镜头、媒体 | [舞台与素材](references/stage-and-assets.md) |
| 演出时间轴、后台循环 | [演出段](references/performance.md) |
| UI、主题、数据表 | [UI 与数据](references/ui-and-data.md) |
| 预览、调试、导出 | [预览与构建](references/preview-and-build.md) |
| 扩展开发／使用插件 | [扩展](references/extensions.md)／[插件知识](references/plugin-skills.md) |
| 撤销、恢复、多人范围 | [恢复与协作](references/collaboration-git.md) |
| 临时文件、删除占用 | [精确清理](references/asset-cleanup.md) |

工程操作开始前执行一次[低频静默版本检查](references/version-compatibility.md#低频静默开工检查)，比较宿主主次版本与实际 Stable／Beta 身份，同系列补丁及热修复不单独触发确认；同一有效实例／任务复用结果。正常匹配不提示、不反复联网。不匹配先暂停目标执行，只在当前使用者明确同意本次例外后继续；纯讨论不触发。附加包按启用状态加载，暂停项保持暂停。

设置重置前读[默认态与恢复](references/extensions.md#设置存档与资源)；调度修改前读[完整调度恢复](references/collaboration-git.md#限定恢复与读回)；官方文件会话写入前读[空差异处理](references/mcp-workflow.md#外部编辑与无-mcp-回退)。

## 修改与交付

- 按授权范围修改。保留已有／已采用内容和后来编辑；本次受托草稿可连续迭代，部分采用只整合相应部分。
- 写前备有覆盖改动的恢复点；写后读回目标。保留稳定 ID、富文本及非目标字段，按改动验证相关行为。格式兼容见 [JSON](references/json.md#序列化与保真)。
- 遵守宿主确认、只读及拒绝。独有内容删除、不可逆覆盖和外部发布按具体授权执行；需要判断范围时查[安全边界](references/safety.md)。

交付结果、必要验证和未决项。作品决定归工程，偏好及插件知识归用户区；主 Skill 自身使用主包安装入口。
