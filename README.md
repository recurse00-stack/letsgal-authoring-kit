# LetsGal 创作与协作 · 公共技能候选版

版本：0.1.0-preview.5。独立技能名称：`letsgal-authoring`。

帮助 AI 理解制作目标、查官方教程、编写与检查章节 JSON、组织协作和 Git，并保护用户已有内容。支持向 Codex、Claude Code、Cursor、GitHub Copilot 和 DSH 导入标准 Skill。它不是 LetsGal 官方产品，也不包含引擎、模型、账号或 MCP 服务。

本包依据官方资料独立编写；安装器只操作名为 `letsgal-authoring` 的目标目录，其他名称的个人技能保持原样。

快速入口：[完整使用手册](MANUAL.md) · [工具兼容表](COMPATIBILITY.md) · [稳定版／Beta 规则](skills/letsgal-authoring/references/version-compatibility.md) · [验证报告](VALIDATION.md) · [隐私说明](PRIVACY.md)。

## 稳定版与 Beta 都按项目选择

Skill 先核对本作品的 Studio 完整版本、发布通道、SDK 和可用功能。旧稳定版不会因更新 Skill 被自动升级、迁移 JSON 或切换到蓝图；Beta 项目的规则也不会成为其他作品的全局默认。版本约定记录在各项目的 LETSGAL.md。

本包的 preview 是技能包自己的发布状态，与 LetsGal 引擎的 Beta 通道无关。安装本包不要求使用 Beta 引擎；目前也没有声称已在全部历史版本上运行验收。

## Windows 简易安装

1. 把 ZIP **完整解压**到一个普通文件夹。
2. 双击 `Install.cmd` 打开中文图形界面，选择 Agent；一般保留“个人 · 所有项目”。
3. 点击“导入到 …”。DSH 迁移过数据位置时，点“浏览…”选择实际 DSH 数据文件夹；项目导入则选项目文件夹。
4. 看到“导入完成”后，点“复制验证提示词”，在 Agent 新会话中粘贴。

首次默认 Codex／个人；安装成功后记住选择。若选项或日志无法保存，界面单独显示提示，并保留真实的文件安装结果；下次需重新核对目标位置。更新时解压新版，再运行同一个入口。无需输入命令，也不要求管理员。安装器不下载软件，不修改 API Key、MCP 或模型配置。

启动器对本次 PowerShell 进程使用 Bypass，使同包脚本可启动；不修改系统或用户的持久执行策略。组织策略或系统警告仍可能阻止运行，不要为本包关闭安全保护；可以手动安装。安装文件无需 Python，附带的可选 JSON 检查器需要 Python 3.9+。

安装器拒绝链接／junction 目标，保留未知或已修改的旧技能，替换前完整备份；备份在所选 `skills` 目录旁的 `.letsgal-authoring-backups`，不会被当作另一个 Skill 加载。备份和目标在同一卷，支持 AI 配置在 C 盘、项目在其他盘。

## 特调一次，升级保留

| 内容 | 位置 | 升级时 |
| --- | --- | --- |
| 公共技能与检查器 | AI 工具的 skills 目录 | 校验后更新，旧版备份 |
| 个人长期偏好 | `~/.letsgal-authoring/preferences/user.md`；旧用户沿用原 user.md | 原样保留，不自动迁移 |
| 用户插件 Skill | `~/.letsgal-authoring/plugins/<插件ID>/<版本>/SKILL.md` | 用户独立维护，安装／更新／卸载均保留 |
| 作品规则 | 工程根 `LETSGAL.md`，可链接已有项目文档 | 原样保留；安装器不写它 |

`~` 是实际运行 AI 的用户主目录。远程机器、WSL、容器和云端不是本机；需要在对应环境另行安装／复制配置。设置个人偏好可以对 AI 说：

> 请把我的跨项目制作习惯记入 letsgal-authoring 的 user.md；只属于当前作品的规则写入 LETSGAL.md，不修改公共 Skill。先保留已有内容，再按我明确说过的偏好更新。

例如文风、命名、目录、Git 分支习惯、确认节奏和验证深度都可特化。当前请求优先于一般偏好；这些配置不改变宿主权限和指令优先级。

如果直接改过公共 Skill，安装器会检测差异并停止自动覆盖。让 AI 比较旧包和新包，将个人部分迁入外部配置；备份保留原文。不要把其他私有技能的全部内容自动导入公共版。

## 用户区：个人偏好与插件 Skill 分开

`preferences/` 存个人习惯；`plugins/` 存用户自己的插件 Skill 和必要参考资料。导入器显示两个位置，只创建缺失项，不覆盖已有文件。旧版 user.md 继续在原位置使用，不要求重新配置；两处偏好都存在时应比较原文，不自动合并。

对已加载本技能的 AI 说：

> 分析我指定的这个插件，为它编写插件 Skill。按 letsgal-authoring 的规范自动存入用户插件区，用真实插件 ID 和版本区分，补充插件索引。保全已有内容，不修改插件代码、不启用项目依赖；完成后告诉我保存路径、来源和未验证项。

默认落点是 `~/.letsgal-authoring/plugins/<插件ID>/<版本>/SKILL.md`。具体规范和模板见 [用户插件 Skill](skills/letsgal-authoring/references/plugin-skills.md)。主 Skill 按当前项目选择读取它，不把多个版本自动注册为 Agent 的同名独立技能。插件的代码、构建产物与安装升级继续由原扩展工程／Studio 管理，不打进公共包。

## 验证 AI 真正加载

打开一个 LetsGal 工程，在新会话中选择／调用 `letsgal-authoring`。Codex 可输入 `$letsgal-authoring`；Claude Code、Cursor 可在 `/` 菜单查找；Copilot、DSH 按当前客户端的技能列表与调用入口使用。DSH 需要启用文件系统技能提供器及技能工具；若看不到技能，先核对运行实例的数据目录和提供器配置，安装器不会擅自修改预设或重启服务。

复制这段提示：

> 使用 letsgal-authoring。只读检查：告诉我实际读取的技能文件路径、个人偏好、项目约定和实际使用的插件 Skill 入口；不存在就明确说不存在。定位当前工程与章节，并说明写 JSON 前会查哪一页官方规范。不要修改文件或启动引擎。

核对路径和真实结果。安装器的 `ai_loaded=not_tested` 是有意保留的边界：文件安装、AI 发现技能和引擎实际运行分别验证。请勿把模型声称“已加载”作为唯一证据；可检查技能选择器、读取操作和一个小型实际任务。

## 支持与手动安装

详细目录和范围见 [COMPATIBILITY.md](COMPATIBILITY.md)。将整个 `skills/letsgal-authoring` 文件夹复制到目标 skills 根目录；不要只复制 SKILL.md，也不要多嵌套一层文件夹。若已存在同名内容，先保全完整旧目录，移到技能扫描目录之外，再复制新版；不要选择系统的“合并文件夹／替换所有文件”，这会留下过期文件或覆盖本地改动。

Codex、Cursor、当前 Copilot 支持 `.agents/skills`，本安装器优先复用这一共同位置，减少重复副本；Claude Code 使用 `.claude/skills`。Cursor 可能同时发现其他工具目录的同名技能，安装器会提示已有副本但不删除它们。自定义配置目录、旧客户端和远程运行环境可选“自选技能目录”。

DSH 已提供专用入口：个人技能进入 `DSH_HOME/skills`，默认是 `~/.dsh/skills`；项目技能进入最近 Git 仓库根的 `.dsh/skills`，没有 Git 仓库时使用所选项目目录。如果启动器单独设置了 DSH_HOME，安装器无法从系统环境猜出它，请在界面选择实际数据文件夹。已配置特殊技能根目录的工具可选“其他 Agent”。详见 [DSH 兼容说明](COMPATIBILITY.md#dsh)。

## 命令行、检查与卸载

界面“更多选项”可检查或卸载；也可以双击 `Check.cmd` 或 `Uninstall.cmd`，在同一图形界面选位置并执行。卸载先移到备份，仍保留个人配置。

在包根目录运行（PowerShell）：

```powershell
.\Install.ps1 -Harness Codex -Scope User -NonInteractive
.\Install.ps1 -Action Check -Harness Codex -Scope User -NonInteractive
.\Install.ps1 -Action Uninstall -Harness Codex -Scope User -NonInteractive
.\Install.ps1 -Harness DSH -Scope User -NonInteractive
.\Install.ps1 -Harness DSH -Scope User -DshHome "<实际 DSH 数据目录绝对路径>" -NonInteractive
```

工程安装加 `-Scope Project -ProjectPath "<工程绝对路径>"`。自选目录使用 `-Harness Manual -SkillsDirectory "<skills根目录绝对路径>"`。`-UserHome` 供便携环境或隔离测试指定实际用户主目录，不会修改系统用户目录。

卸载只把该技能目录移到备份，**个人配置、项目文件和历史备份全部保留**。用户已改动公共文件时仍会停止；界面的“备份后继续”或命令行 `-ReplaceModified` 表示明确同意先完整备份再替换／移走，日常更新不需要它。

安装成功时界面显示本次旧技能备份位置；更详细的记录位于 skills 旁的 `.letsgal-authoring-backups/*-install.json`（卸载为 `*-uninstall.json`）。项目内安装时备份可能含私有特调，提交 Git 前按项目规则排除；安装器不修改项目的 .gitignore。

恢复旧版：先保留现用目录，再从安装日志标明的备份目录复制回相同目标，重新验证加载；也可让 AI 按精确路径完成恢复。不要直接覆盖后续新增的特调。没有自动清理历史备份的功能。

## JSON 与维护

- [技能入口](skills/letsgal-authoring/SKILL.md) 按任务路由到制作、JSON、安全、Git、扩展和定制参考。
- [原创章节例子](skills/letsgal-authoring/examples/选择练习.json) 不依赖图像／音频；是待导入章节，不是完整游戏。复制前重生成 ID。
- 运行 `python "skills/letsgal-authoring/scripts/check_project.py" "<工程或章节绝对路径>"` 做只读的部分静态检查。对话不会被输出，但诊断会显示文件名。
- [资料来源](SOURCES.md)、[验证结果](VALIDATION.md)、[工坊投稿准备](WORKSHOP.md)。

## 当前发布状态

这是可分发的技能及安装器候选包，**不是已通过 LetsGal 投稿检查的引擎扩展**。没有伪造 extension.json 或运行入口。工坊的承载方式、下载结果和审核仍待验证；GitHub 源码发布不代表工坊通过。

尚未指定开源许可证；请勿把公开源码状态自动理解为已授予任意再分发许可。
