# 0.2.3 当前维护入口

包修订 20261020-beta280-modular，发行号 0.2.3；协作附加包 0.1.3 在[同一发布页](https://github.com/recurse00-stack/letsgal-authoring-kit/releases/tag/v0.2.3)单独提供。Beta 目标 2.8.0-beta.1，修订随本包；Stable 目标 2.5.0，完整目录保留 20261020-beta280-mcp 修订。主包和附加包统一按发行号管理：同一未发布候选只更新内部修订，下一次对外发行才递增，不为安装保护冲突而升号。

Beta 入口、执行流程、制作能力、扩展开发、内容授权、恢复、格式与资料路由按任务重构。历史公告和测试细节留在来源／验收文档，不在日常入口叠加。当前有限实测复用[宿主记录](../HOST-VALIDATION.md)，重构核对见[验证说明](../VALIDATION.md)。

[共享白名单](shared-skill-files.json)仅保留 9 份未变通用文件，由 Stable 向 Beta 显式比较同步；其他文件独立维护。Beta-only 工作先保存完整 Stable 哈希，结束逐文件核对，不能为同步修订而改 Stable。build_release.py 保留显式包修订，并记录各通道修订，安装器以所选通道清单为准。

使用 release-files 白名单核 bundle、SHA、ZIP、隐私与发行者口吻；保留旧候选及已发布资产。自用和加载副本按绑定同步，保留个人区与 Git 状态；外部发布须当次授权。详见[发行门槛](RELEASE-GATES.md)。
