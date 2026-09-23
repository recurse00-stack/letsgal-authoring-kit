# 怎样找到可靠资料

## 查找顺序

先记录用户实际安装／运行的 Studio 版本（包含 beta 后缀）、目标工程格式和目标扩展 SDK。安装文件、运行实例与文档发布日期是不同证据。不要用本技能的发行日期推断所有引擎版本兼容。

稳定版、Beta 与旧版的判断按 [版本兼容](version-compatibility.md) 执行。查到较新的字段或接口时，先查该功能适用版本；不能把最新网页完整移植进旧工程。

1. 在目标工程找到同类、已能工作的内容样本，确定真实文件位置和引用对象。
2. 查 [官方文档首页](https://docs.avg-engine.com/) 的导航或站内搜索。`/llms.txt` 只是便利入口；失效时改走页面导航或定向搜索，不停在 404。
3. 搜索示例：`site:docs.avg-engine.com 选项 分支`、`site:docs.avg-engine.com 剧本 JSON <指令名>`、`site:docs.avg-engine.com extensions <API名>`。打开结果正文核实，不能只凭搜索摘要写代码。
4. 扩展任务可从 [官方 AI 扩展指导](https://docs.avg-engine.com/extensions/llms.txt) 进入，再按目标扩展的 `sdk/` 类型确认签名。SDK 文件存在不等于接口已经在宿主中通过测试。
5. 文档与样本冲突时，记录两者版本和差异；优先在隔离样例工程验证目标宿主的保存与执行行为。对缺失字段暂缓写入，不用旧网页、社区示例或推测补全。

## 主题入口

| 查什么 | 官方入口 | 使用方式 |
| --- | --- | --- |
| 章节与 Block 的磁盘结构 | [剧本 JSON](https://docs.avg-engine.com/reference/script-json) | 先看结构，再跳到此次指令及引用规则 |
| 选项返回与片段执行 | [Branch](https://docs.avg-engine.com/manual/writing/blocks/branch) | 区分调用返回和结束路线 |
| 跨章节路线 | [章节调度与蓝图](https://docs.avg-engine.com/advanced/chapter-scheduling) | 不把画布位置当执行顺序 |
| 创建及构建扩展 | [扩展开发](https://docs.avg-engine.com/extensions/develop/) | 核对目标 SDK、源码与构建入口 |
| 多人同时编辑 | [实时协作](https://docs.avg-engine.com/manual/overview/collaboration) | 确认编辑权、同步和冲突 |
| 备份及恢复影响 | [时光机](https://docs.avg-engine.com/manual/overview/backup) | 恢复是写入操作，先判断覆盖范围 |
| 工坊分发 | [扩展工坊](https://docs.avg-engine.com/manual/overview/extension-market/) | 投稿格式、完整文件包、审核要求 |
| Git 行为 | [status](https://git-scm.com/docs/git-status)、[worktree](https://git-scm.com/docs/git-worktree)、[restore](https://git-scm.com/docs/git-restore) | 按所用命令核对选项及影响 |

更多指令沿官方页面链接继续找，不把本表当作全量 API。版本记录可从 [官网](https://avg-engine.com/) 进入；页面抓取失败时写明无法读取，不把失败当作无更新。

## 把找到的信息留下

需要长期复用时，在项目既有开发说明记录“主题、完整 URL、查阅日期、适用版本、所用字段、验证层次”。只记录本次用到的结论和原始链接，不下载整站或复制整套手册到作品里。

离线时利用已保存且带日期的规范与现有样本，清楚标记时效限制。需要新版能力而无法取得依据时，只隔离该不确定部分；不要擅自升级宿主或改低 SDK 要求。
