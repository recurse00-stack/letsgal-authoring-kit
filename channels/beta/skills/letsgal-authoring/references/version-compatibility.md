# Beta 当前维护边界

本载荷登记 **2.9.0-beta.1** 与 **2.8.0-beta.1**；Skill 发行号为 0.2.8。按专题的版本条件取用，2.9 选择示例只用于 2.9。

宿主证据取目标运行实例、关于页或 EXE FileVersion；项目格式／作品版本保留原值。扩展另外核 SDK 来源和要求。

`scripts/inspect_version.py` 保留 --studio-version、--studio-exe、--project-version、--channel、--sdk：

- 已登记目标且无冲突：reference_selected／退出码 0，路由到[能力索引](current-capabilities.md)。
- 缺失、冲突或未登记版本：UNKNOWN／退出码 2，按原因补查资料，继续已有证据覆盖的工作。
- --project-version 只传项目明确固定的目标引擎版本。

通道不匹配时选择对应载荷；多个通道工程可用项目范围安装并核实际发现优先级，同一位置保留一份同名入口。版本选择只负责资料路由；升级、迁移与发布按任务授权执行。

查目标资料用[正式清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-stable.json)、[Beta 清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-beta.json)或[旧发行](https://github.com/recurse00-stack/letsgal-authoring-kit/releases)。运行兼容按目标版本实测记录判断。
