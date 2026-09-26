# 官方 SDK 总入口缺文件与本扩展的构建处理

2026-09-26：历史阻断已针对本指引使用的接口解除；没有修复或补造官方缺失功能。

Stable 官方通道指向 Studio 2.0.0，从官方 Windows ZIP 的 resources/app.asar.unpacked/dist/sdk/ 取得完整分发目录（29 个文件）。Beta 基线为 2.2.0-beta.1，由官方初始化流程取得对应 SDK。两份 index.ts 都重新导出 ./extension-inspector，而分发目录没有该模块。直接将 TypeScript paths 指向 index.ts，会复现 TS2307。该问题仍存在。

本扩展只用 Extension、extension、ExtensionProps 和 ExtensionRenderData。types/sdk-api.d.ts 只从官方 extension-module、extension-decorator 原文件重新导出这些名称；两版总入口也公开导出这两组接口。它不声明 any、空模块或替代实现，不修改 SDK。TypeScript 的路径映射仅影响类型解析，运行程序继续从 @avg-studio/sdk 导入，由宿主提供单实例。

两版实际检查结果：strict=true、skipLibCheck=false 均通过；故意导入不存在接口得到 TS2305，故意给 component 传数字得到 TS2322；Vite 实际构建通过且两版程序及源码映射字节一致。输入 SDK 的文件哈希前后相同。使用官方 extension 函数直接装饰类，避免打入编译器装饰器辅助实现。

清单采用 ^2.0.0，是因为使用的接口已在两版官方 SDK 中完成上述校验，不是只降低版本号。两版官方 isSdkCompatible 函数均接受 2.0.0 和 2.2.0-beta.1，拒绝 1.9.9 和 3.0.0。此证据证明类型及范围判断，不证明已在宿主加载、预览、存读档或导出；运行实测暂缓。

维护时须从官方渠道取得完整 SDK 目录，再按 workshop-guide/README.md 构建；不能只抽取几个声明冒充官方 SDK。新增 API 必须同步类型入口并核对两版实际定义；若新增功能需要缺失的 inspector，仍应取得官方修复版，不能照此做空实现。官方修复总入口后可重新验证并恢复直接映射。

官方依据：[Stable 通道清单](https://static-lg-studio.cn-gd.ufileos.com/studio/latest-stable.json)、[扩展结构与版本规则](https://docs.avg-engine.com/extensions/project-structure/)、[TypeScript paths](https://www.typescriptlang.org/tsconfig/paths.html)。清单和 SDK 可能继续更新，上述结果仅针对记录中的基线。
