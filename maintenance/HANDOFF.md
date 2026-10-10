# 0.2.1 当前指引维护入口

发行修订20261010-reviewed-guides，版本保持0.2.1；main为当前源码，原v0.2.1标签和初版包／凭证保留，发布页使用新增的独立修订附件。版本号按发布号管理，不因本地修订增号。

当前正式版2.5.0、Beta2.6.0-beta.1，每通道只有当前完整指引＋任务专题。旧版有效知识融合到current-capabilities，历史原文在维护归档与旧Release；不将旧运行证据转换为新版本通过。未知／冲突仅阻塞相关操作，不自动升级。

共享维护源在channels/stable，显式清单见[shared-skill-files.json](shared-skill-files.json)。修改前先比较Beta现有差异，合并后再显式同步；sync_shared_skill.py默认只检查，--apply执行清单内同步。入口、工作流、当前能力、版本选择及Agent元数据独立；每份载荷自包含。build_release.py检查共享一致，不静默同步。

Beta默认推荐获准官方MCP；尚未接入提示一次，不自动注册。真实能力缺口可用获准Computer Use，权限限制不绕过；正式版保留原生／合法离线。已做好／采用／定稿内容须范围授权，受托未定稿草稿可迭代；工程改动至少一种覆盖恢复，Git可选，维护环境原有Protect约定仍执行。

本轮只做机械交付检查，不加模型或宿主测试，不声称实际提速／token收益。Skill changed，安装代码changed、安装说明changed，人类手册changed。构建使用release-files白名单，核bundle、ZIP、SHA和隐私／发行者口吻；未变代码复用有效证据。

同号修订构建到独立目录并使用独立附件名，绝不覆盖已发布资产。Windows使用完整包，其他平台手动安装，保留个人区、旧版与备份。实际发布另需当次授权，源码、标签、Release、附件、匿名下载分别记录，工坊not-applicable。详见[发行门槛](RELEASE-GATES.md)。
