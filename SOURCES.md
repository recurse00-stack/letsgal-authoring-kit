# 资料来源与范围

本指南依据官方资料、目标样本与注明版本的有限观察独立编写。2026-10-10读取[正式版清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-stable.json)和[Beta清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-beta.json)，当前维护目标分别为2.5.0和2.6.0-beta.1。清单不证明本机安装或运行验收；本修订没有新增宿主和模型测试。

## 按任务查阅

- 剧情：[JSON参考](https://docs.avg-engine.com/reference/script-json)、[分支](https://docs.avg-engine.com/manual/writing/blocks/branch)、[If](https://docs.avg-engine.com/manual/writing/blocks/if/)、[调用片段](https://docs.avg-engine.com/manual/writing/blocks/call-fragment)、[章节调度](https://docs.avg-engine.com/advanced/chapter-scheduling)。main文字冲突保留，不能依单页改掉既有内容。
- 本次补齐：[2.5功能说明](https://docs.avg-engine.com/updates/2-5-0)中的超链接三种动作，以及[场景管理](https://docs.avg-engine.com/manual/creating/scenes/)中的背景合成／分别创建，2026-10-10查阅；仅为资料依据，未新增功能实测。
- 演出：[角色](https://docs.avg-engine.com/manual/creating/characters/)、[对白](https://docs.avg-engine.com/manual/writing/blocks/dialogue/)、[动态图像](https://docs.avg-engine.com/manual/creating/dynamic-visuals)、[浮字](https://docs.avg-engine.com/manual/writing/blocks/floating-text)、[本地化](https://docs.avg-engine.com/manual/writing/localization)。
- 预览与发布：[编辑器](https://docs.avg-engine.com/manual/overview/editor)、[构建](https://docs.avg-engine.com/manual/overview/build)、[游戏统计](https://docs.avg-engine.com/manual/overview/game-stats)。网页基础描述、版本公告、目标保存形式与运行分别判断。
- 恢复：[项目历史](https://docs.avg-engine.com/manual/overview/history)、[时光机](https://docs.avg-engine.com/manual/overview/backup)、[版本管理](https://docs.avg-engine.com/manual/overview/version-control)、[协作](https://docs.avg-engine.com/manual/overview/collaboration)。恢复覆盖不扩大修改授权；原生Git与同步上传不是同一动作。
- 扩展：[官方AI指导](https://docs.avg-engine.com/extensions/llms.txt)、[创建扩展](https://docs.avg-engine.com/extensions/develop/)。实际接口以当前工程SDK及来源为准，不将声明等同运行通过。
- MCP：[官方接入](https://docs.avg-engine.com/manual/overview/mcp)及当前服务instructions、quickstart、script/syntax、advanced/file-edit、guide/errors、guide/preview-testing；首次读取，工程／重连／版本／冲突变化时刷新。2026-10-08／09曾读取2.6.0-beta.1指导并做有限隔离测试，本修订不把它扩大为全部功能验收。
- 版本：[更新日志](https://avg-engine.com/changelog)、[发布历史](https://static-lg-studio.cn-gd.ufileos.com/studio/releases-history.json)。以目标完整版本辨别，不累加公告条数作为能力或通过数量。

## 设计与使用证据

按需上下文与工具边界参考[OpenAI Skill设计](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)、[Anthropic工具设计与评估](https://www.anthropic.com/engineering/writing-tools-for-agents)；客户端工具搜索参考[官方说明](https://developers.openai.com/api/docs/guides/tools-tool-search)，创作者反馈参考[Wordcraft研究](https://magenta.withgoogle.com/wordcraft-writers-workshop)。这些是设计依据，不将其他产品的效果数字视作本项目收益。

2026-10-05的2.5.0有限宿主记录、2026-10-08／09的MCP与模型记录继续按原范围引用；更早Beta资料与累积过程已从当前载荷移出。历史原文保留在维护归档和[已发布版本](https://github.com/recurse00-stack/letsgal-authoring-kit/releases/tag/v0.2.1)，实际范围见[验证摘要](VALIDATION.md)。官方网页主要维护正式版；Beta公告不能替代完整schema，旧版实测不转换为新版通过。

Agent目录来源见[兼容表](COMPATIBILITY.md)，未在本修订重复验证所有客户端。公共示例不含私人作品、SDK副本、账号、实际本机地址；原始日志与含私人界面的截图不随包公开。安全默认、范围授权、至少一种恢复保护和有限检查器是本Skill的工作约定，不宣称为官方强制流程。
