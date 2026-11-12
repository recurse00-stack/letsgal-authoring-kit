# 可视化 UI 与数据表

字段查当前 ui-document-format、ui-elements、ui-actions、ui-smart-components、data-formats 及工具 schema。

## 先确定页面与作用范围

ui_read 的 documents／slots 定位实际文档、来源、可写性和槽位绑定，再取目标 revision。创建使用唯一名称，后续使用返回的 document。页面预览与全局槽位绑定按各自授权范围执行。

已有页面优先 ui_edit 局部修改；调用内别名在写后换成真实 ID。整页替换先完整读取，保留元素 ID、非目标字段、状态、动画、子模板和引用；ui_replace_document 带 baseRevision，并保存返回的备份入口。ui_remove_elements 删除前核子节点和引用。

按宿主规则使用 CSS、资源路径及链接；被拒绝时调整设计。写后读回并执行相关 project_validate(kind="ui")，然后检查布局与交互。

## 状态、动作与智能组件

- 本地 UI 状态和游戏变量各明确 source、ID、类型、初值。核初始显示、真实点击后的值／显示、关闭及重开状态。
- 动画观察进退场和持续时间，等淡入完成后评估最终布局。
- generatedDefault=true 的子模板首次持久化可能换 ID；首次修改后重读再编辑。
- 保留智能宿主标记和模板结构；数据列表绑定启用扩展公开的数据源别名，核行字段、权限、真实数据与空态。

预览目标用 `ui:<文档名>`，页面 ui.open 动作按其 schema 填目标。open_ui／close_ui 读取容器、topModal 和输入通道；按钮效果通过真实点击检查。

带图片的数据列表在应用 3.0 r5 后核预览，再重新导出需要交付的游戏；官方说明该补丁的列表修复适用于补丁后的新导出产物，已有导出包需重新生成。分别核对列表图片、数据绑定和交互，保留产物的实际验证范围。

模态 UI 从前一句连续进入，检查等待、关闭后正文和输入穿透。seek 可能跳过 skip-if-seeking 指令。按改动选择“读回校验 → 布局 → 动作与条件 → 关闭／重开 → 剧情返回”；输入不可用则记录该项待验。

## 主题与样式的恢复

theme_edit 写样式，theme_apply 选择生效样式；读 current 的 source、id、selectedExplicitly，再核画面。测试前保存原选择与恢复点；原先未显式选择时，用限定配置恢复并读回这三个字段。

CG／片段鉴赏的角色分类按当前组件 schema 使用（含 cg-character-tabs），保留数据源绑定。鉴赏排序使用扩展设置中的分类数组，以实际条目 ID／资源路径读写，核顺序和鉴赏页。重置排序前先读[设置默认态与恢复](extensions.md#设置存档与资源)，保存原值和默认态，再逐项读回。

## 数据表的编辑与运行

database_read／database_inspect 核表、列类型、契约、扩展依赖及 runtimePolicy；按 readonly／session／archive／profile 的目标范围验证运行与持久化。

upsert_rows 新增时省略 id，让宿主生成；修改使用现存 ID 和 expect。结构修改带 baseRevision，冲突重读；字段按列类型写入。

删行前保存原行、稳定 ID 和引用，并取得覆盖集合文件的项目历史恢复点；核 `project_delete` 的范围、dry-run 和原生确认。其契约不支持 `history_undo`，不能用普通 undo 的成功或零目标判断删行恢复。需要恢复时审阅 `history_restore` 的 filesToWrite／filesToDelete，限定集合文件并保留后来编辑，读回原 ID、字段及引用。素材删除另按返回的隔离区恢复入口处理；具体恢复方式由该操作契约决定。只有已获准重建且不需保留引用的测试行才可创建新 ID。

游戏数据通过扩展依赖或 UI 数据源访问；交付时验证消费者读取、绑定和所需存档范围。
