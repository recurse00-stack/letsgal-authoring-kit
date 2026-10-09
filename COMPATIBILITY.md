# Harness 适配边界

安装时先按目标工程选择正式版或Beta载荷，同一位置只保留一份同名Skill。正式版保持原生／离线流程；Beta优先获准的官方MCP，未启用时保留文件／原生流程。MCP是可选能力，安装Skill不注册服务。直接写磁盘前关闭目标工程；当前实例状态、工具目录和批准分别核对，见[Beta MCP工作流](channels/beta/skills/letsgal-authoring/references/mcp-workflow.md)。

本说明对应0.2.1。Windows安装程序新增正式版／Beta选择和切换，原有目录选择与个人区保留机制继续使用；所选载荷按完整宿主版本选择资料，未知或冲突标UNKNOWN，运行证据按实际宿主记录。

手动导入前阅读 [风险说明与免责声明](channels/beta/skills/letsgal-authoring/references/risk-notice.md)，完整复制 Skill 目录以保留随包说明；导入不授予 AI 额外文件权限。

Agent的导入目录兼容与LetsGal引擎版本兼容分别判断。安装后按所选通道的[正式版规则](channels/stable/skills/letsgal-authoring/references/version-compatibility.md)或[Beta规则](channels/beta/skills/letsgal-authoring/references/version-compatibility.md)读取版本资料；通道不符先改装对应载荷，未知继续无版本依赖工作，不以“最新版文档”替代宿主证据。下表只说明Agent技能入口。

2026-09-30 按当前官方目录文档重新复核；DSH 安装 provider 的运行结果仍是注明版本的历史证据。以下为当前格式／目录适配，不代表全部客户端版本、远程环境或真实 AI 行为均已验收。

| 本地工具 | 个人安装 | 工程安装 | 核对来源 |
| --- | --- | --- | --- |
| Codex | 全新默认 `~/.agents/skills/letsgal-authoring`；唯一已有 `~/.codex/skills/letsgal-authoring` 时沿用旧入口 | `<工程>/.agents/skills/letsgal-authoring` | [官方](https://learn.chatgpt.com/docs/build-skills) |
| Claude Code | `~/.claude/skills/letsgal-authoring` | `<工程>/.claude/skills/letsgal-authoring` | [官方](https://code.claude.com/docs/en/skills) |
| Cursor | `~/.agents/skills/letsgal-authoring` | `<工程>/.agents/skills/letsgal-authoring` | [官方](https://cursor.com/docs/skills) |
| GitHub Copilot | `~/.agents/skills/letsgal-authoring` | `<工程>/.agents/skills/letsgal-authoring` | [官方](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) |
| DSH / DeepSeek Harness | `<DSH_HOME>/skills/letsgal-authoring`，未设时为 `~/.dsh/skills/letsgal-authoring` | `<最近 Git 根或所选目录>/.dsh/skills/letsgal-authoring` | [官方](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md) |

`~` 是实际运行Agent的用户主目录，发行包不固定作者的用户名、盘符或绝对路径。Codex个人安装仅有一个已存在的 `letsgal-authoring` 入口时沿用它；`.agents/skills` 和 `.codex/skills` 两处都已有时拒绝自动选择。先核对客户端实际加载路径，再选“其他 Agent / 指定目录”明确一个已配置的 `skills` 根目录；不迁移或另建副本。

Cursor 也支持 `.cursor/skills`，Copilot 也有 `.copilot/skills`（个人）和 `.github/skills`（工程）。这里选共用路径，是安装器设计选择，不宣称其他路径无效。自定义目录可浏览或粘贴，安装器追加 `letsgal-authoring`；导入本包 Skill、创建缺失用户区并保存安装记录，不为Agent修改发现配置。工程范围可浏览或填写工程目录。

### 软件位置与自动定位范围

软件的 EXE 安装目录不参与 Skill 目录解析。Agent 或 LetsGal 安装到其他盘、技能目录仍为标准位置时，按上表安装即可。Windows 安装器按运行它的用户主目录定位，请与 Agent 使用同一用户／环境；界面显示的是安装目标，不是对运行中 Agent 的数据目录检测结果。

安装器不会自动解析自定义 `CODEX_HOME`、扫描便携／迁移目录或读取 Agent 配置来猜位置。这些情况先核对 Agent 实际读取的 `skills` 根，再选“其他 Agent / 指定目录”；不选程序文件夹或末级 `letsgal-authoring`。DSH 的首次进程环境默认值及保存选择见下文。自选目录不修改 Agent 的发现设置；文件校验通过后仍须在新会话核对实际来源。

必须使用具有项目文件访问能力的模式；只在普通聊天里贴技能文字不赋予编辑器控制能力。`agents/openai.yaml` 只提供 Codex 界面元数据，核心工作流不依赖它。官方 MCP 工作流按当前服务的工具名和 schema 适配，不固定模型或作者本机地址；无 MCP 的使用方式保持可用。

工具目录有跨客户端发现时，同名个人／项目／其他 harness 副本可能同时出现。不要为去重删除未知副本；先看客户端的加载列表、作用域与优先级。

本安装器面向 Windows PowerShell 5.1／PowerShell 7。macOS／Linux 可手动复制技能目录和 user.md；此版没有宣称在这些系统上验证了安装程序。云端／容器须在该环境单独配置，个人本机目录不会自动上传。

用户配置文件结构约定版本为 1：只含 Markdown，自定义内容原样读取。此版安装器不做迁移和重写；未来若需要迁移，应采用有版本、备份、可审查差异的流程，不静默重置。

## 当前引擎资料路由

两份载荷各有只读版本工具：[正式版](channels/stable/skills/letsgal-authoring/scripts/inspect_version.py)只选择已核实的2.0.0／2.0.1／2.5.0资料；[Beta](channels/beta/skills/letsgal-authoring/scripts/inspect_version.py)只选择2.3.0-beta.1／2.4.0-beta.1／2.4.0-beta.2／2.5.0-beta.1／2.6.0-beta.1资料。通道不符、缺失、冲突或未登记版本返回UNKNOWN，不推定兼容。资料实现、EXE读取、SDK指纹与真实运行分别记录，见[验证范围](VALIDATION.md)。下载清单与发布历史可能不同，不依赖“最新”标签。主Skill不嵌套为自己的插件。

## DSH

2026-10-05重新测试实际DSH0.2.0-rc.1所带官方 `@deepseek-ai/dsh-skill-filesystem`：26项隔离发现与正文读取通过。0.1.6-alpha.2保留为历史证据；provider读取和完整模型任务分别记录，不将它称为模型通过。

- 个人导入采用界面指定／上次保存的位置；首次从安装器进程的 `DSH_HOME` 读取，未设时建议 `~/.dsh`。这只是默认值，不表示检测到了正在运行的 DSH。命令行显式 `-DshHome` 优先于环境变量。
- 如果启动器或提供器配置另设了 `dshHome`，请在界面选择对应数据目录。支持 `~` 展开，其余路径须为绝对路径。不扫描账号、配置内容或全部磁盘来猜位置。
- 项目目录按 DSH 官方算法向上寻找最近的 `.git`（目录或文件），找不到时使用所选目录。界面与安装后端共用同一套解析代码。
- 官方提供器也支持 `.agents/skills`；本包的 DSH 入口明确使用 `.dsh/skills`。同名项目技能优先于个人技能，另有副本时先核对实际来源，不自动删掉它们。
- DSH 必须已启用文件系统技能提供器，且没有关闭默认根目录；使用自定义 `customSkillDirs` 时可选“其他 Agent / 指定目录”导入到已配置的根目录。安装器不编辑 DSH 预设，不启动／重启 DSH。
- 技能内容与相对参考文件可读取，不依赖特定模型或 MCP。个人偏好仍在实际运行 AI 的用户主目录 `~/.letsgal-authoring/preferences/user.md`（旧版根目录 user.md 继续兼容），不随 DSH_HOME 搬入公共技能；插件 Skill 独立放在同一用户区的 plugins/ 中，由主 Skill 按项目需要读取。

DSH 来源：[文件系统技能提供器](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md)、[数据目录解析](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/util/home-paths/src/index.ts)。

## 目录适配与实际使用证据

| 层次 | 当前已有证据 | 不能据此推定 |
| --- | --- | --- |
| 标准格式／目录 | 上表五款 Agent 的官方资料与本包路径规则 | 所有客户端版本、远程配置都能自动发现 |
| Codex实际使用 | 旧技能名制作／发现记录保留；0.2.0当前模型与安装入口按本版验证摘要核对 | 单次制作不能保证所有模型、作品或宿主 |
| DSH provider | 0.2.0-rc.1官方文件系统提供器26项隔离发现和正文读取，旧0.1.6-alpha.2保留历史 | 完整模型任务、更新后新会话调用 |
| Claude Code、Cursor、Copilot | 格式与目录资料适配 | 完整模型制作或宿主播放 |
| 安装程序 | 历史 Windows 后端安装／升级／保留验证，0.1.5 路径和 WPF 组件检查 | 原生浏览、取消、全流程和所有缩放通过 |

0.2.0整理正式版2.5.0制作／排错指引，安装程序保持原字节；文件、安装和真实宿主证据见[验证报告](VALIDATION.md)，旧模型任务不计为本版新实测。

使用时根据实际 Agent 核对发现设置与权限，然后完成一个当前工程的小任务。其余 Agent 和平台测试是补充覆盖，Skill 不要求先通过所有环境才可使用或发布。

建议在 Agent 设置中暂时停用功能重叠的 LetsGal／引擎创作 Skill，保留原文件及特调；安装器不会自动禁用或删除其他技能。
