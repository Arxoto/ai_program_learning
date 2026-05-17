# AI 应用开发框架

## LangChain

LangChain 是目前最主流的大模型应用开发框架，提供了一套构建 LLM 应用的标准化组件和抽象，让开发者可以用统一的方式组合模型、工具、记忆和检索。

**核心定位**

LangChain 本身不训练模型，也不提供模型服务——它是一套"胶水框架"，将 LLM、向量数据库、工具 API、文档加载器等不同组件串联为可运行的 AI 应用 pipeline。

**LangChain 核心组件**

- **Model I/O（模型输入输出）**
  - LLM：统一的大模型调用接口，屏蔽不同 Provider 的 API 差异
  - Chat Model：支持多轮对话消息（SystemMessage、HumanMessage、AIMessage）的聊天模型抽象
  - Prompt Template：模板化 prompt 构建，支持变量插值、Few-shot 示例模板、Chat Prompt 模板等

- **Chain（链）**
  - 将多个组件串联为固定的处理流水线——上一个组件的输出是下一个的输入
  - 支持顺序链、路由链、并行链等多种链式编排方式
  - LCEL（LangChain Expression Language）：用 `|` 管道操作符声明式编写链，代码更简洁

- **Retrieval（检索）**
  - Document Loader：从 PDF、网页、数据库、Notion 等各类来源加载文档
  - Text Splitter：文档分块
  - Embedding：文本向量化
  - Vector Store：向量存储与检索
  - Retriever：统一的检索器抽象
  - 以上组件串联即为完整的 RAG 检索链

- **Agent（智能体）**
  - Agent 是一个使用 LLM 来决定行动序列的实体，动态选择工具和行动顺序（不同于 Chain 的固定流程）
  - 核心循环：LLM 根据当前状态选择工具 → 执行工具 → 观察结果 → 继续推理
  - LangChain 提供多种 Agent 类型：ReAct Agent、OpenAI Tools Agent、Structured Chat Agent 等

- **Memory（记忆）**
  - 不同粒度的对话历史管理：ConversationBufferMemory（全部保留）、ConversationSummaryMemory（摘要）、ConversationBufferWindowMemory（滑动窗口）
  - 提供统一的记忆接口，Agent 和 Chain 均可使用

- **Tools & Toolkits（工具与工具集）**
  - 将外部功能封装为 LLM 可调用的工具
  - 内置常用工具集：搜索、计算、代码解释、数据库查询等

**LangChain 核心架构**

LangChain 采用分层架构：

1. 最底层：Provider 适配层，统一不同模型厂商的 API
2. 中间层：核心抽象——Chain、Agent、Retriever 等
3. 最上层：LangServe（部署为 API）、LangSmith（调试、测试、监控）、LangGraph（状态图编排）

**LangChain Model 的作用**

LangChain Model 组件封装了与 LLM 交互的所有细节——请求构造、API 调用、响应解析、以及重试和流式处理。开发者不需要关心底层 Provider 的差异，切换模型只需修改一个参数。

## LangGraph

LangGraph 是 LangChain 生态中的状态图编排框架，用有向图（Graph）来定义 Agent 的执行流程。

**LangGraph 编排原理**

- 将 AI 应用的执行流程建模为节点（Node）和边（Edge）组成的有向图
- 节点：执行单元，可以是 LLM 调用、工具执行、条件判断或任意自定义逻辑
- 边：定义了节点间的流转关系——普通边（固定流转）、条件边（根据结果路由到不同节点）
- 状态（State）：在整个图执行过程中流转的共享数据结构，每个节点可以读取和修改状态
- 图中可以包含循环边，实现 ReAct 等需要反复执行的流程，这是 Chain 做不到的

**LangChain 与 LangGraph 的区别**

| 维度 | LangChain | LangGraph |
|------|-----------|-----------|
| 流程模型 | 固定链式流程（A→B→C） | 灵活的图结构（支持循环和条件分支） |
| 适用场景 | 简单线性流程 | 复杂多步 Agent、条件分支多的流程 |
| 循环 | 不支持原生循环 | 支持，核心能力 |
| 状态管理 | 各链独立 | 统一状态对象在图节点间流转 |
| 学习曲线 | 低，直觉化 | 中，需要理解图编程概念 |

关系：LangGraph 是 LangChain 的补充，用于解决 Chain 无法处理的循环和复杂分支场景。两者共享 LangChain 的 LLM、Tool、Retrieval 等底层组件。

## LlamaIndex

LlamaIndex 是专注于数据索引和检索的框架，在 RAG 场景下与 LangChain 形成互补。

**核心概念**

- 数据连接器：从各类数据源加载数据
- 索引：将数据组织为不同的检索结构（向量索引、树索引、关键词索引、知识图谱索引等）
- 查询引擎：统一的查询接口，支持语义搜索、结构化查询、多步推理查询

**LlamaIndex 的独特优势**

- 对文档结构的深度支持——章节、层级、表格、图像
- 更丰富的索引类型——向量索引只是其中一种
- 内置数据合成和评估工具

**与 LangChain 结合**

两者不是竞争关系，而是侧重不同：
- LangChain 侧重流程编排（Chain、Agent），检索只是其中一个模块
- LlamaIndex 侧重数据构建（索引、查询引擎），深入研究数据的高效组织和检索

常见的组合方式是：用 LlamaIndex 构建索引和查询引擎，将查询引擎包装为 LangChain 的 Retriever 或 Tool，然后由 LangChain 的 Agent 来调度使用。

## 其他重要框架与项目

### LangChain4j

LangChain 的 Java 实现，让 Java 生态的开发者可以使用 LangChain 的编程模型。核心概念一一对应：ChatLanguageModel、EmbeddingModel、Tool、Agent、AiServices（类似 Chain 的声明式接口）。

### Spring AI

Spring 生态的 AI 集成框架，提供 Spring Boot 风格的自动配置和 starter：

- 统一的 ChatClient 和 EmbeddingClient 接口
- MCP Server/Boot 集成支持
- 内置 RAG 支持（DocumentReader、DocumentWriter、VectorStore 实现）
- Advisors 模式（类似 AOP 拦截器）对请求做预处理和后处理
- 与 Spring 生态深度集成——配置管理、可观测性、异步支持

### Manus

Manus 是一个通用 AI Agent 产品，强调长时间自主执行复杂任务的能力。核心理念是让 Agent 在沙箱环境中自主规划、执行、验证，直到输出完整交付物。主要创新在于长时间（数小时级别）自主运行和环境交互的工程实现。

### AutoGPT

最早的自主 Agent 开源项目之一，验证了"给 AI 一个目标让它自己想办法完成"的可行性。技术贡献在于定义了 GPT 驱动的自主 Agent 的基本范式——目标拆解、工具使用、记忆管理、循环执行。后续的 Agent 框架（如 OpenClaw）在 AutoGPT 的基础上做了更多工程化改进。

### Google ADK（Agent Development Kit）

Google 推出的 Agent 开发工具包，提供构建生产级 Agent 的标准化组件和最佳实践。与 A2A 协议紧密配合——ADK 用于构建 Agent，A2A 用于 Agent 之间的通信协作。
