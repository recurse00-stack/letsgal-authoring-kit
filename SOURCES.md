# 资料来源与适用范围

2026-11-11 再次核对[正式清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-stable.json)为 3.0.0，[Beta 清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-beta.json)为 2.9.0-beta.1。此处记录查阅日期，不表示清单此后不会变化；实际操作仍核目标实例。

Stable 依据[3.0 更新说明](https://docs.avg-engine.com/updates/3-0-0)、该版宿主返回的 68 项工具 schema、quickstart／剧情／UI／扩展／预览参考，以及官方 init_program 生成的 SDK 3.0.0、llms.txt 和 Studio 组件类型。Beta 依据 2.9 的 67 项 schema、对应参考及 2.8 SDK／宿主资料。完整快照与逐项测试留维护记录，不复制进公共指南。

3.0.0 的 r1／r2 热修复说明来自官方客户端更新日志；本机官方 renderer-patch/current.json 登记 baseVersion=3.0.0、channel=stable、rev=2。更新偏好另为 beta，两者独立。r1 涉及旧 SDK 声明识别；r2 涉及热更新检查及正式版解包，保留旧 SDK 声明兼容。此说明不据此撤销既有三类 MCP 差异，相关运行证据仍按原范围。

## 按任务查询

| 任务 | 官方入口 |
| --- | --- |
| 功能选型 | [功能全景](https://avg-engine.com/studio/features)、[FAQ](https://docs.avg-engine.com/reference/faq) |
| 剧情 | [JSON](https://docs.avg-engine.com/reference/script-json)、[分支](https://docs.avg-engine.com/manual/writing/blocks/branch)、[章节调度](https://docs.avg-engine.com/advanced/chapter-scheduling) |
| 舞台与语言 | [角色](https://docs.avg-engine.com/manual/creating/characters/)、[动态图像](https://docs.avg-engine.com/manual/creating/dynamic-visuals)、[本地化](https://docs.avg-engine.com/manual/writing/localization) |
| 扩展 | [官方 AI 指导](https://docs.avg-engine.com/extensions/llms.txt)、[创建扩展](https://docs.avg-engine.com/extensions/develop/)、目标 SDK 的公开类型与 studio-ui/README.md |
| 连接与构建 | [MCP 接入](https://docs.avg-engine.com/manual/overview/mcp)、[构建](https://docs.avg-engine.com/manual/overview/build) |
| 恢复 | [项目历史](https://docs.avg-engine.com/manual/overview/history)、[时光机](https://docs.avg-engine.com/manual/overview/backup)、[版本管理](https://docs.avg-engine.com/manual/overview/version-control) |
| 版本与旧资料 | [引擎发布历史](https://static-lg-studio.cn-gd.ufileos.com/studio/releases-history.json)、[Skill 发行历史](https://github.com/recurse00-stack/letsgal-authoring-kit/releases) |

功能图和网页按其查阅版本使用，不能代替目标工具契约。参考之间冲突时，工具参数查当前 schema，扩展方法查目标 SDK 类型，实际行为按同版本最小调用核实。例如 3.0 not-exposed 的跨系统构建限制与当前 supportedSystems／dry-run 不同，采用后者说明本机规划能力；这不等于目标产物运行已验。名称翻译及旧 branch 的跨章规则也分别对照当前接口，不外推到其他调用或 Beta。

设置 reset、调度撤销及官方文件编辑的差异依据 2026-11-10 原始 MCP 返回和最小样本；区分契约、静态类型和观测，见[宿主范围](HOST-VALIDATION.md)。只有承诺支持的行为与实测不一致才归为缺陷。数据删除不支持普通撤销、未声明字段以及正常预览渲染边界分别按能力限制处理。

Agent 目录来源和历史 provider 范围见[兼容说明](COMPATIBILITY.md)。公共示例使用合成内容，不含私人作品、个人偏好、插件私有指南、SDK 副本、账号或实际连接令牌。
