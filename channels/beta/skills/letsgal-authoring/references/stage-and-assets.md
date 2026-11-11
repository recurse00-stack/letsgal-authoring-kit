# 舞台、角色与素材

按当前对象读取本页相应段落；时间轴见[演出段](performance.md)，工程写入见 [MCP](mcp-workflow.md)。

## 素材落点与引用

将输入放入 `.studio/mcp/inbox/`，通过 `asset_import` 导入。读取返回的实际路径、hash、登记及引用，再绑定作品对象。导入会按内容复用已有文件；角色立绘必须位于 assets/characters，复用到 assets/ui 的图片需按宿主支持的方式安排落点。

重命名先完成 `asset_manage` 并读回新路径，再提交依赖新路径的引用。force-pack 只控制打包。临时输入与导出从创建时按[清单](asset-cleanup.md#记录真实对象)记录新建／复用、实际路径、哈希与 ID。

**删除后列表仍有旧项**：核文件和引用，使用 `asset_manage` rescan 再读回登记。2.9 无引用配音样本经此刷新移除了旧行。

**GIF/WebP 删除占用**：2.9 曾在 quarantine 的 rmSync 清理处报 EPERM，关闭测试窗口后原文件仍报 WinError 32。先读回部分结果，记录路径、哈希、引用和副本；等相关工作能保存退出，再核占用并[逐项清理](asset-cleanup.md#保存关闭后逐项处理)。完整退出后的清理效果以现场结果为准。

## 选择实际使用的演出对象

| 对象 | 制作要点 |
| --- | --- |
| 角色与模型 | 核表情、皮肤／姿势／部位、层序、逐句覆盖及静态回退。差分共享部位、同句换皮肤后核其他姿势和表情。Spine 核骨骼／Atlas／纹理／运行时；Live2D 核 model3 依赖和 Core 授权。按实际采用的模型验眨眼、姿态及表情切换 |
| 立绘动作 | 先读 positions 与角色 layout／profiles，按独立布局优先级取参数。入场 showCharacter，在场更新 updateCharacter，退场 removeCharacter；平滑位移用 placementTransition。单句覆盖用块级 motionPreset，保留角色默认 |
| 动作参数 | motionDuration／placementTransitionDuration 用数字；camera.duration 用毫秒字符串。新演出使用当前动作与 camera，已有 animateSprite／stageAnimation 按迁移范围保留或转换 |
| 序列／网格 | 序列引用独立表情，排除自身引用；网格读回层、关键帧和循环，再看连续画面 |
| 对白头像 | 启用角色头像、在对话框布局加入头像组件；`portrait_bake(kind="dialogue_portrait")` 的目标来源选 static。取得新缓存及 cacheReady 后核对白显示 |
| 场景 | 根据构图选择多层合成或独立场景，核尺寸、层序、位置及剧情引用 |
| 镜头 | 明确 targets、位移、缩放、持续时间；省略参数保留原值。按 cameraBound／深度决定对象跟随，角色另核缩放。需要复位时 resetCamera，再读回复位值 |
| 粒子 | 先提供存在的 textureUri，再预检及播放；2.8／2.9 样本仅给预设会报 compile-particle-texture 并跳过。show／hide 配同一 effectId，空 hide ID 清全部粒子 |
| 视频 | uri 相对 assets，videoId 配对播放与 stopVideo；空停止 ID 清全部视频。按需要选择 normal／mixed、静音、循环、等待和层级；循环视频显式停止 |
| 浮字 | 为地点牌等分配独立 ID，分别设置等待、停留和历史收录。无限停留时允许剧情推进，用同 ID 隐藏；空 ID 按全体范围核对 |
| 行内动作 | 按 schema 选择网页、UI 或扩展动作，保留内联格式和真实目标 ID。验点击、穿透及剧情推进；对话框样式按全局／角色／逐句范围修改 |
| 声音 | 区分单轨、分类、全局和试听音量。暂停后 resume 延续；停止后需重新播放。stopSound 按类型与 soundId 定位，空 ID 控制该类型默认轨道；淡出到时再核音量和停止状态，并试听 |

## 头像批量与预制包

2.9 可将当前头像设置应用到角色全部普通立绘；先核覆盖范围，应用后按表情读回。裁剪清空按当前 schema，返回 cleared 后核实际字段；需要恢复时限定角色数据。

多皮肤预制包可选择携带皮肤，默认形态必带。预计大小考虑素材复用；导出后核包内皮肤与依赖。2.9 界面提示上限 128MB，大包交付按实际大小验证。

## 2.9 演出状态、口型与镜头

`character_edit.set_performance` 配置项目／角色效果；剧情使用 `portraitStyleRule(performanceStateVersion=1)` 启用所需状态：stateMotion／stateSpeaking／stateBreath／stateCrossfade，以及 stateCamera=spatial|real。set 读取项目配置，custom 使用本块覆盖；核角色局部设置与继承。

真实摄像机按对象远近、视野、运动和光圈构图；景深与镜头呼吸核启用条件及连续变化。粒子 optionsJson 可含 camera_follow／camera_interleave；当前 stage_edit.patch_particle_options.set 未暴露这两个键，按实际块 schema 局部更新原 JSON，保留其他选项。scene 插层使用自身层级规则。视频分别设置 layer、mixed、cameraBound、fadeInDuration，并配停止 ID。

口型先核 Live2D、Spine 或差分的实际映射，再配置文字／配音驱动。当前 character_edit 无专用口型设置操作，需要调整时使用获准原生界面。核发言人切换和停止复位；普通图片使用适配的口型方案。

按作品实际使用的对象观察开始、变化和结束，先找有明确来源的现有素材，缺项再生成或导入。LUT、幕布、CG、网格及 UI 子模板动画按需查对应 schema。

[角色](https://docs.avg-engine.com/manual/creating/characters/) · [场景](https://docs.avg-engine.com/manual/creating/scenes/) · [动态图像](https://docs.avg-engine.com/manual/creating/dynamic-visuals) · [浮字](https://docs.avg-engine.com/manual/writing/blocks/floating-text)
