# 8. 更新、切换、卸载与备份恢复

## 更新或切换前准备什么

准备完整的新包，确认当前安装路径、通道、版本及修订，并备份作品与需要迁移的个人资料。同一产品版本可能有不同候选修订；“内容不同”不表示哪一份更新。未标注修订的旧包也不能凭目录日期猜先后。

## 用同一安装器更新

1. 把新包完整解压到另一普通目录，运行 `Install.cmd`。
2. 选择同一实际 Agent 位置和所需 Stable／Beta。核对预览中的已装与本包信息，再导入。
3. 内容一致时应校验后保持不变；内容不同则先完整备份旧 Skill，再安装所选载荷。
4. 检查安装，并在新会话核实际路径和修订。新会话应能读到所采用的修订。

个人偏好、插件知识和作品配置保留，主包不升级宿主、不启用暂停资料。遇到已安装文件被个人改动，先比较并把个人部分迁到用户区；只有明确选择“备份后继续”才替换，旧改动不会自动合并进新版。

## 备份在哪里，怎样恢复

旧 Skill 存在 skills 目录旁的 `.letsgal-authoring-backups`，安装结果及 `*-install.json`／`*-uninstall.json` 日志记录准确备份路径。备份不会作为第二份 Skill 自动发现。不要通过清空所有备份排错。

> 请找到上次安装日志指向的旧 Skill 备份，比较当前与备份的通道、修订和文件。先保全当前内容，只恢复指定 Skill，个人区和工程文件保持；恢复后校验文件及新会话读取。

恢复前保留当前新增内容，按准确目录核对后恢复；不复制到另一默认目录制造同名入口。个人区要另行备份，安装器旧 Skill 备份不包含它。备份可能有私人特调，提交 Git 或公开分享前检查内容。

## 卸载与换电脑

“更多选项”中的卸载或 `Uninstall.cmd` 会把当前 Skill 移入备份，保留用户区、作品和历史备份。引擎及插件的安装保持原状。

换电脑、账号、WSL 或远程环境时，在实际运行 AI 的环境另行安装；只按需要复制自己的偏好与插件资料，再核路径和版本。迁移材料作为个人备份单独保存。

## 查阅：手动安装与命令行

Windows 完整包根目录示例：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Install.ps1 -Harness Codex -Scope User -Channel stable -NonInteractive
powershell -NoProfile -ExecutionPolicy Bypass -File .\Install.ps1 -Harness Codex -Scope User -Channel stable -Action Check -NonInteractive
```

| 参数 | 用途 |
| --- | --- |
| `-Action` | Install、Check 或 Uninstall，默认 Install |
| `-Harness` | Codex、Claude、Cursor、Copilot、DSH、Manual |
| `-Scope` | User 或 Project；Project 配 `-ProjectPath` 工程绝对路径 |
| `-Channel` | stable 或 beta；非交互必须明确选择 |
| `-SkillsDirectory` | Manual 的已配置 skills 根，安装器追加 letsgal-authoring |
| `-DshHome` | DSH 实际数据目录；显式值优先于环境默认 |
| `-UserHome` | 实际用户主目录，隔离安装检查可用独立目录 |
| `-NonInteractive` | 非交互执行；不会替你解决路径歧义或修改冲突 |
| `-ReplaceModified` | 比较并明确批准后，完整备份已修改载荷再替换 |

安装器不自动扫描自定义 CODEX_HOME 或便携目录。目录兼容、同名入口处理和 DSH 配置详见[兼容说明](../../COMPATIBILITY.md)。不要关闭系统保护来绕过执行策略；可按客户端要求手动安装。

macOS／Linux 或自选环境：仅复制所选通道的完整 `skills/letsgal-authoring` 目录到已配置的 skills 根，保留原版备份和随包风险说明，再核实际发现。不要混合两通道或只复制 SKILL.md；Windows 安装程序的验证范围见下方说明。已有用户区保持，首次需要偏好时在实际用户主目录建立相应文件。

## 遇到安装差异

目录重叠时重新选择互不包含的包、技能与用户区位置，不删除个人区绕过。安装锁被占用时等另一个安装结束，不删除活动锁。如果 Skill 已完成但选项或日志保存失败，核真实文件、备份路径和提示，下次重新选位置，不反复强制覆盖。

本包当前验证边界见[验证范围](../../VALIDATION.md)，宿主操作证据见[宿主范围](../../HOST-VALIDATION.md)。
