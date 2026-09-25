# 验证状态

2026-09-25，0.1.0-preview.4：**172 项隔离检查通过，0 项失败**。明细见 [validation-results.json](validation-results.json)，改动审阅见 [REVIEW.md](REVIEW.md)。另通过 skill-creator 格式检查（Windows 使用 Python UTF-8 模式）。

| 层次 | 结果 | 覆盖 |
| --- | --- | --- |
| 基础回归 | 46 项 | JSON、错误结构与引用、未知字段保留、安装／升级／备份／卸载、四种原有 Agent、链接拒绝 |
| DSH 适配与官方 provider | 26 项 | 两种 PowerShell、默认／环境／指定数据目录、Git 根、官方 provider 的发现与读取、卸载状态 |
| WPF 组件事件 | 30 项 | 两种 PowerShell 各 15 项：用户区两类路径显示、选择、路径、隐藏后端、完成结果、重复导入、检查、本地修改保护 |
| 安装安全回归 | 22 项 | 两种 PowerShell 各 11 项：异常路径、真实跨进程锁与释放、目标原文保留、配置类型和无效 DSH 路径 |
| 用户区保护与真实旧版升级 | 32 项 | 两种 PowerShell 各 16 项：preview.3 到当前版、偏好与多版本插件逐字节保留、旧偏好不被空白配置遮挡、重复安装／检查／卸载、异常对象与失败更新保护 |
| 版本与发布边界 | 16 项 | 未知章节／索引／参数格式、只查语法、功能未验证标记、隐私检测、实际 ZIP 排除未列出的私人文件 |

DSH 使用 0.1.6-alpha.2 随附官方文件系统 provider，在指定的隔离目录中运行，关闭 watcher。没有访问真实 DSH 服务、模型、预设或账号数据。

安装／升级测试保留个人 user.md、项目 LETSGAL.md 和另一个名称的私有技能，按字节比较。新增用户区测试同时保留新旧偏好、两个插件版本的 SKILL.md、插件索引、未知二进制补充文件与原插件源码。安装器自己的 installer-state.json 用于保存选项，可随安装更新；它不属于用户偏好或插件资料。不同版本号及不同内容的升级测试仍覆盖；不是用同包重装代替升级。路径含中文、空格、撇号。

WPF 测试直接触发本程序事件，通过正常隐藏子进程调用后端。已查看导入前后渲染；没有宣称它等于操作系统鼠标点按验收。渲染用于核对组件布局，不等于操作系统鼠标点按验收。

## 复现

在包根目录运行，scratch 都应是新建的绝对路径：

```powershell
python -B maintenance/build_release.py
python -B maintenance/review_release.py
python -B maintenance/run_checks.py --scratch "<基础检查目录>"
python -B maintenance/run_review_checks.py --scratch "<版本与发布检查目录>"
python -B maintenance/run_user_area_checks.py --previous-bundle "<已解压的原版 preview.3 包目录>" --scratch "<用户区保护检查目录>"
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
