# 可选附属包与 Wiki 接入

本协议用于独立分发的可选 Skill 包。包的下载和安装由使用者决定；主包提供登记、按需读取和 Wiki 聚合，不附带包正文。

## 包结构与声明

包根包含 `addon.json`、`Install.py`、`workbench_runtime.py` 和 `payload/`。安装器及运行时使用本包 `maintenance/install_addon.py` 与 `maintenance/workbench_runtime.py` 的实体副本。打包时固定所采用的版本并完成隔离检查。

payload 包含根级 SKILL.md、其引用、独立人类手册和 wiki-library.json。addon.json schema 为 1，kind 为 letsgal-skill-addon；声明 id、version、revision、title、summary、entry（SKILL.md）、section（references 或 skills），以及 files（payload 相对路径到 SHA-256 的完整映射）。manual 可指定独立手册的相对路径，默认 docs/README.md，必须在 files 中。

wiki-library.json 使用 letsgal-wiki-library / schema 1，包含一个与包身份一致的 item。可使用 maintenance/build_workbench.py 的 read_item 从显式 Wiki 清单和 Markdown 生成；构建需要 Python Markdown，安装仅需 Python 3.10+ 标准库。前端按通用内容规则展示正文，过滤可执行内容。

## 安装调用

```text
python Install.py --skills-root "<Agent 的 skills 根>" --user-area "<实际用户区>"
python Install.py --skills-root "<Agent 的 skills 根>" --user-area "<实际用户区>" --install
```

第一条预览且不写入。检测到有效主 Skill 后安装到 addons/<id>/<version>，没有主 Skill 时安装到所选 skills 根成为独立技能。同名主 Skill 目录身份冲突时停止。相同载荷仅校验；不同载荷默认停止，明确 --replace 才完整备份后替换。--select 选择本次版本，--enable 恢复启用；未传时保留已有选择与暂停状态。

## 唯一状态与总入口

addons/<id>/state.json 记录 schema1、id、enabled、selected_version 及 versions；各版本记录 revision、title、summary、section、entry 和 files。INDEX.md 中本包的 addon:<id>:start / end 标记块只导航到状态文件。旧自由文本登记需要先核对，再按具体包的迁移说明转换。

主包部署用户区 workbench/MANUAL.html。附属包安装、启停和切版会自动刷新该总入口；尚未部署主工作台时保留安装并报告 pending，之后装主包自动汇总。刷新只读取明确登记的包；未登记个人资料沿原接入清单管理。

管理命令、旧清单和个人资料接入见[工作台手册](wiki/10-workbench-interface.md)。安装后的 AI 状态和人类阅读入口共用版本登记；用户或作品的明确要求仍按主 Skill 的规则处理。

## 打包前核对

检查默认预览无写入、首次与重复安装、同版不同内容的备份、新版本保留选版、暂停保留、独立模式、主包后装汇总、损坏清单停止，以及其他资料不变。包内容的适用范围与来源由各包自己说明。
