import React, { useState } from "react";
import { riskNotice } from "./risk-notice";
import type { ExtensionProps } from "@avg-studio/sdk";

export interface AuthoringGuideProps extends ExtensionProps {}

const agents = ["Codex", "Claude Code", "Cursor", "GitHub Copilot", "DSH", "其他 Agent"] as const;
const field: React.CSSProperties = { width: "100%", boxSizing: "border-box", padding: "12px 14px", borderRadius: 9, border: "1px solid #bbc9cf", background: "#fff", color: "#183b46", font: "inherit" };
const card: React.CSSProperties = { padding: 26, borderRadius: 16, border: "1px solid #d7e1e3", background: "#fff" };

export function AuthoringGuide(_props: AuthoringGuideProps) {
  const [agent, setAgent] = useState<string>("Codex");
  const [channel, setChannel] = useState("未知");
  const [version, setVersion] = useState("");
  const [task, setTask] = useState("检查安装与读取规则");
  const prompt = `请使用 letsgal-authoring 技能。我的工具是 ${agent}，目标 LetsGal 通道是 ${channel}，完整版本为 ${version.trim() || "待核实"}。本次任务：${task}。\n先确认技能实际来源、用户主目录、个人偏好和目标工程 LETSGAL.md；版本不明时先查证，不默认 Beta。\n插件知识从独立用户区按插件 ID 和实际版本读取。新建插件 Skill 时保存到用户区的 plugins/<插件ID>/<版本>/SKILL.md，并增补索引，保留已有内容；不修改公共技能和插件代码。\n首次写工程前简短说明 AI 误改、误删和资料外发风险，核对可写范围与备份；已说明且范围不变时不重复告警。修改前保全原文，列出范围；不执行未授权删除、不重置用户特调、不升级引擎。区分静态检查与真实宿主运行，报告证据和未验证项。`;
  return <main style={{ width: "100%", height: "100%", boxSizing: "border-box", overflow: "auto", background: "#eef4f4", color: "#183b46", padding: "40px 5%", fontFamily: '"Microsoft YaHei", system-ui, sans-serif', fontSize: 20, lineHeight: 1.6 }}>
    <header style={{ display: "flex", justifyContent: "space-between", alignItems: "start", gap: 30, marginBottom: 28 }}>
      <div><div style={{ color: "#46777d", letterSpacing: 3, fontSize: 16 }}>LETSGAL AUTHORING KIT · 社区工具</div><h1 style={{ fontSize: 42, margin: "8px 0" }}>把 AI 接入你的创作流程</h1><p style={{ margin: 0 }}>导入技能、保留个人特调，再按作品版本开始协作。</p></div>
      <div style={{ borderRadius: 10, background: "#dcebe8", padding: "12px 18px", fontSize: 16 }}>独立技能包<br/>工坊指引入口 · 0.1.0</div>
    </header>
    <section aria-label="使用风险与免责声明" style={{ background: "#fff2de", border: "1px solid #c98d29", borderRadius: 12, padding: "18px 22px", marginBottom: 24 }}>
      <strong>使用前请阅读 · 数据风险与免责声明</strong>
      <p style={{ margin: "6px 0", fontSize: 18 }}>AI 可能误改、误删或泄露资料。请先备份作品并限制 Agent 可写范围；技能备份不包含作品。</p>
      <p style={{ margin: "6px 0", fontSize: 17 }}>本包按现状提供，不提供担保；作者及贡献者不对使用或无法使用本包造成的任何损失承担责任。</p>
      <details><summary style={{ cursor: "pointer", fontSize: 17 }}>展开完整说明</summary><pre style={{ whiteSpace: "pre-wrap", overflowWrap: "anywhere", font: "inherit", fontSize: 16, maxHeight: 320, overflow: "auto" }}>{riskNotice}</pre></details>
    </section>
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1.12fr", gap: 26 }}>
      <section style={card}><h2 style={{ margin: "0 0 18px", fontSize: 26 }}>三步完成导入</h2>
        <ol style={{ paddingLeft: 28, margin: 0 }}>
          <li style={{ marginBottom: 18 }}>在工坊详情选择“查看源码”，下载完整源码包并解压，找到 <code>assets/skill-kit.zip</code>，再解压到新目录。也可从 <a href="https://github.com/recurse00-stack/letsgal-authoring-kit/releases" target="_blank" rel="noopener noreferrer">GitHub 发布页</a> 下载独立 ZIP。<div style={{ fontSize: 15, overflowWrap: "anywhere" }}>https://github.com/recurse00-stack/letsgal-authoring-kit/releases</div></li>
          <li style={{ marginBottom: 18 }}>Windows 双击 <b>Install.cmd</b>，选择 Agent 和个人／工程范围，确认显示的目标路径后导入。macOS／Linux 按包内 <b>MANUAL.md</b> 手动安装。</li>
          <li>建议先停用其他同类 LetsGal／引擎创作 Skill，保留原文件与特调，避免重复调度和额外上下文开销。再在 Agent 新会话中发送右侧提示，核对实际加载的 Skill 路径。DSH 使用自定义数据目录时，在安装界面选择真实 DSH_HOME。</li>
        </ol>
        <h2 style={{ fontSize: 25, marginTop: 28 }}>你的内容留在用户区</h2>
        <p style={{ marginBottom: 8 }}>个人偏好：<code>~/.letsgal-authoring/preferences/user.md</code></p>
        <p style={{ marginTop: 0 }}>插件知识：<code>~/.letsgal-authoring/plugins/</code></p>
        <p style={{ fontSize: 17, color: "#4c6872" }}>旧版 user.md 保留。插件 Skill 由用户维护，公共技能更新不会覆盖它。遇到修改冲突，安装器停止并提示备份。</p>
      </section>
      <section style={card}><h2 style={{ margin: "0 0 18px", fontSize: 26 }}>生成一条开始协作的提示</h2>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <label>Agent<select aria-label="Agent" style={field} value={agent} onChange={e => setAgent(e.target.value)}>{agents.map(x => <option key={x}>{x}</option>)}</select></label>
          <label>作品的目标通道（选填）<select aria-label="作品的目标通道（选填）" style={field} value={channel} onChange={e => setChannel(e.target.value)}>{["未知", "稳定版", "Beta"].map(x => <option key={x}>{x}</option>)}</select></label>
          <label>完整版本<input aria-label="完整版本" style={field} value={version} maxLength={80} placeholder="尚未核实时留空" onChange={e => setVersion(e.target.value)} /></label>
          <label>要做什么<select aria-label="要做什么" style={field} value={task} onChange={e => setTask(e.target.value)}>{["检查安装与读取规则", "分析插件并创建插件 Skill", "制作一个可玩的剧情片段", "检查已有章节 JSON"].map(x => <option key={x}>{x}</option>)}</select></label>
        </div>
        <label style={{ display: "block", marginTop: 20 }}>选中下面文字并复制给 Agent<textarea aria-label="协作提示" readOnly value={prompt} onFocus={e => e.currentTarget.select()} style={{ ...field, height: 310, fontSize: 18, resize: "vertical" }} /></label>
        <p style={{ marginBottom: 0, fontSize: 17, color: "#4c6872" }}>这一步生成文本；请在有工程文件访问能力的 AI 工具中使用。模型服务和账号由你自行配置。</p>
      </section>
    </div>
    <footer style={{ paddingTop: 24, fontSize: 17, color: "#4c6872" }}>Stable 2.0.0 与 Beta 2.2.0-beta.1 已通过官方 SDK 类型检查和构建，宿主运行暂未实测。技能按当前工程确认版本，不把当前编辑器版本当作所有作品的目标版本。界面不扫描工程、不会自动联网、不执行安装，也不写入存档或个人配置。</footer>
  </main>;
}
