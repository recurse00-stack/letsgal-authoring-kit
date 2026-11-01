# 按问题取得资料

先用当前工程已有样本及已核实资料；同工程、宿主与SDK未变时可复用。纯文字修改不自动联网、查SDK或读取版本历史。字段未知、能力变化或证据冲突时只查相关部分。

## 先确认能力，再选择做法

用户问“能不能做”或尚未确定实现方式时，先在[官网功能全景](https://avg-engine.com/studio/features)搜索目标与近义词，定位功能名称，再进入相关官方用法。比如“静态立绘呼吸／对嘴”查网格动画／口型同步，“道具面板”区分数据集合、可视化 UI 与工坊扩展；不因本 Skill 或工具列表没有同名条目就判定引擎不支持。已有可靠依据的普通修改不重复查询；官网不可达时转用下列文档、目标宿主指导或已核实样本，不把访问失败当作不支持。

功能图注明按最新版本汇总，未逐项限定 Stable／Beta；它是发现入口，不是目标版本的字段、工具或兼容承诺。分清四件事：引擎是否有该功能、当前宿主／平台是否适用、当前接口与权限是否可用、作品中是否实际验证。某层未知只补该层依据；“官网有”“MCP 没有”和“作品已通过”不能互相替代。

未指定技术路线时，先核原生指令、角色／场景配置和可视化 UI 是否满足目标；需要现有扩展时核真实 ID、版本、安装／启用状态及适用范围，最后为缺口开发程序。功能图中“官方扩展”仍需从工坊安装，并不代表已内置或已在本工程启用；不因同名系统替换项目现有实现。用户明确要求程序开发时沿其目标执行，不把此选型顺序变成强制返工。

常规标题页／菜单／HUD 可先核可视化 UI；需要复杂动态逻辑时再评估控制器或程序界面。游戏 UI 与扩展在 Studio 内的设置页／检查器分别查对应专题。作品已有源码、授权与状态归属保持，不为查看能力顺带安装、启用、升级或发布。选型背景见[官方 FAQ](https://docs.avg-engine.com/reference/faq)，具体参数仍以目标契约为准。

## 查找顺序

1. 定位目标和同类已工作的内容，取得真实对象、字段与引用；样本只能证明其保存形式。
2. 看[当前能力](current-capabilities.md)对应主题。通过MCP操作时，当前服务schema／官方指导决定工具参数；扩展开发另查目标SDK公开导出。
3. 从[官方文档](https://docs.avg-engine.com/)导航或定向搜索进入正文。llms.txt失效就用站内导航，不停在404；不凭搜索摘要生成字段。
4. 资料冲突时记录来源、版本和冲突点，不选一页就判已有数据损坏；暂缓依赖未知事实的写入，继续已确认内容与独立草稿。

| 问题 | 资料入口 |
| --- | --- |
| 宿主与通道 | [版本边界](version-compatibility.md)、[正式清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-stable.json)、[Beta清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-beta.json) |
| 字段／选项／变量 | [JSON](https://docs.avg-engine.com/reference/script-json)、[Branch](https://docs.avg-engine.com/manual/writing/blocks/branch)、[变量](https://docs.avg-engine.com/advanced/variables) |
| 跨章与蓝图 | [章节调度](https://docs.avg-engine.com/advanced/chapter-scheduling) |
| 扩展接口 | [扩展AI索引](https://docs.avg-engine.com/extensions/llms.txt)、[运行时接口](https://docs.avg-engine.com/extensions/api-context)与目标sdk/index.ts |
| 协作／恢复 | [协作](https://docs.avg-engine.com/manual/overview/collaboration)、[项目历史](https://docs.avg-engine.com/manual/overview/history)、[时光机](https://docs.avg-engine.com/manual/overview/backup) |
| 旧版追溯 | [发行历史](https://github.com/recurse00-stack/letsgal-authoring-kit/releases)、[引擎公告历史](https://static-lg-studio.cn-gd.ufileos.com/studio/releases-history.json)，仅在任务需要时查 |

官网手册、公告、SDK声明、保存样本和运行结果是不同证据。Beta公告不是完整参数规范；旧版观察不自动成为当前版结论。证据缺失用UNKNOWN说明具体缺项，不把整个任务一并阻断。

需要长期复用的结论写回项目已有说明：主题、完整链接、查阅日期、适用版本、所用字段与实际验证层次。保留必要结论，不复制整站、公告全集或私密过程到公共Skill。离线资料标明日期，不能为补资料自动升级宿主或降低SDK要求。
