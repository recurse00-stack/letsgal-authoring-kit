# 资料来源与查阅范围

本包依据官方资料、目标版本样本和有限实测独立编写。0.1.8于2026-10-02刷新官方Beta／Stable清单和发布历史，补充2.4.0-beta.2的五项公告；0.1.7读取的角色／对白／扩展页面保留原日期；各项实测按完整版本注明。历史来源仍保留原日期，不保证网页此后保持原样。

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

本版补充读取：[角色管理](https://docs.avg-engine.com/manual/creating/characters/)、[对白](https://docs.avg-engine.com/manual/writing/blocks/dialogue/)、[创建扩展](https://docs.avg-engine.com/extensions/develop/)。前两页用于正式资料基线；2.4具体差异按公告与目标样本分别判断。根目录llms.txt本次仍404，已改走正式页面，未将404当作无更新。
