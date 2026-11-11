# 资料与证据索引 · Stable 3.0

此路径供版本检查脚本返回。按[任务入口](../SKILL.md#按当前任务读取)选择专题；查询未列能力使用[官方选型入口](research.md#先确认能力再选择做法)。

| 任务 | 需要注意的版本条件 | 详情 |
| --- | --- | --- |
| 剧情 | 新建嵌套菜单／条件；旧 branch 可跨章调用唯一启用片段，旧 if／普通 call 仍限同章 | [剧情](story-and-voice.md#剧情变量与流程)、[JSON](json.md#引用与控制流) |
| 多窗口 | 端点与工程 ID 配对；studio_open_project 会切换本窗口，独立窗口另行初始化 | [MCP](mcp-workflow.md#连接与目标) |
| 演出 | 配置后在剧情启用；粒子准备贴图；循环明确停止 | [舞台](stage-and-assets.md)、[演出段](performance.md) |
| 桌面构建 | 按当前 supportedSystems 选择目标 | [构建](preview-and-build.md#构建与导出) |
| Steam | 按连接、结果和恢复状态处理 | [Steam](extensions.md#steam-接入) |
| 设置 reset | 写前保存值与默认态，写后逐项读回，区分缺值与默认态 | [设置](extensions.md#设置存档与资源) |
| 调度撤销 | 核模式、策略、完整图和入口数，数量恢复不等于完整恢复 | [恢复](collaboration-git.md#限定恢复与读回) |
| 文件会话 | 预期有改动却 dry-run 空变更时停止 commit | [文件编辑](mcp-workflow.md#外部编辑与无-mcp-回退) |
| 删除恢复 | project_delete 不支持普通 undo；按数据历史／素材隔离区恢复 | [数据表](ui-and-data.md#数据表的编辑与运行)、[精确清理](asset-cleanup.md) |
| 未声明字段 | 不假定任意键都能往返，这属于格式契约边界 | [格式兼容](json.md#序列化与保真) |

2.8 的扩展参数校验缺口、识别 BUSY 及高级调度定位条件，分别保留在[扩展](extensions.md#参数与校验)、[声音](story-and-voice.md#本地化与语音识别)、[预览](preview-and-build.md#预览范围)的版本段落。3.0 不直接继承这些运行结论；按受影响路径的实际结果处理。完整实测证据随发行验证说明维护。
