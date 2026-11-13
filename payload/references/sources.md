# 来源与证据范围

方法依据 LetsGal Studio 扩展工坊的“模拟经营玩法套件”《制作人的日常》，ID `letsgal.producer-daily`，源码包版本 **0.1.1**，取得日期 2026-11-12。工坊作者显示“愤怒的泡面”，包内清单 author 为 `LetsGal Studio`，SDK 声明为 `>=2.9.0-beta.1`。

源码包 SHA-256：`EAB7128CD5EDD4890FFBBB064F362BCE1BABDB0A482333C604A49AC0AEF9229D`。下表路径、行号均相对于这份固定源码包；可在工坊相同条目的源码浏览器核对。这里不附带原源码和素材。

| 方法 | 观察依据 |
| --- | --- |
| D01 站位与留场 | `src/event-stories.ts` 128–158 |
| D02 转场种类 | `src/event-stories.ts` 161–174；`src/scene-transition.ts` 3–14；`src/town-screen.tsx` 23–57；`src/day-transition.tsx` 4–17；`ui/producer-day-turn.json` |
| D03 注意力 | `src/satellite-map.tsx` 261–300；`src/visual-views.ts` 217–235；随包地图与手册截图 |
| D04 反馈层次 | `src/visual-views.ts` 112–175、186–214、372–383；`src/game-state.ts` 149–220 |
| D05 正式与闲逛 | `src/game-state.ts` 86–132、205–220、251–263 |
| D06 随机排班 | `src/town-events.ts` 113–173；`src/index.tsx` 242–264 |
| D07 行动选项 | `src/event-stories.ts` 23–46、128–176 |
| D08 关系行动 | `data/roles.json`；`src/game-state.ts` 233–248；`src/visual-views.ts` 485–520 |
| D09 特点回顾 | `src/playtest-report.ts` 22–51；`src/visual-views.ts` 186–214 |
| D10 状态指引 | `src/visual-views.ts` 307–365、485–520 |

本包的设计方法是从实现中作出的归纳，适用条件与新例子由本包编写，不声明为官方设计准则或作者意图。

研究覆盖源码、数据、生成脚本、UI 文档和随包截图。原包纯逻辑测试 26 项通过；使用 Node.js 24.16.0 和模拟宿主，未覆盖真实 Studio／Player。模板可生成 56 段，默认事件表配置 15 条，源码包未附完整游戏章节。动态试玩未完成，因此不据此宣称节奏、音画或易用性已获玩家验证。

本包不依赖该扩展，不继承它的 SDK 版本作为本包运行要求。方法可供不同通道讨论，具体实现仍须由主 Skill 核对实际宿主。原样例素材另有使用限制，本包不含其美术、截图、完整剧本或源码；本包许可只覆盖本包自身提供的内容。
