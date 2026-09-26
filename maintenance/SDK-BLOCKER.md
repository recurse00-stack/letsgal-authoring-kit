# 官方 SDK 缺文件：正式发行阻断项

2026-09-26 对两份官方来源分别复现：

- Stable：官网当前 Stable 通道清单指向 Studio 2.0.0。直接取得官方 Windows 压缩包 `resources/app.asar.unpacked/dist/sdk/` 下完整 29 个文件；constants.ts 声明 SDK_VERSION 为 2.0.0。原文未修改。
- Beta：Studio 2.2.0-beta.1 初始化程序生成的 SDK；本机安装包内的对应 SDK 目录也没有缺失文件。

两份 SDK 的 index.ts 第 22 行均从 `./extension-inspector` 导出 ExtensionInspector 和 ExtensionInspectorProps，但没有相应 .ts、.tsx 或声明文件。对本项目运行真实 TypeScript 检查得到：

```text
sdk/index.ts(22,8): error TS2307: Cannot find module './extension-inspector' or its corresponding type declarations.
```

依赖安装成功后仍复现。构建脚本在此停止，没有生成可投稿审核包。Stable SDK 通过 TypeScript 路径映射读取完整原始目录，不补写 SDK 实现或 npm 包元数据；Beta 使用官方初始化目录。不是 Vite 构建是否成功的问题。

修复条件：取得对应版本完整的官方 SDK，重新执行类型检查、构建、源码映射／许可检查及同一包的双宿主验收。不得自行声明空模块、删除官方导出、降低 sdkVersion 或跳过类型检查后将本项记为通过。现有 SDK 声明暂不下调。

官方出处：[Studio 下载页](https://avg-engine.com/)、[Stable 通道清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-stable.json)、[扩展开发流程](https://docs.avg-engine.com/extensions/develop/)、[SDK 版本声明](https://docs.avg-engine.com/extensions/project-structure/)。在线清单可能继续更新，此记录仅描述上述日期的取得结果。

本文件是可供复现的项目记录；没有代用户联系或向官方提交反馈。
