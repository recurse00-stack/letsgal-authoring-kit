# 当前维护入口

当前源码为 0.1.0-rc.1，尚未正式发布。原创代码和文档已选择 MIT；风险文本采用 2026-09-26.3。公开的 preview.7 保留不覆盖。

源维护只在此独立公共包内进行，不读取或同步私人 Skill。用户偏好和插件资料是外部用户数据；安装、更新和卸载必须保留。建议用户停用同类 Skill，由用户决定，安装器不修改其他技能或 Agent 全局配置。

首发要求稳定版与 Beta 双支持，包括工坊指引；以真实 SDK 和宿主验收决定兼容范围，不降低 sdkVersion 绕过检查。Codex、Claude Code、DSH 需真实会话验收，Cursor、Copilot 仅目录适配。独立 AI 测试只用合成资料，最多两轮。

先运行 maintenance/build_release.py 同步 BOM、技能清单和校验值，再运行相关隔离检查。release-files.json 是核心分发白名单；workshop-guide 使用单独源码和打包清单。SDK、node_modules、测试日志、截图、个人资料、完整工程均不能进入公共包。

两轮独立 AI 已完成，不再自动启动额外轮次。当前 Stable 2.0.0 与 Beta 2.2.0-beta.1 的官方 SDK 都有 TS2307 缺文件错误；完整复现见 SDK-BLOCKER.md。Codex 已实际发现正确来源，但三款模型任务未通过；安装器组件测试不能代替原生点击。

测试必须使用全新隔离目录。带 junction 的测试目录不得随意递归清理。保留旧 ZIP、发布记录与备份；同版本 ZIP 不覆盖。完整源码从 stage_publication.py 生成全新暂存目录。正式发布后续入口为 RELEASE-GATES.md，最终状态和未通过项见 VALIDATION.md。
