# Harness 适配边界

手动导入前阅读 [风险说明与免责声明](skills/letsgal-authoring/references/risk-notice.md)，完整复制 Skill 目录以保留随包说明；导入不授予 AI 额外文件权限。

Agent 的导入目录兼容与 LetsGal 引擎版本兼容分别判断。稳定版、Beta、旧工程和未知版本均走 [项目版本规则](skills/letsgal-authoring/references/version-compatibility.md)，不以“最新版文档”替代目标宿主证据。下表只说明 Agent 的技能入口。

2026-09-26 按官方文档复核。以下为当前格式／目录适配，不代表全部客户端版本、远程环境或真实 AI 行为均已验收。

| 本地工具 | 个人安装 | 工程安装 | 核对来源 |
| --- | --- | --- | --- |
| Codex | `~/.agents/skills/letsgal-authoring` | `<工程>/.agents/skills/letsgal-authoring` | [官方](https://learn.chatgpt.com/docs/build-skills) |
| Claude Code | `~/.claude/skills/letsgal-authoring` | `<工程>/.claude/skills/letsgal-authoring` | [官方](https://code.claude.com/docs/en/skills) |
| Cursor | `~/.agents/skills/letsgal-authoring` | `<工程>/.agents/skills/letsgal-authoring` | [官方](https://cursor.com/docs/skills) |
| GitHub Copilot | `~/.agents/skills/letsgal-authoring` | `<工程>/.agents/skills/letsgal-authoring` | [官方](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) |
| DSH / DeepSeek Harness | `<DSH_HOME>/skills/letsgal-authoring`，未设时为 `~/.dsh/skills/letsgal-authoring` | `<最近 Git 根或所选目录>/.dsh/skills/letsgal-authoring` | [官方](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md) |

Cursor 也支持 `.cursor/skills`，Copilot 也有 `.copilot/skills`（个人）和 `.github/skills`（工程）。这里选共用路径，是安装器设计选择，不宣称其他路径无效。Codex 本机可能仍有 `.codex/skills` 等旧版目录；无需迁移原技能。

必须使用具有项目文件访问能力的模式；只在普通聊天里贴技能文字不赋予编辑器控制能力。`agents/openai.yaml` 只提供 Codex 界面元数据，核心工作流不依赖它。未硬编码任何一家工具的函数名、模型或 MCP 地址。

工具目录有跨客户端发现时，同名个人／项目／其他 harness 副本可能同时出现。不要为去重删除未知副本；先看客户端的加载列表、作用域与优先级。

本安装器面向 Windows PowerShell 5.1／PowerShell 7。macOS／Linux 可手动复制技能目录和 user.md；此版没有宣称在这些系统上验证了安装程序。云端／容器须在该环境单独配置，个人本机目录不会自动上传。

用户配置文件结构约定版本为 1：只含 Markdown，自定义内容原样读取。此版安装器不做迁移和重写；未来若需要迁移，应采用有版本、备份、可审查差异的流程，不静默重置。

## DSH

已对本机安装的 DSH 0.1.6-alpha.2 所带官方 `@deepseek-ai/dsh-skill-filesystem` 进行隔离发现与正文读取测试；没有向真实服务导入，也没有调用模型。

- 个人导入采用界面指定／上次保存的位置；首次从安装器进程的 `DSH_HOME` 读取，未设时建议 `~/.dsh`。这只是默认值，不表示检测到了正在运行的 DSH。命令行显式 `-DshHome` 优先于环境变量。
- 如果启动器或提供器配置另设了 `dshHome`，请在界面选择对应数据目录。支持 `~` 展开，其余路径须为绝对路径。不扫描账号、配置内容或全部磁盘来猜位置。
- 项目目录按 DSH 官方算法向上寻找最近的 `.git`（目录或文件），找不到时使用所选目录。界面与安装后端共用同一套解析代码。
- 官方提供器也支持 `.agents/skills`；本包的 DSH 入口明确使用 `.dsh/skills`。同名项目技能优先于个人技能，另有副本时先核对实际来源，不自动删掉它们。
- DSH 必须已启用文件系统技能提供器，且没有关闭默认根目录；使用自定义 `customSkillDirs` 时可选“其他 Agent”导入到已配置的根目录。安装器不编辑 DSH 预设，不启动／重启 DSH。
- 技能内容与相对参考文件可读取，不依赖特定模型或 MCP。个人偏好仍在实际运行 AI 的用户主目录 `~/.letsgal-authoring/preferences/user.md`（旧版根目录 user.md 继续兼容），不随 DSH_HOME 搬入公共技能；插件 Skill 独立放在同一用户区的 plugins/ 中，由主 Skill 按项目需要读取。

DSH 来源：[文件系统技能提供器](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md)、[数据目录解析](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/util/home-paths/src/index.ts)。

## 首发验收分级

Codex、Claude Code、DSH 的完整模型任务及更新后会话暂未验证，不作为 0.1.0 的发行门槛。Codex 有真实技能发现证据，DSH 有官方 provider 读取证据；Claude Code、Cursor、Copilot 标为格式／目录适配。命令存在、目录被发现、模型实际使用和宿主运行是不同证据，不相互替代；详见 VALIDATION.md。

建议安装或启用本技能前，在 Agent 的技能设置中暂时停用其他功能重叠的 LetsGal／引擎创作类 Skill，避免重复触发、相互矛盾的指令和额外上下文开销影响执行效果。也请核对个人与工程范围是否装了多个同名副本。保留原文件及特调；由你决定停用哪一份，安装器不会自动禁用或删除其他 Skill。
