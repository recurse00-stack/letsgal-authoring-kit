# 编写依据与证据范围

2026-10-01本轮只读刷新：[Beta清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-beta.json)的Windows项仍为2.3.0-beta.1，[Stable清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-stable.json)仍为2.0.0。没有下载引擎或重验发布历史；历史2.0.1记录保留原核对日期。首轮官方初始化SDK的来源及有限history接口实测已有证据，见[宿主记录](HOST-VALIDATION.md)；其他SDK／其他项目仍独立核对，不沿用早期全部UNKNOWN的检查点。

2026-09-30 0.1.4补充：将Windows 2.3.0-beta.1的五个原生调用用例整理为[宿主证据](HOST-VALIDATION.md)，区分官方文档声明、编辑器提示、OP与播放。非循环main调用已有限验证；一般循环算法、深度上限、Stable及导出仍未据此确认。复核前处理索引、安装预览和人类案例，当前验收见VALIDATION，不把旧数量累计为本次全面通过。

2026-10-01累计补齐：重新读取三份官方JSON清单／历史，独立整理正式版到2.1／2.2／2.3的38个公告顶层条目及验证要求，见[累计差异](skills/letsgal-authoring/references/versions/beta-differences.md)。Stable清单仍2.0.0，历史另有2.0.1；不把下载清单与发布历史混为最新宿主。原始响应与SHA只保存在本机维护凭证，不进入公共包。官网文档只更新正式版的范围来自用户2026-10-01转述官方答复，未取得原文、官方链接及答复日期；不伪造外部来源。公告之外的有限实测与待验证推断分别标记，未新增宿主验收。

2026-09-30 全面修订：重新核对现有 20 个 Skill 文件、官方 JSON／调用片段／调度、变量、扩展开发／SDK 要求、存档、资源／数据库／原生能力及 Agent 目录入口；具体纠正与未覆盖项见 [AUDIT.md](AUDIT.md)。官方资料不完全同步，main 调用和静态展开按争议记录。扩展指导关于本地 SDK 配套的概述不能替代实际同步来源证明。当前脚本／安装实测见 VALIDATION，旧数量不累计为当前完整验收。

2026-09-30 历史补充：读取官方 [Beta 清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-beta.json)确认 Windows 2.3.0-beta.1，并与[发布历史](https://static-lg-studio.cn-gd.ufileos.com/studio/releases-history.json)交叉核对。Stable 清单仍为 2.0.0，发布历史已有 2.0.1，不据此统一宣称“最新”。基于公告独立整理 [Beta 使用说明](skills/letsgal-authoring/references/versions/beta-2.3.md)，没有复制引擎或 SDK。新历史追加签名、行内超链接和部位序列化需实际 SDK／样本，本轮保持 UNKNOWN；当前官方 JSON 与历史 API 页不能替代目标 Beta 类型。双宿主运行仍未完成。

历史版本依据：2026-09-26 复核时，[Stable 清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-stable.json) 指向 2.0.0，Beta 基线为 2.2.0-beta.1。这不是对当前最新版本的声明。社区技能包本身不依赖 SDK 构建；创作时仍按目标工程的版本证据查阅资料，完整宿主运行仍需另行验证。

本包独立编写，未复制用户的私有技能、游戏正文、账号或本地索引。以下链接于 2026-09-23 用网页检索／正文读取核对；公开文档更新不齐，不把页面抓取成功当作某一宿主版本已验收。

- [剧本 JSON](https://docs.avg-engine.com/reference/script-json)：磁盘结构、序列化参数及片段引用。
- [分支](https://docs.avg-engine.com/manual/writing/blocks/branch)：玩家选项与返回语义。
- [章节调度](https://docs.avg-engine.com/advanced/chapter-scheduling)：基础／蓝图与跨章节流程。
- [官方更新日志](https://avg-engine.com/changelog)：完整版本与通道的检索入口，不将当前网页认定为所有历史版本规范。2026-09-23 复核章节调度页明确将蓝图标为 v2.0.0 新增；以该事实阻止对旧版工程默认启用蓝图。
- [扩展 AI 指导](https://docs.avg-engine.com/extensions/llms.txt)、[创建扩展](https://docs.avg-engine.com/extensions/develop/)：源码、SDK、构建和接口查询。
- [实时协作](https://docs.avg-engine.com/manual/overview/collaboration)：编辑权及冲突覆盖。
- [时光机](https://docs.avg-engine.com/manual/overview/backup)：备份、恢复影响。
- [Git status](https://git-scm.com/docs/git-status)、[worktree](https://git-scm.com/docs/git-worktree)、[restore](https://git-scm.com/docs/git-restore)：工作区、隔离与恢复操作。
- [Codex Skills](https://learn.chatgpt.com/docs/build-skills)、[Claude Code Skills](https://code.claude.com/docs/en/skills)、[Cursor Skills](https://cursor.com/docs/skills)、[Copilot Skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)：当前技能目录规范。
- [DSH 文件系统技能提供器](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md)、[实现](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/src/index.ts)、[数据目录解析](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/util/home-paths/src/index.ts)：个人／项目发现路径、最近 Git 根、DSH_HOME 与正文读取。另对安装版本 0.1.6-alpha.2 所带官方 provider 做了隔离调用，不把上游 master 文档当成已发布版本保证。

查阅中的限制：文档根 llms.txt 曾返回 404；部分版本管理、变量、赋值和导出页面正文抓取失败。因此不把这些失败页当成已核查正文，也不以失败证明产品缺少对应功能。所需字段回到成功读取的官方 JSON 参考和目标工程核对。

2026-09-25 复核：剧本 JSON 页明确允许旧分支缺省 mode 按 jump 兼容；检查器 auto 因此保留旧数据，显式 fragments 模式继续采用新建约定。重新检查了扩展创建和章节调度入口；未将这些页面核对替代真实宿主运行。

安全默认、Git 协作建议、个人／项目配置分层、安装器和测试为本包设计，并非官方对所有用户的强制工作流。JSON 示例使用原创文本与独立 ID，仅为格式教学；附带检查器覆盖有限字段，不是官方 schema。
