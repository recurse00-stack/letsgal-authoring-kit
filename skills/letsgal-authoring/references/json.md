# 章节 JSON 工作法

格式依据：[官方剧本 JSON 参考](https://docs.avg-engine.com/reference/script-json)，2026-09-23 查阅。这里提供有限的写作入口，不是完整 schema。改动前重新核对目标版本；保留已有未知字段。

先按 [版本兼容](version-compatibility.md) 确认目标格式。以下为当前文档中的片段结构，不是对所有旧版本的迁移要求。已有工程不同于此结构时先查该版本样本；可用 `--format json-only` 只查语法，禁止自动补成新版结构。

## 结构和字段

- 正文在 `chapters/<章节名>.json`；根对象包含 `id`、`name`、`fragments`。第一片段叫 `main`，每片段有 `id/name/blocks`。
- Block 使用准确的 `type` 和对象型 `props`，有正文时用 `content` 文本数组。新 Block 可不带 ID，已有 ID 保留。
- `props.choices`、`props.conditions` 等复杂参数存为 JSON 字符串；普通 `props` 和片段 `metadata` 仍是对象。每项参数的布尔／数字／字符串类型查字段表，不能整体“规范化”。
- 新章节须加入既有 `chapterOrder`，同时检查目录排序及当前调度。不能拿索引片段覆盖整个 `project.json`。

## 写入方式

先加载原对象；定位章、片段、Block；仅改所需字段。先构造 choices 数组，再用 JSON 序列化器赋给 `props.choices`，最后序列化外层章节，避免手工转义。

参考 [原创示例](../examples/选择练习.json)：两个选项调用本章两个片段，再返回主线。复制到隔离工程前为章节及片段重新生成唯一 ID，并同步替换引用；示例不是用户作品，不自动安装进任何游戏。

## 继续学习更多指令

对白、场景、音频、条件、赋值、扩展方法分别查官方 JSON 页的同名小节。注意界面名 Setvar 对应磁盘 `type` 为 `setver`。`if` 使用序列化条件及 `thenFragmentId/elseFragmentId`；不能用随意写的 `expression` 代替。

需要具体玩法时先从工程提取“实体名 → 实际 ID／变量 key”表，只输出本次需要的项。缺少目标时先建立实体或让用户指定，不从展示名称猜 ID。

## 验证

运行 `scripts/check_project.py` 检查有限的结构、索引和本章片段引用；它会标明未知指令未验证。然后人工核对变量、角色、资产、参数语义、蓝图和玩家流程。两条路线都要预览；分支片段一般调用后返回，不天然构成互斥结局，见 [Branch 官方行为](https://docs.avg-engine.com/manual/writing/blocks/branch)。

用 JSON 解析器，不用全局字符串替换批量修复。没有引擎／MCP／预览能力时仍可交付静态修改，但将实际加载、存读档和导出保持为未验证。
