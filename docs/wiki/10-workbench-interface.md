# 接入我的资料

工作台提供两个扩展位置：**Skill Wiki** 接插件手册，**个性化** 接个人偏好和作品约定。它们与安装器保留的 `plugins/`、`preferences/` 用户区对应；主包的通用说明继续在“主体”中。

## 日常怎样阅读

公共 `MANUAL.html` 可直接离线打开，左侧切换区域，搜索框按全文查找；`Ctrl+K` 定位搜索，清空后继续阅读，浏览器后退可回到上一章节。“完整阅读与打印”展示全部正文，打印也包含所有已接入的可阅读资料。

公共页不会自行扫描硬盘。已有插件手册准备好接入清单后，让 AI 运行下面的本地生成命令；生成的工作台会自动显示符合格式的条目。也可以在页面右上角“载入本地资料”，选择生成的 JSON，替换本次页面中的资料列表。页面内载入只保留在内存，刷新后恢复到 HTML 文件本身带有的资料。

## 给插件增加一个接入清单

在 `~/.letsgal-authoring/plugins/<插件ID>/<版本>/` 内放 `wiki.json`。以下为虚构示例，ID、版本和路径应替换为真实值：

```json
{
  "schema": 1,
  "kind": "plugin",
  "id": "example.weather",
  "version": "1.0.0",
  "revision": "guide.1",
  "title": "天气示例插件",
  "summary": "天气切换的准备、调用与核对方法。",
  "status": "available",
  "documents": [
    {"id": "guide", "title": "使用指南", "path": "docs/USER-GUIDE.md"}
  ]
}
```

ID、版本必须与目录一致。`documents` 可登记多篇 Markdown，路径相对于清单所在目录；同包已登记文档之间的链接会转为工作台内跳转。已有手册不用搬出自己的版本目录。工作台按 ID、版本和修订保留身份，不自动选择最新版本。

给资料制作者的机器可读字段定义见 [Wiki 清单 schema](../../maintenance/wiki-manifest.schema.json)。清单字段检查之外，生成器还会核对目录身份、文件位置和重复文档标识。

`status` 可为 `available` 或 `paused`。暂停时只展示名称、版本和简介，正文跳过加载与搜索。生成器只接入资料，插件的安装与启用仍在 Studio 中管理。

## 接入个人资料

在 `~/.letsgal-authoring/preferences/wiki.json` 使用同一结构，将 `kind` 设为 `personal`，例如 ID 为 `my-authoring-notes`，标题为“我的创作约定”。`documents` 中可以显式登记已有 `user.md`，也可登记同目录下单独维护的作品约定说明。真实作品规则仍以工程中的原文为准，这里是阅读入口。

生成器只读取清单明确列出的文件。不要为了展示建立第二份需要手动同步的偏好正本；已有偏好位于旧根目录时，可先保留旧位置，只接入单独的说明，或经核对后另行整理资料。

## 生成本地工作台

维护工具需要 Python 3.9+ 和 Python Markdown；普通阅读和主 Skill 安装不需要这些依赖。工具从完整包根目录运行，下面的尖括号替换为实际路径：

```text
python maintenance/build_workbench.py --user-area "<实际用户区>" --check
python maintenance/build_workbench.py --user-area "<实际用户区>" --output "<新建的个人工作台.html>" --data-output "<新建的资料.json>"
```

`--check` 只校验清单和当前可阅读文档。第二条生成一份包含主手册与本地资料的完整离线 HTML，同时生成供页面载入的 JSON。输出目录需已存在，输出文件须是新文件，且位于公共发行工程之外；工具不会覆盖原页面或改写用户区。更新资料后再生成新文件，核对后自行采用。

JSON 接口名为 `letsgal-wiki-library`、schema 为 `1`，由工具生成。前端同时暴露 `LetsGalWiki.register(data)`，供将来的本地集成复用同一校验与展示流程。数据只有资料身份和正文；不支持执行扩展脚本、样式或嵌入窗口。

## 怎样核对接入结果

1. 生成结果列出资料、正文和暂停条目数量；不符合格式时给出具体原因，原文件保留。
2. 在对应区域核对标题、ID、版本和修订，打开正文，搜索一段独有文字。
3. 从结果跳转到相关段落，再检查同包文档链接与打印。
4. 暂停条目只能看到身份，不应搜到其正文。

含私人资料的 HTML、JSON 和打印稿请按[隐私说明](../../PRIVACY.md#本地-wiki)单独保存与分享。点击外部资料链接会离开离线页面。

下一步：[插件指南](09-plugin-wiki.md) · [个人偏好](06-personal.md) · [更新与恢复](08-maintenance.md)。
