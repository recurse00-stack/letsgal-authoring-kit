# 维护交接

当前：独立公共技能 letsgal-authoring，0.1.0-preview.4。已加入 DSH 适配与图形导入器。本包是维护源与分发候选，不是任何机器的已注册技能。修改范围是此目录，不能同步覆盖其他个人技能。

本轮新增：用户区 preferences/ 与 plugins/ 分离，旧版 user.md 原位兼容；插件 Skill 自动按 ID／版本落位，用户独立维护。安装器只创建缺失用户项，不覆盖现有内容；真实旧版升级及失败保留测试见验证记录。

入口：README.md 面向使用者；skills/letsgal-authoring/SKILL.md 面向 AI；SOURCES.md 保存来源；VALIDATION.md 标记验证层次；WORKSHOP.md 列投稿剩余事项。

修改后：核官方规范和目标版本，更新公共技能／脚本；对公共文件重算 bundle.json 的 SHA-256。个人特调不写进包。新增用户配置格式须另做有备份的显式迁移；当前 Markdown 格式不需要迁移。

运行 maintenance/run_checks.py 时传全新隔离目录。PS1 使用 UTF-8 BOM 兼容 Windows PowerShell 5.1；CMD 使用 ASCII／CRLF。检查器只依赖 Python 标准库。bundle.json 只列技能目录中的文件，不能包含上跳路径。最终重新生成 SHA256SUMS.txt 和 ZIP，并解包逐项核对。

Import.xaml / Import.ps1 是 WPF 界面；Install.ps1 是实际修改文件的后端；Import.Paths.ps1 供双方共用路径算法。界面通过隐藏子进程调用后端，使用 EncodedCommand 和单引号转义处理含空格／中文／撇号的目录。-PrepareOnly 只供同进程组件测试构建界面，正常启动不使用它。

maintenance/run_dsh_checks.py 需要显式传入当前安装的官方 provider 文件及新的 scratch；不启动 DSH 服务。maintenance/Test-ImportUI.ps1 测 WPF 自身事件并渲染 PNG，不是鼠标点击验收。新增的测试目录可能含 junction，不能顺手递归清理。

维护时先用 python -B maintenance/build_release.py 更新清单与编码，然后运行 VALIDATION.md 中的测试，更新验证记录；最后加 --zip 构建新包（拒绝覆盖已存在 ZIP）。不要把测试目录、真实数据路径或用户配置加入发行包。

公共包不存在完整 LetsGal SDK 或已初始化的引擎扩展源码。若开始工坊承载开发，先核当前表单与 SDK，按官方初始化流程实施；不要靠伪清单跳过真实验证。没有任何持续进程、网络端口或后台服务属于本包。

本轮复核：加入项目版本分流、未知格式保留、同目标进程锁、回滚边界、发布文件白名单与隐私检测。MANUAL.md 是用户手册；PRIVACY.md 是实际发布边界。发布文件必须逐项加入 release-files.json，再运行 review_release.py；任何测试目录、截图和安装状态不在清单中。

待发布目标是独立 GitHub 仓库，仓库地址与本机过程仅留在维护会话，不硬编码进公共 Skill。GitHub 上传、真实引擎版本验收和工坊审核分别核实，不能以其中一项替代另一项。
