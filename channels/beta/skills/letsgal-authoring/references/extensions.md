# 扩展开发：从契约到宿主验证

实现路线未定时查[选型](research.md#先确认能力再选择做法)。修改方法先读[参数](#参数与校验)，涉及存档再读[恢复](#运行状态与恢复)，制作 Studio 内界面时读[编辑组件](studio-editor-ui.md)。

## 确定源码与目标 SDK

1. 从 extension.json 核清单 ID、源码关联及内部模块 ID，保留既有标识和命名空间。定位源码、Studio 关联、发行快照，只改本次目标；源码缺失时先补来源。
2. 程序开发读当前 `studio://dev/extension-guide`（topic=`dev-extension-guide`）或目标 sdk/llms.txt，使用该工程 SDK 的公开导出。记录宿主完整版本、sdkVersion 要求、SDK 自报版本和同步来源；缺项[定向查证](research.md)。纯可视化扩展可直接使用其配置和 UI。
3. 新扩展通过 ext_enable 的 create／init_program 取得真实 ID；需要编辑界面时用 `init_program(studioEntry=true)`。已有程序按[入口与构建](studio-editor-ui.md#入口与构建)补组件依赖后同步 SDK。
4. 按生成项目的实际 package scripts 构建，保留既有定制及 React／React DOM／SDK 外置单实例配置，再到目标宿主验证。

## 参数与校验

写调用前用 `ext_read(view="methods")` 取声明，核 method ID、可用键、必需项／默认值、类型、枚举、范围和资源引用；确定是普通调用还是条件，参数使用字面量还是变量。

| 参数／配置 | 实施规则 |
| --- | --- |
| list | 声明 item；行字段限 string、number、boolean、enum、asset、character，保持单层列表。检查行数及每格约束 |
| data | default 必填且非 null，类型由 default 推导；需要精确空数组类型时显式声明 |
| list／data 的赋值 | 提交字面量；这两种类型不绑定变量 |
| validate | 使用带参数类型的箭头函数，如 `validate: (value: unknown) => ...`，按契约返回 true／false／错误提示 |
| 运行约束 | list 行数范围由编辑／MCP 检查；data.validate 运行失败只告警仍执行。影响业务状态完整性的约束在运行实现中处理 |
| inspectorLayout | schema 仍平铺传给 run；tabs 与顶层 groups 二选一，fields／summaryFields 引用原字段，保留方法 ID |
| 参数预设 | settingsKey 指向 array 设置，行含 id／name／paramsJson。保存整套参数，应用时按 preserveFields 保留指定值 |

完成输入检查后 dry run、提交并读回。

**2.8 MCP 校验缺口**：普通标量类型／范围／枚举、未知参数键和列表行内数值范围有漏检样本，可到达运行方法；这些约束先按声明自行检查。list 行数／字段类型／未知行字段、data=null、变量绑定及自定义 validate 已有拒绝样本；原生 useParam 拒绝数字越界。各入口按自身检查结果处理。

**已有无效参数**：编辑同一调用的其他值时，extensionParamWarnings 的 preexisting=true 表示保留旧值。本次新增／修改的值按声明检查，旧值仅在获准范围修复。未触及该调用或脚本 append 时，仍需按目标原文判断旧值状态。

## 设置、存档与资源

作者配置存 settings，玩家状态存 save。slot 对应槽位，shared 跨档，session 对应本次 App 启动；项目变量“启动重置”按变量自身语义处理。数组更新使用目标 SDK 的 set 接口触发通知；按需求检查历史追加、去重及跨重启持久化。

MCP 改设置先读原值和 expected，长文本用返回哈希锁定原值，见[MCP 流程](mcp-workflow.md)。reset 后读回默认状态，并通过实际方法核取值。

| 需要的能力 | 读取契约与检查点 |
| --- | --- |
| 设置／存档 | [save schema](https://docs.avg-engine.com/extensions/save-schema)：作用域、保存、恢复 |
| 数据库 | [数据库](https://docs.avg-engine.com/extensions/database)：别名、集合策略、权限、拒绝处理 |
| 资源 | [扩展资源](https://docs.avg-engine.com/extensions/runtime/extension-resource)：相对扩展根、无 ./，发行物包含文件 |
| 原生能力 | [native node](https://docs.avg-engine.com/extensions/runtime/native-node)：获准接口、拒绝降级及可加载依赖 |
| 系统插槽 | [插槽](https://docs.avg-engine.com/extensions/system-slots)：按任务绑定，保留选项原始序号 |
| 历史 | [运行历史](https://docs.avg-engine.com/extensions/runtime/history)：按目标验证跨重启持久化 |

## Studio 设置页与检查器

schema 管数据，组件管布局。制作扩展的设置页／方法检查器时，按[Studio 编辑界面](studio-editor-ui.md)处理双入口、命名、变量、只读和局部写入。游戏菜单／HUD 使用 [UI 与数据](ui-and-data.md)。

## 运行状态与恢复

| 场景 | 操作与检查 |
| --- | --- |
| 隐藏方法／模块 | method({hidden:true})／@extension({hidden:true}) 隐藏选择项并保留旧调用。UI hidden 与 exposeUI:false 各按声明使用，访问权限单独处理 |
| 跟随舞台立绘 | 用 ctx.character.getStagePlacement(id) 取快照，React 用 useStagePlacement 订阅。未上场为 null，隐藏查 visible；目标离场就停止跟随该目标。viewport／localBounds／transform 使用扩展 UI 视口坐标，放到窗口布局前做坐标转换 |
| 演出时间轴 | 用 ctx.performance 的 isActive／isPaused／getInfo／onChange 观察；getInfo 为即时快照，订阅结束清理。段内 callFragment 会告警并结束 Promise，unsafe_goToFragment／hideBox 也受限制，跳转安排到允许的位置；模态 UI 会暂停／恢复时间轴 |
| 存档／快照重建 | 在产生副作用处读取 ctx.flow.isRestoring，跳过重复结算，同时保留恢复子片段所需的 callFragment。最深落点恢复后标志立即变化；JavaScript 局部状态按实际存档机制重建 |

普通快进和调试定位不进入 isRestoring 恢复态。按实际保存位置验证父方法重入、子片段恢复及防重结算；重复预览／卸载后清理订阅、输入和 UI。演出重播见[演出段](performance.md)，兼容旧宿主时复测对应存档路径。

## Steam 接入（2.9）

作品需要 Steam 时读当前 dev-extension-guide 和 SDK types/steam.ts，使用 ctx.steam：

1. 用 isAvailable() 查接入条件，getStatus() 查连接。真实调用使用已开启集成的桌面产物；Studio 预览、扩展沙箱和 Web 按 unavailable 处理。
2. 先判断 result.ok，再处理 unavailable／invalid／failed／unsupported。queued 记为待重试并等待宿主处理。
3. 隐藏且未解锁的成就隐藏标题和描述。本地成就与 Steam 成就分别维护。
4. ctx.flow.isRestoring 或 runImmediately 的重建路径跳过成就解锁和统计修改。
5. 隔离替身验证错误反馈、隐藏展示及防重复副作用；真实账号、Steamworks 配置与桌面运行按具体授权验收。

## 交付检查

按改动检查构建、作品启用、程序加载、方法调用、所需持久化和导出。缺宿主时交付静态／构建结果及待运行项。

发行物包含清单、UI、资源和构建入口，核自定义资源完整；src／sdk 留在开发流程。扩展运行安装与[插件 Skill 知识](plugin-skills.md)分别交付，外部发布及账号配置按具体授权执行。
