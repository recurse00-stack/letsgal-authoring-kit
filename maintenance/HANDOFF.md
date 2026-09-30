# 社区版维护交接

源码版本 0.1.2，MIT，风险文本保持 2026-09-26.3。仅通过社区和 GitHub Releases 分发；版本字段不等于已发布。旧发行包保留原字节。

release-files.json 是核心 ZIP 与 GitHub 源码的唯一白名单。修改后运行 maintenance/build_release.py 刷新 bundle.json 和 SHA256SUMS.txt；加 --zip --archive <固定版本区内的全新 ZIP 路径> 创建新版本归档（包内根目录始终为 bundle.owner，不随 source 目录名变化），再用 maintenance/stage_publication.py --output <全新目录> 准备公开源码。所有输出使用新路径。

公共规则、个人偏好、版本化插件知识独立维护。不要把本机目录、安装日志、真实作品、账号、历史备份或私人资料加入公开文件。维护源码不等于自动安装，文件部署不等于模型或引擎验收。

检查与未验证范围见 RELEASE-GATES.md 和 ../VALIDATION.md。保全既有 Git HEAD、索引和未提交内容；公开提交、Release 与下载读回分别记录。
