# Agent 安装位置与兼容范围

本说明对应 **3.0.2 / 20261112-window-visibility**。Stable 载荷 3.0.2 面向 Studio 3.0 正式系列；Beta 载荷 2.9.0 面向 2.9 Beta，并保留 2.8 Beta 兼容路线。Agent 的技能目录与 Studio 版本分别选择：前者决定从哪里加载，后者决定使用哪份资料。

## 安装目录

下表是本安装器的目录规则。`~` 为实际运行 Agent 的用户主目录；安装后用新会话核对加载路径。

| Agent | 个人安装 | 工程安装 | 目录资料 |

| --- | --- | --- | --- |

| Codex | 全新默认 `~/.agents/skills/letsgal-authoring`；唯一已有 `~/.codex/skills/letsgal-authoring` 时沿用 | `<工程>/.agents/skills/letsgal-authoring` | [官方](https://learn.chatgpt.com/docs/build-skills) |

| Claude Code | `~/.claude/skills/letsgal-authoring` | `<工程>/.claude/skills/letsgal-authoring` | [官方](https://code.claude.com/docs/en/skills) |

| Cursor | `~/.agents/skills/letsgal-authoring` | `<工程>/.agents/skills/letsgal-authoring` | [官方](https://cursor.com/docs/skills) |

| GitHub Copilot | `~/.agents/skills/letsgal-authoring` | `<工程>/.agents/skills/letsgal-authoring` | [官方](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) |

| DSH / DeepSeek Harness | `<DSH_HOME>/skills/letsgal-authoring`，未设置时为 `~/.dsh/skills/letsgal-authoring` | `<最近 Git 根或所选目录>/.dsh/skills/letsgal-authoring` | [官方提供器](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md) |

Cursor 的 `.cursor/skills`、Copilot 的 `.copilot/skills` 或 `.github/skills` 等已配置入口，也可通过“其他 Agent / 指定目录”选择。填写 **skills 根目录**，安装器会追加 letsgal-authoring。

Codex 两个个人入口都有同名 Skill 时，先核对客户端实际加载路径，再明确选择一个根。多个个人／项目副本同样按实际作用域和优先级处理，保留原文件以供比较。

## 自定义与远程环境

Studio 或 Agent 的程序安装盘符不决定 Skill 位置。自定义 CODEX_HOME、便携或迁移目录，需要先确认实际 skills 根，再选指定目录；安装器保持 Agent 的发现配置。

Windows 安装器支持 PowerShell 5.1／7。macOS／Linux 使用[手动安装](docs/wiki/08-maintenance.md#查阅手动安装与命令行)。WSL、SSH、容器和云端分别安装到该环境，并复制所需个人资料。

工程制作需要能访问项目文件的 Agent 模式，以及目标 Studio 的 MCP 连接；讨论和草稿可先进行。`agents/openai.yaml` 提供 Codex 的显示信息，正文与相对参考文件由 Skill 入口读取。

## DSH

- 首次建议位置读取安装器进程的 DSH_HOME，未设置时用 `~/.dsh`；命令行 `-DshHome` 优先。提供器另设 dshHome 时选择实际数据目录。

- 项目范围向上查找最近 `.git`，找不到时使用所选目录。官方提供器还支持 `.agents/skills`，本安装器的 DSH 入口使用 `.dsh/skills`。

- DSH 需启用文件系统技能提供器和对应发现根。自定义 customSkillDirs 可用指定目录安装。

- 个人偏好仍位于实际用户主目录的 `~/.letsgal-authoring/preferences/user.md`，插件资料在同一用户区的 plugins/；二者独立于 DSH_HOME。

数据目录来源：[官方解析实现](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/util/home-paths/src/index.ts)。文件提供器 0.2.0-rc.1 已完成隔离发现与正文读取检查；其他版本在实际环境核对。

## 引擎版本与验证

所选通道通过 [Stable 版本工具](channels/stable/skills/letsgal-authoring/scripts/inspect_version.py)或 [Beta 版本工具](channels/beta/skills/letsgal-authoring/scripts/inspect_version.py)路由资料。按主次版本与实际发行身份路由。未登记系列、通道不符、身份缺失或冲突返回 UNKNOWN／退出码 2；补齐依据或按本次许可继续。同系列补丁与热修复不单独阻断。2.5 的完整包在[历史发行](https://github.com/recurse00-stack/letsgal-authoring-kit/releases)。

开始工程操作还要检查版本工具的 `operation_gate`：匹配时静默继续，系列或实际发行身份不匹配时暂停并向当前使用者取得本次范围的明确许可。检查结果按目标实例和任务复用；更新偏好与实际版本分别识别，见[连接与版本 Wiki](docs/wiki/02-connection.md)。

当前已核 Codex 发现、独立任务和双通道安装；Claude Code、Cursor、Copilot 的完整制作任务未在本版执行。具体层次与结果见[验证说明](VALIDATION.md)。安装、更新和恢复统一见[维护 Wiki](docs/wiki/08-maintenance.md)。

