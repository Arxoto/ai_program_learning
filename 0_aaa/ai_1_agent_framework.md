# AI Agent 框架 —— 2026 年技术全景与面试准备

> 结合 2025-2026 年招聘 JD 要求 + 社区最新动态整理，聚焦 Agent 框架选型、核心机制与面试高频考点。
> 整理日期：2026-05-25

---

## 一、Agent 框架全景图（2026）

```
                        Agent 框架生态

  ┌───────────────────────────────────────────────────────────┐
  │                    编排层 (Orchestration)                  │
  │  LangGraph ★★★★★  │  LlamaIndex Workflows  │  CrewAI  │
  │     AutoGen/AG2       │  Google ADK            │  Dify    │
  ├───────────────────────────────────────────────────────────┤
  │                    通信层 (Communication)                  │
  │  A2A Protocol (Agent↔Agent)  │  MCP Protocol (Agent↔Tool) │
  ├───────────────────────────────────────────────────────────┤
  │                    可观测性 (Observability)                │
  │  LangSmith  │  Arize Phoenix  │ LangFuse  │ OpenTelemetry │
  ├───────────────────────────────────────────────────────────┤
  │                    评估层 (Evaluation)                     │
  │   agentevals  │  DeepEval  │ Ragas  │  LLM-as-Judge       │
  └───────────────────────────────────────────────────────────┘
```

---

## 二、核心框架深度解析（对应 JD 2.1）

### 2.1 LangChain / LangGraph —— 面试"必考"框架

**JD 热度：80%+ | GitHub Stars：119K**

#### 2026 年关键版本里程碑

| 版本 | 时间 | 核心变化 |
|------|------|----------|
| LangChain 1.0 | 2025.10 | 正式稳定版，API 冻结 |
| LangGraph 1.2 | 2026.05 | DeltaChannel、超时策略、优雅停机、V3 事件流 |
| Deep Agents 0.6 | 2026.05 | CodeInterpreter、异步子Agent、V3 流事件 |

#### LangGraph v1.2 面试重点

- **DeltaChannel（beta）**：每步只存增量而非全量快照，大幅降低长运行 Agent 的 checkpoint 开销。配合 `snapshot_frequency=K` 定期写完整快照
- **Per-node 超时策略**：`run_timeout`（硬限制）和 `idle_timeout`（有进展则重置），超时后触发 `NodeTimeoutError`，由重试策略接管
- **优雅停机**：`RunControl.request_drain()` 在下一个 superstep 边界暂停，保存可恢复的 checkpoint
- **V3 事件流**：以 Content Block 为核心的流，支持按通道投影订阅（`run.messages`、`run.toolCalls`、`run.subgraphs`）

#### Deep Agents v0.6 —— 长运行自主 Agent 的答案

处理长时间运行的复杂 Agent 场景，核心能力：
- **异步子 Agent**：后台非阻塞子任务，用户可同时交互
- **多模态**：PDF、音频、视频处理
- **CodeInterpreter**：沙箱化 QuickJS 运行时执行代码
- **Anthropic Prompt Caching**：优化长对话的成本和延迟

#### 面试追问：Chain vs Agent vs Graph 的区别

| 维度 | Chain | Agent | Graph（LangGraph） |
|------|-------|-------|---------------------|
| 流程 | 固定 DAG（A→B→C） | LLM 动态决策 | 开发者定义的图结构 + LLM 节点 |
| 循环 | 不支持 | LLM 自主循环 | 图中有循环边，可控 |
| 状态 | 无共享状态 | 对话历史隐含 | 显式 State 对象全图流转 |
| 适用 | 确定的 RAG pipeline | 开放式工具调用 | 复杂的多步多分支编排 |

---

### 2.2 LlamaIndex —— RAG / GraphRAG 的首选

**JD 热度：50%+ | GitHub Stars：44K**

#### 2026 年核心定位

LlamaIndex 的核心价值在 **数据层**，不是编排层。最重要的三个模块：

**PropertyGraphIndex（GraphRAG 实现）**
```
文档切片 → LLM 抽取实体/关系三元组 → Neo4j/其他图库存储
         → Embedding 附加到节点 → 向量检索定锚点
         → 图遍历扩展 1-2 跳 → 子图 + 问题 → LLM 合成答案
```

**Agent Workflows（事件驱动异步编排）**
```python
from llama_index.core.workflow import Workflow, step, Event, StartEvent, StopEvent

class RAGWorkflow(Workflow):
    @step
    async def retrieve(self, ctx, ev: StartEvent) -> RetrievalEvent:
        ...
    @step
    async def synthesize(self, ctx, ev: RetrievalEvent) -> StopEvent:
        ...
```
- Async-first，天然适配 FastAPI
- Pydantic 模型作为事件，编译时类型安全
- 默认无状态，方便水平扩展

#### LlamaIndex vs LangChain 定位对比

| 维度 | LlamaIndex | LangChain / LangGraph |
|------|-----------|----------------------|
| 核心定位 | 数据索引与检索 | Agent 编排与流程控制 |
| 状态管理 | 默认无状态 | 内置 Checkpoint（SQLite/PG/Redis） |
| Human-in-the-loop | 需手动实现 | 原生 `interrupt()` |
| RAG 代码量 | 少 30-40% | 更灵活但更冗长 |
| GraphRAG | PropertyGraphIndex 原生 | GraphCypherQAChain（Text-to-Cypher） |

**结论：生产系统最佳实践是两者组合**——LlamaIndex 构建索引和查询引擎，LangGraph 负责多 Agent 编排。

---

### 2.3 AutoGen → AG2 —— 对话驱动的多 Agent

**JD 热度：40%+（上升中）**

#### 设计哲学：对话即协作

AutoGen 将多 Agent 协作建模为**多轮对话**，Agent 之间通过自然语言交流、协商和知识共享。

- **核心理念**：群体智能涌现，动态角色切换
- **原生支持 Human-in-the-loop**：`human_input_mode` 参数，人类随时介入
- **强项**：需求模糊的探索性任务、多方案并行验证、动态协商

#### 2026 重大变化：Microsoft Agent Framework

2025 年 10 月，AutoGen 与 Semantic Kernel 融合为 **Microsoft Agent Framework**，标志着：
- 从研究项目进入**生产级**产品
- 获得 Microsoft 生态的深度支持（Azure、Copilot、Teams）
- AG2 作为社区 fork 继续维护原 AutoGen 路线

---

### 2.4 CrewAI —— 角色驱动的流水线

**JD 热度：30%+**

#### 设计哲学：模拟工业流水线

- 预定义角色（Role）+ 目标（Goal）+ 任务（Task）→ 确定性的执行流程
- Token 消耗比对话式框架低 30-33%，适合成本敏感场景

#### AutoGen vs CrewAI 选型

| 场景特征 | 推荐 |
|----------|------|
| 需求不确定、需要探索 | AutoGen |
| 流程标准化、需要确定性 | CrewAI |
| 需要人类专家介入 | AutoGen（原生 HITL） |
| 成本敏感、大批量处理 | CrewAI |
| 电商订单处理等标准管道 | CrewAI |
| 多方案并行生成 + 辩论择优 | AutoGen |

**混合架构**：CrewAI 做主流程骨架（支付→库存→物流），AutoGen 嵌入灵活决策节点（特殊配送协商）。

---

### 2.5 低代码 Agent 平台 —— JD 高频要求"至少会用一种"

**JD 热度：30%+**

| 维度 | Dify | Coze（扣子） | n8n |
|------|------|-------------|-----|
| GitHub Stars | 142K | 闭源 | 188K |
| 定位 | LLM 应用全栈平台 | 零代码 Bot 构建 | 工作流自动化中枢 |
| 部署 | Docker 自托管 | 纯云（无法私有化） | Docker 自托管 |
| RAG | ★★★★ | ★★ | ★★ |
| 集成量 | 中 | 中 | **400+** |
| 适合 | 内部 AI 工具开发 | 快速验证原型 | 系统集成+自动化 |

**2026 年最热门的企业架构：Dify + n8n 双栈**
- n8n：负责外部系统集成（手脚）——400+ 连接器，数据流入流出
- Dify：负责 LLM 应用逻辑（大脑）——RAG、Agent、Prompt IDE

---

## 三、Agent 通信协议 —— MCP + A2A（2026 年最显著的技能差异化点）

### 3.1 MCP（Model Context Protocol）

**定位**：Agent ↔ 工具/数据（纵向调用）

**2026 年关键里程碑**
- SDK 月下载量 9,700 万次，公共 MCP Server 17,468+ 个
- 2025.12 捐赠给 Linux 基金会，Anthropic + OpenAI + AWS + Google + Microsoft 共同治理
- **MCP Apps**（官方扩展）：工具可返回交互式 UI（HTML/JS/CSS），被 Claude/ChatGPT/VS Code 等采纳
- **网关模式**成共识：Uber 内部通过 MCP Gateway 暴露数千个端点
- **无状态传输（SEP-1442）**：解决水平扩展瓶颈
- Claude Code 渐进式工具发现：token 使用量降低约 85%

### 3.2 A2A（Agent-to-Agent Protocol）

**定位**：Agent ↔ Agent（横向协作）

**2026 年关键数据**
- 150+ 组织生产使用，22K+ GitHub Stars
- 5 种语言 SDK：Python / JS / Java / Go / .NET
- 三大云原生集成：Google Cloud + Azure AI Foundry + AWS Bedrock
- **Agent Cards**：`/.well-known/agent-card.json`，描述 Agent 能力、技能、认证要求

### MCP vs A2A —— 互补而非竞争

```
        A2A (横向)
  Agent A ←→ Agent B ←→ Agent C
     │          │          │
     │  MCP     │  MCP     │  MCP  (纵向)
     ▼          ▼          ▼
   工具集     工具集      工具集
```

| | MCP | A2A |
|------|-----|------|
| 连接对象 | Agent ↔ 工具/数据 | Agent ↔ Agent |
| 解决的问题 | "我能用什么？" | "我能跟谁协作？" |
| 发起方 | Anthropic (2024.11) | Google (2025.04) |
| 治理 | Linux Foundation | Linux Foundation |

---

## 四、Agent 可观测性与评估 —— 2026 年从"加分项"变"必选项"

### 4.1 评估体系

**核心原则：评估基础设施比模型选择更重要**

Arize AI 2026 年报告：仅通过 RL 启发的评估循环迭代优化 system prompt，SWE-Bench Lite 提升 11%，无需改模型权重。

**评估维度**
| 维度 | 指标 |
|------|------|
| 任务成功率 | 端到端完成率 |
| 工具调用 | 选择准确率、重试率 |
| 忠实度 | 幻觉检测、引用准确性 |
| 延迟 | p50/p95 端到端延迟 |
| 成本 | Token 消耗 / 任务 |
| 安全 | Prompt 注入、PII、有害内容 |

**LLM-as-Judge 最佳实践**：人工标注 50-200 prompt → 调优 rubric → Cohen's kappa > 0.6 → 多 Judge 处理高风险决策

### 4.2 关键工具

| 工具 | 定位 |
|------|------|
| **LangSmith / Fleet** | LangChain 官方平台，15B+ traces，ABAC 权限 |
| **LangFuse** | 开源 LLM 可观测性 |
| **Arize Phoenix** | OpenTelemetry-native 可观测性 |
| **agentevals**（Solo.io） | 2026.03 发布，OTel-native，从已有 trace 离线评估 |
| **DeepEval** | 开源评估框架 |
| **Ragas** | RAG 专用评估 |

### 4.3 推荐的分阶段上线节奏

```
Week 1: OTel 追踪埋点 + 100-prompt CI 评估集 + merge 门禁
Week 2: 10% 流量线上评估 + PII/注入 guardrails + 漂移告警
Week 3+: Provider 网关路由 + Agent 回归套件 + 仿真测试
```

---

## 五、框架选型决策矩阵

### 按任务类型选

| 你的任务 | 首选框架 | 原因 |
|----------|----------|------|
| 单 Agent + 工具调用 | LangGraph | 状态管理、HITL、Streaming 最强 |
| RAG / 知识库 | LlamaIndex | 索引和检索是它的核心 |
| GraphRAG | LlamaIndex PropertyGraphIndex | 原生图+向量混合检索 |
| 标准流水线多 Agent | CrewAI | 角色驱动、流程确定、Token 省 |
| 探索性多 Agent 协商 | AutoGen | 对话驱动、动态调整 |
| 快速原型 / 非技术用户 | Dify / Coze | 可视化、低代码 |
| 系统集成自动化 | n8n | 400+ 连接器 |
| 企业级 Agent 部署 | LangSmith + LangGraph | 全套企业能力 |

### 按团队水平选

| 团队水平 | 推荐组合 |
|----------|----------|
| 非技术用户 | Coze（验证想法） |
| 初级开发者 | Dify（Docker 部署） |
| 中高级开发者 | LangGraph + LlamaIndex + Dify/n8n 辅助 |
| 企业架构师 | LangGraph（编排）+ LlamaIndex（检索）+ LangSmith（观测）+ MCP/A2A（集成） |

---

## 六、2026 年关键趋势总结

1. **LangGraph 成为编排层事实标准**——所有 Agent 模式（ReAct、Plan-Execute、Multi-Agent）收敛到统一图引擎
2. **MCP + A2A 构成开放协议层**——Agent 互操作性的基础设施，Linux 基金会治理
3. **评估从"最好有"变"必须有"**——无评估体系 = 无生产可靠性，面试中越来越看重
4. **流式架构从 token 流到事件流**——Content Block 协议、按通道订阅、断线重连语义
5. **低代码 + 专业框架双轨并行**——Dify/n8n 做快速验证和集成，LangGraph/LlamaIndex 做深度定制
6. **AI Coding 工具深度使用成准入门槛**——Cursor、Claude Code、Copilot 的深度使用经验被几乎所有 JD 要求
7. **仅会 API 调用的"提示词工程师"被淘汰**——能端到端设计、部署、评估 Agent 系统的架构师才是市场需要的

---

## 七、面试复习优先级建议

```
P0（必会，JD 提及 > 70%）：
  LangGraph Agent 手写 + Function Calling 完整链路 + RAG 管道 + Prompt Engineering

P1（高频，JD 提及 40-70%）：
  Multi-Agent（至少一种框架实战） + MCP 协议 + Memory 管理 + Agent 评估

P2（差异化，JD 提及 20-40%）：
  A2A 协议 + Agent 可观测性 + LlamaIndex GraphRAG + 低代码平台

P3（高级岗位加分）：
  模型微调（SFT/LoRA/DPO） + 分布式 Agent 架构 + Token 成本优化
```

---

## 参考链接

- [LangGraph v1.2 Changelog](https://docs.langchain.com/oss/python/releases/changelog)
- [LangChain March 2026 Newsletter](https://www.langchain.com/blog/march-2026-langchain-newsletter)
- [From Token Streams to Agent Streams](https://www.langchain.com/blog/token-streams-to-agent-streams)
- [A2A Protocol One Year Anniversary](https://opensource.googleblog.com/2026/04/a-year-of-open-collaboration-celebrating-the-anniversary-of-a2a.html)
- [MCP Roadmap](https://modelcontextprotocol.io/development/roadmap)
- [MCP Dev Summit 2026 (InfoQ)](https://www.infoq.com/news/2026/04/aaif-mcp-summit/)
- [Best AI Agent Frameworks for 2026 (Airbyte)](https://airbyte.com/agentic-data/best-ai-agent-frameworks)
- [Open-Source Stack for Reliable AI Agents in 2026](https://futureagi.com/blog/open-source-stack-for-building-reliable-ai-agents)
- [Dify vs Coze vs n8n 2026 深度对比](https://news.qiniu.com/archives/1779099154106)
- [A2A Protocol 2026 (Programming Helper)](https://www.programming-helper.com/tech/agent-to-agent-protocol-2026-google-a2a-standard)
