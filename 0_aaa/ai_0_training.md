# 大模型基础

## 大模型训练流程

大语言模型（LLM, Large Language Model）的训练分为三个主要阶段：

**预训练（Pre-training）**

在海量无标注文本语料上进行自监督学习，目标是让模型学会语言的统计规律和世界知识。

- 数据：数万亿 token 级别的网页、书籍、代码等
- 任务：Next Token Prediction（自回归），即给定上文预测下一个 token
- 关键要素：高质量数据清洗与配比、分布式训练框架（如 Megatron-LM、DeepSpeed）、并行策略（数据并行 + 张量并行 + 流水线并行）
- 产物：Base Model（基座模型），具备语言理解和生成能力，但不会遵循指令

**指令微调（Instruction Tuning / SFT）**

在高质量指令-回答对上进行监督学习，让模型学会遵循指令。

- 数据：人工标注或模型生成的指令-回答对，覆盖推理、写作、编程、对话等场景
- 目标：将基座模型的原始续写能力对齐到"问答/助手"行为模式
- SFT 后的模型已经能较好地执行指令，但可能存在安全性与偏好对齐问题

**人类对齐（Alignment / RLHF）**

通过人类反馈信号进一步优化模型行为，使其更安全、更有帮助、更符合偏好。

- RLHF（Reinforcement Learning from Human Feedback）：训练奖励模型 → PPO 强化学习优化策略
- DPO（Direct Preference Optimization）：直接从偏好对中学习，无需显式训练奖励模型，简化流程
- 也包括红队测试、安全护栏、价值观对齐等工程实践

## Transformer 架构

Transformer 是大模型的基础架构，由 Google 在 2017 年提出（论文《Attention Is All You Need》）。核心创新是用自注意力机制（Self-Attention）替代 RNN 的序列计算，实现并行化训练。

**Encoder-Decoder 结构**

原始的 Transformer 采用 Encoder-Decoder 架构，但在大模型时代，通常只使用其中一部分：

- **Encoder（编码器）**：将输入序列编码为上下文表示。每层包含多头自注意力 + 前馈网络，自注意力可以看到所有位置的 token（双向注意力）
  - 代表模型：BERT 系列，适合理解类任务（分类、实体识别、信息抽取）
  - 核心特点：双向上下文感知，训练时通过完形填空（MLM, Masked Language Modeling）让模型学会从上下文推测被遮住的词

- **Decoder（解码器）**：根据上文自回归生成下一个 token。每层包含带掩码的多头自注意力 + 交叉注意力（如果有 Encoder 输出）+ 前馈网络
  - 自注意力使用因果掩码（Causal Mask），每个 token 只能看到自己和之前的 token
  - 代表模型：GPT 系列（GPT-3、GPT-4、ChatGPT）、LLaMA、Claude 等，适合生成类任务
  - 核心特点：单向注意力 + 自回归生成，天然适合文本生成

- **Encoder-Decoder（完整架构）**：保持原始设计，Encoder 编码输入，Decoder 交叉注意力接收 Encoder 输出再生成
  - 代表模型：T5、BART，适合序列到序列任务（翻译、摘要、文生图提示词编码等）

**自注意力机制（Self-Attention）**

核心公式：`Attention(Q, K, V) = softmax(QK^T / √d_k) × V`

- Q（Query）：当前 token 想要查询什么
- K（Key）：每个 token 能提供什么信息
- V（Value）：每个 token 实际包含的信息

`QK^T` 计算 token 之间的相关性（注意力分数），`√d_k` 为缩放因子防止 softmax 梯度消失，最终对 V 加权求和得到当前位置的上下文表示。

**多头注意力（Multi-Head Attention）**

将 QKV 拆分为多组（头），每组独立计算注意力再拼接。不同头可以关注不同维度的信息（语法、语义、位置关系等），增强模型表达能力。

**位置编码（Positional Encoding）**

Transformer 本身不具备序列位置感知能力，需要通过位置编码注入位置信息：

- 正弦位置编码（原论文方案）：固定函数生成，不需要额外参数
- 可学习位置嵌入：作为参数训练
- RoPE（旋转位置编码）：通过旋转矩阵编码相对位置，LLaMA、Qwen、DeepSeek 等主流模型采用，支持更好的长度外推

## 分词器（Tokenizer）

分词器负责将原始文本转换为模型可处理的 token ID 序列，是模型输入输出的第一道工序。

**核心概念**

- Token：模型处理的最小语义单元，可以是一个词、一个子词（subword）或一个字符
- 词表（Vocabulary）：模型支持的全部 token 集合，大小通常为 32K ~ 256K
- Tokenization：文本 → token 序列的过程；De-tokenization：token 序列 → 文本的逆过程

**主流分词算法**

- BPE（Byte Pair Encoding）：从字符开始，不断合并高频字符对，构建子词词表。GPT 系列使用，处理英文等字母语言效果好
- WordPiece：与 BPE 类似但合并策略基于似然提升而非频率，BERT 使用
- SentencePiece / Unigram：以概率方式选择子词，T5、LLaMA 使用，对多语言支持更好

**分词器对模型行为的影响**

- 中文分词不当可能导致语义碎片化，影响模型理解和推理（部分模型中文效率显著低于英文的原因之一）
- 数字、代码的分词策略影响数学推理和编程能力
- 词表大小直接影响训练和推理效率（大词表增加嵌入层参数量）

**特殊 Token**

- `[PAD]`：填充 token，批量处理时对齐长度
- `[BOS]` / `[EOS]`：序列起始/结束标记
- `[UNK]`：未知 token，现代大模型通常不使用，改为回退到子词
- `[SEP]`：分隔 token，区分不同句子或段落
- Chat Template 中的角色标记：`<|user|>`、`<|assistant|>`、`<|system|>` 等，用于区分对话角色

## Embedding 嵌入

Embedding 是将离散的符号（token、词语、句子、文档）映射到连续低维向量空间的表示方法，使语义上相近的对象在向量空间中距离相近。

**Token Embedding**

模型的输入嵌入层，将 token ID 映射为稠密向量。每个 token 对应一个可训练的 d 维向量（d 通常为 768 ~ 8192，取决于模型规模）。

**Word Embedding 经典方法**

- Word2Vec（CBOW / Skip-gram）：通过预测上下文或中心词学习词向量，轻量级但无法处理一词多义
- GloVe：基于全局词共现矩阵分解，结合了统计信息和向量空间方法

**大模型中的 Embedding**

在大模型场景下，Embedding 通常指从模型中提取的文本表征向量，用于语义搜索、聚类、分类等下游任务：

- 通用文本嵌入模型：text-embedding-3、bge-large、M3E、Jina Embeddings 等
- 选型考量：向量维度（影响存储和精度）、最大输入长度、多语言支持、检索/分类/聚类任务表现
- 评估基准：MTEB（Massive Text Embedding Benchmark），涵盖分类、聚类、配对、检索、摘要、重排序等多维度
- 真实应用需结合实际语料自行评估，通用基准排名不代表在你的场景下表现最优

**Embedding 在 RAG 中的角色**

将用户查询和知识库文档分别编码为向量，通过向量相似度检索最相关文档，是 RAG 检索引擎的核心基础。

## 模型推理的关键参数

**温度值（Temperature）**

控制输出的随机性。作用于 softmax 之前，将 logits 除以温度 T：

- T → 0：分布趋于 one-hot，输出确定性强，适合数学、代码、事实问答
- T = 1：原始分布，不改变模型输出的概率分布
- T → 高值：分布趋于均匀，输出更加多样和随机，适合创意写作、头脑风暴
- 典型设置：事实任务 0 ~ 0.3，通用对话 0.5 ~ 0.8，创意任务 0.8 ~ 1.2

**Top-p（核采样 / Nucleus Sampling）**

只从累积概率质量达到 p 的最小 token 集合中采样，动态截断长尾低概率候选。

- p = 0.1：仅保留最可能的 token（保守）
- p = 1.0：考虑全部 token（不截断）
- 与 Temperature 组合使用：先温度缩放，再 top-p 过滤

**Top-k**

只从概率最高的 k 个 token 中采样，固定截断数量。

- k 越小越保守，越大越多样
- top-k 的缺陷：对于分布尖锐或平坦的上下文，固定 k 可能截掉重要候选或保留过多噪声

**参数组合与场景推荐**

| 场景 | Temperature | Top-p | 说明 |
|------|------------|-------|------|
| 代码生成 | 0 ~ 0.2 | 0.95 | 需要精确一致 |
| 数学推理 | 0 | - | 确定性输出 |
| 翻译 | 0.2 ~ 0.5 | 0.95 | 平衡准确和自然 |
| 通用对话 | 0.6 ~ 0.8 | 0.95 | 自然多样 |
| 创意写作 | 0.8 ~ 1.0 | 0.9 ~ 0.95 | 需要多样性 |

## 结构化输出（Structured Output）

让大模型按照预定义的格式（如 JSON Schema）返回结果，而非自由文本。

**实现方式**

- JSON Mode：要求模型输出合法 JSON，但不保证字段结构符合预期（多数 API 支持）
- Structured Outputs / Function Calling strict mode：强制模型输出严格匹配指定的 JSON Schema，底层通过约束解码（constrained decoding）限制 token 生成范围
- 约束解码原理：在每一步生成时，根据目标 Schema 的动态有限状态机，将不合法 token 的 logit 设为负无穷，确保最终输出的结构合规性

**应用场景**

- API 调用参数生成（Function Calling 的内部实现）
- 信息提取（从非结构化文本中提取结构化字段）
- 数据分析 pipeline 中的数据转换环节

**局限与注意**

- 强约束可能降低生成质量（模型无法自由选择表达方式）
- 复杂嵌套 Schema 可能影响推理性能
- 不同模型/Provider 对 Structured Output 的支持程度差异较大

## Computer Use

Computer Use 是一种让 AI 模型直接操作计算机界面的能力，模型通过截图理解屏幕内容，生成鼠标点击和键盘输入操作。

**核心原理**

- 视觉理解：模型接收屏幕截图作为输入，理解 GUI 元素（按钮、输入框、菜单等）的位置和功能
- 动作生成：输出结构化的操作指令，如 `click(x, y)`、`type("text")`、`scroll(direction)`、`key_press("Enter")`
- 循环执行：截图 → 分析 → 操作 → 等待结果 → 截图，形成感知-决策-执行循环

**技术挑战**

- 屏幕分辨率与模型输入尺寸的坐标映射
- 动态 UI 变化的处理（弹窗、加载动画、异步渲染）
- 操作序列的长程规划与错误恢复
- 安全边界控制（防止误操作系统关键设置）

**代表实现**

- Claude Computer Use：Anthropic 提供的原生屏幕操作能力
- OpenAI Operator：基于 GPT-4o 的 CUA（Computer-Using Agent）
- 开源方案：OS-Copilot、UFO、CogAgent 等
