# RAG（检索增强生成）—— 2026 年技术全景与面试准备

> 结合 2025-2026 年招聘 JD 要求 + 社区最新动态，覆盖分块策略、混合检索、Re-rank、GraphRAG、向量数据库选型与评估体系。
> 整理日期：2026-05-25

---

## 一、RAG 技术全景架构

```
                          RAG 管道（2026 生产标准）

  ┌─────────────────────────────────────────────────────────────────────┐
  │                        预处理层 (Pre-processing)                     │
  │  文档解析 → 分块策略 → Contextual Retrieval → Embedding → 向量存储    │
  ├─────────────────────────────────────────────────────────────────────┤
  │                        检索层 (Retrieval)                            │
  │  查询改写 → 混合检索(BM25+Dense) → Re-rank → 结果融合                 │
  ├─────────────────────────────────────────────────────────────────────┤
  │                        生成层 (Generation)                           │
  │  上下文组装 → Prompt 模板 → LLM 生成 → 引用溯源 → 幻觉检测             │
  ├─────────────────────────────────────────────────────────────────────┤
  │                        进阶层 (Advanced)                             │
  │  Self-RAG │ CRAG │ GraphRAG │ Agentic RAG │ Multi-hop QA            │
  ├─────────────────────────────────────────────────────────────────────┤
  │                        评估层 (Evaluation)                           │
  │  Ragas │ DeepEval │ TruLens │ LLM-as-Judge │ 端到端回归测试          │
  └─────────────────────────────────────────────────────────────────────┘
```

---

## 二、文档分块策略（JD 核心考点）

**核心认知：分块策略就是检索策略。** 分块错了，后面的检索和生成都不会对。

### 2.1 三大主流策略对比

| 策略 | 原理 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|----------|
| **Fixed-size**（固定大小） | 按 N 字符/token 均分 | 实现简单，可预测 | 切断句子/语义，丢失上下文 | 原型验证、同质文本 |
| **Recursive**（递归拆分） | 段→句→词逐级降级切分 | **推荐基线**，保持语义完整 | 块大小不均 | 通用场景首选 |
| **Semantic**（语义拆分） | 计算句子 embedding 相似度，低于阈值即切分 | 主题一致性强 | 基准测试表现不稳定，索引更大 | 主题明确的语料 |

### 2.2 关键参数设置

```
chunk_size:      512 tokens   （适配主流模型上下文窗口）
chunk_overlap:   64 tokens    （10-15%，保证跨块语义连续性）
separators:      ["\n\n", "\n", ".", ";", ",", " "]  （多级拆分）
```

### 2.3 2026 年进阶分块技术

| 技术 | 描述 | 效果 | 复杂度 |
|------|------|------|--------|
| **Late Chunking** | 先对整个文档做 embedding，再切块——每块的向量"知道"完整文档上下文 | 长文档检索提升约 3% | 中 |
| **Contextual Retrieval**（Anthropic） | LLM 为每块预置上下文描述后再 embedding | **减少 67% 检索失败**（配合 rerank） | 低-中 |
| **命题/原子分块** | LLM 将文本拆解为独立事实语句再 embedding | 精确事实检索强 | 高（索引时需 LLM 调用） |
| **混合粒度（父子块）** | 索引小粒度块做精准检索，返回大粒度父块供生成 | 兼顾精度和上下文完整性 | 中 |
| **Pseudo-Instruction Chunking** | 用文档级摘要指导切块边界 | hits@5: 58.4（vs 固定 54.5 / 语义 56.0） | 中 |

**面试追问：chunk_overlap 为什么重要？**
- 防止关键信息恰好落在两个块的边界上
- 保证检索结果覆盖完整的语义单元
- 但过大则增加存储和检索噪声

---

## 三、混合检索 + 重排序（JD 核心考点）

### 3.1 为什么混合检索是生产标配

单一检索的致命缺陷：
- **纯向量检索**：抓不住精确术语（SKU、零件号、缩写、人名）
- **纯关键词检索（BM25）**：理解不了同义词和概念级改写

| 方法 | 优势 | 劣势 |
|------|------|------|
| Dense Vector（语义） | 同义词、概念相似度 | 精确术语匹配差 |
| Sparse Keyword（BM25） | 精确术语、代码、编号 | 无法理解语义变化 |

**基准测试数据**（Redis 2026 研究）：
- 混合检索将召回率提升 **3-3.5 倍**
- 复杂推理任务端到端准确率提升 **11-15%**

### 3.2 融合方法

**RRF（Reciprocal Rank Fusion）**——最常用：
```
RRF_score(d) = Σ 1 / (k + rank_i(d))    # k ≈ 60
```
将两个检索器的排序列表按倒数排名融合，简单有效。

**加权线性组合**：
```
Final_Score = α × Semantic_Score + (1-α) × Keyword_Score    # α ≈ 0.7
```

### 3.3 Re-rank（重排序）——性价比最高的精度提升

**原理**：粗筛（多路检索返回候选）→ 精排（Cross-Encoder 重打分）

| 阶段 | 模型 | 速度 | 精度 |
|------|------|------|------|
| 粗筛（Retrieval） | Bi-Encoder（双塔） | 快 | 中 |
| 精排（Re-rank） | Cross-Encoder（交叉） | 慢 | 高 |

**实战数据**（EACL 2026 混合文档基准测试，23,088 条金融 QA）：

| 方法 | Recall@5 | MRR@3 |
|------|----------|-------|
| BM25 | 0.644 | 0.411 |
| Dense (OpenAI text-embed-3-large) | 0.587 | 0.351 |
| HyDE | 0.544 | 0.318 |
| Hybrid (BM25 + Dense + RRF) | 0.695 | 0.433 |
| **Hybrid + Cohere Rerank** | **0.816** | **0.605** |

**代价**：rerank 增加约 9 倍延迟（0.22s → 2.02s），生产需评估是否需要。

### 3.4 流行的 Re-ranker

| 工具 | 特点 |
|------|------|
| **Cohere Rerank** | API 服务，开箱即用，常用 baseline |
| **BGE-Reranker**（BAAI） | 开源，中文友好，v2 版性能领先 |
| **Prism-Reranker**（2026.04） | 不止打分，还输出贡献声明和证据摘要 |
| **LLM-based Rerank** | 用 GPT/Claude 直接打分，成本高但效果好 |

---

## 四、GraphRAG —— 知识图谱 + 向量检索融合（JD 核心考点）

### 4.1 传统 RAG 的盲区（GraphRAG 解决什么）

```
问题："这家公司的CEO和CTO之间是什么关系？"
传统RAG：分别检索到CEO和CTO的个人简介 → 但无法关联两人
GraphRAG：从知识图谱中直接遍历 CEO-[同事]-> CTO 的关系路径
```

**GraphRAG 核心流程**：
```
文档 → 实体/关系抽取 → 知识图谱构建 → 混合检索（向量 + 图遍历）→ 子图推理 → LLM 合成
```

### 4.2 三大主流方案深度对比（2026 最新）

| 维度 | **Microsoft GraphRAG** | **LightRAG** | **FalkorDB GraphRAG-SDK** |
|------|----------------------|-------------|--------------------------|
| GitHub Stars | 31K+ | 29K+ | 新兴 |
| 核心机制 | Leiden 社区检测 + 层次摘要 | 双层检索（低层+高层） | 图遍历 + 混合检索 |
| 查询 Token | ~610K | ~100 | 中等 |
| 查询延迟 | 基准 | 快 **12 倍** | 中等 |
| 增量更新 | ❌ 需全量重建 | ✅ 仅追加新数据 | 部分支持 |
| 硬件要求 | GPU 集群 | 普通 CPU | 中等 |
| 全局概览能力 | ★★★★★ | ★★☆☆☆ | ★★★☆☆ |
| 事实检索精度 | ★★★☆☆ | ★★★★☆ | ★★★★☆ |

**GraphRAG-Bench 2026.04 综合得分**：
1. FalkorDB GraphRAG-SDK：63.73
2. AutoPrunedRetriever：63.72
3. MS-GraphRAG (local)：50.93
4. LightRAG：45.09

### 4.3 选型决策

```
评估查询复杂度：
  简单→中等   → LightRAG（够用 + 极低成本）
  复杂→超复杂 → MS GraphRAG（全局视野 + 多跳推理）

评估响应要求：
  实时（<1s）    → LightRAG
  非实时         → MS GraphRAG

评估数据动态性：
  频繁更新 → LightRAG（增量追加）
  静态数据 → MS GraphRAG（全量构建）

评估预算：
  有限 → LightRAG（成本低 99%+）
  充足 → MS GraphRAG 或混合架构
```

### 4.4 混合方案（2026 最佳实践）

```
日常简单查询 → LightRAG（速度 + 成本）
复杂多跳推理 → MS GraphRAG（深度 + 全局）
共享底层知识图谱存储（如 Neo4j）
```

---

## 五、向量数据库选型（JD 核心考点）

### 5.1 四大主流方案对比

| 维度 | **ChromaDB** | **PgVector** | **Qdrant** | **Milvus** |
|------|-------------|-------------|-----------|-----------|
| 定位 | 嵌入式/轻量 | PostgreSQL 扩展 | 原生向量数据库 | 分布式向量数据库 |
| 语言 | Python | C（PG 扩展） | Rust | Go + C++ |
| 部署难度 | 极低 | 低（已有 PG 即可） | 中 | 高 |
| 规模上限 | 10 万级 | 百万级（~5-50M） | 亿级 | 十亿-万亿级 |
| P99 延迟 | 50-150ms | 100-300ms | <20ms | 50-200ms |
| 混合检索 | 基础元数据 | SQL 过滤 | 原生 full-text + payload | 原生支持 |
| GPU 加速 | ❌ | ❌ | ❌ | ✅ |
| 适合阶段 | 原型/Demo | 中小型生产 | 性能型生产 | 大规模生产 |

### 5.2 选型决策

```
规模：
  <10 万向量            → ChromaDB（最快上手）
  10 万 - 500 万        → PgVector（已有 PG）或 Qdrant
  500 万 - 10 亿        → Qdrant
  >10 亿                → Milvus

团队运维能力：
  无运维               → ChromaDB / PgVector / 托管云
  有一定运维            → Qdrant 自托管
  K8s 运维能力强        → Milvus 自托管

核心需求：
  最快延迟              → Qdrant（Rust，P99 <20ms）
  SQL + 向量联合查询    → PgVector（ACID、JOIN）
  海量吞吐 + GPU 加速   → Milvus
  最快上线              → ChromaDB
```

---

## 六、RAG 高级范式（2026 前沿）

### 6.1 Self-RAG

训练 LLM 在生成过程中输出**特殊反思 token**来决定何时检索、检索内容是否相关、生成是否被检索支撑。

- 只有 **2%** 的正确预测来自检索外知识（vs 传统 LLM 的 15-20%）
- ICLR 2024 Oral（top 1%），2026 年仍是最具影响力的 RAG 范式之一
- 代价：需要 7B+ 模型 + 特殊训练数据

### 6.2 CRAG（Corrective RAG）

轻量级检索评估器，在生成前对检索质量打分：

```
检索结果 → 评估器打分 →
  ✅ 高质量  → 直接生成
  ⚠️ 中质量 → 检索 + 补充 web 搜索
  ❌ 低质量 → 完全回退到 web 搜索
```

**安全注意**：web 回退路径可能引入恶意内容注入风险。

### 6.3 Agentic RAG

将 RAG 管道中的关键决策点交给 Agent 自主判断：

```
用户问题
  → Agent 判断检索策略（向量/关键词/图？）
  → Agent 选择数据源（哪个库？哪个表？）
  → Agent 评估结果质量
  → 不够就改写查询重试
  → 够了就合成答案
```

**SCIM**（2026.02，250M Flan-T5）：无需微调，自适应 Augment/Refine 模式，+17.2% over 标准 RAG，匹配 7B+ 模型效果。

### 6.4 ReflectiveRAG（EACL 2026）

- **自反思检索控制器**：小 LM 迭代评估证据充分性
- **对比噪声移除**：embedding 过滤冗余/无关片段
- 减少证据冗余 **30.88%**，仅增加 **18ms** 延迟

### 6.5 高级 RAG 技术栈总结（按 ROI 排序）

```
1. 混合检索（BM25 + Dense + RRF）      ← 性价比最高，生产基线
2. Cross-Encoder Re-rank               ← 成本低，收益明确
3. Recursive/Semantic Chunking         ← 基础工程
4. Contextual Retrieval                ← 减少 67% 检索失败
5. 查询改写（Query Transformation）     ← 短查询/模糊查询有效
6. Self-RAG / CRAG                     ← 高精度场景
7. GraphRAG                            ← 多跳推理场景
8. Agentic RAG                         ← 复杂自适应场景
```

---

## 七、RAG 评估体系

### 7.1 评估指标

| 维度 | 指标 | 说明 |
|------|------|------|
| 检索质量 | Recall@K, MRR, NDCG | K 个候选中命中的比例、排序质量 |
| 答案忠实度 | Faithfulness | 答案是否完全基于检索内容得出 |
| 答案相关性 | Answer Relevancy | 答案是否回应用户问题 |
| 上下文精度 | Context Precision | 检索到的内容中有多少是相关的 |
| 上下文召回 | Context Recall | 相关内容中有多少被检索到了 |
| 幻觉率 | Hallucination Rate | 答案中无依据内容比例 |

### 7.2 评估工具

| 工具 | 定位 | 特点 |
|------|------|------|
| **Ragas** | RAG 专用评估框架 | 最流行，LangChain/LlamaIndex 集成 |
| **DeepEval** | 通用 LLM 评估 | 支持 RAG 指标，CI/CD 集成 |
| **TruLens** | RAG 可观测性 | 反馈函数机制，可视化 triad |
| **LangFuse** | LLM 可观测性平台 | 开源，OTel-native，支持评估 |
| **MLflow Eval** | 实验追踪 + 评估 | MLOps 生态 |

### 7.3 LLM-as-Judge 最佳实践

```
1. 人工标注 50-200 条数据 → 建立 ground truth
2. 设计评估 rubric（二分评判优于打分，LLM 不擅长细腻打分）
3. 计算 Cohen's kappa（目标 > 0.6）验证一致性
4. 高风险决策使用多 Judge 交叉验证
5. 持续审计，防止评估漂移
```

**关键经验**：二分类评估（"答案是否引用了非检索内容？"）优于范围打分（"答案质量 1-5 分？"）——LLM 在细腻打分上不一致。

---

## 八、RAG 面试高频追问

### 8.1 "RAG 的检索质量很差，你怎么排查和优化？"

排查链路（自上而下）：
```
1. Embedding 模型是否匹配语料领域？（通用 vs 领域微调）
2. 分块策略是否合理？（块大小、overlap、拆分方式）
3. Chunk 的上下文是否完整？（无头无尾的片段无法匹配）
4. 用户查询是否做了改写？（口语化表述 → 检索友好格式）
5. 只用向量检索？（加 BM25 做混合检索）
6. Re-rank 用了吗？（粗筛 20 条 → 精排 top 3）
7. 基准测试 → 定位瓶颈 → 逐一优化 → 重新评估
```

### 8.2 "混合检索的融合权重怎么定？"

- 先线上小流量 A/B，观察用户反馈/点击率
- 离线用标注数据集 grid search：α ∈ {0.3, 0.5, 0.7, 0.9}
- 语义为主场景 α 偏大（0.7-0.8），术语密集 α 偏小（0.3-0.5）
- RRF 天然不敏感，大多数场景直接可用

### 8.3 "GraphRAG 成本这么高，什么时候才值得？"

- 多跳推理需求（A → B → C 的关系链）
- 全局摘要需求（"这个代码库整体架构是什么？"）
- 低延迟不是核心要求（可等待秒级响应）
- 数据更新不频繁（重建索引成本可接受）
- 上面条件不满足 → 先用混合检索 + rerank

### 8.4 "你的 RAG 系统中 LLM 幻觉的比例大概是多少？怎么降低？"

- 引用溯源：每个断言标注来源 chunk
- Faithfulness 自动评估（Ragas / TruLens）
- 长上下文反而增加幻觉（Lost in the Middle），精简注入的上下文
- Self-RAG 的反思 token 机制自动化检测和修正
- 系统 prompt 约束："如果检索结果不包含答案，明确说不知道，不要编"

---

## 九、关键结论

1. **混合检索 + Re-rank 是 2026 年生产基线**，不做就是 naive RAG
2. **分块策略是 RAG 系统的第一性原理**——在这上面省时间=后续所有优化打折
3. **GraphRAG 解决多跳推理**，但不是所有场景都需要——先评估查询类型
4. **PgVector 已成中小规模首选**，Qdrant 是性能型生产首选，Milvus 是海量场景首选
5. **Contextual Retrieval**（Anthropic）成本低效果好，是 2026 年最值得投入的优化
6. **评估体系从 Day 1 就要建**——没有评估的优化 = 凭感觉重构
7. **Agentic RAG 是方向**——检索质量不足时自动改写查询、切换策略、回退 web 搜索

---

## 参考链接

- [12 Advanced RAG Techniques 2026 (Atlan)](https://atlan.com/know/advanced-rag-techniques/)
- [Best Vector Databases 2026 Comparison](https://encore.dev/articles/best-vector-databases)
- [GraphRAG SDK 1.0 (FalkorDB)](https://www.falkordb.com/blog/graphrag-sdk-knowledge-graph/)
- [Advanced RAG Methods (Google Codelabs)](https://codelabs.developers.google.com/codelabs/production-ready-ai-with-gc/8-advanced-rag-methods/advanced-rag-methods?hl=en)
- [Chunking Strategy for RAG Pipelines (Redis)](https://redis.io/blog/chunking-strategy-rag-pipelines/)
- [CRAG Benchmark 2026 - Text-and-Table Documents](https://arxiv.org/html/2604.01733v1)
- [Prism-Reranker (arXiv 2026.04)](https://arxiv.org/html/2604.23734v1)
- [SCIM: Self-Correcting Iterative Mechanism (MDPI 2026)](https://www.mdpi.com/2079-9292/15/5/996)
