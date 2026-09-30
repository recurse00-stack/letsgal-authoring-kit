# 宿主原生证据

验证日期：2026-09-30。Windows LetsGal Studio 实际EXE FileVersion与原生界面版本均为 **2.3.0-beta.1**。以下仅是对应版本与入口的实际观察。

## callFragment五个最小用例

由官方空白工程骨架创建独立合成章节，只用旁白及调用指令，没有素材、变量、扩展或真实作品内容。

| 源结构 | 本轮实际顺序 | 验证层 |
| --- | --- | --- |
| main=[C0,call A,C2]；A=[C1] | C0 → C1 → C2 | 原生调试及OP视图 |
| main=[M_ENTER,call main,M_RETURN] | M_ENTER → M_RETURN | 原生调试及OP视图，4条OP |
| main=[X0,call A,X2]；A=[X1,call main,X3] | X0 → X1 → X3 → X2 | 原生调试 |
| main=[S0,call A,S2]；A=[A_ENTER,call A,A_RETURN] | S0 → A_ENTER → A_RETURN → S2 | 原生调试 |
| main=[T_MAIN]；A=[T_ENTER,call main,T_RETURN] | T_ENTER → T_MAIN → T_RETURN | 原生片段预览及OP视图 |

目标下拉可选择main及自身；保存／重开后目标UUID保留。非循环调用main的OP_If.trueStatment确有T_MAIN；自调用的4条OP只有两条旁白及其销毁，没有重复展开。

因此当前Beta允许非循环callFragment→main的片段预览与返回。三个循环用例的回边没有重复输出；尚未确定一般循环检测算法或最大深度。

[JSON执行模型](https://docs.avg-engine.com/reference/script-json)把callFragment目标与branch／if一起限定为非main；[调用片段手册](https://docs.avg-engine.com/manual/writing/blocks/call-fragment)允许main／自身，并声称循环最多静态展开30层。前者与非循环实测不符，30层声明也与本轮自调用OP不一致。默认制作仍使用无环普通复用片段，不能将默认约定写成引擎绝对禁止。

本证据未覆盖Stable／其他版本、无循环main调用的全局入口／独立玩家／导出、branch／if／扩展流接口、一般循环策略和深度边界。原始截图、AX及路径保留在维护者私有凭证，不公开账号或作品。

## 0.1.4选择练习与调试存读档

2026-10-01，仍为实际2.3.0-beta.1，在官方空白骨架新建的独立合成工程中：

| 用例 | 原生观察 | 限制 |
| --- | --- | --- |
| 石桥路线 | 开场 → 选择石桥 → 桥栏新划痕 → 返回路口 | 一次从main入口运行 |
| 花园路线 | 开场 → 选择花园 → 花园门旁的伞 → 返回路口 | 重新从main入口运行 |
| 禁用旁白 | 可见开始 → 可见结束；禁用标记未进入OP或播放 | 仅一个props.disabled=true旁白 |
| 快存／快读 | 石桥处快存，继续到返回台词，再快读恢复石桥处 | 同一调试会话；不证明重启／导出／扩展状态 |

禁用字段按[官方JSON参考](https://docs.avg-engine.com/reference/script-json)位于block.props.disabled。制作本用例时在加载前纠正了测试夹具字段位置；Skill与检查器没有由此推定全部指令的可达性。原始私人界面未写入公共材料，只保留合成观察摘要。
