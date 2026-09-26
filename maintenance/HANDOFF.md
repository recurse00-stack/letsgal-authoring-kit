# 当前维护入口

源码版本 0.1.0，MIT，风险文本 2026-09-26.3。发布状态以对应 GitHub Release 与工坊真实回执为准，不从版本字段推断已上线；旧 preview.7 保留。

只维护独立公共包，不读取或同步私人 Skill。个人偏好、用户插件资料与作品必须原样保留；同类 Skill 停用由用户决定，安装器不修改其他技能或 Agent 全局配置。

Stable 2.0.0／Beta 2.2.0-beta.1 的共同接口通过真实严格类型检查、错误用法检查和构建。官方总入口缺文件仍存在，本指引以仅重导出所用官方类型的入口避开无关模块，运行时保持宿主 SDK 外部导入；见 SDK-BLOCKER.md。

不方便的运行实测本轮暂缓：三款完整模型任务、原生安装操作、双宿主剧情／存读档／导出。公开仅标理论兼容或已完成的验证层级。独立 AI 两轮已经完成，不再自动开启额外轮次。

maintenance/build_release.py 刷新 BOM、清单和校验值。release-files.json 控制核心分发；workshop-source-files.json 控制独立工坊源码。先生成核心 ZIP，再以 build_workshop.py 构建工坊包，最后 stage_publication.py 准备公开源码。所有输出用全新目录，保留失败记录、旧包和备份；不得随意递归清理带 junction 的测试区。

发行检查、暂缓项和后续流程见 RELEASE-GATES.md；验证范围见 VALIDATION.md。源代码、构建产物、GitHub 发布、工坊提交及审核结果分别记录。
