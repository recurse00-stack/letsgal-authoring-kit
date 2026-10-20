# 素材与舞台

按当前角色、场景、stage 和 blocks 参考确定字段。素材定义、逐句编排和实际播放分别处理；[演出段](performance.md)另有时间轴合同。

## 导入与引用

素材导入只能从 `.studio/mcp/inbox/` 交给 `asset_import`，外部文件工具只准备该入口，不直改活动工程 assets 或 JSON。导入后核真实路径、hash、登记和引用；新资源不等于已在作品使用。导入可能按内容复用已有路径，指定 folder 不保证得到该目录下的新副本；立绘要求 assets/characters，复用到 assets/ui 的图片仍会被角色工具拒绝。不要仅凭请求的目标目录写引用。`asset_manage` 重命名后若下一步引用新路径，先完成调用并重新读取再修改；同批预检可能尚不认识新路径。新路径尚未落地时，不把依赖它的操作放进同一预检批次。`force-pack` 是打包策略，不代表运行中已被使用。

## 选择实际使用的演出对象

- **角色与模型**：区分素材登记、表情、皮肤／姿势／部位和对白头像。保留层序、逐句覆盖和静态回退；差分同名部位可能影响其他姿势，同句换皮肤仍核表情。Spine 核骨骼／Atlas／纹理／运行时，Live2D 核 model3 及依赖，Core 授权按官方流程处理，不随 Skill 分发。模型已登记不等于已显示或在动；连续帧核眨眼／姿态和表情动画切换。Spine 结果不能替代 Live2D、序列帧或网格变形验收。
- **立绘放置与动作**：先读 positions 和角色的 layout／profiles，独立布局会覆盖全局，不能假定 middle 一定是倍率 1。入场用 showCharacter；已在场的表情／位置变化用 updateCharacter，其 placementTransition 字段控制平滑移动；退场用 removeCharacter。块级 motionPreset 覆盖只作用于本次演出，避免为单句改全局或角色默认动作。数字类型按 schema：motionDuration／placementTransitionDuration 为数字，camera.duration 为毫秒字符串。别新建已弃用的 animateSprite／stageAnimation。
- **对白头像与序列动画**：序列帧引用实际独立表情，不能包含序列自身；网格预设写入后读回层、关键帧和循环，仍需连续画面验运动。`portrait_bake(kind="dialogue_portrait")` 要启用对白头像并为目标表情选择 static 来源；原立绘是图片也可能默认使用动态对白头像。烘焙返回新缓存且 cacheReady=true 证明生成，不代替对白画面验收。
- **背景与场景**：多图合成一个多层场景还是分别建场景按任务选择；核层序、尺寸、位置和剧情引用。导入文件不等于已创建或引用场景。
- **镜头**：明确 targets、位移、缩放和持续时间；未填参数表示保留原值。角色是否随镜头移动取决于 cameraBound／深度，角色不自动继承场景缩放。段末按需要 resetCamera 并读回复位值，不把静态终点图当作补间过程证据。
- **粒子**：用独立 effectId 配对 show／hide，空 hide ID 会清全部粒子。2.8.0-beta.1 实测仅给预设、textureUri 为空时出现 `compile-particle-texture` 并跳过显示；因此先确认存在的粒子贴图，填入其资源相对路径，再检查编译和画面。宿主字段说明虽称贴图常用于 custom，不能据此忽略实际警告；不为消警告改无关公共预设。
- **视频**：uri 相对 assets，videoId 是运行效果 ID，不是文件 hash；播放与 stopVideo 用同一 ID，空停止 ID 会清全部视频。区分 normal 覆盖与 mixed 叠加、静音、循环和等待；循环视频没有自然结束。至少观察两帧及停止后的画面。
- **浮字**：独立 ID、等待、停留与历史收录分别核对。地点牌可“显示 → 剧情 → 同 ID 隐藏”；无限停留要允许推进，空 ID 可能隐藏全部浮字。按 schema 取参数，不能将界面文案当 JSON 键。
- **行内链接与界面**：网页、UI、扩展方法是不同动作；保留内联格式及真实目标 ID，不能猜 link 字段。实际核点击、穿透与是否意外推进。角色专属对话框、全局样式与逐句样式各核作用范围。
- **声音与编辑模拟**：单轨、分类、全局和试听音量分别判断；暂停保留进度，停止后 resume 不重播。stopSound 的类型与 soundId 对应播放轨道，空 ID 控制该类型默认轨道，不是所有轨道。淡出期间 playing 仍可能为 true，过时长再核 playerVolume 与停止状态。loaded／playing 只能证明引擎状态，听感、音质与设备实际出声需试听。UI 变量／状态模拟、预设预览和素材库展示不代表玩家实际状态。

演出测试按内容列有限清单：静态立绘、项目实际采用的动态模型、进退场／位移、场景／镜头、粒子、音视频及演出段。每类观察开始、变化和清理；纯文字短篇通过不能概括为演出通过。缺素材先查现有合规资源，确需生成／导入时单列素材任务和引用验证；素材所在的协作房间不改变以上通用制作语义。



按任务查询 LUT、幕布、CG、网格、UI 子模板动画等具体对象；不因更新公告批量重设既有参数。参考入口：[角色](https://docs.avg-engine.com/manual/creating/characters/)、[场景](https://docs.avg-engine.com/manual/creating/scenes/)、[动态图像](https://docs.avg-engine.com/manual/creating/dynamic-visuals)、[浮字](https://docs.avg-engine.com/manual/writing/blocks/floating-text)。
