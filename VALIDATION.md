# 0.1.3 当前验证范围

2026-09-30 全面修订及纠正见[AUDIT.md](AUDIT.md)。以下都是本轮候选实际执行结果，旧版结果不累计为当前完整验收。

46项 installer_and_checker、20项 version_routing、13项 authoring_diagnostics、23项 public_boundary_and_archive、32项 upgrade_from_0.1.2通过；Skill格式、公开隐私与相对引用通过。13项新诊断检查在真实Python CLI运行合成章节，验证引用冲突、转换风险提示、前处理、未覆盖数量及只读性；并非Studio转换／播放测试。完整结果见[validation-results.json](validation-results.json)。

实际只读提取EXE FileVersion=2.3.0-beta.1。既有SDK副本自报1.21.0且没有历史追加声明，工具保留来源UNKNOWN和兼容未验证，不将该副本当配套Beta SDK。官方当前历史页也未给追加签名，UNKNOWN保留。

独立代理在当前会话按候选Skill完成两个只读任务：版本冲突与旧SDK/新API处理，实际调用路由／检查器并查证源码与官方页。此项仅验证当前会话的限定行为，不是三款安装后Agent完整任务。Cursor／Copilot仍只有官方格式与目录依据。

安装器控制逻辑／GUI原字节保留；新payload仍从不可变0.1.2完整包做实际隔离升级，核对个人区、插件知识、旧版备份及失败分支。运行两个现有Windows PowerShell，不操作真实账号或作品。

原生安装GUI点击／取消／缩放、Stable与Beta完整剧情／存读档／全新启动／Windows导出仍未完成；当前工具缺原生窗口操作能力，没有以API或脚本绕过。main调用及禁用块转换、新Beta参数与序列化仍需目标宿主SDK／保存样本。

Markdown和离线HTML同步。运行脚本从完整包根或实际Skill绝对目录调用，安装不要求Python；可选工具需要Python3.9+。复核新增诊断可在全新scratch中运行maintenance/run_authoring_checks.py。

源码、GitHub main、tag、Release、附件和匿名下载分别记录，候选静态检查不表示外部发布。工坊not-applicable；门禁见[RELEASE-GATES.md](maintenance/RELEASE-GATES.md)。
