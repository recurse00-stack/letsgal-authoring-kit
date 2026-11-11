# 7. 已知差异、排错与精确恢复

## 写前准备与写后核对

准备至少一种实际可用、覆盖本次改动的恢复点，优先已有项目历史／检查点或支持该操作的撤销；素材、独立源码等没有覆盖的部分另做备份。安装器只备份 Skill，不备份作品。已有有效保护可以复用。

> 请只恢复本次试改的内容。先比较原恢复点与当前文件，列出会写回或删除的对象，保留试改之后我新增的内容；恢复后逐项读回，说明还存在的差异。

精确恢复按对象、字段或限定文件进行。整工程恢复可能移除备份后新增文件，不默认采用。若后来编辑与恢复目标重叠，先合并可确定的差异，再把仍需决定的部分说明清楚。

## 三类已确认差异

**Studio 3.0.0 的官方 MCP 复测**曾出现以下差异，相关操作先按右侧步骤保存原态并核对结果。

| 操作 | 实际遇到的差异 | 怎样核对与继续 |
| --- | --- | --- |
| 扩展设置 reset | 官方内置壳的 boolean、enum 改值后 reset 成功，但读回 isDefault=false 且缺 value；数组字段也有默认态标记差异 | 写前保存值是否存在、值与默认态。写后逐项比较。缺值不解释成 false、空字符串或默认值。显式写回旧值和恢复默认态分别报告 |
| 修改入口数量后 undo | basic／linear 改入口数后变为 advanced／extension；undo 恢复数量却未完整恢复模式、策略和图 | 写前保存四项。撤销后逐项读回，必要时审阅限定历史恢复。把原图显式写回而策略变成 graph，不算完整还原原来的 linear |
| 官方文件编辑会话 | 有效会话内的单句文件修改可能回到原文，dry-run 随后为空变更；仅启用内置壳也复现 | 普通修改优先专用 MCP。预期有改动却为空时停止 commit，保留拟写内容，核会话、文件、保存与编辑状态；安全结束会话后用获准专用接口重新读取并修改 |

设置字段未声明默认值时，缺 value 本身可能正常；上述 MCP 读回差异不证明 SDK 运行取值、界面重置按钮或 Player 都出错。文件会话切换章节后仍有复现，切章节不是已验证解决办法。不要为了恢复状态反复重载工程、覆盖整份配置或丢掉后来编辑。

AI 的详细操作规则按通道查阅：Stable 3.0 使用[扩展设置](../../channels/stable/skills/letsgal-authoring/references/extensions.md#设置存档与资源)、[调度恢复](../../channels/stable/skills/letsgal-authoring/references/collaboration-git.md#限定恢复与读回)和[文件会话](../../channels/stable/skills/letsgal-authoring/references/mcp-workflow.md#外部编辑与无-mcp-回退)；Beta 2.9／2.8 使用[Beta 设置](../../channels/beta/skills/letsgal-authoring/references/extensions.md#设置存档与资源)、[Beta 恢复](../../channels/beta/skills/letsgal-authoring/references/collaboration-git.md#限定恢复与读回)和[Beta 文件会话](../../channels/beta/skills/letsgal-authoring/references/mcp-workflow.md#外部编辑与无-mcp-回退)。Beta 的历史现象保留其版本条件，不把 3.0 复测直接当作 Beta 重测。

## 哪些情况不应直接叫缺陷

- `project_delete` 明确不支持普通 undo。数据行依项目历史限定恢复，素材按隔离区恢复入口；普通 undo 未找回删除对象不构成该契约的失败。
- 任意添加的未声明字段没有保真承诺。使用受支持的数据位置，保留格式契约内的内容。
- 等待批准、只读、关闭工具组、不支持的目标平台，以及本次调用参数错误，分别按权限、能力和输入处理。
- GIF／WebP 的 3.0 独立样本限定撤销与删除通过，旧占用现场不再列为 Stable 当前故障。出现新失败仍需核部分完成结果、引用、文件与隔离区。

只有目标版本承诺支持的行为与符合契约的实际调用不一致，才列为问题。遇到结果未知，先读回目标或操作历史，不能把超时当作完全没写。

## 预览与构建

`WINDOW_HIDDEN` 先核具体 reason 和预览状态。最小化、锁屏、遮挡或停在其他模块可能不满足官方渲染条件；不在前台本身不能证明隐藏。按授权恢复对应条件后再试一次，仍失败就保留未验项。窗口仍可见却被判为隐藏时，记录 reason、窗口状态和最小调用再反馈。

构建先核配置、工具链和 dry-run；桌面目标按实际 `supportedSystems` 选择，不从旧网页或操作系统名称推测。构建计划有效、产物生成、产物在目标系统运行分别验收。未构建过的导出不能写成已通过。

## 反馈问题要准备什么

提供 Skill 修订、Agent、Studio 完整版本、具体工具、最小输入、预期与实际返回、恢复状态。先排除版本不符、输入错误及本来不支持的操作；只发脱敏片段或独立样本。不要上传完整私人作品、账号、令牌或未经清理的截图。可以在[仓库 Issues](https://github.com/recurse00-stack/letsgal-authoring-kit/issues)反馈 Skill 问题；宿主问题提交实际可复现的现象和步骤。
