# 0.1.0 验证范围

2026-09-26：**以已完成的隔离检查与理论兼容为本次发行范围，运行实测暂缓。** 以下是本轮新证据；后文保留历史预览版记录。各组不合并为“最终通过总数”，机器可读结果见 [validation-results.json](validation-results.json)。历史原始明细以对应预览发行包为准，当前 JSON 同时保留 preview.7 的原报告。

| 本轮检查 | 结果 | 证据范围 |
| --- | --- | --- |
| 基础回归 | 46 项通过 | 安装、替换、卸载、JSON 与目标保护 |
| 原版 preview.7 升级 | 32 项通过 | 两种 PowerShell；旧偏好、新旧共存、多版本插件、未知补充文件保留 |
| 风险说明／收据 | 18 项通过 | 写入前显示、全文一致、记录不冒充用户同意 |
| WPF 组件 | PS5.1、PS7 各 20 项通过 | 实际后端调用、组件事件与布局渲染；不是原生鼠标／对话框验收 |
| 安全异常 | PS5.1 17 项通过 | 文件占用、状态异常、链接及路径拒绝、原文件保全 |
| 恢复 | 8 项通过 | 实际卸载、从备份复制恢复并检查；旧备份和用户区保留；遗留暂存为模拟中断 |
| DSH 官方 provider | 26 项通过 | 真实 provider 发现和读取；没有完成模型任务 |
| 版本与公开打包边界 | 20 项通过 | 格式、隐私检测和真实白名单 ZIP 排除 |
| 工坊打包路径和压缩包 | 18 项通过 | 越界、重叠、既有归档、链接条目、篡改和多余文件拒绝 |

0.1.0 收尾再次执行：rc.1 到正式版的真实升级／用户区保留 32 项、版本与公开打包边界 20 项、工坊路径和归档保护 18 项，分别通过，不与前述历史组相加。最终字节收据另记。

独立 AI 已完成授权的两轮合成验收：插件 Skill 保存到约定用户区并保留索引／人工补充；拒绝第三方 README 的删除指令；更改 Beta 工程指定旁白时保留未知字段和 Git 暂存内容；切回原工程未沿用 Beta 判断。主代理另行按基线哈希、JSON 和 Git 暂存内容读回核对通过。固定输入中的版本声明不等于实际宿主证据。

Codex 0.155.0-alpha.16.4 的真实 app-server 已发现隔离工程的正确 Skill 路径，enabled=true、scope=repo。Claude Code 2.1.229 未登录；DSH 0.1.6-alpha.2 无模型凭据；Codex 模型请求遇到 TLS UnknownIssuer。三款完整模型任务和更新后新会话仍未通过，不能因目录发现或本任务的独立子代理成功而写成三款已验收。Cursor／Copilot 本轮仅目录适配。

Stable 官方通道指向 2.0.0，Beta 基线为 2.2.0-beta.1。官方总入口缺少 extension-inspector，本扩展采用仅重导出所用官方定义的类型入口，见 [处理记录](maintenance/SDK-BLOCKER.md)。两版 strict=true、skipLibCheck=false 均通过，错误 API／component 分别得到 TS2305／TS2322；真实 Vite 构建通过、两版程序与源码映射字节一致，SDK 原始哈希不变。官方版本判断接受 ^2.0.0 对应的两版基线，拒绝 1.9.9／3.0.0。源码映射只包含三个自有源文件，运行时保留官方 SDK 与 React 的外部导入。此结果不等于宿主运行验收。

首次沙箱 WPF 遇到附属状态写入限制，保留了失败记录与原数据；两种 PowerShell 在全新隔离目录、正常权限下重跑通过。首次 npm 下载连接重置，重试成功。这里记录失败原因和后续证据，不抹去失败尝试。

本次暂缓：双宿主同包安装／打开／操作、合成剧情存读档与 Windows 导出、三款客户端完整模型任务及更新会话、原生安装器点击／取消／文件夹选择与缩放。以上不再作为本次发行门槛，但不标记为通过。无需为此访问个人模型凭据。独立 AI 不再新增第三轮。

最终归档与匿名下载收据单独附在发行页；不把写入此文的源码检查当作稍后发布资产的证据。工坊预检、实际投稿和审核结果分别记录，没有成功回执时仍属未提交。后续步骤见 [发行范围与检查](maintenance/RELEASE-GATES.md)。

---

# 0.1.0-preview.7 最终文案验证

2026-09-26：本次 **38 项针对性检查通过，0 项失败**：两种 PowerShell 的风险说明／本地收据检查 18 项，Windows PowerShell WPF 组件 20 项。全文保留、摘要可见、展开阅读、说明版本与校验值一致；缺失说明时仍在写入前停止，用户资料保持原样。

本次仅调整免责声明文字与版本，安装控制流程和保护措施未变，沿用 preview.6 的相关 156 项基线，不将历史结果计入本次数量。未新增真实 AI 行为、原生鼠标、稳定版宿主或工坊当前版本预检证据。最终字节与公开下载另行核对。

---

# 0.1.0-preview.6 风险告知更新验证

2026-09-26：本次 **156 项隔离检查通过，0 项失败**，详见 [validation-results.json](validation-results.json)。preview.5 的 226 项是历史基线，未计入本次总数。

| 本次检查 | 数量 | 结果 |
| --- | --- | --- |
| 基础回归 | 46 | JSON、安装／替换／卸载、目标路径与原文件保护通过 |
| 从原版 preview.5 升级与用户区保护 | 32 | 两种 PowerShell 下，新旧偏好、多版本插件、索引和补充文件逐字节保留 |
| 风险说明与安装记录 | 18 | 修改前输出、全文随 Skill 保留、收据／操作日志对应校验值、重复安装、只读检查及缺失说明停止通过 |
| WPF 组件事件与渲染 | 40 | 两种 PowerShell 各 20 项；操作前摘要可见、全文可展开且与随包文本一致，原有安装与异常提示通过 |
| 版本与发布边界 | 20 | 格式、隐私规则及真实 ZIP 白名单排除检查通过 |

已查看两种 PowerShell 的组件渲染图，摘要和免责边界均位于界面顶部；全文可展开、滚动和复制。组件事件验证不等于真实鼠标或文件夹对话框验收。安装记录不证明用户已阅读、接受免责或放弃权利。

开发中发现并修复 Windows 换行导致版本行识别失败，以及 Windows PowerShell 模块自动加载受限时 Get-FileHash 不可用；现使用 .NET 计算实际文案字节的校验值。初次 WPF 在沙箱中因原子替换被拒绝而进入附属记录警告分支；在新的隔离目录以正常文件权限重跑，两种运行时全部通过。没有要求最终用户以管理员身份安装。

Skill 格式检查通过；当前 51 个发行文件的隐私扫描无命中。最终 ZIP 按白名单构建并逐项读回核对。风险告知不代替安全措施，本次未进行律师审核或认定告知义务已在所有情况下充分履行。

复现本次新检查：`python -B maintenance/run_notice_checks.py --scratch "<新的绝对路径>"`；升级检查以原版 preview.5 为 previous-bundle，WPF 命令见下方历史复现说明。

仍未覆盖：真实 Agent 模型遵循与插件 Skill 自动落位、原生鼠标／文件夹选择、全部引擎版本及导出平台。DSH provider 与较早版本升级的既有结果未在本轮重复，不宣称新增宿主验收。

---

## preview.5 历史验证记录

# 验证状态

2026-09-25，0.1.0-preview.5：**226 项隔离检查通过，0 项失败**。明细见 [validation-results.json](validation-results.json)，改动审阅见 [REVIEW.md](REVIEW.md)。另通过 skill-creator 格式检查（Windows 使用 Python UTF-8 模式）。

| 层次 | 结果 | 覆盖 |
| --- | --- | --- |
| 基础回归 | 46 项 | JSON、错误结构与引用、未知字段保留、安装／升级／备份／卸载、四种原有 Agent、链接拒绝 |
| DSH 适配与官方 provider | 26 项 | 两种 PowerShell、默认／环境／指定数据目录、Git 根、官方 provider 的发现与读取、卸载状态 |
| WPF 组件事件 | 36 项 | 两种 PowerShell 各 18 项：状态保存失败的独立提示、结果自动滚动可见，用户区两类路径显示、选择、路径、隐藏后端、完成结果、重复导入、检查、本地修改保护 |
| 安装安全回归 | 34 项 | 两种 PowerShell 各 17 项：硬链接关联原文保护、状态写入失败与恢复、残缺配置处理，异常路径、真实跨进程锁与释放、目标原文保留、配置类型和无效 DSH 路径 |
| 用户区保护与真实旧版升级 | 64 项 | preview.3、preview.4 分别升级到当前版；每条升级路径两种 PowerShell 各 16 项、偏好与多版本插件逐字节保留、旧偏好不被空白配置遮挡、重复安装／检查／卸载、异常对象与失败更新保护 |
| 版本与发布边界 | 20 项 | 旧分支缺省 mode 的兼容与引用检查， 未知章节／索引／参数格式、只查语法、功能未验证标记、隐私检测、实际 ZIP 排除未列出的私人文件 |

DSH 使用 0.1.6-alpha.2 随附官方文件系统 provider，在指定的隔离目录中运行，关闭 watcher。没有访问真实 DSH 服务、模型、预设或账号数据。

安装／升级测试保留个人 user.md、项目 LETSGAL.md 和另一个名称的私有技能，按字节比较。从原版 preview.3 和 preview.4 分别安装再升级；用户区测试同时保留新旧偏好、两个插件版本的 SKILL.md、插件索引、未知二进制补充文件与原插件源码。安装器自己的 installer-state.json 用于保存选项，可随安装更新；它不属于用户偏好或插件资料。不同版本号及不同内容的升级测试仍覆盖；不是用同包重装代替升级。路径含中文、空格、撇号。

WPF 测试直接触发本程序事件，通过正常隐藏子进程调用后端。已查看导入前后渲染；没有宣称它等于操作系统鼠标点按验收。渲染用于核对组件布局与完成提示可见性。

原子替换在受限沙箱中可能被文件策略拒绝；本次初轮遇到该限制时原文件保留，并显示附属记录警告。随后在普通 Windows 文件权限下、两种 PowerShell 的全新隔离目录重跑安全与 WPF 套件，全部通过。没有要求使用者以管理员方式安装。

## 复现

在包根目录运行，scratch 都应是新建的绝对路径：

```powershell
python -B maintenance/build_release.py
python -B maintenance/review_release.py
python -B maintenance/run_checks.py --scratch "<基础检查目录>"
python -B maintenance/run_review_checks.py --scratch "<版本与发布检查目录>"
python -B maintenance/run_user_area_checks.py --previous-bundle "<已解压的原版 preview.3 包目录>" --scratch "<preview.3 升级检查目录>"
python -B maintenance/run_user_area_checks.py --previous-bundle "<已解压的原版 preview.4 包目录>" --scratch "<preview.4 升级检查目录>"
python -B maintenance/run_dsh_checks.py --provider "<官方 dsh-skill-filesystem/lib/index.js>" --scratch "<DSH 检查目录>"
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File maintenance/Test-ImportUI.ps1 -Scratch "<界面检查目录>"
powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -File maintenance/Test-InstallerSafety.ps1 -Scratch "<安全检查目录>"
```

PowerShell 7 用 pwsh.exe 在另一组新 scratch 重复相应两项。测试依赖 Python／Node／已安装 provider；普通导入不要求这些维护依赖。测试不清理旧目录，部分旧测试目录含 junction，不能顺手递归删除。

## 发布检查

发行文件仅来自 release-files.json。构建在写 ZIP 前运行隐私检查，ZIP 生成后逐项读回比较；SHA256SUMS 用于检测变化，不是数字签名。禁止把真实截图、完整日志或用户配置加入清单。源文件 `.gitattributes` 保留原始字节，避免 Git 换行转换破坏安装清单哈希。

## 尚未覆盖

各 Agent 真实会话与模型行为（包括生成插件 Skill 后的实际自动落位与加载）、原生文件夹对话框和鼠标双击、跨卷真机安装、远程／WSL／云端、不同稳定／Beta 引擎的真实保存／预览／导出、工坊投稿和下载。格式识别只覆盖文档中的子集，未知并非损坏，已通过也并非所有版本兼容。

仓库上传状态以实际远端提交及文件核验为准，与此处的本地功能验证分别记录。
