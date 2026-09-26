# AI 创作技能 · 安装与协作指引

0.1.0，独立社区工具。导入 AI 创作技能，按作品版本协作，个人特调升级保留。它提供风险说明、下载链接和提示词生成界面，不读取作品、不自动安装、不修改个人配置或存档。

## 使用

1. 从 [GitHub Releases](https://github.com/recurse00-stack/letsgal-authoring-kit/releases) 下载 letsgal-authoring-kit-0.1.0.zip。工坊开源详情的“查看源码”也可下载完整包，解压后找到 assets/skill-kit.zip，再解压；真实工坊下载路径在上架后另验。
2. Windows 双击 Install.cmd，选择 Agent 和目标范围，核对显示路径后导入；macOS／Linux 阅读包内 MANUAL.md 手动导入。
3. 建议暂时停用其他同类 LetsGal／引擎创作 Skill，保留原文件与特调，避免重复调度和额外上下文开销。开启新会话，发送指引生成的提示，核对实际技能来源。

个人偏好位于 ~/.letsgal-authoring/preferences/user.md；插件知识位于 ~/.letsgal-authoring/plugins/<id>/<version>/SKILL.md，由用户独立维护。旧版偏好原位保留，公共包更新不会重置它们。

使用前请阅读：AI 可能误改、误删或泄露资料。先备份作品并限制 Agent 可写范围；技能备份不包含作品。本包按现状提供，不提供担保；作者及贡献者不对使用或无法使用本包造成的任何损失承担责任。完整说明见打包后的 assets/risk-notice.md。

## 兼容与验证

Stable 2.0.0 和 Beta 2.2.0-beta.1 官方 SDK 均通过严格类型检查及实际构建，同一源码生成相同程序。清单采用 ^2.0.0，使用两版共有接口。两版宿主运行、剧情／存读档／导出暂未实测；三款 Agent 完整模型任务和安装器原生操作也暂未验证，不将构建通过视为运行通过。核心 ZIP 的 VALIDATION.md 保留详细层级。

## 从源码构建

在完整源码仓库运行，不在仅含核心文件的安装 ZIP 中构建。需要 Node.js／npm 和 Python，依赖由 package-lock.json 固定。验证环境为 Node.js 24.16.0、Vite 5.4.21；SDK 从目标 Studio 官方开发流程或官方安装包的 dist/sdk 目录完整取得，不加入仓库或审核包。

先用 `python -B maintenance/build_release.py --zip` 生成新的核心 ZIP，再运行：

```powershell
python -B maintenance/build_workshop.py --sdk "<完整官方 SDK 目录>" --core-zip "<刚生成的核心 ZIP>" --build-dir "<全新构建目录>" --output "<全新审核包目录>"
```

对另一基线重复时使用另一份官方 SDK、同一核心 ZIP 和新的输出目录。固定输入字节与工具版本可复现构建；已有目录、同名 ZIP、路径重叠、链接和不匹配的核心 ZIP 均会拒绝。失败保留诊断目录，不自动清理。网络不稳定可使用已校验完整性且与锁文件匹配的 npm 缓存，不关闭 TLS 校验。

types/sdk-api.d.ts 只重新导出本扩展使用的官方原始类型，以避开官方总入口缺失的无关 inspector 模块；strict=true、skipLibCheck=false，SDK 不修改。运行时 @avg-studio/sdk 与 React 仍由宿主提供，绝不导入宿主私有深路径或打入 SDK 副本。详细原因见仓库 maintenance/SDK-BLOCKER.md。

原创代码与文档采用 MIT；第三方边界见 THIRD-PARTY.md。审核包包含核心 ZIP、统一风险全文、源码和构建结果。提交采用开源方式，仓库填写 https://github.com/recurse00-stack/letsgal-authoring-kit 。构建成功不代表已提交、审核通过或上架。
