# 资料来源与适用范围

2026-11-12 再次核对[正式清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-stable.json)为 3.0.0，[Beta 清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-beta.json)为 2.9.0-beta.1。清单会随发行更新，实际操作以目标实例的身份核对为准。

Stable 依据[3.0 更新说明](https://docs.avg-engine.com/updates/3-0-0)、该版宿主返回的 68 项工具 schema、quickstart／剧情／UI／扩展／预览参考，以及官方 init_program 生成的 SDK 3.0.0、llms.txt 和 Studio 组件类型。Beta 依据 2.9 的 67 项 schema、对应参考及 2.8 SDK／宿主资料。各项运行覆盖见[宿主验证范围](HOST-VALIDATION.md)。

3.0.0 r1–r5 依据官方[引擎发布历史](https://static-lg-studio.cn-gd.ufileos.com/studio/releases-history.json)及客户端同版更新日志。r3、r4 发布于 2026-11-11，r5 发布于北京时间 2026-11-12；本轮宿主安装标识为 3.0.0-stable-r5。r1／r2 的旧 SDK 声明兼容、更新检查与解包修复保留为历史依据。

r3 的自定义站位与 MCP 设置／调度／文件会话调整，结合本机当前生成参考和定向复测更新指导；r4 的剧本卡顿修复、r5 的长章节优化、声音波形、列表与扩展添加修复按官方公告说明。具体运行覆盖见[宿主验证范围](HOST-VALIDATION.md)。热修复编号用于定位这些变化；[日常版本检查](docs/wiki/02-connection.md)仍按系列和实际发行身份进行。

预览窗口说明依据 2026-11-12 的 3.0.0-r5 宿主 `quickstart`、`guide-preview-testing` 和本项目同日 MCP 补充实测。窗口可见性结论按[对应验证范围](HOST-VALIDATION.md#300-r5预览窗口)使用。

2026-11-13 的历史问题复测沿用同一 stable-r5，补充设置／撤销、文件会话、GIF／WebP 与扩展参数证据。参数规则对照目标 SDK 3.0.0、ext_read(methods) 和[官方方法文档](https://docs.avg-engine.com/extensions/method)；not-exposed 的构建／名称翻译描述另与当前工具返回核对。具体分类见 [Wiki](docs/wiki/07-recovery.md#参数校验的自测范围)。

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

## 资料有差异时怎样查证

- 工具名称与参数查当前 MCP schema；扩展方法与编辑组件查目标 SDK 的公开类型。
- 行为差异用对应版本的最小输入与返回核对。构建平台尤其应查询当前 `supportedSystems` 与工具链，随后验证实际产物。
- 公开示例使用合成内容；Agent 目录依据与适用环境见[兼容说明](COMPATIBILITY.md)，自测观察见 [Wiki](docs/wiki/07-recovery.md#本项目自测问题历史)。

## Wiki 工作台组织

2026-11-11 查阅 [GitBook 的分区与版本组织](https://gitbook.com/docs/guides/editing-and-publishing-documentation/complete-guide-to-publishing-docs-gitbook)和 [Mintlify 的文档搜索说明](https://www.mintlify.com/blog/launch-week-3-day-2)，采用分区导航、正文目录和搜索结果直达的组织方式。工作台页面、离线搜索和本地资料协议由本项目实现，不依赖这些服务的托管或账号。
