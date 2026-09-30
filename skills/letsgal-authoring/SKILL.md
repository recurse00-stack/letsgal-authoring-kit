---
name: letsgal-authoring
description: 在 LetsGal Studio 工程中制作剧情、分支、章节 JSON、变量、素材与扩展，排查格式和流程，并维护相关插件 Skill。依据目标工程、宿主版本、官方文档及实际样本工作；不把一般创作讨论自动升级为工程修改。
metadata:
  version: 0.1.3
---

# LetsGal 创作与维护

这是社区 Skill，提供可复用的制作方法和资料入口，不包含引擎、SDK、模型或 MCP。用户当前需求决定交付形式；讨论、文字草稿、章节源文件、扩展构建和可运行游戏分别交付与验收。

## 进入当前工程

- 读取用户指定工程的规则和简短当前状态，定位 `project.json` 或扩展的 `extension.json`。只展开本次相关章节、实体与配置，不把 Studio 安装目录、Skill 目录或别的作品当工程。
- 按[本地定制](references/customization.md)读取实际用户主目录的 `.letsgal-authoring/preferences/user.md`，兼容旧 `user.md`；读取工程已有 `LETSGAL.md`。具体工程选择优先于个人一般偏好；用户当前要求优先。缺少这些文件可以直接工作，不强制新建体系。
- 写版本相关字段或代码前，按[版本与证据](references/version-compatibility.md)核对实际 Studio 完整版本、通道、工程调度及相关 SDK。可用 `scripts/inspect_version.py` 选择资料；版本缺失或冲突保留 UNKNOWN，继续无版本依赖的工作。不得把本机 Beta 设成其他项目默认。
- 按[官方资料查找](references/research.md)查到具体字段与行为。当前网页不是所有旧版本的保证，官方页面之间也可能冲突；先保留原结构和未知字段，不能用一个未核实示例批量“修复”作品。

## 按任务读取

| 当前任务 | 入口与重点 |
| --- | --- |
| 制作或修改一个可玩片段 | [制作流程](references/production.md)：章内回流、跨章调度、变量生命周期及观察结果 |
| 章节源 JSON、引用、序列化或检查器诊断 | [JSON 工作法](references/json.md)：区分生成约定、兼容读取及文档冲突 |
| 扩展程序、界面、数据库、资源或存档 | [扩展开发](references/extensions.md)：以实际 SDK 查签名，在源码实现并构建 |
| 分析插件、生成插件使用 Skill | [用户插件知识](references/plugin-skills.md)：版本化资料库与真实安装／启用分开 |
| 多作者、Git、冲突和交接 | [协作与 Git](references/collaboration-git.md)：共享文件单一写入者，保留 HEAD／索引及既有改动 |
| 个人习惯和作品选择 | [本地定制](references/customization.md)，需要时参考[工程模板](templates/LETSGAL.example.md) |

不要每次预读全部参考文件。找不到字段、真实 ID、素材或参数依据时，明确缺项并继续独立工作，不编造接口。

## 修改与验证

写前按[安全操作](references/safety.md)核对可写范围和受影响原文，确认没有另一作者正在保存。首次工程写入的关键风险说明及完整[风险文本](references/risk-notice.md)随包保留；已说明且范围未变时不重复宣读，也不要求每个可逆步骤重新确认。

仅修改此次需要的对象，保留未知字段、稳定 ID、原编码和他人的改动。新示例的 ID 需重新生成并同步引用。保存后重读差异，验证本次可观察行为：路线、状态变化、失败情况、返回／重入；涉及持久数据时再查存读档和全新启动。

可选只读检查：`python "<实际 Skill 绝对目录>/scripts/check_project.py" "<章节文件或工程目录>"`，Python 3.9+ 标准库。它只查有限结构，不能验证全部参数、变量、资源、蓝图或真实运行；`--format fragments` 也不是完整 schema。未知布局用 `--format json-only` 只查语法。具体退出码和诊断见 JSON 工作法。

使用当前可用文件工具和宿主工具。没有编辑器控制能力时仍完成已授权静态工作并给出人工预览步骤，不能声称已播放。官方 MCP 可按实际提供的来源、工具与权限使用；不固定未知工具名，不为普通任务自行恢复或部署工具。

交付说明修改与玩家行为、实际验证层次、未完成项及恢复入口，复用工程已有记录。文件安装、Agent 发现／实际读取、Studio 加载、播放、存读档和导出分别记结果。

跨项目偏好只在用户明确要求时记入个人区；作品选择写工程入口。插件 Skill 默认保存到 `.letsgal-authoring/plugins/<插件ID>/<版本>/SKILL.md`，主 Skill 按项目读取；它不是插件运行时，也不等于 Agent 独立发现。主 Skill 本身仍用主 Skill 安装器安装，不能嵌套成自己的子插件。
