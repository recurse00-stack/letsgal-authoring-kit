# LetsGal Authoring Kit 使用 Wiki

**0.2.9 / 20261111-stable300**。Stable 面向 Studio 3.0.0，Beta 面向 2.9.0-beta.1／2.8.0-beta.1。本包帮助 AI 按任务制作并核对工程；Skill 安装不包含引擎或 MCP，不自动升级作品。

## 快速开始

完整解压后运行 Install.cmd，选择通道和实际 Agent 目录，检查安装；打开 AI 新会话，要求它实际读取 letsgal-authoring 并报告路径、修订和通道。连接目标工程后，从一次局部改句开始。详细步骤见[入门](docs/wiki/01-start.md)。

先备份作品并限制 AI 可写范围。Skill 备份与作品备份不同；见[风险说明](RISK-NOTICE.md)。当前版本与旧版资料在[历史发行](https://github.com/recurse00-stack/letsgal-authoring-kit/releases)。

## 按任务阅读

| 主题 | 你将完成什么 |
| --- | --- |
| [1. 入门、安装与确认 AI 实际读取](docs/wiki/01-start.md) | 装好 Skill 并确认 AI 读取来源 |
| [2. Stable／Beta、工程身份与 MCP](docs/wiki/02-connection.md) | 选版本、接对窗口、处理权限与断连 |
| [3. 一次完整的剧情修改与分支练习](docs/wiki/03-story.md) | 完成双选项练习，再局部改字与加条件 |
| [4. 舞台、演出、多语言与配音](docs/wiki/04-performance.md) | 让配置进入剧情，核对声音和各语言 |
| [5. UI、数据和扩展选型](docs/wiki/05-ui-data.md) | 按用途选实现并核对实际效果 |
| [6. 个人偏好、插件指南的建立与使用](docs/wiki/06-personal.md) | 保存私人资料，让主 Skill 主动找到它 |
| [7. 已知差异、排错与精确恢复](docs/wiki/07-recovery.md) | 理解已确认差异并保留后来编辑 |
| [8. 更新、切换、卸载与备份恢复](docs/wiki/08-maintenance.md) | 切换载荷、保留用户区、找回旧版本 |

每个主题从准备、需求示例、预期结果、核对和差异处理展开。Markdown 分页是正文正本；[完整离线 HTML](MANUAL.html)将同一正文合并成一页，断网可阅读、搜索和打印。HTML 的 Wiki 导航均在页内跳转；API 参考和官方链接继续指向对应资料。

## 查阅

[正式版差异](channels/stable/MANUAL.md) · [Beta 差异](channels/beta/MANUAL.md) · [安装目录兼容](COMPATIBILITY.md) · [资料来源](SOURCES.md) · [验证范围](VALIDATION.md) · [宿主证据](HOST-VALIDATION.md) · [隐私](PRIVACY.md)

<a id="手动安装与命令行"></a>
<a id="更新卸载与恢复"></a>
安装参数与旧版恢复已移到[第 8 章](docs/wiki/08-maintenance.md#查阅手动安装与命令行)。

<a id="从选择练习走完一个最小完整案例"></a>
剧情案例已移到[第 3 章](docs/wiki/03-story.md)。

<a id="官方-mcp-与无-mcp-两种用法"></a>
<a id="安装位置怎样选择"></a>
连接与路径问题分别见[第 2 章](docs/wiki/02-connection.md)和[第 1 章](docs/wiki/01-start.md)。

<a id="从测试中看到的实际帮助"></a>
测试的范围与限制见[验证说明](VALIDATION.md)，不提供未经对照的提速百分比。
