# 维护入口

本版 0.2.9 / 20261111-stable300，Stable 3.0.0，Beta 2.9.0-beta.1／2.8.0-beta.1。后续发行单独确定版本与发布范围。名称、原检查命令参数、JSON 输出与退出码保持兼容。

## 手册生成

MANUAL.md 是导航，docs/wiki/ 的八页是正文正本。修改正文后执行 `python -B maintenance/build_manual.py`，只检查生成物是否最新时加 `--check`。维护环境需要 Python Markdown 包；生成的 MANUAL.html 自包含，不需要 Python、网络或脚本运行时。布局、旧锚点兼容和页面顺序登记于 manual-layout.json。

新增公共文件先加入 release-files.json；运行 build_release.py 刷新通道清单与 SHA256SUMS，按 --zip / --archive 创建新候选，不能覆盖已发布附件。Markdown／HTML 本地链接、内容一致性和桌面／窄屏／打印布局需要分别核对。

## 通道与验证

shared-skill-files.json 只列完整通用文件，先审阅差异再用 sync_shared_skill.py --apply。其余专题按段评估，不能整份跨版本覆盖。受影响检查器使用真实 CLI 验证；安装器使用新的隔离目录核安装、重复安装、切换、备份和个人区。原生宿主、SDK、模型行为、页面布局与静态检查分别报告，具体范围见[验证说明](../VALIDATION.md)。

## 公开边界

个人偏好与插件指南只从实际用户区读取，不能进入公共源、包或测试夹具。原始宿主返回、私人审阅说明、恢复包与工作过程留所属维护工程；公共内容保持读者可直接使用的说明。旧版有效知识按版本保留；退出使用的正文从历史发行或内部原文备份追溯，不在现用正文追加互相冲突的更正。
