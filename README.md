# LetsGal 创作与协作 · 公共技能包

源码版本：0.1.5 候选，尚未发布。当前已发布版本仍为 0.1.4。独立技能名称：`letsgal-authoring`。

帮助 AI 理解制作目标、查官方教程、编写与检查章节 JSON、组织协作和 Git，并保护用户已有内容。支持向 Codex、Claude Code、Cursor、GitHub Copilot 和 DSH 导入标准 Skill。它不是 LetsGal 官方产品，也不包含引擎、模型、账号或 MCP 服务。

本包依据官方资料独立编写。安装器校验并更新 `letsgal-authoring`，只创建缺失的用户区项，并保存安装选项、记录和旧技能备份；不覆盖个人偏好、插件资料、作品或其他技能。

快速入口：[完整使用手册](MANUAL.md) · [离线 HTML 手册](MANUAL.html) · [工具兼容表](COMPATIBILITY.md) · [稳定版／Beta 规则](skills/letsgal-authoring/references/version-compatibility.md) · [验证报告](VALIDATION.md) · [隐私说明](PRIVACY.md)。

**使用前请阅读：AI 可能误改、误删或泄露资料。请先备份作品并限制 Agent 可写范围；技能备份不包含作品。** 本包按现状提供，不提供担保；作者及贡献者不对使用或无法使用本包造成的任何损失承担责任。详见[风险说明与免责声明](skills/letsgal-authoring/references/risk-notice.md)。

## 稳定版与 Beta 都按项目选择

Skill 先核对本作品的 Studio 完整版本、发布通道、SDK 和可用功能。旧稳定版不会因更新 Skill 被自动升级、迁移 JSON 或切换到蓝图；Beta 项目的规则也不会成为其他作品的全局默认。版本约定记录在各项目的 LETSGAL.md。

本包版本与 LetsGal 引擎的发布通道分别管理。安装本包不要求使用 Beta 引擎。稳定版和 Beta 的实际预览、存读档及导出仍需按工程验证。客户端完整任务、原生宿主及安装器的具体通过范围与缺口分别见验证报告；目录适配不等于各客户端已经实测。

0.1.5候选另补齐正式版到2.1／2.2／2.3 Beta的[38项累计公告](skills/letsgal-authoring/references/versions/beta-differences.md)，区分官方说明、有限实测和待验证问题；不会把获取公告称为已实现新功能。官网文档仅更新正式版的消息按用户转述记录，尚未取得官方原文／链接。

0.1.5 候选修正安装反馈和目录选择：操作结果显示在固定底部状态栏，详情采用中文摘要；Codex 个人安装沿用唯一已有入口，避免更新时另建同名副本。0.1.4 已补入有限原生 Beta 的 main／循环证据、前处理索引与长链检查、安装预检及完整案例。版本工具仍按项目选择 Stable／Beta，自报 SDK 与来源分开。见[修订记录](AUDIT.md)、[宿主证据](HOST-VALIDATION.md)和 [Beta 专页](skills/letsgal-authoring/references/versions/beta-2.3.md)。

## 安装与启用前

建议安装或启用本技能前，在 Agent 的技能设置中暂时停用其他功能重叠的 LetsGal／引擎创作类 Skill，避免重复触发、相互矛盾的指令和额外上下文开销影响执行效果。也请核对个人与工程范围是否装了多个同名副本。保留原文件及特调；由你决定停用哪一份，安装器不会自动禁用或删除其他 Skill。

## Windows 简易安装

1. 把 ZIP **完整解压**到一个普通文件夹。
2. 双击 `Install.cmd` 打开中文图形界面，选择 Agent；一般保留“个人 · 所有项目”。
3. 核对本包／已装版本、安装状态和实际目录，再点击“导入到 …”。项目导入可浏览或填写工程目录；DSH 可选择实际数据目录。指定其他位置时，选“其他 Agent / 指定目录”，浏览或粘贴 Agent 已配置的 `skills` 根目录。
4. 查看窗口底部的固定状态栏。显示“导入完成”后，可展开“更多选项”点击“检查安装”；显示“安装文件校验通过”后，点“复制验证提示词”，在 Agent 新会话中粘贴。

首次默认 Codex／个人；安装成功后记住选择。若选项或日志无法保存，界面单独显示提示，并保留真实的文件安装结果；下次需重新核对目标位置。更新时解压新版，再运行同一个入口。无需输入命令，也不要求管理员。安装器不下载软件，不修改 API Key、MCP 或模型配置。

目录按实际执行用户解析，发行包没有绑定作者的用户名或磁盘位置。Codex 个人安装：仅 `~/.codex/skills/letsgal-authoring` 已存在时沿用旧入口；仅 `~/.agents/skills/letsgal-authoring` 已存在时沿用它；全新安装默认 `~/.agents/skills`。两处都有时会停止自动选择，请先核对实际加载来源，再用“其他 Agent / 指定目录”明确目标。自选目录应是 `skills` 根目录，安装器会追加 `letsgal-authoring`；选择一个未配置的位置不会自动使 Agent 发现它。

### 软件装在其他盘，怎么选目录

**软件安装文件夹和技能目录是两回事。** Agent 或 LetsGal 装在 D／E 盘，不代表 Skill 也要放进程序文件夹。个人模式按运行安装器的 Windows 用户定位标准目录；请使用与 Agent 相同的用户环境，并核对界面显示的最终路径。

- **只改了软件安装位置，技能目录仍为标准位置：** 保留对应 Agent 的个人模式即可。
- **另设了技能／数据目录：** 选“其他 Agent / 指定目录”，点击“浏览…”或粘贴 Agent 已配置的 `skills` 根目录；DSH 可直接选择实际数据文件夹。安装器不会自动识别所有便携版、迁移目录或自定义 `CODEX_HOME`。
- **手动选择时：** 选父级 `skills` 文件夹，不选末级 `letsgal-authoring`。例如 Agent 已配置 `<自定义数据目录>/skills`，导入后为 `<自定义数据目录>/skills/letsgal-authoring`；尖括号内容替换为你的实际目录，这不是默认路径。

安装器导入本包 Skill、创建缺失用户区并保存安装记录，不修改 Agent 的目录配置。任意选一个文件夹不能保证被加载；先确认 Agent 会读取它，安装后再用新会话核对实际 Skill 来源。更多目录与 DSH 默认值见[手册](MANUAL.md)和[兼容表](COMPATIBILITY.md)。

操作期间底部显示正在处理；结束后明确显示校验通过、需备份或操作失败，并同步结果详情。检查只验证已装 Skill 文件，不能证明 AI 已加载或工程能运行。

启动器对本次 PowerShell 进程使用 Bypass，使同包脚本可启动；不修改系统或用户的持久执行策略。组织策略或系统警告仍可能阻止运行，不要为本包关闭安全保护；可以手动安装。安装文件无需 Python，附带的可选 JSON 检查器与版本资料工具需要 Python 3.9+。

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

2026-10-01 对已安装 0.1.4 补验：新鲜官方 Codex 在两个工作目录发现唯一启用的用户入口；仅以技能名运行的真实制作任务正常完成，独立29项核对通过。新生成章节的钟楼／水井两条路线分别在实际2.3.0-beta.1观察到开场、选项、各自旁白及公共返回文字。结束章后的调试画面空白，但Studio仍显示运行中；具体范围见[验证报告](VALIDATION.md)。此结果不等于0.1.5候选安装后已通过同样验证。

## 支持与手动安装

详细目录和范围见 [COMPATIBILITY.md](COMPATIBILITY.md)。将整个 `skills/letsgal-authoring` 文件夹复制到目标 skills 根目录；不要只复制 SKILL.md，也不要多嵌套一层文件夹。若已存在同名内容，先保全完整旧目录，移到技能扫描目录之外，再复制新版；不要选择系统的“合并文件夹／替换所有文件”，这会留下过期文件或覆盖本地改动。

Codex、Cursor、当前 Copilot 支持 `.agents/skills`；Codex 个人安装还会沿用唯一已有的 `.codex/skills/letsgal-authoring`，不自动迁移。Claude Code 使用 `.claude/skills`。Cursor 可能同时发现其他工具目录的同名技能，安装器会提示已有副本但不删除它们。自定义配置目录、旧客户端和远程运行环境可选“其他 Agent / 指定目录”，选择该 Agent 已配置的技能根目录。

DSH 已提供专用入口：个人技能进入 `DSH_HOME/skills`，默认是 `~/.dsh/skills`；项目技能进入最近 Git 仓库根的 `.dsh/skills`，没有 Git 仓库时使用所选项目目录。如果启动器单独设置了 DSH_HOME，安装器无法从系统环境猜出它，请在界面选择实际数据文件夹。已配置特殊技能根目录的工具可选“其他 Agent / 指定目录”。详见 [DSH 兼容说明](COMPATIBILITY.md#dsh)。

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
- 在完整解压包根目录运行 `python "skills/letsgal-authoring/scripts/check_project.py" "<工程或章节绝对路径>"` 做只读的部分静态检查。对话不会被输出，但诊断会显示文件名。
- [资料来源](SOURCES.md)、[全面修订](AUDIT.md)、[验证结果](VALIDATION.md)。

从作品目录调用工具时，用实际加载 Skill 的绝对目录，例如 `python "<实际 Skill 绝对目录>/scripts/check_project.py" "<章节绝对路径>"`；安装不要求一直保留或使用下载目录。

当前0.1.5三份21文件一致；完整包安装、Check、两目录官方发现、显式小型制作任务和安装入口的技能名只读调用已通过各自范围。制作任务有3条静态警告，新章节未实际播放；原生导入器浏览／取消、Stable及其他Agent仍待验。详见[当前与历史检查点](VALIDATION.md#当前候选与历史检查点)。

## 当前发布状态与许可证

本项目仅通过社区与 [GitHub Releases](https://github.com/recurse00-stack/letsgal-authoring-kit/releases) 维护和分发。下载页列出的版本才是已发布版本；源码版本不代表已经发布。请下载核心包 `letsgal-authoring-kit-<版本>.zip`，完整解压后交给 Agent 按附带手册协助安装。Windows 可运行安装器，其他平台手动导入。实际支持范围见 [验证报告](VALIDATION.md)。

本项目原创代码与文档采用 [MIT 许可证](LICENSE)。第三方引擎、SDK、工具及插件适用各自条款。本包不包含 LetsGal 引擎或 SDK。


0.1.5 初稿只改元数据时已核对原绑定与官方发现；后续Beta资料和实测规则已修订，不能继续称为“制作方法未改”。0.1.4两路线制作到播放证据保留历史范围；当前0.1.5另有有限制作与只读调用任务，尚无该新章节的播放结果。

当前补验：实际2.3.0-beta.1选项赋值为42、slot数值变量及桌面玩家快读／槽位读档跨进程恢复通过有限用例；扩展追加历史未自动恢复。配置步骤与限制见[人类手册](MANUAL.md)，具体层次见[验证记录](VALIDATION.md)。0.1.5的渠道状态与下载验证以GitHub发行页及随版凭证为准。
