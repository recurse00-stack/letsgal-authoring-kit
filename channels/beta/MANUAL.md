# Beta Skill 使用指南 · 0.2.6

适用 **Studio 2.8.0-beta.1**，发行修订 **20261031-studio-ui**，Authoring Kit 版本为 0.2.6。完整安装见[总手册](../../MANUAL.md)。

## 安装与开始使用

完整解压后运行 Install.cmd，选择 Beta、实际 Agent 和安装范围；同一位置只安装一份同名 letsgal-authoring。更新先保全旧安装，个人偏好与插件知识保留，不升级引擎。新会话核实际读取路径、通道及宿主版本；未知版本继续无版本依赖的讨论／草稿，接口用法另补依据。

命令行在包根运行 `powershell -NoProfile -ExecutionPolicy Bypass -File .\Install.ps1 -Harness Codex -Scope User -Channel beta -NonInteractive`；检查另加 `-Action Check`。其他平台按[手动安装](../../MANUAL.md#手动安装与命令行)复制本通道完整载荷。

## 按任务使用

主入口只负责选专题。一次制作不必先读全部能力，也不要求把整套引擎重新验收。

| 任务 | 方法与专题 |
| --- | --- |
| 改几句对白 | 从原富文本改目标文字，保留 ID、配音和演出；[MCP 执行](skills/letsgal-authoring/references/mcp-workflow.md) |
| 分支、变量、翻译、配音 | 核实际入口、状态范围、源哈希和语言覆盖；[剧情与配音](skills/letsgal-authoring/references/story-and-voice.md) |
| 立绘、动画、场景与媒体 | 核导入的实际路径、定义、引用、变化与退出；[素材与舞台](skills/letsgal-authoring/references/stage-and-assets.md) |
| 演出段 | 核时间单位、轨道、段尾和重播副作用；[时间轴](skills/letsgal-authoring/references/performance.md) |
| 按钮页面、主题与表数据 | 区分文档／系统槽位、本地状态／游戏数据；[UI 与数据](skills/letsgal-authoring/references/ui-and-data.md) |
| 看效果、完整调试或导出游戏 | 核真实位置、输入和终态，构建后另测运行；[预览与构建](skills/letsgal-authoring/references/preview-and-build.md) |
| 扩展开发 | 核参数声明、目标 SDK 及实际调用；[扩展开发](skills/letsgal-authoring/references/extensions.md) |
| 扩展设置页、方法检查器 | 按需读取 [Studio 编辑界面](skills/letsgal-authoring/references/studio-editor-ui.md)，保留变量绑定、只读与原存值；游戏 UI 使用前述 UI 专题 |
| 多人房间 | 先核个人设置／索引中的启用状态及宿主范围，再按需加载独立 letsgal-collaboration；暂停时跳过，通用制作继续 |

## 一次完整的小修改

例如：“做一个灯光开关页面，点击能切换提示，关闭后回到当前剧情；不要替换标题页。”

AI 先核工程及相关内容，复用或建立覆盖改动的恢复点，创建独立文档并使用返回的真实文档名。读回和校验后，在实际预览点击按钮，检查状态提示、关闭返回和重开初值；不能只改变初值截图就说点击通过。最后给出页面入口、检查结果和恢复方式。

讨论草案不自动写入工程；明确委托后，范围内的可逆步骤连续完成。“已采用”的内容按已有正文保护，恢复能力不扩大修改授权。

## 确认与恢复

“每次写入确认”和高影响、删除、恢复、主题应用等类别分别生效。关闭前者后仍可能弹出类别确认；AI 应说明具体操作，等待宿主批准后继续，不额外逐句询问或改变确认设置。[宿主确认](skills/letsgal-authoring/references/mcp-workflow.md#宿主确认)

临时预览语言、主题或配置先记录原值，结束恢复该值而非统一重置默认；期间发生后来编辑时先核对并保留新值。恢复要核实际状态。原来未显式选择样式时，仅再选同名样式未必完全恢复；优先限定本次文件／对象，保留后来编辑。撤销成功也需读回原 ID 和引用。素材不在现有恢复点覆盖范围时补保护。

## 连接异常与临时素材清理

AI 发现不到 MCP 工具时，先定向发现并尝试原生调用；成功立即继续任务。确实不可调用时，核对影响后尝试一轮当前客户端提供的单服务器重连，再用真实工具核验；仍失败时说明原因并询问是否允许 Computer Use 托底。没有单项重连接口时不能假称已重连，也不能直接重启整个应用或跳到界面操作。权限拒绝与工具发现故障分别处理。

建连时的“请求路径不对”可能来自认证元数据探测；只凭红字不能认定断线。GIF／WebP 占用导致撤销、删除失败时，先确认是否部分完成，登记本轮临时文件的实际路径、哈希、素材 ID 和新建／复用来源；待工作允许后保存关闭，严格按清单核对、删除并读回。全部处理完成后清除无用途的暂存、重复清单和脚本，保留精简结果与必要恢复资料，避免误删原有素材或漏掉失败残留。分别见[连接恢复](skills/letsgal-authoring/references/troubleshooting.md)与[精确清理](skills/letsgal-authoring/references/asset-cleanup.md)。漏记清单须凭历史及文件证据补录；等待关闭、证据不足和失败不计作完成，唯一有效恢复副本保留。

上述处理指引不等于引擎缺陷已经修复。

## 当前证据与限制

本版补充 Studio 编辑界面专题，并修正设置命名及界面／数据职责。新增类型与隔离验证范围见总包报告；既有宿主证据仍按原对象和版本复用，不新增引擎运行通过项。UI 实际按钮、序列帧／网格、翻译、限定文件恢复、Web 构建及取消等已有有限证据；语音识别 BUSY、普通扩展参数校验缺口、数据行撤销异常和高级调度定位限制仍保留。

远端收讫、Live2D、真实听感、独立 Player、存读档与导出游戏运行尚未验收。Web 构建成功和运行游戏是不同结果。完整范围见[验证说明](../../VALIDATION.md)及[宿主证据](../../HOST-VALIDATION.md)。
