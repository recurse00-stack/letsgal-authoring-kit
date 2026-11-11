# 资料与证据索引 · Beta 2.9 / 2.8

此路径供版本检查脚本返回。按[任务入口](../SKILL.md#按当前任务读取)选择专题；查询未列能力使用[官方选型入口](research.md#先确认能力再选择做法)。

| 任务 | 需要注意的版本条件 | 详情 |
| --- | --- | --- |
| 剧情 | 2.9 新建嵌套菜单／条件，旧 branch／if 定向维护 | [剧情](story-and-voice.md#剧情变量与流程)、[JSON](json.md#引用与控制流) |
| 多窗口 | 端点与工程 ID 配对，切换后刷新 | [MCP](mcp-workflow.md#连接与目标) |
| 演出 | 配置后在剧情启用；粒子准备贴图；循环明确停止 | [舞台](stage-and-assets.md)、[演出段](performance.md) |
| 桌面构建 | 按当前 supportedSystems 选择目标 | [构建](preview-and-build.md#构建与导出) |
| Steam | 2.9 按连接、结果和恢复状态处理 | [Steam](extensions.md#steam-接入29) |
| 撤销／空提交 | 核正文、原 ID 和完整调度；有差异按目标恢复 | [MCP](mcp-workflow.md)、[恢复](collaboration-git.md)、[数据表](ui-and-data.md#数据表的编辑与运行) |
| 未声明 props | 无任意键往返承诺，使用受支持的数据位置 | [格式兼容](json.md#序列化与保真) |
| 素材占用 | 2.9 出现隔离目录 EPERM 及原 GIF/WebP 占用，记录后延期处理 | [舞台](stage-and-assets.md#素材落点与引用)、[精确清理](asset-cleanup.md) |

2.8 的扩展参数校验缺口、识别 BUSY 及高级调度定位条件，分别保留在[扩展](extensions.md#参数与校验)、[声音](story-and-voice.md#本地化与语音识别)、[预览](preview-and-build.md#预览范围)的版本段落。新版本复测受影响路径后更新这些条件。完整实测证据随发行验证说明维护。
