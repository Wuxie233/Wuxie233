<p align="center">
  <picture>
    <source media="(max-width: 600px)" srcset="./assets/cover-mobile.svg" />
    <img src="./assets/cover.svg" alt="Wuxie, independent product developer and AI-native full-stack builder." width="100%" />
  </picture>
</p>

我做能直接使用的产品，也喜欢把复杂系统整理成顺手的工具。从产品定义、交互和系统设计，到前后端实现、部署与验证，我会完整负责一条产品线。

Agents 已经进入我的日常开发流程；需求取舍、架构决策、集成质量和最终结果仍由我负责。

`Product` · `Full-stack` · `AI agents` · `Developer tools` · `Interaction design`

<p>
  <a href="https://wuxie233.com">Website</a> ·
  <a href="https://space.bilibili.com/254160530">Bilibili</a> ·
  <a href="mailto:445714414@qq.com">Email</a>
</p>

<picture>
  <source media="(max-width: 600px)" srcset="./assets/github-stats-mobile.svg" />
  <img src="./assets/github-stats.svg" alt="GitHub contributions over the latest rolling year" width="100%" />
</picture>

## Products

### [Pulse](https://pulse.wuxie233.com) · 交易前，看清钱包风险

<img src="./assets/pulse.png" alt="Pulse wallet health analysis product interface" width="100%" />

面向 Mantle 的钱包健康分析与交易前风险工具。确定性模型先计算集中度、流动性、协议依赖等五类风险，AI 再解释结果；提交交易前还会解码 calldata，给出安全、谨慎或危险判断。报告哈希可由具备 ERC-8004 身份的 Agent 发布到链上复核。

**我负责：** 产品定义、风险模型、合约、前后端、交互、部署。<br />
**可验证：** [线上 App](https://pulse.wuxie233.com) · [公开仓库](https://github.com/Wuxie233/pulse)

`TypeScript` `Onchain` `Risk model` `AI explanation`

---

### [CodeCarry](https://github.com/Wuxie233/codecarry) · 把本地 Coding Agent 带到手机上

<p align="center">
  <picture>
    <source media="(max-width: 600px)" srcset="./assets/oc-chat.jpg" />
    <img src="./assets/oc-showcase.jpg" alt="CodeCarry server, coding agent conversation, and settings screens" width="100%" />
  </picture>
</p>

从 [`crim50n/oc-remote`](https://github.com/crim50n/oc-remote) 出发后独立维护的 Android 客户端，用手机连接远端 OpenCode、Codex app-server、Pi Roundtable 和 Pi Stack。我补上了 Codex 协议接入、移动端 Terminal / PTY、多服务器、15 种语言、离线草稿，以及大型会话在内存和历史上的稳定性。

**我负责：** 上述功能的设计、实现、移动端体验和问题修复。<br />
**可验证：** [独立仓库](https://github.com/Wuxie233/codecarry)

`Kotlin` `Android` `Codex app-server` `PTY`

---

### [BDXSuperTool](https://bdx.wuxie233.com/) · 命令链格式转换工具

<picture>
  <source media="(max-width: 600px)" srcset="./assets/bdx-overview-mobile.svg" />
  <img src="./assets/bdx-overview.svg" alt="BDXSuperTool verified feature overview, not a product screenshot" width="100%" />
</picture>

把 Minecraft 基岩版命令链的转换和维护集中到一个 Web 工具里。支持 `MCFunction → BDX`、`BDX → MCFunction / JSON`、`文本 → BDX`，并提供增量更新、命令链属性配置和深浅主题。

**个人独立开发，源码私有。**<br />
**可验证：** [线上产品](https://bdx.wuxie233.com/)

`FastAPI` `React` `Minecraft Bedrock` `Format conversion`

---

### [FlyBuild](https://build.flyshop.chat/) · 跨格式建筑工作台

<picture>
  <source media="(max-width: 600px)" srcset="./assets/flybuild-overview-mobile.svg" />
  <img src="./assets/flybuild-overview.svg" alt="FlyBuild verified feature overview, not a product screenshot" width="100%" />
</picture>

面向 Minecraft 基岩版（网易版优先）建筑团队和服主的云端工作台。自己写了 `.bdx`、`.mcstructure`、`.schem`、`.schematic`、`.litematic`、`.mcworld` 以及常见图片格式的解析与封装；任务真正进服时，还要适配网易版登录和租赁服 / 我的山头 / 联机大厅入口。上面再叠文件库、分片上传、任务调度、3D 预览、分享码和工作流。

**个人独立开发，源码私有。** 产品正在运营，社群成员近 500 人。<br />
**可验证：** [线上产品](https://build.flyshop.chat/)

`Go` `Gin` `Vue 3` `PostgreSQL` `Redis` `Bedrock / NetEase`

## Engineering Work

### [micode](https://github.com/Wuxie233/micode)

面向 OpenCode 的多 Agent 工程插件。起点是 [`vtemian/micode`](https://github.com/vtemian/micode)，后来我重做了工作流、领域边界、GitHub 生命周期和分层知识。

设计上我不把 Agent 当成更快的聊天框。需求先对齐，再规划，再实现；跨前后端时先冻结 API 契约，再并行改代码。项目知识分成三层：代码怎么写、仓库怎么组织、过去为什么这么选。后者进 SQLite，worktree 清掉以后还在。远程写 git 之前先判断仓库归属，不自动推 upstream，不用 `--force`。

### [OpenCode Ensemble](https://github.com/Wuxie233/opencode-ensemble)

从 [`hueyexe/opencode-ensemble`](https://github.com/hueyexe/opencode-ensemble) 出发后独立维护的 Agent 团队运行时。上游解决的是「把多个 Agent 同时跑起来」；我继续做的是协调协议本身：谁能写、谁只读、任务依赖怎么解锁、崩溃后工作不能丢。

并行本身不够。Writer 进独立 worktree，Reviewer 不许落盘，Lead 负责集成和终验。队友中途挂掉，应该留下分支和结构化结果，而不是在主工作区留一个洞。仪表盘按排障来做：先看到谁卡住，再点进对应会话。

### [RimWorld AI](https://github.com/Wuxie233/RimWorldMod_RimWorldAI)

RimWorld 多 Agent 殖民地管理系统。游戏 Mod 通过 MCP 暴露受控工具，独立 Runtime 负责规划与调用，WebUI 负责状态、日志和人工控制。

### [SpireVibePlaying](https://github.com/Wuxie233/SpireVibePlaying)

《Slay the Spire 2》AI 辅助 Mod。它跟踪牌堆并计算抽牌概率，用确定性 DFS 求解战斗，再让 LLM 结合上下文解释建议。

## Capability Stack

| Product | Engineering | AI systems |
|---|---|---|
| 产品定义、交互设计、风险与失败路径 | TypeScript、Go、Python、Kotlin、C#、Vue / React、Gin、FastAPI | LLM API、MCP、Function Calling、多 Agent 编排 |
| 原型验证、Web / Android 体验 | PostgreSQL、Redis、GitHub Actions、容器、部署、日志与测试 | 工具权限、上下文管理、人工接管与结果验收 |

## Elsewhere

<table>
  <tr>
    <td width="96"><a href="https://space.bilibili.com/254160530"><img src="./assets/bilibili-avatar.jpg" alt="无邪大得很 Bilibili avatar" width="72" /></a></td>
    <td><strong><a href="https://space.bilibili.com/254160530">无邪大得很</a></strong><br />在 B 站分享 Minecraft 命令、工具开发、创意和实现思路。相比完整教学，我更常讲清一个想法怎样落地。</td>
  </tr>
</table>

<p align="center"><strong>Wuxie · Build the product, then prove it works.</strong></p>
