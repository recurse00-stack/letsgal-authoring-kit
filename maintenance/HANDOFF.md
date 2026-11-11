# 维护入口

当前总包与 Stable 载荷 3.0.0，Beta 载荷 2.9.0，统一修订 20261111-series300。开工按主次版本与实际发行身份检查，同系列补丁／热修复不单独暂停；Beta 保留 2.8 兼容路线。总包与通道版本分别登记。

## 手册生成

MANUAL.md 是导航，docs/wiki/ 为专题正本，manual-layout.json 登记顺序、三分区与旧锚点。wiki.html、wiki.css、wiki.js 分别维护页面模板、样式和本地交互。修改正文或前端后执行 `python -B maintenance/build_manual.py`，只检查生成物是否最新时加 `--check`。维护环境需要 Python Markdown；生成的 MANUAL.html 内嵌正文、样式和 JavaScript，不需要 Python、网络或服务端，禁用脚本时仍可完整阅读。

build_workbench.py 只在显式 --user-area 下读取接入清单；个人产物必须新建在公共发行工程外，不能回写 MANUAL.html。字段见 wiki-manifest.schema.json，用法见[资料接入](../docs/wiki/10-workbench-interface.md)。run_wiki_checks.py 使用新的 --scratch 合成夹具目录，按需提供 --browser-path；浏览器检查需 Playwright，仅读取本轮生成代码，不复用个人浏览器会话。

新增公共文件先加入 release-files.json；运行 build_release.py 刷新通道清单与 SHA256SUMS，按 --zip / --archive 创建新候选，不能覆盖已发布附件。Markdown／HTML 本地链接、内容一致性和桌面／窄屏／打印布局需要分别核对。

## 通道与验证

shared-skill-files.json 只列完整通用文件，先审阅差异再用 sync_shared_skill.py --apply。其余专题按段评估，不能整份跨版本覆盖。受影响检查器使用真实 CLI 验证；安装器使用新的隔离目录核安装、重复安装、切换、备份和个人区。原生宿主、SDK、模型行为、页面布局与静态检查分别报告，具体范围见[验证说明](../VALIDATION.md)。

## 公开边界

个人偏好与插件指南只从实际用户区读取，不能进入公共源、包或测试夹具。原始宿主返回、私人审阅说明、恢复包与工作过程留所属维护工程；公共内容保持读者可直接使用的说明。旧版有效知识按版本保留；退出使用的正文从历史发行或内部原文备份追溯，不在现用正文追加互相冲突的更正。
