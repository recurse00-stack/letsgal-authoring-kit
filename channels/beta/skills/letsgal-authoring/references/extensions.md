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
