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

模态 UI 从前一句连续进入，检查等待、关闭后正文和输入穿透。seek 可能跳过 skip-if-seeking 指令。按改动选择“读回校验 → 布局 → 动作与条件 → 关闭／重开 → 剧情返回”；输入不可用则记录该项待验。

## 主题与样式的恢复

theme_edit 写样式，theme_apply 选择生效样式；读 current 的 source、id、selectedExplicitly，再核画面。测试前保存原选择与恢复点；原先未显式选择时，用限定配置恢复并读回这三个字段。

鉴赏排序使用扩展设置中的分类数组，以实际条目 ID／资源路径读写，核顺序和鉴赏页。2.9 reset 后出现“持久值已清、无 value、isDefault=false”时，先核保存结果，待安全重载后再读默认标记；该样本重载后恢复 true。

## 数据表的编辑与运行

database_read／database_inspect 核表、列类型、契约、扩展依赖及 runtimePolicy；按 readonly／session／archive／profile 的目标范围验证运行与持久化。

upsert_rows 新增时省略 id，让宿主生成；修改使用现存 ID 和 expect。结构修改带 baseRevision，冲突重读；字段按列类型写入。

删行前保存原行、ID 和引用，核 project_delete 范围及确认。撤销后读回原 ID、字段和引用。**2.8／2.9 的删行撤销样本返回成功却 targets=0，原行未恢复**：核快照及后续编辑，再通过 history_restore 限定原集合文件恢复；2.9 样本恢复了原 ID。仅无保留引用且可重建的测试数据可用新 ID 向前修复。

游戏数据通过扩展依赖或 UI 数据源访问；交付时验证消费者读取、绑定和所需存档范围。
