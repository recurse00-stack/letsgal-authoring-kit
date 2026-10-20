# 扩展：源码、契约与交付

先判断配置已有功能还是开发扩展，不把普通剧情扩大成系统重建。活动工程的关联、界面、初始化、加载与构建按本通道执行流程处理；独立源码和SDK查阅使用文件工具，运行快照不能当开发源。

## 识别工程

以extension.json定位真实ID与源码。纯可视化扩展可能没有package.json或sdk，不强制npm；需要程序而尚未初始化时使用Studio官方“初始化程序”。工具不可用先完成独立设计并说明入口，不猜造整套脚手架。[项目结构](https://docs.avg-engine.com/extensions/project-structure)

已投入使用的清单ID影响设置、存档和调用命名空间，保持不变；内部模块ID另核。扩展版本、sdkVersion要求、SDK自报版本、同步来源和实际宿主分别判断，不把编译通过当运行兼容。

程序改源码，dist由实际构建脚本产生，不手改发行产物；找不到源码就说明缺项。SDK由目标Studio同步，不私改声明补接口；保留模板React／React DOM／SDK外置单实例配置，不再打入另一份。[开发指导](https://docs.avg-engine.com/extensions/llms.txt)

## 按需读取契约

从目标sdk/index.ts公开导出进入，只读相关类型和官方页。来源未知时可以设计和读取，依赖接口的实现／兼容结论要等依据，不能仅从旧网页缺少方法认定新版不支持。

| 需求 | 入口与边界 |
| --- | --- |
| 方法与参数 | [方法](https://docs.avg-engine.com/extensions/method)：字面量、变量、条件与普通调用分别核schema |
| 设置与存档 | [save schema](https://docs.avg-engine.com/extensions/save-schema)：作者设置与玩家save分开，类型声明不等于运行校验 |
| 数据库 | [数据库](https://docs.avg-engine.com/extensions/database)：实际别名、集合策略、权限及拒绝处理 |
| 资源 | [扩展资源](https://docs.avg-engine.com/extensions/runtime/extension-resource)：相对扩展根、无./，核实进入发行物 |
| 原生能力 | [native node](https://docs.avg-engine.com/extensions/runtime/native-node)：按宿主权限和拒绝降级，不据此任意加载npm |
| 系统插槽 | [插槽](https://docs.avg-engine.com/extensions/system-slots)：普通面板不自动占插槽，核声明和选项原始序号 |
| 运行历史 | [历史](https://docs.avg-engine.com/extensions/runtime/history)：追加、去重与跨重启持久化分别核对，不能将同会话仍可见当保存成功 |

扩展slot、shared、session分别对应槽位、跨档和本次App启动；session与项目变量“启动重置”不同。按目标SDK契约更新数组，不原地push绕过set；订阅、输入和UI在重复预览／卸载时清理。当前范围和版本特例见[当前能力](current-capabilities.md)。

## 构建、启用与发行

构建按真实package scripts。安装、作品启用、程序加载、方法调用、持久化和导出各有结果，不能由一个成功推导其他全部通过。发行快照通常仅含清单、ui、assets、构建入口等运行文件，核实自定义资源，不把src／sdk混作运行依赖；纯UI导入能力按实际入口判断。

改动影响哪些层次就检查哪些层次；无宿主工具只报告静态／构建结果与人工步骤。插件运行安装与[插件Skill知识](plugin-skills.md)分开维护；本主Skill仍是社区辅助资料，不是引擎扩展。当前任务不授权顺带外部发布或修改账号配置。

## Beta 2.8 扩展开发

仅在目标宿主／SDK 明确支持时使用以下能力；正式版 2.5.0 不能直接套用。开发先读目标 `sdk/llms.txt` 或当前 MCP `studio://dev/extension-guide`；自定义编辑界面再读 `studio-ui/README.md` 或 `studio://dev/studio-ui`。旧项目需要时经官方“同步 SDK”取得配套资料，不私改 SDK。

- 新程序可用 `ext_enable(action="init_program", studioEntry=true)` 初始化双入口；`sync_sdk` 更新配套 SDK、开发指导及 studio-ui。构建后 `ext_reload` 核 sourceStatus、studioEntry.loaded、settingsPage、inspectors 和 unknownInspectors；再实际打开设置页／检查器并读回写入。注册信息不代表界面已渲染。
- 游戏入口 `src/index.tsx` 与仅 Studio 加载的 `src/studio.tsx` 分开。后者具名导出 `settingsPage`／`inspectors`；清单 `studioEntry` 指向独立 `dist/*.js` 或 `.mjs`，不能与 entry 相同。按官方模板两次构建到同一个 dist，后一次不能清空前一次产物；运行入口不能引入 `@avg-studio/studio-ui` 或 `@chakra-ui/react`，包括子路径。
- `useSetting`／`SettingField` 使用“模块ID.字段名”；检查器键用实际 method id，不能以标签替代。设置页只是编辑布局，仍按 settings／方法 schema 保存；构建、Studio 加载、读回与游戏调用分别验证。
- `list` 参数必须声明 item，只支持 string、number、boolean、enum、asset、character 行字段，不能套列表；`data` 的 default 必填且非 null，类型按 default 推导，精确空数组类型显式声明。二者只接收字面量，不能绑定变量。行数范围只在编辑／MCP 写入检查，运行时不检查；data.validate 在运行时失败只告警而仍执行，业务必须自行保证必要约束。
- 2.8.0-beta.1 实测：MCP 拒绝 list 行数／字段类型／未知行字段、data=null、list／data 变量绑定及 data.validate 失败；普通标量类型、枚举、数值范围、未知参数键和列表行数值范围尚不能依赖 MCP 完整拦截。按声明自行检查；本次数字与枚举越界值实际写入并到达方法，而原生 useParam 检查器拒绝同类越界值。该差异不代表应绕过原生校验。
- 扩展规则变化使旧参数失效时，块编辑可保留原值并返回 extensionParamWarnings、preexisting=true；这是兼容保留，不能报成参数已修好。未触及该调用或脚本 append 不保证报告旧问题；新插入／改变后的非法值仍会被拒绝。是否修旧值按当前委托范围决定。
- `validate` 写为带参数类型的箭头函数，例如 `validate: (value: unknown) => ...`；方法简写或 function 表达式会使当前类型推导失败。返回 true／false／错误提示，按实际 schema 校验，不以编译代替运行防护。
- `method({hidden:true})`／`@extension({hidden:true})` 隐藏选择项，不使旧调用失效；hidden UI 与 exposeUI:false 不同，不把隐藏当权限或卸载。
- `ctx.performance` 提供 isActive／isPaused／getInfo／onChange；getInfo 是读取瞬间快照，订阅须清理。旧宿主无该字段时用可选链等实际兼容策略。演出中 callFragment 会只告警并正常结束 Promise、不跳转；unsafe_goToFragment 和 hideBox 也受限制，不能把“不抛错”当已完成。存档重播与扩展副作用按演出段契约验证。

