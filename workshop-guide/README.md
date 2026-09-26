# AI 创作技能 · 安装与协作指引

独立社区工具，帮助将 letsgal-authoring 导入本地 AI Agent；提供风险说明、下载链接与协作提示。此处是工坊入口源码，不是已通过双版本验收的正式发布。

下载技能：[GitHub Releases](https://github.com/recurse00-stack/letsgal-authoring-kit/releases)。工坊完整包中的 assets/skill-kit.zip 是同一核心安装包。解压后 Windows 双击 Install.cmd，其他平台阅读 MANUAL.md 手动导入。

安装或启用前，建议暂时停用其他同类 LetsGal／引擎创作 Skill，避免重复调度、规则冲突和额外上下文开销。保留原文件及特调，由用户决定停用哪份；本工具不会自动修改其他技能。

使用前请阅读：AI 可能误改、误删或泄露资料。先备份作品并限制 Agent 可写范围；技能备份不包含作品。本包按现状提供，不提供担保；作者及贡献者不对使用或无法使用本包造成的任何损失承担责任。完整说明见打包后的 assets/risk-notice.md。

## 维护与构建

源码、核心技能分别维护；个人偏好和用户插件 Skill 不属于本包。核心版本来自仓库 bundle.json。构建使用 maintenance/build_workshop.py，传入从目标 Studio 官方开发流程取得的完整 SDK、已验证核心 ZIP、全新构建目录与全新输出目录。脚本执行锁定依赖安装、类型检查、构建和白名单打包，任何检查失败都停止，不能降级 sdkVersion 绕过。

SDK、node_modules、构建缓存及真实用户配置不进入仓库。可使用官方安装包完整的 dist/sdk 目录，或由 Studio 初始化取得的完整 SDK；类型检查通过路径映射读取其原始 index.ts 和所有引用，不要求给原始 SDK 添加 npm 元数据。不会补造缺失的 SDK 类型或跳过检查。源码的扩展 ID 保持不变。当前 sdkVersion 保持先前真实宿主要求，双版本成功前不能声称稳定版已支持。

这些构建命令应在完整源码仓库运行；面向用户的核心 ZIP 不包含 workshop-guide 源码。先执行 `python -B maintenance/build_release.py --zip` 生成新的核心 ZIP，再执行：

```powershell
python -B maintenance/build_workshop.py --sdk "<官方 SDK 目录>" --core-zip "<刚生成的核心 ZIP>" --build-dir "<全新构建目录>" --output "<全新审核包目录>"
```

既有目录、既有同名 ZIP、路径重叠或不匹配的核心 ZIP 均会拒绝；失败时保留诊断目录，不自动清理。固定依赖锁、输入字节和工具版本后可重复构建。正式包还须完成宿主验收，构建通过不等于可发布。

原创代码与文档采用 MIT。React 和 SDK 由宿主提供，不打入运行 bundle。构建工具和依赖适用其各自许可证，审查范围见 THIRD-PARTY.md。
