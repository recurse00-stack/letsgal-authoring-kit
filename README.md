# LetsGal Authoring Kit

让 AI 按目标版本协助制作 LetsGal Studio 的剧情、分支、演出、UI、数据和扩展，并保留已有内容、读取相关资料、核对修改结果。这是社区 Skill，不包含引擎、模型、账号或 MCP。

当前版本 **0.2.9 / 20261111-stable300**。Stable 目标 **3.0.0**；Beta 目标 **2.9.0-beta.1／2.8.0-beta.1**。两个通道都优先官方 MCP，安装时选一份同名载荷。[下载 0.2.9](https://github.com/recurse00-stack/letsgal-authoring-kit/releases/tag/v0.2.9)；2.5 完整资料和旧版安装包保留在[历史发行](https://github.com/recurse00-stack/letsgal-authoring-kit/releases)。

## 开始使用

1. 完整解压包，在 Windows 双击 Install.cmd。
2. 选目标工程对应的 Stable／Beta、实际 Agent 与范围，核目标路径后导入并检查安装。
3. 新会话让 AI 实际读取 letsgal-authoring，核对路径、修订和通道，再连接目标工程。
4. 从[完整剧情练习](docs/wiki/03-story.md)或一次明确范围的改句开始。

[分主题 Wiki](MANUAL.md) · [完整离线 HTML](MANUAL.html) · [目录兼容](COMPATIBILITY.md) · [手动安装／参数](docs/wiki/08-maintenance.md#查阅手动安装与命令行)

普通 Windows 安装不要求 Python、Node 或管理员权限。可选检查脚本需要 Python 3.9+。其他系统手动复制所选通道的完整 Skill，并核对实际发现；云端和本机是不同环境。

## 0.2.9 的变化

开工前静默核完整版本和热修复基线，同一目标与任务复用结果；不匹配时暂停工程操作，由当前使用者一次明确同意限定范围后继续。更新偏好与实际版本分别识别，正常匹配不打扰、不反复联网。

按 3.0 复测将设置默认态、调度撤销和文件编辑会话的差异放到执行入口前；撤回把不支持的普通删除撤销当作缺陷的旧说明。Beta 同步通用恢复与插件指南读取规则，补齐适用的翻译逐项拒绝处理和 else 检查，保留版本专属边界。

人工手册按八个任务主题重写；同一正文生成一份完整离线 HTML。个人偏好和插件指南继续独立保存在实际用户区，不进入公共包；主 Skill 按真实 ID／版本主动读取，即使子包没有列入全局技能列表。

## 使用边界

安装器更新、切换和卸载保留用户区与备份，不升级引擎、不配置 MCP、不启用暂停资料。协作附加包为独立产品，0.1.3 的原下载入口保留在[原发布页](https://github.com/recurse00-stack/letsgal-authoring-kit/releases/tag/v0.2.3)，主包更新不改变其启停状态。

开始前准备作品备份并设置可写范围，见[使用与备份说明](RISK-NOTICE.md)。数据保存方式见[隐私](PRIVACY.md)，已验证的任务及适用条件见[验证说明](VALIDATION.md)和[宿主范围](HOST-VALIDATION.md)。

[资料来源](SOURCES.md) · [版本记录](RELEASE-NOTES.md) · [问题反馈](https://github.com/recurse00-stack/letsgal-authoring-kit/issues)
