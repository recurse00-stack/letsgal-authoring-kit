# 扩展开发：源码、契约与运行

官方 MCP 可用时，目标工程的扩展设置、UI、关联、加载与构建操作优先选择当前可用的对应工具，并按需读取 `studio://dev/workflow`。独立扩展源码、npm 构建、SDK 查阅及发行材料仍保留原有文件工具；不将游戏内运行快照当源码，不借缺少 MCP 工具直接覆盖活动工程。未接入MCP的Beta继续按下述原生／源码流程工作。

从[创建流程](https://docs.avg-engine.com/extensions/develop/)进入，按[AI 开发指导](https://docs.avg-engine.com/extensions/llms.txt)及[运行时索引](https://docs.avg-engine.com/extensions/api-context)查当前任务。判断用户要配置已有功能还是开发扩展，不把普通剧情扩大为系统重建。插件使用 Skill 独立保存，见[用户插件知识](plugin-skills.md)。

## 识别真实开发工程

以 `extension.json` 定位源码和 ID。纯可视化扩展可能只有清单与 ui/，没有 package.json／sdk/，不需要 npm；其界面优先由编辑器维护。包含程序时读取实际 package.json、src/、sdk/ 与构建入口。需要程序但尚未初始化时使用 Studio 的“初始化程序”流程；工具无法操作就明确该前置缺口，完成独立设计，不手造猜测的脚手架。[项目结构](https://docs.avg-engine.com/extensions/project-structure)

**已投入使用的 extension.json.id 保持不变**，它影响设置、存档和调用命名空间；模块内部 id 与清单 ID 分开核对。扩展版本、清单 sdkVersion 要求、SDK 自报版本、同步来源和 Studio 完整版本分别记录。SDK 文件存在不证明与当前宿主配套，不用旧副本的版本比较器替代当前宿主规则。

所有程序改动写源码，`dist/` 仅由项目构建生成，不手工创建、编辑或修补其中的文件；找不到源码就说明该项无法完成。SDK 由 Studio 同步，不私改。保留模板中 React／React DOM／SDK 外置单实例配置，不把另一份打进运行包。按工程实际 scripts 构建，不凭模板名假定命令。

2026-10-05，2.5.0正式版原生“新建扩展→初始化程序”生成SDK与源码；29个SDK接口文件和该版安装资源一致，另有SDK package.json。保留React／SDK外置配置，修改源码标题后按实际`build`脚本构建；宿主程序预览显示新标题，项目发行dist与构建产物SHA相同。这个最小证据证明初始化／源码构建／预览加载，不证明所有接口、方法、玩家与持久化。

## 按需求查具体契约

先从当前 sdk/index.ts 的公开导出定位声明，再查实现所需类型和官方页。最新文档是检索入口，不证明旧 SDK 或所有宿主支持。

Beta官网文档未同步的范围按[累计差异](versions/beta-differences.md)查公告线索。SDK来源UNKNOWN时，可继续只读查类型及隔离候选实现，但不能把本地自报版本、编译通过或缺少方法推为目标Beta的支持／不支持结论；先取得目标Studio官方同步的SDK及来源记录，再验所需接口。不修改现有SDK来填补声明。

| 需求 | 资料与必须核对的边界 |
| --- | --- |
| 剧本方法、参数或返回 | [剧本方法](https://docs.avg-engine.com/extensions/method)及真实声明；字面量／变量、条件调用和普通方法调用分别取样 |
| 设置与玩家存档 | [存档 Schema](https://docs.avg-engine.com/extensions/save-schema)；设置是作者配置，save 是玩家数据，类型声明不等于运行时校验 |
| 数据库 | [数据库](https://docs.avg-engine.com/extensions/database)；使用声明并绑定的别名，写入需要权限及集合策略，处理拒绝 |
| 扩展内资源 | [资源接口](https://docs.avg-engine.com/extensions/runtime/extension-resource)；路径相对扩展根、没有 ./，确认文件实际进入发行物 |
| 原生 Node 能力 | [原生能力](https://docs.avg-engine.com/extensions/runtime/native-node)；核宿主权限、可用性与拒绝降级，不据此加载 npm 包 |
| 默认壳／系统插槽 | [插槽](https://docs.avg-engine.com/extensions/system-slots)；普通面板不自动占插槽，候选声明与选项原始序号核对 |
| 历史／2.3 新能力 | [历史](https://docs.avg-engine.com/extensions/runtime/history)和[Beta 专页](versions/beta-2.3.md)；公告不代替新增签名，当前未知项保留 UNKNOWN |

持久化分别测试 slot（槽位）、shared（跨档）与 session（本次 App 启动）。session 不写存档，也不因回标题／换档自动清空；它与项目变量的启动重置不同。数组通过整体 set 更新，不原地 push；订阅、输入和 UI 在重复预览／卸载时清理，不能累积处理器。

## 安装、启用与发行分别验收

扩展安装不代表当前作品已启用，启用不代表程序加载或方法运行通过。源码关联与项目的运行发行快照分开，不能把后者当开发源。按官方结构，作品发行通常只复制清单、ui、assets、构建入口等运行文件，不包含 src／sdk；自定义资源目录需实际核包。纯 UI 的压缩包导入能力以当前入口支持为准，不能猜测与程序扩展相同。

构建后检查目标工程加载、参数 UI、正常与失败分支、状态保存、重复预览和目标导出。找不到真实宿主操作工具时记录静态及构建结果，提供人工步骤，不把 TypeScript 成功或文件复制称为运行兼容。

本主 Skill 是 GitHub／社区纯 Skill，按主 Skill 安装器维护；不是 LetsGal 引擎扩展。第三方插件的运行安装与其 AI 资料安装分别处理。

2026-10-01 配套2.3.0-beta.1 SDK的历史追加探针，在新桌面玩家一次调用后快存及普通槽位1保存。全部玩家进程正常退出并重开，两种读取都恢复剧情、slot数值变量与场景，但没有恢复追加的三条历史。自然剧情历史仍可见，不据此称全部历史丢失。此结果符合append／appendBatch“不自动持久化”的声明；扩展持久化的设计与验收仍另做，当前探针没有实现。详见[Beta限定证据](versions/beta-2.3.md)。
