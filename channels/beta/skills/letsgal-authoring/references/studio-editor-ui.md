# Studio 扩展设置页与方法检查器

制作扩展的 Studio 编辑界面时读取。按任务选[构建入口](#入口与构建)、[设置页](#设置页数据名与界面职责)、[方法检查器](#检查器变量上下文与写入)或 [2.9 集合编辑](#29-设置页的集合源数据)；游戏菜单／HUD 使用 [UI 与数据](ui-and-data.md)。

基础方法来自 2.8.0-beta.1 组件包及“Studio 组件包演示”1.0.0；集合编辑使用 2.9.0-beta.1 契约。具体接口查当前 `studio_get_reference(topic="dev-studio-ui")`／studio://dev/studio-ui 或同步的 studio-ui/README.md，构建配置取包内 templates。界面组织与预览表达可按[创作参考](creation-references.md)读取已启用的 `letsgal-extension-design`；本页维护实现契约。

## 入口与构建

1. **准备入口。** 游戏程序用 src/index.tsx，编辑界面用 src/studio.tsx。新程序可 init_program(studioEntry=true)；已有程序补 `@avg-studio/studio-ui: file:./studio-ui`，同步 SDK／依赖并保留既有构建定制。同名目录已有其他内容时先处理冲突。
2. **声明导出。** 编辑入口具名导出无 props 的 settingsPage 组件和／或 inspectors 对象；inspectors 键使用 method ID，值为组件本身。
3. **填写清单。** 已有 entry 才声明 studioEntry；后者相对扩展根，位于 dist/，后缀 .js／.mjs，路径字符为 `[A-Za-z0-9._/-]`，与 entry 忽略大小写后仍须不同。
4. **分别构建。** 每个入口生成一个文件，保留 inlineDynamicImports:true 和两次构建的 emptyOutDir:false。按模板外置 React／React DOM／SDK 单实例依赖。

| 入口 | 依赖范围 |
| --- | --- |
| 游戏入口及依赖 | 保持运行依赖独立，排除 @avg-studio/studio-ui、@chakra-ui/react 及子路径 |
| 编辑入口 | 从组件包或 Chakra 包根导入；排除 Emotion／Ark UI 直导和 CSS 文件导入；使用编辑期 API，排除 useExtensionContext 等游戏运行接口及 Node.js |
| 只借运行类类型 | 使用 import type，例如 `MethodParams<typeof Module.method>` |

构建后核两个入口文件保留、共享依赖按模板外置，随后按[验证步骤](#外观与有限验证)加载。

## 设置页：数据名与界面职责

schema 定义类型、默认值、重置、MCP 访问及运行读取；组件定义布局和交互。

| 声明来源 | useSetting／SettingField／AutoSettings 的名字 |
| --- | --- |
| Extension 类上的设置 | `<模块 ID>.<字段>`，模块 ID 取实际声明 |
| 入口直接导出的共享 settingsSchema | 裸字段名 |

1. SettingField 提供默认提示、重置和联动；useSetting 用于自定义控件，AutoSettings 可用 include／exclude 控制字段范围。按需要选择，保留 schema 的默认值、显隐和联动语义。
2. 自定义行按 info.isEnabled 显示 enabledWhen，并遵守宿主写入权限。恢复默认用 reset()；对象／数组按内容比较，isModified 不作深度差异依据。
3. 页面至少声明一个设置字段；使用 AutoSettings 时核对内建搜索与滚动在当前容器中的行为。

## 2.9 设置页的集合源数据

仅在自定义设置页使用 `useDataCollection<T>(alias)`，读取作者源记录。manifest.dataDependencies 先声明本扩展别名并绑定集合；玩家存档／预览覆盖由运行端处理。

| 操作 | 做法 |
| --- | --- |
| 读取 | 使用 documents 副本，草稿同时保存 records 和当时的 opaque revision |
| 新增 | insertOne，让 Studio 生成 ID |
| 局部改／删 | updateOne／deleteOne，定位已有 ID |
| 整表保存 | saveDocuments 带草稿对应 revision；冲突时重读并合并 |
| 异步结果 | 捕获拒绝并反馈，项目／绑定已变化时作废旧回调 |

作者源编辑按此 API 的权限语义执行；依赖 access=read 或 runtimePolicy=readonly 控制运行访问，仍允许作者编辑。写入由明确交互触发，挂载 effect 保持只读。此 hook 限设置页使用；方法检查器和游戏入口使用各自接口。实测设置页读写、原 ID、撤销及绑定变化。

## 检查器：变量、上下文与写入

useParam(name)／ParamField 使用方法 schema 的裸参数键。先读 useInspectorEnvironment：placement 定位剧情侧栏／条件对话框／UI 编辑器，canUseVariables 决定变量能力，readOnly 决定控件可写状态。UI 点击动作不支持变量；只读时禁用自定义写控件，原因查环境和锁状态。

| 条件／动作 | 实施规则 |
| --- | --- |
| info.isVariable=true 且读值为空 | 保留绑定，用 ParamField 提供变量编辑；预览标“运行时取变量”。自定义 setter 会写固定值并替换绑定 |
| 修改参数 | 仅在交互回调中提交 setParams(patch) 的目标键；每次成功写入为一项撤销，任一校验失败整体不写。选中变化会重新挂载，effect 保持只读 |
| 移动共享预设的坐标 | 同批带上其他共享坐标的当前值，保持切到自定义预设时的位置；片段所属章、镜像值等按官方联动处理 |
| setValue／setParams 返回 false | 查日志，修正输入 |
| 返回 true | 读回目标值；无变化按幂等结果处理 |
| 清空／重置 | 用 undefined／reset() 回到默认，null 按字段类型处理 |
| 场景参数依赖快照 | 用 ParamField 同步 _sceneLayers／_sceneLighting／_sceneName 等关联字段 |

自定义参数控件需要保留 schema 的显隐、联动和变量语义；ParamField／AutoParams 提供相应标准编辑行为。

2.9 “在剧本上显示”选择本项目该方法的卡片参数，作用于其全部调用。调整后看实际卡片；临时验证结束恢复原显示选择，保留方法参数。

## 列表、复杂数据与预览

useParam 返回的对象／数组被冻结，修改时创建新对象／数组。列表新增、删除、排序按 schema 的行数和字段约束；定义与运行检查见[参数与校验](extensions.md#参数与校验)。

读取时结合 isInvalid、reason、rawValue：非法标量可能显示默认值，列表可能补列、去列或修复格子。预览或改其他字段时保留原存值；明确修复该参数时，用 reset／再写流程并读回。修复由交互触发。

列表／data 可按字面量预览；标量变量在运行时解析，编辑期标明尚未求值。应用预设只提交目标参数，说明涉及的值及绑定。编辑期预览用于呈现已知参数，游戏方法仍需运行验证。

## 外观与有限验证

组件包和 Studio 语义 CSS 变量提供主题适配能力；Chakra 用法随目标宿主核对。自定义文字／ariaLabel 通过 useStudioLocale() 选语言，Chakra 浮层按要求标记 data-studio-user-content。toast／confirm 按操作影响使用，普通参数编辑直接完成。

按本次改动选择检查：

1. **构建**：类型检查及双入口构建；核文件、外置依赖和共享 chunk。
2. **加载**：ext_reload 后读 sourceStatus、studioEntry.loaded、settingsPage、inspectors、unknownInspectors，再打开目标界面。
3. **交互**：设置页改值／重置；检查器验证涉及的字面量、变量、只读、预设或列表／data 操作。写后读回，按影响检查撤销与运行读取。

展示异常先查扩展日志和自动表单，保留 schema ID、只读约束及第三方组件包。按完成的构建、交互、保存和运行范围交付。
