# LetsGal Authoring Kit · 社区 Skill

`letsgal-authoring` 帮助 AI 在 LetsGal Studio 工程中制作剧情、分支、变量与章节 JSON，查找官方资料、处理扩展及 Git 协作。它是独立社区 Skill，不包含引擎、模型、账号或 MCP；实际能力取决于 Agent 的工具和项目权限。

本包版本 **0.1.8**，补充2.4.0-beta.2版本识别与头像／界面排错说明。公开可下载版本以发布页实际列出的版本为准。下载见[GitHub Releases](https://github.com/recurse00-stack/letsgal-authoring-kit/releases/latest)；旧版本与凭证保留。源码、标签、附件和匿名下载的核验结果见各版独立发布凭证。

入口：[使用手册](MANUAL.md) · [离线 HTML](MANUAL.html) · [Agent 与目录兼容](COMPATIBILITY.md) · [验证范围](VALIDATION.md) · [资料来源](SOURCES.md) · [版本记录](RELEASE-NOTES.md)。

**使用前请备份作品并限制 Agent 可写范围。AI 可能误改、误删或泄露资料；安装器的 Skill 备份不包含作品。** 本包按现状提供，不提供担保；作者及贡献者不对因使用或无法使用本包造成的损失承担责任。详见 [风险说明与免责声明](skills/letsgal-authoring/references/risk-notice.md) 和 [隐私说明](PRIVACY.md)。

## Windows 安装

1. 下载完整的 `letsgal-authoring-kit-<版本>.zip`，解压到普通文件夹，再双击 `Install.cmd`。不要在 ZIP 内运行，不要单独运行摘出的 `Install.ps1`。
2. 选择实际使用的 Agent，一般采用“个人 · 所有项目”；只给一个作品用时选择“项目 · 仅此工程”并浏览工程目录。
3. 核对最终目录、本包／已装版本及预览状态，点击“导入到 …”。底部固定状态栏显示处理和完成结果。
4. 展开“更多选项”，点击“检查安装”。底部显示“检查安装 · 校验通过”，页面结果框标题为“安装文件校验通过”。再复制验证提示词，在 Agent 新会话中核对实际加载路径。

普通导入需要 Windows PowerShell 5.1 或 PowerShell 7，不要求 Python、Node 或管理员权限。可选只读工具需要 Python 3.9+。macOS／Linux 等环境按 [手动安装](MANUAL.md#手动安装与命令行) 复制完整 Skill，自动安装器仅支持 Windows。

## 路径可以手动选择

发行包没有绑定作者的盘符或用户名。软件安装目录和 Skill 目录分别管理：Agent 或 LetsGal 装在其他盘，仍使用标准技能目录时，选择对应 Agent 的个人模式即可。

Codex 个人安装沿用唯一已有的 `~/.codex/skills/letsgal-authoring` 或 `~/.agents/skills/letsgal-authoring`；全新默认 `~/.agents/skills`。两处已有同名 Skill 时，安装器停止自动选择。`~` 是运行安装器的用户主目录，请与 Agent 使用同一用户／环境。

如果 Agent 另设了数据或技能目录，先确认它实际读取的位置，再选“其他 Agent / 指定目录”，点击“浏览…”或粘贴已配置的 **skills 根目录**。安装器追加 `letsgal-authoring`，不要选择末级 Skill 文件夹或程序文件夹。DSH 可在专用选项中选择实际数据目录。

安装器不扫描整盘、不读取账号配置、不自动解析所有便携目录或自定义 `CODEX_HOME`，也不修改 Agent 的发现设置。文件校验通过只证明安装文件状态，加载仍需在新会话确认。详见 [安装位置说明](MANUAL.md#安装位置怎样选择)。

## 开始一个任务

安装或启用前，建议在 Agent 设置中暂时停用其他功能重叠的 LetsGal／引擎创作 Skill，核对个人和项目范围是否存在重复入口。保留原文件与特调，由你选择使用哪份；安装器不会自动禁用其他 Skill。

在作品目录打开新会话，调用 `letsgal-authoring`，可以粘贴：

> 使用 letsgal-authoring。先读本工程的规则和当前状态，核对实际 Skill 路径及 Studio 完整版本／通道。只处理我指定的内容，保留已有 ID、未知字段和其他改动；缺少版本或字段依据时说明 UNKNOWN，继续不依赖它的工作。完成后说明文件变化、实际验证结果和需要我预览的入口。

第一项练习可从手册的 [完整双选项案例](MANUAL.md#从选择练习走完一个最小完整案例) 开始。Skill 不要求先验收引擎全部功能；本次使用哪个功能，就核对对应资料、样本和必要行为。

## 正式版与 Beta 按工程选择

Skill 包版本和引擎版本独立。稳定版、Beta 和旧工程均先核对目标宿主；不以作者本机 Beta 为默认，不因更新 Skill 升级引擎、迁移作品或刷新已导出的游戏。

版本工具对已核实的 2.0.0／2.0.1 选择 Stable 资料，对 2.3.0-beta.1／2.4.0-beta.1／2.4.0-beta.2 分别选择对应 Beta 资料。未知、冲突和其他完整版本返回 UNKNOWN；[资料路由](skills/letsgal-authoring/references/version-compatibility.md) 与真实宿主运行分别记录。

Beta资料包含正式版基线到2.1／2.2／2.3／2.4的[56项公告](skills/letsgal-authoring/references/versions/beta-differences.md)，[2.4用法](skills/letsgal-authoring/references/versions/beta-2.4.md)与[2.3有限实测](skills/letsgal-authoring/references/versions/beta-2.3.md)分别维护。公告、保存样本、SDK声明和运行观察分开，不推定所有能力已通过。

## 个人偏好、插件资料与升级

个人偏好保存在 `~/.letsgal-authoring/preferences/user.md`，旧版根目录 `user.md` 原位兼容；插件使用 Skill 保存在 `~/.letsgal-authoring/plugins/<插件ID>/<版本>/SKILL.md`。主 Skill 按项目选择读取，插件代码和运行安装仍由原扩展工程／Studio 管理。主 Skill 不作为自己的子插件安装。

项目约定写工程 `LETSGAL.md`。公共更新和卸载保留用户区、旧版及已有备份；如果公共 Skill 有特调，先比较并保全，再决定“备份后继续”。完整步骤见 [更新、卸载与恢复](MANUAL.md#更新卸载与恢复)。

本产品仅在 GitHub／社区分发，工坊不适用。程序、说明和验证范围见 [修订记录](AUDIT.md) 与 [验证报告](VALIDATION.md)；未宣称所有 Agent、引擎版本或平台都已测试。
