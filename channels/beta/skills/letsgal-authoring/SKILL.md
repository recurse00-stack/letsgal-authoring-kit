---
name: letsgal-authoring
description: 制作和修改 LetsGal Studio 的剧情、分支、演出、UI 与扩展，处理工程格式及运行排错；一般创作讨论不自动写入工程。
metadata:
  version: 0.2.4
  channel: beta
  revision: 20261023-guidance
---

# LetsGal Beta 创作

本载荷面向 **Studio 2.8.0-beta.1**；其他版本按[版本边界](references/version-compatibility.md)选择依据。Skill 不提供引擎、MCP 或模型，安装不升级作品。

## 从任务进入

沿用本次已明确的创作目标和授权。讨论／改稿只读相关原文；需要落到工程时，再读该工程入口、简短 CURRENT 和本次对象。按[个人定制](references/customization.md)加载已有偏好；插件知识只在用到该插件时读取。

| 要完成的工作 | 读取这里 |
| --- | --- |
| 创作讨论、改写、分支设计与反馈整合 | [制作与创作](references/production.md) |
| 通过 Studio 读取、定位和修改工程 | [MCP 执行](references/mcp-workflow.md) |
| 剧情流程、变量、本地化与配音 | [剧情与配音](references/story-and-voice.md) |
| 素材导入、角色动画、场景、镜头和音视频 | [素材与舞台](references/stage-and-assets.md) |
| 演出段时间轴、段尾和重播副作用 | [演出段](references/performance.md) |
| 页面、按钮、主题与数据绑定 | [UI 与数据](references/ui-and-data.md) |
| 预览选择、完整调试、构建和交付检查 | [预览与构建](references/preview-and-build.md) |
| 扩展方法、SDK、设置页与检查器 | [扩展开发](references/extensions.md)；专属知识见[插件 Skill](references/plugin-skills.md) |
| 保护、恢复、Git 或多人实时协作入口 | [恢复与协作](references/collaboration-git.md) |
| 序列化排错或资料不足 | [JSON](references/json.md)／[定向查证](references/research.md) |

只加载相关专题。需要浏览能力范围时用[能力索引](references/current-capabilities.md)，不把全部专题作为每次任务的前置阅读。

## 修改与验收

已有、已采用和定稿内容按[内容授权](references/safety.md)保护；本次受托未定稿草稿可在目标内迭代。重要歧义才集中澄清，明确委托内的可逆步骤连续完成。

工程修改优先已获准的官方 MCP，并有实际覆盖改动的恢复方式。复用有效上下文和恢复点；换工程、等待确认或发生冲突后刷新相关身份与 revision。写后读取真实目标，保留 ID、富文本、未知字段和非目标内容。

验收随本次影响选择：改字核原文差异，路线改动核实际入口与终点，交互核真实输入，持久数据另核存读档，游戏交付另核产物运行。定位成功、状态标志或静态检查不能代替后一层证据。

结束时说明实际变化、通过的层次、未决项和恢复入口，将采用的作品决定写回所属工程。运行问题归对应制作专题；只有成员占用、共享对象权限和同步差异进入多人协作附加包。
