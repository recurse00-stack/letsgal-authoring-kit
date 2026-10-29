# 项目采用 Git 时

仅在 Git 操作与恢复确实相关时读取；一般作品修改的恢复选择见[恢复与协作](collaboration-git.md)。

只检查目标仓库根、分支、暂存和工作区差异，保留 HEAD、索引及原工作。只读检查优先 `git --no-optional-locks`，避免刷新索引。不开跨作品父目录大库，不用 reset --hard、clean -fdx 或覆盖式 restore 换取干净状态。

提交按项目约定和当前授权，只纳入审阅范围。同文件部分暂存时，`git commit --only` 使用工作区内容，不等于仅提交已审阅的暂存片段；不擅自 stash／unstage 他人工作、推送或改写公共历史。JSON 冲突按结构合并，保留双方内容与 ID，不能整份选 ours／theirs 就称解决。

worktree 不自动包含未提交内容，也不备份素材；LFS、忽略和发行策略沿已有约定。安装备份可能含特调，不提交整个备份目录。恢复先把旧内容取到独立位置比较，核源版本、路径及 `git restore` 对工作区／索引的影响。

[commit](https://git-scm.com/docs/git-commit) · [restore](https://git-scm.com/docs/git-restore)
