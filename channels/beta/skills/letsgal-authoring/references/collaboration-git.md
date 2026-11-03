# 恢复、Git 与协作入口

## 选择覆盖本次改动的保护

工程落盘前保有可用恢复点：原生历史／检查点、支持该操作的撤销、Git 或核验过的备份。优先已有能力，按一个可审查批次保全原文，复用有效快照。

MCP 可用 history_checkpoint，支持的操作保存 opId，定稿记恢复标识。核剧情与素材覆盖，图片、音频、独立源码及未收录文件补相应备份。Skill／插件发行遵循所属工程保护流程。

恢复前保全最新编辑并审阅影响，优先小范围。[时光机](https://docs.avg-engine.com/manual/overview/backup)整工程恢复可能移除备份后新增文件。保护不足先补保护，或交付草稿。[项目历史](https://docs.avg-engine.com/manual/overview/history)

## 限定恢复与读回

history_undo 先 dry run 核 opId 和对象。UNDO_CONFLICT 时重读，只向前修复获准差异。按 undone 对应原操作，读回原对象、ID、字段及引用。

**调度恢复**核 mode、strategy、graph 和入口数量。2.9 样本只恢复了数量：同类情况用保存的原流程及当前 revision 限定修复，并完成高影响确认。

**撤销／删除 INTERNAL、EPERM、EBUSY**先核部分完成结果与历史，剩余文件进入[精确清单](asset-cleanup.md#撤销删除失败与文件占用)，后续只处理剩余项。

**文件历史恢复**审阅 filesToWrite／filesToDelete，限定目标文件；快照中不存在的临时配置按计划删除。恢复后读实际生效值并保留后来编辑。数据行处理见[数据表](ui-and-data.md#数据表的编辑与运行)。

## 多人协作

进入获准房间后，按[附加包启停](customization.md#附加包的启用与暂停)核状态；已启用且适配当前宿主才加载 letsgal-collaboration。附加包管理本人范围、共享影响、成员占用及同步；通用演出／UI／调试由主包维护。

附加包未启用时仍核本人和获准章节，重读后局部编辑、保留他人修改。CHAPTER_LOCKED 依据 details.reason 处理行占用、对齐或操作限制；确认同步时读取远端结果。

资格看当前账号和官方入口。创建云空间、上传作品及启动额外代理按各自明确授权执行。

## 项目选择 Git 时

项目采用 Git 且本次需要操作时，读[Git 工作流](git-workflow.md)。

## 交接

更新工程已有简短状态：目标、已采用决定、修改范围、验证、未决项、恢复标识及仍运行进程。完整过程归历史记录。
