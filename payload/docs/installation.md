# 安装、启停与工作台

需要 Python 3.10+。在解压后的包根运行 `python Install.py`，先查看目标、版本与是否需要备份；确认后运行 `python Install.py --install`。

默认检查个人 Codex 的 skills 根；使用其他 Agent 或自定义用户区时，传入 `--skills-root` 与 `--user-area`。检测到主 Skill 时，将本包放入用户区的 `addons/letsgal-extension-design/<版本>/`；没有主 Skill 时安装为独立 Skill，手册保留在其 `docs/README.md`。

主包支持自动接入时，安装完成后在用户区 `workbench/MANUAL.html` 的“创作参考”中打开本包。主包较旧时显示等待接入，安装结果保留；以后安装支持该接口的主包即可自动汇总。

## 更新与切换

相同内容重复安装只校验。相同版本的内容不同，安装器会停止；核对更改后使用 `--replace`，原文件保存在用户区 backups。安装另一版本保留原选版，显式 `--select` 才改为本次版本。已暂停的包继续暂停，`--enable` 才恢复。

新式包的状态保存在 `addons/letsgal-extension-design/state.json`。可请 AI 使用工作台的状态命令切版或暂停；例如在用户区执行：

```text
python workbench/workbench_runtime.py state --user-area . --id letsgal-extension-design --enabled no
```

暂停保留文件，Wiki 只显示条目信息。主 Skill 更新及卸载保留这些资料。需要移除本包时，先暂停，再按安装记录备份并移出该 ID 对应的版本与登记；保留其他包和个人资料。

旧索引已有本包但没有机器可读状态时，需要先核原有启停及选版，安装器不会从自由文本猜测迁移状态。
