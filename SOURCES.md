# 编写依据与证据范围

本包独立编写，未复制用户的私有技能、游戏正文、账号或本地索引。以下链接于 2026-09-23 用网页检索／正文读取核对；公开文档更新不齐，不把页面抓取成功当作某一宿主版本已验收。

- [剧本 JSON](https://docs.avg-engine.com/reference/script-json)：磁盘结构、序列化参数及片段引用。
- [分支](https://docs.avg-engine.com/manual/writing/blocks/branch)：玩家选项与返回语义。
- [章节调度](https://docs.avg-engine.com/advanced/chapter-scheduling)：基础／蓝图与跨章节流程。
- [官方更新日志](https://avg-engine.com/changelog)：完整版本与通道的检索入口，不将当前网页认定为所有历史版本规范。2026-09-23 复核章节调度页明确将蓝图标为 v2.0.0 新增；以该事实阻止对旧版工程默认启用蓝图。
- [扩展 AI 指导](https://docs.avg-engine.com/extensions/llms.txt)、[创建扩展](https://docs.avg-engine.com/extensions/develop/)：源码、SDK、构建和接口查询。
- [实时协作](https://docs.avg-engine.com/manual/overview/collaboration)：编辑权及冲突覆盖。
- [时光机](https://docs.avg-engine.com/manual/overview/backup)：备份、恢复影响。
- [工坊](https://docs.avg-engine.com/manual/overview/extension-market/)：引擎扩展投稿和完整审核包；未证明纯技能包可被审核接受。
- [Git status](https://git-scm.com/docs/git-status)、[worktree](https://git-scm.com/docs/git-worktree)、[restore](https://git-scm.com/docs/git-restore)：工作区、隔离与恢复操作。
- [Codex Skills](https://learn.chatgpt.com/docs/build-skills)、[Claude Code Skills](https://code.claude.com/docs/en/skills)、[Cursor Skills](https://cursor.com/docs/skills)、[Copilot Skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)：当前技能目录规范。
- [DSH 文件系统技能提供器](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md)、[实现](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/src/index.ts)、[数据目录解析](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/util/home-paths/src/index.ts)：个人／项目发现路径、最近 Git 根、DSH_HOME 与正文读取。另对安装版本 0.1.6-alpha.2 所带官方 provider 做了隔离调用，不把上游 master 文档当成已发布版本保证。

查阅中的限制：文档根 llms.txt 曾返回 404；部分版本管理、变量、赋值和导出页面正文抓取失败。因此不把这些失败页当成已核查正文，也不以失败证明产品缺少对应功能。所需字段回到成功读取的官方 JSON 参考和目标工程核对。

2026-09-25 复核：剧本 JSON 页明确允许旧分支缺省 mode 按 jump 兼容；检查器 auto 因此保留旧数据，显式 fragments 模式继续采用新建约定。重新检查了扩展创建和章节调度入口；未将这些页面核对替代真实宿主运行。

安全默认、Git 协作建议、个人／项目配置分层、安装器和测试为本包设计，并非官方对所有用户的强制工作流。JSON 示例使用原创文本与独立 ID，仅为格式教学；附带检查器覆盖有限字段，不是官方 schema。
