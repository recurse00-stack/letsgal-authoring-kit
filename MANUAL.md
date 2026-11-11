# LetsGal 创作 Wiki 工作台

**3.0.0 / 20261111-series300**。Stable 载荷 3.0.0 面向 Studio 3.0 正式系列；Beta 载荷 2.9.0 面向 2.9 Beta，保留 2.8 Beta 兼容路线。前两位随主要目标系列，第三位由本项目用于修订。本包帮助 AI 按任务制作并核对工程；Skill 安装不包含引擎或 MCP。

## 三个区域，一套阅读入口

| 区域 | 对应的安装内容 | 在这里查什么 |
| --- | --- | --- |
| 主体 | Agent 技能目录中的主 Skill | 安装与连接、剧情与演出、排错与维护 |
| [Skill Wiki](docs/wiki/09-plugin-wiki.md) | 用户区 `plugins/<ID>/<版本>/` | 插件指南、方法和完整用例，按真实版本分别阅读 |
| [个性化](docs/wiki/06-personal.md) | 用户区 `preferences/` 与作品约定 | 个人偏好、作品规则和显式接入的私人资料 |

[打开离线工作台](MANUAL.html)。页面提供全文搜索、范围筛选、段落定位、章节目录和提示词复制。插件与个人资料按[接入格式](docs/wiki/10-workbench-interface.md)登记后，可以生成到自己的本地工作台；公共页仅带通用说明。

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
| [6. 个人偏好与作品约定](docs/wiki/06-personal.md) | 保存个人偏好，区分跨作品要求和当前作品规则 |
| [7. 排错、精确恢复与自测问题历史](docs/wiki/07-recovery.md) | 核对操作结果、保留后来编辑，按需查阅本项目自测记录 |
| [8. 更新、切换、卸载与备份恢复](docs/wiki/08-maintenance.md) | 切换载荷、保留用户区、找回旧版本 |

每个主题从准备、需求示例、预期结果、核对和差异处理展开。Markdown 分页是正文正本；[完整离线 HTML](MANUAL.html)内嵌同一正文，按区域或完整长页阅读，断网可搜索和打印。Wiki 内部链接直接跳到对应段落；API 参考和官方链接继续指向对应资料。

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
已检查的任务、环境和方法见[验证说明](VALIDATION.md)。
