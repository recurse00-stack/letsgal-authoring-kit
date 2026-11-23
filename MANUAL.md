# LetsGal 创作 Wiki 工作台

**3.5.0 / 20261123-studio350**。Stable 载荷 3.5.0 面向 Studio 3.5 正式系列，兼容 3.0 正式系列；Beta 载荷 2.9.2 面向 2.9 Beta，保留 2.8 Beta 兼容路线。前两位随主要目标系列，第三位由本项目用于修订。本包帮助 AI 按任务制作并核对工程；Skill 安装不包含引擎或 MCP。

## 总工作台与资料空间

[打开离线工作台](MANUAL.html)。首页提供“主体／Skill Wiki／个性化”三个模块，也可直接搜索全部正文。主体放主 Skill 手册，Skill Wiki 放插件及功能型附属资料，个性化先提供“我的个人包”，再提供其他个人资料与可选创作参考。主 Skill 与其他指南共用相同的阅读布局。

进入一份指南后，侧栏显示该空间当前阅读版本的目录。通过侧栏顶部切换模块或指南，点击“主页”回到总览；顶部“上一步／下一步”沿实际浏览记录返回与前进。每个空间有自己的首页、导览分组和正文目录；多版本资料在空间内选择阅读版本。

阅读选版只改变当前页面；AI 实际使用的版本、启停与暂停展示由包管理保存。插件和私人资料按[接入说明](docs/wiki/10-workbench-interface.md)汇入自己的工作台，公共包只带通用正文与空白个人包模板。个人包的填写、保存和优先关系见[个人资料](docs/wiki/06-personal.md)。

## 快速开始

完整解压后运行 Install.cmd，选择通道和实际 Agent 目录，检查安装；打开 AI 新会话，要求它实际读取 letsgal-authoring 并报告路径、修订和通道。连接目标工程后，从一次局部改句开始。详细步骤见[入门](docs/wiki/01-start.md)。具备 Python 3.10+ 时，安装器会生成用户区 `workbench/MANUAL.html`，此后安装符合协议的附属包会自动接入。

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

每个主题从准备、需求示例、预期结果、核对和差异处理展开。Markdown 分页是正文正本；[完整离线 HTML](MANUAL.html)内嵌同一正文，按空间或完整长页阅读，断网可搜索和打印。Wiki 内部链接直接跳到对应段落；API 参考和官方链接继续指向对应资料。

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


## 本机包管理

总 Wiki 提供附属 Skill 与插件指南的启用、暂停、版本选择，以及“暂停时仍显示 Wiki”。管理入口及兼容包接入方法见[包管理说明](docs/wiki/10-workbench-interface.md)。离线 HTML 继续可读，管理服务按需启动。
