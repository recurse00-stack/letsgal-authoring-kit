# Harness 适配边界

源码0.1.5候选，尚未发布；当前GitHub发布仍为0.1.4。下述目录选择修订属于候选安装器，历史验收按实际版本分别记录。

手动导入前阅读 [风险说明与免责声明](skills/letsgal-authoring/references/risk-notice.md)，完整复制 Skill 目录以保留随包说明；导入不授予 AI 额外文件权限。

Agent 的导入目录兼容与 LetsGal 引擎版本兼容分别判断。稳定版、Beta、旧工程和未知版本均走 [项目版本规则](skills/letsgal-authoring/references/version-compatibility.md)，不以“最新版文档”替代目标宿主证据。下表只说明 Agent 的技能入口。

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

必须使用具有项目文件访问能力的模式；只在普通聊天里贴技能文字不赋予编辑器控制能力。`agents/openai.yaml` 只提供 Codex 界面元数据，核心工作流不依赖它。未硬编码任何一家工具的函数名、模型或 MCP 地址。

工具目录有跨客户端发现时，同名个人／项目／其他 harness 副本可能同时出现。不要为去重删除未知副本；先看客户端的加载列表、作用域与优先级。

本安装器面向 Windows PowerShell 5.1／PowerShell 7。macOS／Linux 可手动复制技能目录和 user.md；此版没有宣称在这些系统上验证了安装程序。云端／容器须在该环境单独配置，个人本机目录不会自动上传。

用户配置文件结构约定版本为 1：只含 Markdown，自定义内容原样读取。此版安装器不做迁移和重写；未来若需要迁移，应采用有版本、备份、可审查差异的流程，不静默重置。

## 当前引擎资料路由

[只读版本工具](skills/letsgal-authoring/scripts/inspect_version.py)对已核实的 2.0.0／2.0.1 选择 Stable 资料，对 2.3.0-beta.1 选择 Beta 资料；缺失／冲突／其他版本返回 UNKNOWN，不推定兼容。资料实现、EXE 版本读取、SDK 指纹与真实宿主运行分别记录，见 [验证范围](VALIDATION.md)。下载清单与发布历史可能不同，选择不依赖“最新”标签。安装主 Skill 不嵌套为自己的插件。

## DSH

已对本机安装的 DSH 0.1.6-alpha.2 所带官方 `@deepseek-ai/dsh-skill-filesystem` 进行隔离发现与正文读取测试；没有向真实服务导入，也没有调用模型。

- 个人导入采用界面指定／上次保存的位置；首次从安装器进程的 `DSH_HOME` 读取，未设时建议 `~/.dsh`。这只是默认值，不表示检测到了正在运行的 DSH。命令行显式 `-DshHome` 优先于环境变量。
- 如果启动器或提供器配置另设了 `dshHome`，请在界面选择对应数据目录。支持 `~` 展开，其余路径须为绝对路径。不扫描账号、配置内容或全部磁盘来猜位置。
- 项目目录按 DSH 官方算法向上寻找最近的 `.git`（目录或文件），找不到时使用所选目录。界面与安装后端共用同一套解析代码。
- 官方提供器也支持 `.agents/skills`；本包的 DSH 入口明确使用 `.dsh/skills`。同名项目技能优先于个人技能，另有副本时先核对实际来源，不自动删掉它们。
- DSH 必须已启用文件系统技能提供器，且没有关闭默认根目录；使用自定义 `customSkillDirs` 时可选“其他 Agent / 指定目录”导入到已配置的根目录。安装器不编辑 DSH 预设，不启动／重启 DSH。
- 技能内容与相对参考文件可读取，不依赖特定模型或 MCP。个人偏好仍在实际运行 AI 的用户主目录 `~/.letsgal-authoring/preferences/user.md`（旧版根目录 user.md 继续兼容），不随 DSH_HOME 搬入公共技能；插件 Skill 独立放在同一用户区的 plugins/ 中，由主 Skill 按项目需要读取。

DSH 来源：[文件系统技能提供器](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md)、[数据目录解析](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/util/home-paths/src/index.ts)。

## 当前候选与历史检查点

2026-10-01最终交付核对：最新四份参考资料已按原绑定同步，公共源码／自用维护／原Codex加载副本21个载荷文件逐字节一致。完整包后端安装备份了全部22个旧安装文件，26个非安装器个人文件保留；安装后Check返回current、matches_bundle=true。官方app-server在两个目录强制刷新，均发现唯一启用的原用户入口；未添加发现根或改用户配置。版本号相同不能替代逐文件校验。

当前候选显式制作任务正常结束，170.516秒、exit 0、turn.completed，独立22项核对通过：只改空白副本main，两个选项以原生vars字面量样本分别设为42／7；ID、未知字段、变量声明与其他26个原文件保留。只读检查0错误／3警告，实际EXE路由为2.3.0-beta.1，故意版本冲突返回UNKNOWN，任务SDK仍UNKNOWN。新章节尚未实际播放，此结果是有限制作与资料路由验收。

另以技能名调用原安装入口完成69.125秒只读任务，独立10项核对通过；执行记录证明实际读取入口及四份最新资料，正确说明字符串aLit、追加历史不自动恢复和版本／SDK证据边界。它证明当前安装资料被模型读取，不是完整制作到播放验收。较早累计公告、0.1.4制作到播放及失败尝试仍按原检查点记录，不能替代当前结果。渠道发布与匿名下载另见GitHub和发行附件。

## 当前验收分级

2026-10-01，已安装0.1.4补验：新鲜官方Codex app-server在两个工作目录自然发现唯一启用的原用户入口；未添加发现根或变更用户目录。随后仅以技能名进行真实Codex CLI最小制作任务，618.707秒正常完成，退出码0、最终事件`turn.completed`，独立29项核对通过。此前显式读取候选路径的任务另记，不能代替本次发现证据；这些结果不计作0.1.5完整模型任务通过。详见[验证报告](VALIDATION.md)。

本次模型生成的钟楼／水井两条路线分别从main入口在实际2.3.0-beta.1播放，开场、选择、各自旁白及公共返回均正确，形成已安装0.1.4的有限制作到播放链。执行到结束章指令后的画面空白与Studio“运行中”状态分别记录，不能从文字播放正确推定完整调试终态、独立玩家或导出通过；该历史播放任务不覆盖当前0.1.5新生成章节。

DSH有官方provider隔离读取证据，完整模型任务及更新后自动发现仍未验证；Claude Code、Cursor、Copilot为格式／目录适配。Stable真实运行仍有缺口；本轮Beta重启快读、Windows／Web玩家与导出、官方配套SDK历史API已取得有限证据，完整持久状态及其他新功能仍未全验，详见HOST-VALIDATION.md。命令存在、目录被发现、模型实际使用和宿主运行分别记录，不相互替代。

建议安装或启用本技能前，在 Agent 的技能设置中暂时停用其他功能重叠的 LetsGal／引擎创作类 Skill，避免重复触发、相互矛盾的指令和额外上下文开销影响执行效果。也请核对个人与工程范围是否装了多个同名副本。保留原文件及特调；由你决定停用哪一份，安装器不会自动禁用或删除其他 Skill。


初稿0.1.5曾按原绑定同步，并在两个目录官方强制刷新发现唯一启用原入口；当时仅元数据变化，完整模型任务未重跑。当前又新增Beta累计差异与证据规则，自动发现及完整模型任务须按当前内容另记，不能无条件继承初稿结论。

累计公告整理阶段21文件同步后，曾通过两目录官方app-server强制刷新，原用户入口唯一启用；这是历史检查点；最终同步／发现及模型补验另见本节开头。模型任务当时未重跑；有限Beta原生／SDK／导出结果及剩余缺口在宿主记录单列。公告覆盖2.1／2.2不代表版本工具新增该宿主路由，这些完整版本仍返回UNKNOWN。

2026-10-01继续补验：同一Beta的合成副本原生创建slot数值变量、切换选项变量操作并赋值42；调试与新桌面玩家点击通过。桌面正常完全退出后分别快读／读取普通槽位1，剧情位置、变量42及双图层场景恢复，三条扩展追加历史均未恢复。仅有限配置和两个存档，不能推为全部持久状态。Skill与人类手册changed，安装程序verified-unchanged，完整包／说明／校验随修订更新；原生安装测试另按人工反馈与文件读回分层记录。未发布新版本。
