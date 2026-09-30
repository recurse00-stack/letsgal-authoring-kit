# 0.1.3 全面修订记录

2026-09-30 逐项审查原有全部 **20个Skill文件**，并复核安装控制、公开边界、资料与人类说明。依据当前官方正文和实际隔离执行纠正问题；有效内容经核对保留，没有为增加改动量强行改写示例／许可证。旧已发布包和历史凭证保持原字节。

## 确认的纠正

| 原问题 | 当前处理 | 依据与验证 |
| --- | --- | --- |
| callFragment→main 一律报错 | 官方描述冲突标警告，保留既有引用 | [JSON](https://docs.avg-engine.com/reference/script-json)与[调用片段](https://docs.avg-engine.com/manual/writing/blocks/call-fragment)；真实CLI样例 |
| 静态环被称作直接运行失败 | 描述转换期展开风险；增加无环超过30层提示 | 调用片段页；循环／禁用／31层隔离样例，非转换器实测 |
| 前处理被提示加入普通索引 | 识别schedule-preprocessing，不建议加入chapterOrder | [调度](https://docs.avg-engine.com/advanced/chapter-scheduling)；与普通未登记章对照 |
| 未覆盖指令数记作章节数 | 分别报告unsupported_chapters／unsupported_blocks／unchecked_blocks | 一章两块等实际CLI样例 |
| fragments模式被说成检查新字段完整 | 明确只是有限结构，列未覆盖类型／参数／实体／表达式 | 异常标量与缺角色样例可得到零错误，文档不掩盖边界 |
| SDK数字暗示当前宿主配套 | 分开清单要求、自报值、指纹、来源与运行兼容 | 实际EXE和既有SDK只读探测，自报1.21.0不作为2.3配套结论 |
| 扩展定位／修改指导不够准确 | 纯UI不强求npm；源码构建；稳定清单ID；存档／资源等契约入口 | [官方AI指导](https://docs.avg-engine.com/extensions/llms.txt)、[结构](https://docs.avg-engine.com/extensions/project-structure)、[存档](https://docs.avg-engine.com/extensions/save-schema) |
| 制作流程缺变量生命周期与运行入口 | 当前档／跨档／启动重置与扩展session分开，导出验证启动行为 | [变量](https://docs.avg-engine.com/advanced/variables)；本轮未声称宿主实测 |
| 命令隐含工作目录、资料表格及旧当前描述 | 标明完整包根／实际Skill绝对目录；修表格和当前／历史入口 | 文件路径、链接与HTML检查 |

## Skill逐项结果

| 文件 | 结果 | 核对与改动 |
| --- | --- | --- |
| `agents/openai.yaml` | verified-unchanged | 界面入口与能力范围一致，不改调用政策 |
| `examples/选择练习.json` | verified-unchanged | 官方结构／回流与真实CLI读取通过；未运行Studio |
| `LICENSE` | verified-unchanged | 原创MIT原文保留 |
| `references/collaboration-git.md` | changed | 限定路径提交的工作区与索引语义 |
| `references/customization.md` | verified-unchanged | 用户区与工程规则、旧偏好兼容已核对 |
| `references/extensions.md` | changed | 扩展形态、源码／稳定ID、SDK契约、持久化及资源发行 |
| `references/json.md` | changed | 重写结构、序列化、前处理、调用冲突与诊断边界 |
| `references/plugin-skills.md` | verified-unchanged | 资料库、实际安装启用与Agent发现分离已核对 |
| `references/production.md` | changed | 章内／跨章与完整案例、变量生命周期及验证入口 |
| `references/research.md` | changed | 修正表格，明确官方页之间的内容冲突 |
| `references/risk-notice.md` | verified-unchanged | 现有公开风险文本及安装生成一致性保留 |
| `references/safety.md` | verified-unchanged | 原文保护、可逆推进及恢复影响已核对 |
| `references/version-compatibility.md` | changed | SDK要求／自报／来源区分，诊断范围及前处理 |
| `references/versions/beta-2.3.md` | verified-unchanged | 重新核Beta公告及签名缺口，UNKNOWN仍成立 |
| `references/versions/stable-2.0.md` | verified-unchanged | 重新核Stable清单与发布历史，当前文字成立 |
| `scripts/check_project.py` | changed | 纠正误判／计数，增加深度提示，所有路径报告只读边界 |
| `scripts/inspect_version.py` | changed | 有限SDK指纹与自报值分开，来源及兼容状态保持未知 |
| `SKILL.md` | changed | 重写范围、按任务路由与证据／交付闭环 |
| `templates/LETSGAL.example.md` | changed | 补全SDK事实分层及验证入口 |
| `templates/PLUGIN-SKILL.example.md` | changed | 补全来源／版本／指纹，避免虚构配套 |

## 三部分交付

Skill本体 **changed**；辅助安装与说明 **changed**（新版payload，控制脚本／GUI verified-unchanged）；人类Markdown／离线HTML手册 **changed**。没有缺项；这不表示所有客户端、宿主和平台已经运行验收。

当前实际检查见[VALIDATION.md](VALIDATION.md)。独立代理在当前会话用候选Skill完成两个只读任务，核对版本冲突与旧SDK签名缺失；这是有限行为验证，不是Codex／Claude／DSH安装后完整任务。所有官网与SDK结论均带证据层次；网页读取、模拟或类型存在不等于运行通过。

## 保留的不确定性

Beta历史追加签名、超链接／部位和数据列表动作的序列化仍需配套SDK或2.3保存样本。官方JSON与调用片段说明不一致；真实main调用／转换及禁用处理尚未验收。当前工具不能操作Studio原生窗口，Stable／Beta播放、存读档、全新启动和导出、原生安装GUI及完整Agent客户端任务仍未完成。未知部分不猜测补齐。

仅GitHub／社区维护，工坊not-applicable。个人偏好、插件知识、真实作品、内部日志和保护库不进入公开文件。原生运行待办属于验收缺口，不能凭本次静态修订改成通过。
