# Beta当前维护边界

本载荷仅登记 **2.6.0-beta.1**；0.2.1是Skill发行号。2026-10-10核对官方清单，当前内容已按主题融合，不要求先读旧版本增量。

按目标工程约定与实际Studio完整版本／通道核对，运行实例、关于页或EXE FileVersion可作宿主证据。project.json中的version／engineVersion及SDK自报值不必是宿主版本，保留原值；扩展另外核SDK来源。

scripts/inspect_version.py支持原有--studio-version、--studio-exe、--project-version、--channel、--sdk。本目标且无冲突时返回reference_selected／退出码0，并指向[当前能力](current-capabilities.md)；其他版本、缺失或冲突返回UNKNOWN／退出码2，说明具体原因。输出和退出码只表示资料选择，不证明运行兼容。

旧版和未知新版不套用当前版本专属结论，也不自动升级、迁移或换通道。先继续讨论、读取、草稿及已有证据覆盖的工作；确需该版本能力时再查目标资料或[旧发行](https://github.com/recurse00-stack/letsgal-authoring-kit/releases)。新版本不能仅按版本号大小推断兼容。

通道不匹配时提示选择对应载荷；同时维护不同通道工程可用项目范围安装，核实际发现优先级，同一位置不并装两个同名入口。历史资料留在维护归档与旧包，不进入日常载荷。

[正式清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-stable.json) · [Beta清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-beta.json)。官网资料、目标样本、SDK和运行分别标明证据；无证据时不猜字段。
