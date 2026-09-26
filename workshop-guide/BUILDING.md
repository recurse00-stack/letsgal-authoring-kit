# 工坊包构建与投稿前检查

本页供维护者使用，普通用户按 README.md 安装。

扩展 ID 固定为 `io.github.letsgal-authoring-kit.guide`。本地 SDK 的 ID 规则较宽，不能代替工坊的小写反域名格式检查。`npm run typecheck`、`npm run build` 和 `npm run watch` 会先执行只读清单检查；`npm run test:manifest` 包含此次失败 ID 的回归检查。本地检查通过仍不等于服务器接受或审核通过。首次成功投稿后不要随意更换 ID。

修正版沿用 0.1.0（此前工坊投稿未成功），使用新的 `-idfix` 目录与 ZIP 名称。已发布的原 0.1.0 ZIP 和内嵌核心 Skill 字节保留；不要覆盖旧资产或把它们当作修正版。


在完整源码仓库运行，不在仅含核心文件的安装 ZIP 中构建。需要 Node.js／npm 和 Python，依赖由 package-lock.json 固定。验证环境为 Node.js 24.16.0、Vite 5.4.21；SDK 从目标 Studio 官方开发流程或官方安装包的 dist/sdk 目录完整取得，不加入仓库或审核包。

先用 `python -B maintenance/build_release.py --zip` 生成新的核心 ZIP，再运行：

```powershell
python -B maintenance/build_workshop.py --sdk "<完整官方 SDK 目录>" --core-zip "<刚生成的核心 ZIP>" --build-dir "<全新构建目录>" --output "<全新审核包目录>"
```

对另一基线重复时使用另一份官方 SDK、同一核心 ZIP 和新的输出目录。固定输入字节与工具版本可复现构建；已有目录、同名 ZIP、路径重叠、链接和不匹配的核心 ZIP 均会拒绝。失败保留诊断目录，不自动清理。网络不稳定可使用已校验完整性且与锁文件匹配的 npm 缓存，不关闭 TLS 校验。

types/sdk-api.d.ts 只重新导出本扩展使用的官方原始类型，以避开官方总入口缺失的无关 inspector 模块；strict=true、skipLibCheck=false，SDK 不修改。运行时 @avg-studio/sdk 与 React 仍由宿主提供，绝不导入宿主私有深路径或打入 SDK 副本。详细原因见仓库 maintenance/SDK-BLOCKER.md。

原创代码与文档采用 MIT；第三方边界见 THIRD-PARTY.md。审核包包含核心 ZIP、统一风险全文、源码和构建结果。提交采用开源方式，仓库填写 https://github.com/recurse00-stack/letsgal-authoring-kit 。构建成功不代表已提交、审核通过或上架。
