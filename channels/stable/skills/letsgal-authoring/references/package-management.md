# 包管理与按需读取

本页用于管理个人包、已安装的附属 Skill 和插件指南。总 Wiki 的包管理页可以启用、暂停、选择已安装版本，并选择暂停时是否保留手册展示。实际状态保存在用户区，界面操作成功后才生效。

个人包固定键为 `personal/letsgal-personal`，状态位于 `preferences/package-state.json`。它只有启停与暂停展示，没有发行选版；正文按[个人资料](customization.md)读取。

## 在任务入口核状态

只核当前任务相关的包。新式附属包沿 `addons/<id>/state.json`；旧包和插件指南适配登记位于 `workbench/packages/<类型>/<id>/state.json`，类型为 `addon` 或 `plugin-guide`。索引指向已有状态时沿该入口读取；匹配注册缺失时继续使用原索引规则。嵌套包无需进入 Agent 全局发现列表。

`enabled=false` 时跳过 AI 正文读取。阅读空间中的版本切换只影响阅读，AI 选版仍以状态文件为准。`show_when_paused` 仅控制人类 Wiki；即使手册可见，该包仍暂停。状态变化后重新核对，复用正文前确认原选版和启用状态仍适用；同一未变化任务无需逐次调用重复读取。

`selection_mode=fixed` 使用 `selected_version`；插件指南默认 `auto`，按实际插件 ID 和版本查已登记版本。固定版本与工程版本冲突时报告差异，使用匹配的官方资料或主 Skill 能力继续可完成工作。不同作品可使用不同版本，不能按目录排序取最新。适配包入口由版本记录中的用户区相对 `root` 和 `entry` 定位。

需要确定性读取时，调用用户区的工具：

```text
python workbench/workbench_packages.py resolve --user-area . --key personal/letsgal-personal
python workbench/workbench_packages.py resolve --user-area . --key addon/example-reference
python workbench/workbench_packages.py resolve --user-area . --key plugin-guide/example.weather --actual-version 1.0.0
```

个人包 `legacy` 表示旧安装继续使用返回的偏好入口。`ready` 返回所选入口；`paused` 跳过；`unregistered` 沿已有索引定向核查；版本缺失或不符按返回原因处理。工具只读取登记，不载入 Skill 正文，也不操作 Studio。

## 修改管理状态

使用者在 Wiki 点击管理按钮，就是对该项启停或选版的明确选择。AI 按请求使用相同状态工具，保留其他包及版本：

```text
python workbench/workbench_runtime.py state --user-area . --package-type personal --id letsgal-personal --enabled no
python workbench/workbench_runtime.py state --user-area . --id example-reference --enabled no
python workbench/workbench_runtime.py state --user-area . --id example-reference --show-when-paused yes
python workbench/workbench_runtime.py state --user-area . --package-type plugin-guide --id example.weather --version 1.0.0
```

切版不改变启停；显示手册不改变启停。保存失败先读回实际状态，结果未知时不重复提交。状态工具保全原文并同步刷新 Wiki；恢复入口在返回的 backup 中。新安装和主包更新保留已有选择。

## 新包与旧包接入

新式附属包随安装自动登记。已有文件通过完整主包的 `docs/PACKAGE-MANAGEMENT.md` 协议显式注册，可提供多版本 Skill 入口与 Wiki；注册成功后总 Wiki 自动合并。接入工具验证身份、范围和校验值，原载荷保持不变。公共包只携带协议、工具与合成示例，实际个人资料留在用户区。
