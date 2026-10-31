# Studio 扩展设置页与方法检查器

仅在开发扩展的 **Studio 编辑界面** 时读取；游戏中的菜单、HUD 和按钮见 [UI 与数据](ui-and-data.md)，运行逻辑见[扩展开发](extensions.md)。本专题依据 2.8.0-beta.1 的组件包契约与“Studio 组件包演示”1.0.0 提炼，不以示例的 `sdkVersion >=1.0.0` 推定旧宿主支持。

接口先按当前 `studio://dev/studio-ui`（`studio_get_reference(topic="dev-studio-ui")`）或目标工程同步的 `studio-ui/README.md` 核对；只读本次涉及的段落与类型。具体 props 和构建配置用包内 `templates/`，不复制整本手册。演示用于理解组合方法，无须加入作品；它的卡片、评分规则、ID 和默认值不成为业务需求。

## 入口与构建

- 游戏入口 `src/index.tsx` 与编辑入口 `src/studio.tsx` 分离；后者具名导出不接收 props 的 `settingsPage` 组件和／或 `inspectors` 对象，键是 **method ID**。导出组件本身，不是 JSX 元素、default export 或 `lazy()`。
- `extension.json` 已有程序 `entry` 才能声明 `studioEntry`：相对扩展根、位于 `dist/`、以 `.js`／`.mjs` 结尾，路径字符限于 `[A-Za-z0-9._/-]`；与 `entry` 忽略大小写也不能相同。
- 新程序可通过 `init_program(studioEntry=true)` 生成官方模板。已有程序先声明 `@avg-studio/studio-ui: file:./studio-ui`，再按官方流程同步 SDK 和依赖，补编辑入口与双次构建；同名非组件包目录不能直接覆盖。保留既有构建定制，不整份替换后遗漏。
- 每个入口各生成一个文件，沿官方模板保留 `inlineDynamicImports: true` 与两次构建的 `emptyOutDir: false`。共用库外置规则按模板，不另打包 React／SDK 单实例；编辑入口从组件包或 Chakra 的包根导入，不直接导入 Emotion／Ark UI 或 CSS 文件。
- 运行入口及其依赖不能引入 `@avg-studio/studio-ui`、`@chakra-ui/react` 及其子路径；编辑入口也不能调用 `useExtensionContext()` 等游戏运行接口或 Node.js 接口。仅借用运行类的类型时用 `import type`，例如 `MethodParams<typeof Module.method>`。

## 设置页：数据名与界面职责

设置 schema 决定类型、默认值、重置、MCP 访问和运行读取；React 组件决定布局与交互，组件布局不作为设置值或调用参数保存。

| 声明来源 | `useSetting`／`SettingField`／`AutoSettings` 使用的名字 |
| --- | --- |
| `Extension` 类上的设置 | `<模块 ID>.<字段>`；模块 ID 以实际声明为准，不用扩展清单 ID 或显示标签代替 |
| 入口直接导出的共享 `settingsSchema` | 裸字段名，不加模块前缀 |

优先用 `SettingField` 保留官方行的默认值提示、重置与联动；仅重点字段用 `useSetting` 加自定义控件，其余交 `AutoSettings` 的 include／exclude。自定义行依据 `info.isEnabled` 展示 `enabledWhen` 状态；不要把界面置灰当权限校验。`reset()` 才表示恢复默认，`isModified` 的对象／数组比较也不能当深度内容差异判断。

每个读取设置的行拆成小组件，使订阅只刷新相关行。`AutoSettings` 直接放 `Panel`，不嵌入 `Section`，以保留滚动时的搜索栏。页面需至少一个 schema 设置字段才会显示。

## 检查器：变量、上下文与写入

`useParam(name)` 与 `ParamField` 用方法 schema 的裸参数键。先判断 `useInspectorEnvironment()`：`placement` 区分剧情侧栏、条件对话框、UI 编辑器；`canUseVariables` 决定能否绑定变量（UI 点击动作不支持），`readOnly` 为真时禁用自定义写控件，宿主仍会拒绝写入。只读可能来自协作锁或普通编辑状态，不归为协作专属限制。

- **变量不能当缺值。** `info.isVariable` 为真时，读值为空；保留 `ParamField` 的变量编辑能力，预览标明“运行时取变量”，不把它补成默认字面量。自定义 setter 写的是固定值，会替换原绑定。
- **仅用户交互触发写入。** 检查器会随选中指令重新挂载，挂载／effect 不做初始化写回。`setParams(patch)` 只放确需修改的键，一次成功写入是一项撤销；任一值校验失败整体不写。不要展开整份 `values` 回写。
- **关联坐标例外。** 移动共享同一位置预设的一个坐标时，要把其他共享坐标按当前读值一并交给 `setParams`，防止转为自定义预设后跳位。片段所属章、镜像值等按官方联动核对。
- `setValue`／`setParams` 返回 `false` 表示拒绝，检查日志并修正输入；返回 `true` 也可能是无变化，不证明存储被改写。`undefined`／`reset()` 表示清空并使用默认值，`null` 按参数类型校验，不是通用清空值。
- 重点参数自定义，其余用 `ParamField`／`AutoParams`，保留条件显隐和官方联动。场景参数若依赖 `_sceneLayers`、`_sceneLighting`、`_sceneName` 快照，用 `ParamField`；仅写 scene ID 不会生成这些快照。检查器行直接相邻排列，卡片之间再加间距；`AutoParams` 可以放进 `Section`，与 `AutoSettings` 不同。

## 列表、复杂数据与预览

`useParam` 读取的对象／数组被冻结，更新用新对象或新数组；列表新增、删行、排序同时遵守 schema 的行数与字段约束。`list`／`data` 的定义及运行检查边界见[参数与校验](extensions.md#参数与校验)，不因编辑控件校验通过推定 MCP 或运行方法也检查一致。

读值不一定是存值：非法标量可能显示默认值，列表可能补列、去列或修复格子。通过 `isInvalid`、`reason`、`rawValue` 区分；只预览或修改另一字段时保留原存值。明确要修复该参数时，依官方 reset／再写流程处理并读回；不要在挂载时自动“修复”，也不要把显示正常说成已保存正常。列表／data 预览使用字面量；标量绑定变量时展示未知运行值，不造计算结果。

批量预设只提交所选预设要改变的参数，并交代它会改变哪些值或绑定。编辑期卡片只是依据当前参数绘制的示意，不调用游戏方法充当预览，不等同实际 Player 演出通过。

## 外观与有限验证

用 Studio 语义 CSS 变量适配主题；组件包优先，Chakra 随宿主升级且不保证相同稳定性。自定义文字和 `ariaLabel` 通过 `useStudioLocale()` 自行选语言；Chakra 浮层按组件包要求标记 `data-studio-user-content`。反馈／确认按具体操作影响使用 `toast`／`confirm`，不为每次普通参数编辑额外审批。

按改动选择验证：

1. 类型检查与双入口构建，核两个文件均保留、没有错误运行依赖或拆出的共享 chunk。
2. 用 `ext_reload` 核 `sourceStatus`、`studioEntry.loaded`、`settingsPage`、`inspectors` 和 `unknownInspectors`；注册成功不代表画面已渲染。
3. 在需要支持的入口实际打开：设置页改值／重置；检查器覆盖字面量与变量、只读、预设及目标列表／data 操作。写后读回，必要时检查撤销及实际运行读取；不用每次测全套功能。

仅有类型、构建或模拟交互时明确记录这一层，不声称已验证宿主保存、协作、Player 或主题显示。展示异常先查扩展日志与自动表单；不为修界面改 schema ID、绕过只读或修改第三方下载包。
