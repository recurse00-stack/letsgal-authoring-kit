# 定向查证

复用当前工程已有且仍适用的证据；纯文字修改不自动联网、查 SDK 或翻版本历史。只在字段未知、能力变化或证据冲突时查对应部分。

## 按问题选择依据

| 问题 | 优先依据 |
| --- | --- |
| 当前可调用工具与参数 | 当前 Studio 的状态、tools/list、schema 和 `studio_get_reference`；网页按钮不能推定 MCP 操作 |
| 扩展 API 与类型 | 目标 SDK 公开导出、sdk/llms.txt；编辑 UI 查 studio-ui/README.md，与实际宿主分别核版本 |
| 原有数据怎样保存 | 当前对象原文和同类工作样本；样本仅证明保存形式，不证明运行正确 |
| 玩家实际行为 | 同一目标版本的真实交互／运行结果；静态与声明不能代替 |
| 宿主和通道 | [版本边界](version-compatibility.md)、官方[正式清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-stable.json)／[Beta 清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-beta.json) |
| 公开说明与旧版追溯 | [官方文档](https://docs.avg-engine.com/)、[扩展索引](https://docs.avg-engine.com/extensions/llms.txt)、必要时才查[发行历史](https://github.com/recurse00-stack/letsgal-authoring-kit/releases)／[引擎历史](https://static-lg-studio.cn-gd.ufileos.com/studio/releases-history.json) |

先用本 Skill 的对应专题定位，再读官方正文；索引失效就用站内导航，不停在 404 或凭搜索摘要生成字段。当前宿主生成的指导与旧网页冲突时优先当前契约；真实行为与声明不符则保留两者和复现范围，不能静默把异常当规范。

证据标明来源、版本与层次。未知项用 UNKNOWN 说明具体缺口，只暂停依赖它的部分，继续独立工作；不能为补资料自动升级宿主或降低 SDK 要求。

需长期复用的结论写回所属工程已有说明，记录主题、完整链接、日期、适用版本、字段和验证范围；公共 Skill 留可复用操作知识，不复制公告全集、测试流水账或私密过程。
