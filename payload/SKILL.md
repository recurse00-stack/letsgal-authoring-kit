---
name: letsgal-extension-design
description: 为 LetsGal 扩展设置页与方法检查器比较布局、字段组织和预览表达方案，提供可改编的界面设计参考。
metadata:
  version: 0.1.0
  revision: 20261113-optional-wiki
---

# 扩展界面设计参考

用于需要设计或改进扩展编辑界面的任务。先读当前作品要求和相关偏好；用户已确定布局时沿用其选择。按作者操作目标提出方案，解释收益及代价，不把案例排列变成固定模板。

- 划分页面、组织字段和选择自定义程度：[布局与字段](references/layout.md)。
- 预览、变量占位、预设和列表反馈：[预览与交互](references/feedback.md)。
- 完整的提示卡编辑界面练习：[案例](references/card-example.md)。
- 借鉴来源与适用范围：[来源](references/sources.md)。

一般给出适合任务的方案及关键取舍即可；只有确有不同目标需要比较时才展开多个方案。设计结果应交代作者从哪里开始、怎样修改、如何观察效果，以及适合继续使用自动表单的部分。

工程实现回到主 Skill 的 `references/studio-editor-ui.md`；没有主 Skill 时查目标宿主的官方 Studio UI 参考及 SDK 类型。绑定、默认值、权限和局部写回按真实接口实现。此包提供方法，不提供游戏运行扩展，不自动安装或启用任何引擎插件。
