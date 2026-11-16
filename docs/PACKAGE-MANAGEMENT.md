# 包管理接入协议

本接口把已安装的 Skill、插件指南和配套手册接入总 Wiki。包的安装由使用者决定；登记只验证和引用已有文件，管理操作保存启停、选版和手册展示，不执行包内脚本。

## 两种兼容入口

已有 `addon.json` 的[新式附属包](ADDON-WIKI.md)继续使用原安装器、版本目录和 `addons/<id>/state.json`。原命令与字段保持兼容，可增加布尔字段 `show_when_paused`，省略时为 false。

已有插件指南或旧附属包使用包外登记：`workbench/packages/<类型>/<id>/state.json` 保存状态，同级各版本的 `wiki-library.json` 保存经声明的阅读内容。原载荷保留在 `plugins/<id>/<版本>` 或 `addons/<id>/<版本>`。同一包只使用一种状态来源。

## 提供登记清单

清单 schema 为 1，kind 为 `letsgal-package-registration`。完整字段见 [schema](../maintenance/package-registration.schema.json) 和[合成模板](../templates/package-registration.example.json)。

| 字段 | 含义 |
| --- | --- |
| package_type / id | `addon` 或 `plugin-guide`；后者 ID 使用实际插件 ID |
| enabled | 首次登记的明确启用选择；已有登记保留原状态 |
| show_when_paused | 暂停时保留手册，默认 false；不启用 AI 指导 |
| selection_mode / selected_version | `fixed` 与具体已装版本；插件指南可用 `auto` 与 null |
| versions | 版本到资料声明的映射；重复登记保留当前选择和其他版本 |
| root / entry | 用户区相对版本目录；入口为 `SKILL.md` |
| revision / title / summary / section | 资料修订、标题、简介；分区为 `skills`、`references` 或 `personal` |
| files | 原载荷相对路径到 SHA-256 的映射，包含 Skill 及其必要资料 |
| wiki_library | 预编译的 `letsgal-wiki-library` schema 1，包含对应版本的一个完整条目 |

Wiki 条目沿现有字段约定，含文档 ID、标题及 HTML。条目 uid 是 `[section,id,version,revision]` 经 `json.dumps(..., ensure_ascii=False)` 编码后的 SHA-256 前16位，加 `ext-` 前缀。可复用维护工具 `build_workbench.read_item` 从显式 Wiki 清单生成；该构建步骤需要 Python Markdown，生成后安装和管理只需 Python 3.10+ 标准库。

原载荷 `files` 的每项都要在指定目录内并通过校验。正文中的脚本、嵌入窗口和外部资源不会执行；新包无需为总 Wiki 提供自己的 JavaScript 或 CSS。没有人类手册时可以明确登记 Skill 资料，不用其他版本手册替代。

## 为指南提供导览

原 Markdown 清单以及预编译 Wiki item 均可增加 `navigation`，原 schema 版本保持兼容。字段见 [Wiki schema](../maintenance/wiki-manifest.schema.json)，[合成登记示例](../templates/package-registration.example.json)包含完整位置。

```json
{
  "navigation": {
    "intro": "从安装和最小示例开始，按任务查阅详细用法。",
    "start": "guide",
    "groups": [
      {"title": "开始使用", "summary": "安装与最小案例。", "documents": ["guide"]},
      {"title": "查阅", "documents": ["reference"]}
    ]
  }
}
```

`start` 和分组中的值均引用当前版本已有文档 ID。分组按声明顺序展示；同一文档只放入一个分组，未分组文档进入“其他资料”。不提供导览时按原文档顺序生成完整目录。声明只包含文字和文档引用，不执行自定义页面代码。

已安装的旧包可在包外登记的 `wiki_library` 中补充导览，再按同版修订流程注册；原载荷文件不变。读者切换阅读版本只改变网址和当前页面，包管理继续保存唯一的 AI 使用状态。

聚合的 schema 2 item 同时提供只读 `selection_mode`、`selected_version`，供工作台确定默认阅读版本；旧 item 缺少这些字段时，单版本直接进入，多版本展示选择。主 Skill 使用随主包的内置导览，与其他空间共用阅读界面。

## 注册与自动合并

安装器先放置并核对自己的文件，再调用当前用户区的工作台工具：

```text
python workbench/workbench_packages.py register --user-area . --manifest registration.json
python workbench/workbench_packages.py register --user-area . --manifest registration.json --apply
```

第一条预览，第二条登记并自动汇总 Wiki。重复同内容登记返回 verified-unchanged；相同版本内容不同默认停止。已审阅的同版资料修订可加 `--replace`，工具备份旧登记及 Wiki 再替换，原载荷仍由其安装工具维护。安装另一版本或更正修订均保留原选版、暂停和展示设置。初次迁移旧包时先明确其原选择，登记清单据此填写。

尚无主工作台时可保留登记，返回的 Wiki 状态为 pending；随后安装主包即自动汇总。旧安装器只认识原登记时，可能生成仅含其认识资料的阅读快照；再次打开新版管理入口会按完整登记重建，不改变各包的选择。

## 管理接口

注册同时在对应的 addons/INDEX.md 或 plugins/INDEX.md 写入本包的导航块，指向唯一状态文件；其他条目和原文保留。之后的启停无需同步多份文字状态。

`workbench_packages.py list --user-area .` 返回已登记包及状态文件指纹。`resolve --key <类型/ID> --actual-version <版本>` 只解析 AI 可使用的入口，不读取正文；插件指南按实际版本解析。没有适配登记的旧包继续沿原索引处理。

原 `workbench_runtime.py state` 增加 `--package-type addon|plugin-guide` 和 `--show-when-paused yes|no`。选版不会隐式启用。自动匹配可在页面选择“自动匹配工程”。

本机页面通过仅回环监听的管理服务调用列举、读取和状态保存接口。保存必须携带原状态指纹；冲突返回409，失败返回明确原因。状态和总 Wiki 同一事务写入，改前备份、失败恢复。浏览器显示“已保存”后才采用新状态。

## 阅读数据与责任范围

新版 `letsgal-wiki-library` schema 2 增加 `enabled` 和 `wiki_visible`，分别表示 AI 使用和手册可见性。`selected` 仅表示已启用的固定选版；自动匹配需结合具体工程确定。旧 schema 1 仍可载入：paused 默认隐藏正文。手动载入 JSON 仅用于阅读，不会注册或启用其中的包。

包管理负责资料登记，不管理 Studio 插件安装、房间权限或远端 Agent。主 Skill 的安装／卸载沿现有安装器；主包内置个人包由独立的用户资料状态管理；其他未登记的个人资料沿原入口。含私有内容的登记、阅读快照和备份只保存在本机。

## 接入验收

核对首次／重复登记、版本并存、暂停保留、暂停但显示手册、恢复启用、固定与自动选版、错误清单保留原状态。最后从 Wiki 打开手册、搜索独有文字、核跨页链接和打印，并确认 AI 解析结果与启用选择一致。

## 内置个人包与编辑接口

`personal/letsgal-personal` 是内置用户资料类型，状态位于 `preferences/package-state.json`。它不通过外部 register 登记，也不使用不可变版本载荷校验；包管理只接受 enabled 与 show_when_paused。catalog 返回 package_type=personal、selection_mode=personal、selected_version=null、versions=[]。原 addon／plugin-guide 接入字段保持。

`resolve` 返回 ready／paused；旧安装无个人状态时返回 legacy 和原偏好入口。个人包的权重由主 Skill 按资料来源处理，外部包清单不能自行声明更高优先级。

本机服务提供 `GET /api/personal/<文档ID>` 和 `POST /api/personal/save`。文档 ID 仅 requirements、memory、guide；保存提交 document、content、expected，expected 为读取所得指纹。冲突返回 409 并保留原文件，成功返回已读回的 document 和 write／wiki 结果。正文上限为 UTF-8 1 MB。保存沿用本机会话鉴权、备份和事务恢复。

聚合 Wiki schema 2 的 personal 文档可携带 markdown 字段，替代 html；浏览器本地解析并清洗后显示。正文不进入公共构建。个人包的文档 ID、阅读锚点保持稳定，内容修改不生成发行版本。
