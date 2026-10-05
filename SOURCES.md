# 资料来源与查阅范围

本包依据官方资料、目标版本样本和有限实测独立编写。0.2.0于2026-10-05核对2.5.0正式版清单与31条汇总，重读编辑器、JSON、调用片段、扩展开发及相关操作页面；配套SDK来自该版Studio原生初始化，29接口文件与安装资源逐项一致。实际模型、调试、Windows／本地Web、有限Windows存档、预览继承与六类剧本导出分别记录。旧Beta68条公告与历史页面保留原归属，不保证网页此后保持原样，也不宣称完整schema或全部API已通过。

## 版本与证据日期

| 日期／归属 | 取得的资料或事实 | 边界 |
| --- | --- | --- |
| 2026-09-23／25 初稿 | 官方章节 JSON、分支、调度、扩展、协作、恢复及 Agent 目录资料；旧分支缺省 mode 的 jump 兼容 | 页面读取不代表所有历史宿主通过 |
| 2026-09-30 全面复核 | 调用片段／JSON 的 main 与静态展开冲突；变量、扩展、SDK、存档、资源与 Agent 路径 | 保留页面冲突，不以单页批量纠正数据 |
| 2026-09-30 0.1.4 | 实际 Windows 2.3.0-beta.1 五个 main／循环用例 | 一般循环算法、深度和 Stable 仍未知 |
| 2026-10-01 0.1.5 | 三份官方 JSON 清单／发布历史，正式基线到三个 Beta 共 38 项公告；后续只读刷新仍为 Windows Beta 2.3.0-beta.1、Stable 清单 2.0.0，历史另列 2.0.1 | 下载清单与历史不混成统一“最新”，不替代目标实际 EXE |
| 2026-10-01 0.1.5 | 该版 Studio 官方向导初始化 SDK 及有限 history API 运行；原生编辑、两个导出玩家和桌面读档 | 只覆盖记录中的接口／样本，其他项目 SDK 单独查证 |
| 2026-10-02／0.1.7 | Beta清单与历史列2.4.0-beta.1，新增13项公告；Stable清单仍2.0.0；角色、对白及扩展页读取 | 网页未提供完整2.4参数规范；版本相关字段按目标保存样本／SDK补证 |
| 2026-10-02／0.1.8 | Beta清单与历史列2.4.0-beta.2，1项优化和4项修复；Stable清单仍2.0.0 | 仅取得公告，无beta.2宿主、SDK接口或新增JSON字段实测 |
| 2026-10-04／0.1.9 | Beta清单与历史列2.5.0-beta.1，8项新增／优化和4项修复；Stable清单仍2.0.0 | 公告一致、EXE与随包SDK声明核对；新增功能／SDK接口／玩家／保存／导出未测 |
| 2026-10-04／0.1.9 | 重读浮动文字、动态图像、角色与构建手册 | 页面作基础检索；完整Beta字段、运营统计参数和运行结果UNKNOWN |

原始响应、哈希、工具输出和含私人界面的截图留在维护凭证，公共包只带脱敏摘要。版本早期“新历史 API UNKNOWN”是当时状态；后续探针的已确认范围见 [宿主记录](HOST-VALIDATION.md)，不能将已取得探针来源扩展到所有 API。

## 官方入口

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


- [调用片段](https://docs.avg-engine.com/manual/writing/blocks/call-fragment)：与 JSON 页的文字冲突分别记录。
- [Beta 清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-beta.json)、[Stable 清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-stable.json)、[发布历史](https://static-lg-studio.cn-gd.ufileos.com/studio/releases-history.json)：完整版本、公告和下载条目分别核对。

## 来源限制

文档根 llms.txt 曾返回 404，部分版本管理、变量、赋值和导出页面正文曾抓取失败；这些失败不证明产品缺少功能，也不计为已阅读正文。需要的字段回到成功读取资料、实际 SDK 和目标工程保存样本。网页更新、SDK 声明、保存形式、预览、读档和导出分别判断。

安全默认、Git 协作、个人／项目分层、安装器与有限检查器是本包设计，不是官方对所有用户的强制流程。示例采用原创文本和独立 ID，不包含私人作品或第三方 SDK；静态检查器不是完整官方 schema。[JSON 工作法](skills/letsgal-authoring/references/json.md) 说明其范围。

0.1.7补充读取：[角色管理](https://docs.avg-engine.com/manual/creating/characters/)、[对白](https://docs.avg-engine.com/manual/writing/blocks/dialogue/)、[创建扩展](https://docs.avg-engine.com/extensions/develop/)。前两页用于正式资料基线；2.4具体差异按公告与目标样本分别判断。根目录llms.txt本次仍404，已改走正式页面，未将404当作无更新。

0.1.9页面入口：[浮动文字](https://docs.avg-engine.com/manual/writing/blocks/floating-text)、[动态图像](https://docs.avg-engine.com/manual/creating/dynamic-visuals)、[构建](https://docs.avg-engine.com/manual/overview/build)。基础浮字页的等待措辞与公告不同；构建页未列完整运营统计参数，因此不猜写字段。

## 0.1.10正式版资料刷新 · 2026-10-05

Stable清单的Windows／mac条目及发布历史列2.5.0，Windows正式公告逐字一致；Beta清单仍列2.5.0-beta.1。正式公告31条是多个Beta阶段的汇总，68条旧Beta记录保留历史基线，不相加为新增功能数。公告来源与本机实际版本分别判断；本次读取EXE仍为2.5.0-beta.1，没有升级引擎。

重读编辑器、If、浮动文字、角色、动态图像、构建、译稿校对和扩展AI指导，新增读取[游戏数据统计](https://docs.avg-engine.com/manual/overview/game-stats)。编辑器页仍写章节局部预览，与2.5.0“继承上文”公告按开关／版本分别说明；浮字“阻塞”与Beta“等待结束”名称仍需目标样本映射。统计页补足流程与密钥语义，但不证明服务端／API实测。根llms.txt与sitemap.xml本次仍404，具体页面正文成功读取；不声称官方已全面同步2.5手册。

正式版玩法、保存字段、SDK初始化及运行未测；旧Beta证据不改写为Stable通过。见[正式版指引](skills/letsgal-authoring/references/versions/stable-2.5.md)与[本版验证](VALIDATION.md)。原始响应和哈希只留内部凭证，不随包公开。
