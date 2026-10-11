# 当前修订的验证范围

**0.2.1 · 20261011-beta270-guides 发行修订。** 更新 Beta 2.7.0-beta.1 相关指引和精确版本路由，正式版目标仍为2.5.0。

| 部分 | 状态 | 检查范围 |
| --- | --- | --- |
| Skill本体 | changed | Beta语言配音、MCP设置、SDK语义与当前版本路由；Stable正文和14份共享文件原字节保留，仅同步修订元数据 |
| 辅助安装程序 | verified-unchanged | 安装器代码与已发布修订原字节一致，复用原64项隔离安装／提示检查；本轮另对完整修订包做通道安装检查 |
| 安装与升级说明 | changed | 明确当前完整包与旧附件；选择一份通道安装，备份旧安装并保留个人区 |
| 人类手册 | changed | Beta 2.7操作边界与版本核对；Markdown／HTML同步 |

本轮重新运行56项版本路由检查，覆盖2.7.0-beta.1、旧2.6 Beta、正式版、未知未来版本、通道冲突与参数契约；版本选择仅证明资料路由，不证明引擎兼容。完整包另做22项隔离安装／通道检查，复用既有安装器行为用例。

官方清单、2.7随包SDK声明、当前工具schema和只读状态分别作为资料依据。本修订仅作状态与声明核对，未取得新版quickstart、读取或写入工程、操作原生界面、运行模型任务或测试玩家／存读档／导出。后续制作按当前获准连接刷新指导。

包按release-files白名单核对载荷、共享文件、链接／锚点、HTML、SHA和ZIP逐文件读回；格式与文件一致性不冒充视觉或宿主通过。

## 沿用的证据与限制

此前2.5.0有限宿主、2.6.0-beta.1有界MCP和模型证据继续保留原范围，见[宿主摘要](HOST-VALIDATION.md)。原64项隔离安装／提示组件检查不冒充本次新测，历史凭证见[已发布0.2.1](https://github.com/recurse00-stack/letsgal-authoring-kit/releases/tag/v0.2.1)。

此前小样本只支持部分工具选择、批量操作与恢复检查的改善；也存在漏检、错误完成和部分采用不准。未通过门槛的实验规则保持撤回，不宣称统一提速、token节省或弱模型必然更受益。结构化结果见[validation-results.json](validation-results.json)。

本修订源码同步到main，原v0.2.1标签仍指向初版；发布页新增独立命名的完整包和[下载核验记录](https://github.com/recurse00-stack/letsgal-authoring-kit/releases/download/v0.2.1/DOWNLOAD-VERIFICATION-0.2.1-20261011-beta270-guides.json)。GitHub自动生成的Source code附件对应初版标签，安装本修订请使用带20261011-beta270-guides的完整ZIP。实际下载核验以该独立凭证为准，不增加宿主或模型验收范围。
