# 定向查证

字段未知、能力变化或证据冲突时读取。复用工程中仍适用的证据，按问题补齐缺项。

## 先确认能力，再选择做法

能力查询先在[官网功能全景](https://avg-engine.com/studio/features)搜索目标和近义词，再读对应官方用法。例如立绘呼吸／对嘴查网格动画／口型同步，道具面板查数据集合、可视化 UI 与扩展。官网不可达时使用官方文档、目标宿主指导或已核实样本。

功能图汇总最新能力；落到任务时核 **目标版本／平台 → 可用接口 → 实际配置与运行**。只补未知的一层。界面功能查当前工具 schema 确认 MCP 入口，构建系统查 supportedSystems，角色演出查剧情启用方式。

未指定路线时优先复用原生配置、指令和可视化 UI；需要扩展时核真实 ID、版本及本工程启用状态，再为缺口开发程序。标注“官方扩展”的功能仍需检查安装状态。用户明确要求程序开发时沿该目标执行，保留既有系统与源码归属。

标题页／菜单／HUD 可先评估可视化 UI，复杂动态逻辑可用 TypeScript 控制器和 ctx.visualUI；可视化页面不能表达的需求再评估 React。扩展在 Studio 内的丰富设置页优先使用[编辑组件](studio-editor-ui.md)，少量简单字段可以保留自动表单，游戏页面使用[UI](ui-and-data.md)。选型背景见[官方 FAQ](https://docs.avg-engine.com/reference/faq)。

## 按问题选择依据

| 问题 | 优先依据 |
| --- | --- |
| 工具和参数 | 当前状态、tools/list、schema、studio_get_reference |
| 扩展 API／类型 | 目标 SDK 公开导出、sdk/llms.txt；编辑组件另查 studio-ui/README.md |
| 原有数据的保存形式 | 对象原文和同类有效样本 |
| 玩家行为 | 同目标版本的真实运行／交互 |
| 宿主和通道 | [版本边界](version-compatibility.md)、[正式清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-stable.json)／[Beta 清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-beta.json) |
| 官方用法与历史 | [文档](https://docs.avg-engine.com/)、[扩展索引](https://docs.avg-engine.com/extensions/llms.txt)；追溯时查 [Skill 发行](https://github.com/recurse00-stack/letsgal-authoring-kit/releases)／[引擎历史](https://static-lg-studio.cn-gd.ufileos.com/studio/releases-history.json) |

索引失效就从官方导航定位正文；当前宿主指导与旧网页冲突时核对当前 schema、SDK 类型及最小调用。宿主参考也可能滞后：3.0 的 not-exposed 与当前跨系统构建、角色名称翻译接口存在描述差异。构建查 build_read(view="toolchain").desktop.supportedSystems 及配置／dry-run；名称翻译查 l10n_read(view="names") 和 l10n_write 当前 schema。分别核接口支持、真实写入／产物和目标环境运行，记录采用依据。行为与契约冲突时保存最小输入、版本和结果；未声明字段按格式兼容限制处理，承诺支持的行为失败才记为缺陷。

UNKNOWN 写明具体缺项，继续已有证据覆盖的工作。需要补版本依据时定向查询，保留现有宿主和 SDK 要求。可复用结论归所属专题；完整来源、测试过程和未验项归维护记录。
