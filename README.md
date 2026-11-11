# LetsGal Authoring Kit



让 AI 按目标版本协助制作 LetsGal Studio 的剧情、分支、演出、UI、数据和扩展，并保留已有内容、读取相关资料、核对修改结果。这是社区 Skill，不包含引擎、模型、账号或 MCP。



当前版本 **3.0.0 / 20261111-series300**。Stable 面向 **3.0 正式系列**；Beta 面向 **2.9 Beta 系列**，兼容 **2.8 Beta 系列**。两个通道都优先官方 MCP，安装时选一份同名载荷。[下载 3.0.0](https://github.com/recurse00-stack/letsgal-authoring-kit/releases/tag/v3.0.0)；旧版完整资料在[历史发行](https://github.com/recurse00-stack/letsgal-authoring-kit/releases)。



## 版本编号



Skill 的前两位跟随主要适配的引擎系列，第三位用于我们的修复、小功能、约束和同系列适配。例如 Skill 3.0.0、3.0.1 均服务于 Studio 3.0 系列，补丁编号各自递增。



当前总包与 Stable 载荷为 **3.0.0**，Beta 载荷独立为 **2.9.0**，保留 2.8 Beta 兼容路线。安装器显示所选载荷版本。未来适配新的 Beta 主次版本时，Beta 载荷随该系列调整；实际发行身份由运行版本判断，更新偏好不会改变资料选择。



## 开始使用



1. 完整解压包，在 Windows 双击 Install.cmd。

2. 选目标工程对应的 Stable／Beta、实际 Agent 与范围，核目标路径后导入并检查安装。

3. 新会话让 AI 实际读取 letsgal-authoring，核对路径、修订和通道，再连接目标工程。

4. 从[完整剧情练习](docs/wiki/03-story.md)或一次明确范围的改句开始。



[分主题 Wiki](MANUAL.md) · [完整离线 HTML](MANUAL.html) · [目录兼容](COMPATIBILITY.md) · [手动安装／参数](docs/wiki/08-maintenance.md#查阅手动安装与命令行)



普通 Windows 安装不要求 Python、Node 或管理员权限。可选检查脚本需要 Python 3.9+。其他系统手动复制所选通道的完整 Skill，并核对实际发现；云端和本机是不同环境。



## 三部分 Wiki 工作台



[离线工作台](MANUAL.html)按“主体／Skill Wiki／个性化”对应主 Skill、插件知识和个人资料。提供全文搜索、区域筛选、章节定位、提示词复制、窄屏阅读与完整打印。[接入规范](docs/wiki/10-workbench-interface.md)让匹配 ID 和版本的插件手册、显式选择的个人资料出现在本地工作台；公共包不带私人内容。



自测问题记录见[Wiki 第 7 章](docs/wiki/07-recovery.md#本项目自测问题历史)，包含版本、观察结果与使用提示。AI 操作规则位于对应 Skill 专题。



## 3.0.0 的主要能力



开工前按引擎主次版本与实际 Stable／Beta 身份静默检查，同一目标与任务复用结果。系列或身份不匹配时暂停工程操作，由当前使用者确认本次范围；同系列第三位版本与热修复差异无需确认。更新偏好单独记录，正常匹配不打扰、不反复联网。



设置重置、调度撤销和文件编辑会话均有写前保存、写后核对与精确恢复指导。Beta 同步通用恢复与插件指南读取规则，包含 2.9 翻译逐项处理和 else 检查；各版本专属接口按通道查阅。



人工手册按八个任务主题重写；同一正文生成一份完整离线 HTML。个人偏好和插件指南继续独立保存在实际用户区，不进入公共包；主 Skill 按真实 ID／版本主动读取，即使子包没有列入全局技能列表。



## 使用边界



- **提供内容**：主 Skill、检查脚本、安装工具与人工 Wiki。Studio、模型及 MCP 连接由使用者另行准备。

- **安装范围**：更新、切换和卸载只处理所选 Skill，保留用户区与备份。引擎、MCP 配置和其他资料的启停状态保持原状。

- **独立附加包**：协作附加包单独安装和管理，0.1.3 可从[原发布页](https://github.com/recurse00-stack/letsgal-authoring-kit/releases/tag/v0.2.3)取得。



开始前准备作品备份并设置可写范围，见[使用与备份说明](RISK-NOTICE.md)。数据保存方式见[隐私](PRIVACY.md)，已验证的任务及适用条件见[验证说明](VALIDATION.md)和[宿主范围](HOST-VALIDATION.md)。



[资料来源](SOURCES.md) · [版本记录](RELEASE-NOTES.md) · [问题反馈](https://github.com/recurse00-stack/letsgal-authoring-kit/issues)

