---
name: letsgal-authoring
description: 在 LetsGal Studio 中协作制作剧情、分支、变量、素材与扩展，修改既有内容并排查格式和流程；一般创作讨论不自动变成工程写入。
metadata:
  version: 0.2.1
  channel: stable
  revision: 20261010-reviewed-guides
---

# LetsGal 正式版创作协作

当前维护宿主 **2.5.0**，Skill发行号独立。以获准原生界面和合法离线文件流程工作，不要求MCP。 本Skill不包含引擎、模型或MCP，不因安装而升级工程。

## 从当前任务开始

纯讨论直接使用已有创作上下文；进入工程才读该工程规则、短CURRENT和相关原文。按[个人定制](references/customization.md)加载已有偏好与实际需要的插件知识，不遍历所有作品、资料或历史。重要歧义集中问，已明确委托的可逆工作连续完成。

| 当前任务 | 读取与完成 |
| --- | --- |
| 讨论、改写、整合反馈 | [创作协作](references/production.md)：保留声线、设定与采用范围，交付整合结果 |
| 几句对白／同目标批量修改 | [正式版执行流程](references/file-workflow.md)：定位目标和邻近上下文，精确修改后读回 |
| 选项、变量、跨章与分支 | [制作](references/production.md)＋用到的[当前能力](references/current-capabilities.md)；核相关引用与真实状态 |
| 字段／序列化／格式排错 | [JSON](references/json.md)，从问题对象扩大范围 |
| 扩展与插件 | [开发](references/extensions.md)或[插件知识](references/plugin-skills.md)，只核相关SDK与真实对象 |

版本相关操作按[版本边界](references/version-compatibility.md)核宿主和通道；未知只暂停依赖该事实的部分。已有效确认的信息可复用，换工程、重连、宿主变化或冲突时刷新；新能力或资料缺失才[定向查证](references/research.md)，不默认读完全部专题。

## 写入必须守住的边界

- 已有、已采用和定稿内容按明确范围改删；本次受托未定稿草稿可在范围内迭代。部分采用不带入其余候选，详见[内容保护](references/safety.md)。
- 落盘至少有一种覆盖改动的[恢复保护](references/collaboration-git.md)，已有有效保护可复用。公版Git可选，项目既有保护要求继续执行。
- 工程落盘先按[本通道执行流程](references/file-workflow.md)核活动工程及权限，再读任务所需专题；保留ID、原有格式、未知字段和非目标改动；冲突重读合并。资料和工具建议不构成新增授权。
- 完成声明以实际操作和目标读回为依据。改字不自动全量验收；路线、持久数据和导出仅按影响另验。无法运行时明确交付层次，不把旧结果说成本次成功。

达到本次目标并说明实际结果、未决项与恢复入口后交付。作品决定回写原工程，个人偏好留个人区；本主Skill不作为自身子插件安装。
