# 社区版维护入口

源码版本 0.1.3，MIT，风险文本保持 2026-09-26.3。仅 GitHub／社区分发，工坊 not-applicable；文件版本不等于已发布。旧版本包与凭证保留原字节。

release-files.json 是公开源码和核心 ZIP 的白名单。更新 bundle 版本与 Skill 元数据，运行 maintenance/build_release.py 刷新指纹和 SHA256SUMS；新包用 --zip --archive <固定版本材料中的新路径>，拒绝覆盖。stage_publication.py 输出到全新目录。

本轮完整修订范围、官方冲突及当前验证见 ../AUDIT.md 和 ../VALIDATION.md。安装器控制逻辑保持，但每个新 payload 仍做真实旧包升级及用户资料保留测试。JSON 检查器仍是有限静态工具，fragments 不等于完整 schema。

公共规则、个人偏好、插件知识与真实作品分开，不将绝对本机路径、内部任务、日志、账号、备份或 Git 保护库公开。保全原 HEAD／索引／未提交内容。源码、tag、Release、附件、匿名下载分别核验；每次外部发布按当次具体授权。
