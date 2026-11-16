# 维护入口

当前总包与 Stable 载荷 3.0.5，修订 20261116-r7-workbench：三模块工作台、个人包编辑与包管理保留；r6／r7 用法和定向存读档验证已更新。动态片段读档的镜头状态／画面差异在预览专题与 Wiki 提示。Beta 载荷 2.9.2 / 20261116-workbench；Stable 的新实测结论不转写为 Beta 验证。开工按主次版本与实际发行身份检查，同系列补丁／热修复不单独暂停。

## 手册生成

MANUAL.md 是导航，docs/wiki/ 为专题正本，manual-layout.json 登记正文顺序、主指南导览、资料分类与旧锚点。wiki.html、wiki.css、wiki.js 分别维护页面模板、样式和本地交互。修改正文或前端后执行 `python -B maintenance/build_manual.py`，只检查生成物是否最新时加 `--check`。维护环境需要 Python Markdown；生成的 MANUAL.html 内嵌正文、样式和 JavaScript，不需要 Python、网络或服务端，禁用脚本时仍可完整阅读。

build_workbench.py 只在显式 --user-area 下读取接入清单；个人产物必须新建在公共发行工程外，不能回写 MANUAL.html。字段见 wiki-manifest.schema.json，用法见[资料接入](../docs/wiki/10-workbench-interface.md)。run_wiki_checks.py 使用新的 --scratch 合成夹具目录，按需提供 --browser-path；浏览器检查需 Playwright，仅读取本轮生成代码，不复用个人浏览器会话。

新增公共文件先加入 release-files.json；运行 build_release.py 刷新通道清单与 SHA256SUMS，按 --zip / --archive 创建新候选，不能覆盖已发布附件。Markdown／HTML 本地链接、内容一致性和桌面／窄屏／打印布局需要分别核对。

个人包由 workbench_personal.py 维护固定三页与状态，wiki-personal.js 提供编辑和保存；仅在用户区补缺失文件。Markdown 解析使用随包 Marked，来源和许可见 vendor/marked；页面继续通过统一清理器呈现。run_personal_checks.py 覆盖初始化、旧入口、编辑冲突、状态、导航与服务退出，使用新的隔离 --scratch 目录。离线阅读与本机编辑的连接状态同步；候选中不得嵌入真实个人正文。

## 通道与验证

shared-skill-files.json 只列完整通用文件，先审阅差异再用 sync_shared_skill.py --apply。其余专题按段评估，不能整份跨版本覆盖。受影响检查器使用真实 CLI 验证；安装器使用新的隔离目录核安装、重复安装、切换、备份和个人区。原生宿主、SDK、模型行为、页面布局与静态检查分别报告，具体范围见[验证说明](../VALIDATION.md)。

## 公开边界

个人偏好与插件指南只从实际用户区读取，不能进入公共源、包或测试夹具。原始宿主返回、私人审阅说明、恢复包与工作过程留所属维护工程；公共内容保持读者可直接使用的说明。旧版有效知识按版本保留；退出使用的正文从历史发行或内部原文备份追溯，不在现用正文追加互相冲突的更正。


包管理包含本机管理服务、统一包外登记、启停/选版和暂停时展示；原协议兼容。新注册清单与维护检查见 docs/PACKAGE-MANAGEMENT.md 和 maintenance/run_package_checks.py。个人登记、载荷和测试证据留在用户区或内部任务，不进入发行白名单。
