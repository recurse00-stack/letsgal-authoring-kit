# 扩展开发：从契约到宿主验证

先判断配置已有功能还是开发扩展。普通剧情任务不自动升级插件、同步 SDK 或重建系统；程序源码、Studio 关联和发行快照是不同对象。

## 确定源码与目标 SDK

以 `extension.json` 核真实 ID 和源码关联，保留已使用的清单 ID，它影响设置、存档和调用命名空间；内部模块 ID 另核。纯可视化扩展可以没有 package.json／sdk，不强制 npm。需要程序才用官方初始化；缺源码就说明缺项，不改 dist 代替源码。

开发先读当前 `studio://dev/extension-guide`（topic=`dev-extension-guide`）或目标 `sdk/llms.txt`；接口以该工程同步 SDK 的公开导出为准。宿主完整版本、sdkVersion 要求、SDK 自报版本与同步来源分别记录，不私改声明补接口，不把编译通过当运行兼容。资料不足按[定向查证](research.md)处理。

新扩展通过 `ext_enable` 的 create／init_program 流程取得真实 ID；需要编辑期界面时 `init_program(studioEntry=true)`。`sync_sdk` 同步 SDK、开发指导与 studio-ui。沿生成模板的实际 package scripts 构建，不假设一定有 dev；保留 React／React DOM／SDK 外置单实例配置。

## 参数与校验

配置调用先 `ext_read(view="methods")` 取得真实声明，开发再查 schema 类型。普通调用、条件、字面量和变量引用分别判断，按以下顺序检查后才写：

1. 核 method ID、允许的参数键、必需项／默认值、类型、枚举、范围和资源引用；列表再核行数与每个字段。不要把 MCP 接受当作完整校验。
2. `list` 必须声明 item，行字段只支持 string、number、boolean、enum、asset、character，不能嵌套 list。`data` 的 default 必填且非 null，类型从 default 推导，精确空数组类型应显式声明。二者只接收字面量，不绑定变量。
3. list 行数范围在编辑／MCP 写入检查，运行时不检查；`data.validate` 运行时失败只告警仍执行。涉及业务安全或状态完整性的约束由实现自行处理。
4. `validate` 使用有参数类型的箭头函数，例如 `validate: (value: unknown) => ...`，按契约返回 true／false／错误提示；当前类型推导不宜改成方法简写或 function 表达式。类型检查和运行校验各有作用。

**2.8.0-beta.1 已确认的 MCP 缺口**：普通标量类型／范围／枚举、未知参数键和列表行数值范围未完整拦截；越界值可以写入、通过 project_validate 并到达运行方法。原生 useParam 检查器已验证会拒绝数字越界，但不能由此推定所有入口检查一致。始终做第 1 步，再用 dry run 和目标读回补证。

list 行数／字段类型／未知行字段、data=null、变量绑定和自定义 validate 的拒绝已有有限实测。已有参数因扩展规则变化失效时，编辑同一调用的其他参数可能保留原值并返回 `extensionParamWarnings`、`preexisting=true`；这是兼容保留，不是已修复。新插入／改变后的非法值会被相应检查拒绝，**不代表上述普通参数缺口消失**。未触及调用或脚本 append 可能没有旧值警告；是否修复旧内容按当前委托范围决定。

`inspectorLayout` 只组织表单，schema 仍平铺传给 run；tabs 与顶层 groups 二选一，fields／summaryFields 引用原字段。预设 settingsKey 指向 array 设置，行含 id／name／paramsJson；preserveFields 控制应用时保留值，不改变保存整套参数的行为。不为分组改变方法 ID 或运行数据。

## 设置、存档与资源

作者 settings 与玩家 save 分开；slot、shared、session 分别为槽位、跨档和本次 App 启动，session 不等同项目变量“启动重置”。更新数组按目标 SDK 的 set 契约，不原地 push 绕过通知。历史追加、去重和跨重启持久化分别验证。

MCP 设置写入先读原值和 expected，长文本用返回的哈希做乐观锁，见[MCP 流程](mcp-workflow.md)。reset 后既要读回默认状态，也要检查实际方法取到的值；设置页显示不证明游戏读取一致。

| 需求 | 定向契约 |
| --- | --- |
| 设置与存档 | [save schema](https://docs.avg-engine.com/extensions/save-schema)，按作用域验证保存与恢复 |
| 数据库 | [数据库](https://docs.avg-engine.com/extensions/database)，核别名、集合策略、权限和拒绝处理 |
| 资源 | [扩展资源](https://docs.avg-engine.com/extensions/runtime/extension-resource)，相对扩展根、无 ./，核发行物包含文件 |
| 原生能力 | [native node](https://docs.avg-engine.com/extensions/runtime/native-node)，遵守实际权限与拒绝降级，不任意加载 npm |
| 系统插槽 | [插槽](https://docs.avg-engine.com/extensions/system-slots)，普通面板不自动占插槽，保留选项原始序号 |
| 历史 | [运行历史](https://docs.avg-engine.com/extensions/runtime/history)，同会话仍可见不等于已持久保存 |

## Studio 设置页与检查器

先读 `studio://dev/studio-ui`（topic=`dev-studio-ui`）或同步得到的 `studio-ui/README.md`。游戏入口 `src/index.tsx` 与编辑入口 `src/studio.tsx` 分离，后者具名导出 settingsPage／inspectors；清单 studioEntry 指向独立 dist/*.js 或 .mjs，不能和 entry 相同。

按官方模板两次构建到同一 dist，后一次不能清空前一次产物；运行入口不能引入 `@avg-studio/studio-ui` 或 `@chakra-ui/react` 及其子路径。`useSetting`／`SettingField` 使用“模块ID.字段名”，检查器键用 method ID，不用显示标签。界面布局仍通过 settings／方法 schema 保存。

验证顺序：类型与双入口构建 → `ext_reload` 核 sourceStatus、studioEntry.loaded、settingsPage、inspectors 和 unknownInspectors → 实际打开页面／检查器 → 合法写入读回、非法输入拒绝 → 必要的游戏方法读取。注册信息只证明已注册，不能当界面渲染通过。

## 运行状态与恢复

- `method({hidden:true})`／`@extension({hidden:true})` 隐藏选择项，旧调用仍可执行；hidden UI 与 exposeUI:false 不同。隐藏不是权限控制或卸载。
- `ctx.character.getStagePlacement(id)` 是舞台立绘快照，React 用 useStagePlacement 跟随更新。未上场为 null，隐藏看 visible；精确目标离场后不转向其他层。viewport、localBounds 和仿射 transform 属扩展 UI 视口坐标，不能直接当窗口 CSS 坐标。
- `ctx.performance` 提供 isActive／isPaused／getInfo／onChange；getInfo 为读取瞬间快照，订阅要清理。演出中 callFragment 只告警并结束 Promise、不跳转，unsafe_goToFragment 和 hideBox 也受限制，不把不抛错当已完成。演出中模态 UI 会暂停／恢复时间轴。
- `ctx.flow.isRestoring` 表示当前是否在重建存档／快照路径。读档可能重入等待子片段的父方法：避免重复结算，但仍须调用 callFragment 恢复子片段。最深落点恢复后标志立即变化，不缓存成整个方法的固定值；普通快进／调试定位不是恢复，JavaScript 局部变量不会随档恢复。

清理订阅、输入和 UI，避免重复预览／卸载后残留。定位重放和玩家连续运行分开测试，演出重播副作用见[演出段](performance.md)。跨旧宿主兼容必须有明确目标与实际策略，不凭可选链或新标志声称旧存档问题已解决。

## 交付检查

按本次影响验证源码构建、作品启用、程序加载、真实调用、持久化与导出，不把单层成功扩成全链路通过。发行快照通常只含清单、UI、资源和构建入口；核自定义资源，不以 src／sdk 作为运行依赖。缺宿主只能报告静态／构建结果与未测步骤。

扩展运行安装与[插件 Skill 知识](plugin-skills.md)独立维护。本主 Skill 是辅助资料，不是引擎扩展；开发任务不自动授权外部发布或改账号配置。
