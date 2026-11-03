# 预览、调试与构建

根据任务选择局部预览、完整调试或交付产物，并记录相应结果。

## 预览范围

临时设置先记原值，结束恢复前核工程和值，保留后来修改。先核真实入口和“继承前文／上文”：继承会快进并采用默认路线；持续 BGM、粒子、镜头或角色残留先查前置剧情。

run_from_start 覆盖顺序主片段。高级调度、前处理和片段流程使用完整调试／玩家入口；debug_control.start 后查 warnings 和实际 cursor，目标不在运行列表时可能回到开头。调度器等待选章而 seek／jump 返回 UNSUPPORTED 时，转用实际入口推进。章末按调度核后续。

## 选择与交互

从目标片段可等待位置开始，run_until 到菜单，读取 choice.menuShown 和 options[].index，再 choose 并核终点。连续预览按 position.block 的章／片段／块 ID 定位；位置改变或菜单消失则重读再有限重走。预览前核内容里的扩展、存档或外链副作用。

WINDOW_HIDDEN 时恢复目标窗口可见，锁屏则等解锁；可继续可用的 MCP 读写。输入失败记录未验交互。动画看[连续播放](performance.md#连续播放验证)，模态返回看 [UI](ui-and-data.md#状态动作与智能组件)。

## 构建与导出

build_read(view="config") 核 scheme、设置和 revision。平台、ZIP、加密、debug、Steam、Web 资源 URL、Android 选项属于方案；作品名、版本、图标、Android 包名和运营统计跨方案共享。当前 MCP 修改当前方案，创建／切换方案使用获准原生界面。临时 debug 设置按[确认流程](mcp-workflow.md#宿主确认)执行并恢复，正式产物使用对应正式设置。

**2.9 桌面系统**：先读 supportedSystems，再用 set_desktop_systems 携带 revision 选择。Windows 2.9.0-beta.1 样本仅列 win32-x64，darwin 被拒绝且未写入；以当前返回安排目标。导出验包和目标平台运行分别验证。

剧本导出按章节、指令和语言核实际正文及跳过项；文本、CSV、JSON、Ren’Py、Markdown、Word 各使用对应消费格式。导出 JSON 回写前转换为章节格式；Ren’Py 按支持的指令范围验收。章节迁移和游戏构建各用专用流程。

实际构建前审阅 build_start(dryRun=true) 的路径、覆盖和外部动作；当前宿主计划提示登录时会后台注册游戏统计，先处理相关授权。记录 batchId，完成后查 batch.status、日志及真实 artifacts；输出可包含共用 dist/assets，一并保护。

取消自己的 batchId 后等到 cancelled；已结束返回 NOT_FOUND 时按实际终态处理。运行中配置写入 BUSY 则等待结束，再核当前 revision 恢复本轮设置。取消目录单独标记。

缺资源按引用恢复素材，平台依赖查[构建手册](https://docs.avg-engine.com/manual/overview/build)。宿主运行时修复需要重新构建游戏，再验相关行为。Steam、[运营统计](https://docs.avg-engine.com/manual/overview/game-stats)及密钥仅在任务范围内配置。
