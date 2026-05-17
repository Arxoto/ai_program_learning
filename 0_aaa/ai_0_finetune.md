# 大模型微调（Fine-Tuning）

## 微调概述

微调是在预训练模型的基础上，使用特定领域或任务的数据进行进一步训练，让模型适配特定场景的过程。

**与预训练的核心区别**

- 预训练：海量通用数据，训练基础语言能力，计算量巨大（数千 GPU 周）
- 微调：相对少量高质量标注数据，适配特定任务或领域，计算量远小于预训练

**常见微调任务**

- 指令微调（Instruction Tuning）：用指令-回答对训练，让模型学会遵循指令格式
- 领域适配（Domain Adaptation）：用特定领域文本训练，让模型掌握领域知识和术语
- 任务微调（Task-Specific Tuning）：针对特定任务（分类、信息抽取、代码生成等）优化
- 偏好对齐（Alignment）：通过偏好数据让模型输出更符合人类期望（安全、有用、诚实）

## 全量微调 vs PEFT

**全量微调（Full Fine-Tuning）**

更新模型的所有参数。效果好但需要大量显存——训练时需要存储所有参数的梯度、优化器状态（如 Adam 的动量和方差），显存需求通常是模型参数量的 4~6 倍。

**PEFT（Parameter-Efficient Fine-Tuning，参数高效微调）**

只更新模型的一小部分参数，冻结绝大部分。核心思路：大模型在不同任务上共享大部分知识，只需调整少数参数即可适配新任务。

**PEFT 的优势**

- 大幅降低显存需求（可低至模型参数的 1% 以内）
- 训练速度快（更新的参数少，梯度计算量小）
- 存储高效（每个任务只需保存一个小的适配器文件，而非完整模型副本）
- 避免灾难性遗忘（冻结主干参数保护原有能力）

**PEFT 与全量微调对比**

| 维度 | 全量微调 | PEFT |
|------|---------|------|
| 显存需求 | 模型参数的 4~6 倍 | 远小于模型参数 |
| 训练速度 | 慢 | 快 |
| 存储 | 每个任务存一份完整模型 | 每个任务存一个轻量适配器 |
| 效果上限 | 高 | 接近全量微调，略有差距 |
| 灾难性遗忘风险 | 较高 | 低 |

## 主流微调方法

### LoRA（Low-Rank Adaptation）

目前最广泛使用的 PEFT 方法。核心思想：在预训练权重矩阵旁添加低秩可训练矩阵，只训练这些低秩矩阵。

- 原理：对于原始权重矩阵 W（d × k），不直接更新，而是添加 ΔW = BA，其中 B（d × r）和 A（r × k），秩 r 远小于 d 和 k（典型值 r = 8 ~ 64）
- 前向传播：h = Wx + BAx，原始 W 冻结，只训练 B 和 A
- 合并推理：训练完成后可将 BA 合并到 W 中（W' = W + BA），推理时无额外计算开销

**Q-LoRA**

LoRA + 量化。将预训练模型量化到 4-bit（NF4 量化格式），再在此之上应用 LoRA。进一步降低显存，使 70B 模型在单卡消费级 GPU 上微调成为可能。

**其他 PEFT 方法**

- Adapter：在 Transformer 层之间插入小的可训练瓶颈层。每层需要额外的前向计算，推理时有少量延迟
- Prefix Tuning：在每层的输入前添加可训练的虚拟 token 前缀。不修改模型结构，但长度受限
- Prompt Tuning：在输入层添加可训练的软提示词 token。最简单但表达能力有限，仅适合大模型
- IA³：通过学习缩放向量对注意力机制中的 Key、Value 和 FFN 进行缩放，参数极少

**LoRA 的优势**

- 不增加推理延迟（可合并）
- 参数量少，易于存储和分发
- 可针对不同任务训练多个 LoRA 并在推理时动态切换
- 与全量微调效果接近

## LoRA 微调实践落地

### 主流微调工具与框架

**Hugging Face 生态（transformers + PEFT + TRL）**

最通用的组合，几乎所有开源模型都兼容。适合需要精细控制训练流程的场景。

- `transformers`：模型加载、推理、基础训练的核心库
- `peft`：PEFT 官方库，提供 LoRA/QLoRA/Adapter/Prefix Tuning 等方法的统一实现，只需几行代码即可为模型注入 LoRA 适配器
- `trl`（Transformer Reinforcement Learning）：在 PEFT 之上封装了 SFTTrainer、DPOTrainer 等高层训练器，处理数据加载、梯度累积、checkpoint 保存等工程细节
- `datasets`：数据集加载与预处理，支持流式加载避免内存溢出
- `bitsandbytes`：8-bit/4-bit 量化，QLoRA 的底层依赖

**LLaMA-Factory**

目前中文社区最流行的微调一站式工具，图形化界面 + 命令行双模式。核心优势是开箱即用和低门槛。

- 内置数十种模型的预设配置，覆盖 LLaMA、Qwen、ChatGLM、DeepSeek 等主流中文模型
- 支持全量微调、LoRA、QLoRA、DPO、ORPO 等多种训练方式
- Web UI 可视化操作：上传数据集 → 选择模型 → 配置参数 → 点击开始训练
- 内置数据集处理工具：格式转换、质量检查、数据预览
- 适合快速验证微调效果，本地单卡或云端单机都能跑

**Unsloth**

专注高性能 LoRA 微调，通过手动优化的 CUDA kernel 和内存管理，将训练速度提升 2~5 倍，显存降低 50%~80%。

- 对 LLaMA、Mistral、Qwen、DeepSeek 等主流架构做了针对性 kernel 优化
- 提供 Colab Notebook 一键运行，零环境配置
- API 设计与 Hugging Face 兼容，迁移成本低
- 适合在消费级 GPU（RTX 3090/4090）上微调 7B~14B 模型

**Axolotl**

面向高级用户的灵活微调框架，通过 YAML 配置文件驱动，适合需要精细控制训练细节的场景。支持 LoRA/QLoRA/全量微调/DPO，配置文件即文档，便于团队协作和实验的版本化管理。

### 算力平台选择

| 平台 | 特点 | 适用场景 |
|------|------|---------|
| Google Colab | 免费 T4 GPU（16GB），Pro 版可用 A100 | 7B 模型 QLoRA 微调、快速原型验证 |
| AutoDL | 国内主流，按量计费，A100/H800 可选 | 中小团队生产使用，性价比高 |
| RunPod / Vast.ai | 全球节点按需 GPU 租赁 | 需要弹性资源且不在意国内外延迟 |
| Hugging Face Spaces | 托管式训练，与 HF 生态无缝集成 | 不想管基础设施的团队 |
| 自有 GPU 服务器 | 数据安全，无网络限制 | 数据敏感的企业场景 |

**显存参考**：QLoRA 微调 7B 模型约需 8~12GB，LoRA 微调 7B 约需 16~24GB，全量微调 7B 约需 40~60GB。

### 数据格式

LoRA 微调通常使用指令-回答对格式，两种主流规范：

**Alpaca 格式（简单指令格式）**

```json
{
  "instruction": "用 Python 实现快速排序",
  "input": "",
  "output": "def quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    ..."
}
```

适合单轮指令类任务。LLaMA-Factory 默认兼容此格式。

**ShareGPT 格式（多轮对话格式）**

```json
{
  "conversations": [
    {"from": "human", "value": "什么是 RAG？"},
    {"from": "gpt", "value": "RAG 是检索增强生成..."},
    {"from": "human", "value": "它能解决什么核心问题？"},
    {"from": "gpt", "value": "核心是解决大模型的幻觉和知识时效性问题..."}
  ]
}
```

适合多轮对话场景，更贴近 Agent 和聊天应用的实际使用方式。

**格式选择建议**：如果你的应用有明确的多轮交互需求，优先用 ShareGPT 格式；如果只是单轮问答或分类/抽取任务，Alpaca 格式足够。

### 实战：LLaMA-Factory QLoRA 微调 Qwen 示例流程

以下以 LLaMA-Factory 为例，展示一次完整微调的大致步骤：

**1. 环境搭建**

```bash
git clone https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e ".[torch,metrics]"
```

**2. 准备数据集**

将数据转为 Alpaca 格式的 JSON 文件，放入 `data/` 目录，并在 `data/dataset_info.json` 中注册：

```json
"my_custom_dataset": {
  "file_name": "my_data.json"
}
```

**3. 选择模型与配置**

在 Web UI 中选择基座模型（如 `Qwen/Qwen2.5-7B-Instruct`），或通过命令行指定。LLaMA-Factory 已内置常见模型的适配，无需手动配置 chat template。

**4. 配置 LoRA 参数（关键）**

```
--finetuning_type lora           # LoRA 或 qlora（4bit 量化）
--lora_rank 8                    # 秩 r，典型值 8~64
--lora_alpha 16                  # 缩放因子，通常 alpha = 2 * rank
--lora_target all                # 目标模块，all 对所有线性层加 LoRA
--lora_dropout 0.1               # LoRA dropout，轻微正则化
```

**5. 训练参数配置**

```
--per_device_train_batch_size 2  # 单卡 batch size，QLoRA 通常 2~4
--gradient_accumulation_steps 4  # 梯度累积，等效 batch = 2×4 = 8
--learning_rate 5e-5             # QLoRA 学习率略高于 LoRA
--num_train_epochs 3             # epoch 数
--lr_scheduler_type cosine       # 余弦退火调度
--warmup_ratio 0.1               # 前 10% 步数做 warmup
--logging_steps 10               # 每 10 步打印日志
--save_steps 100                 # 每 100 步保存 checkpoint
--bf16 true                      # bf16 混合精度（A100/H100 推荐）
--fp16 true                      # 无 bf16 支持则用 fp16
```

**6. 启动训练**

Web UI 模式：`llamafactory-cli webui`，浏览器中操作。

命令行模式：
```bash
llamafactory-cli train \
    --model_name_or_path Qwen/Qwen2.5-7B-Instruct \
    --dataset my_custom_dataset \
    --template qwen \
    --finetuning_type lora \
    --output_dir ./output/my_lora_model \
    ...（上述参数）
```

**7. 导出与推理**

训练完成后导出合并模型：

```bash
# 仅导出 LoRA 适配器（体积小，可动态加载）
llamafactory-cli export --model_name_or_path Qwen/Qwen2.5-7B-Instruct \
    --adapter_name_or_path ./output/my_lora_model \
    --template qwen \
    --finetuning_type lora \
    --export_dir ./merged_model \
    --export_size 2    # 2 = 合并 LoRA 到模型权重中

# 或在 Python 中直接加载适配器做推理
from peft import PeftModel
model = PeftModel.from_pretrained(base_model, "./output/my_lora_model")
```

### LoRA 参数调优经验

- **rank r**：8 是最通用的起点。简单任务（分类、相似风格回复）用 4~8 足够，复杂任务（代码、推理）尝试 16~64。r 越大适配器文件越大，但通常 r > 64 的边际收益递减
- **alpha**：通常设为 rank 的 1~2 倍。alpha 越大 LoRA 权重对原始输出的影响力越强。实践中 alpha = 2 × rank 是最常见的经验值，调 alpha 的效果等价于调学习率
- **target_modules**：默认对所有线性层（`all` 或 `q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj`）加 LoRA。如果显存紧张可仅对 Q/K/V/O 投影层加，但覆盖 FFN 层（gate/up/down）通常能带来更好的效果
- **dropout**：数据量 > 1000 条时设 0.05~0.1 有助于防止过拟合，数据量小时可设 0
- **学习率**：LoRA 通常 1e-4 ~ 2e-4，QLoRA 通常 2e-5 ~ 5e-5。如果 loss 震荡剧烈则降低学习率，如果 loss 下降过于缓慢则适当提高

## 微调策略与实践

### 选择预训练模型

- 任务匹配度：模型是否在你的任务类型上表现好（如代码任务选 Code-LLaMA）
- 领域相关性：模型的预训练数据是否覆盖你的领域
- 规模适配：你的数据和计算资源能支撑多大规模的微调
- 许可证：开源模型的商业使用许可
- 长上下文需求：模型是否支持你需要的最长输入
- 多语言需求：目标语言在预训练数据中的占比

### 常用优化器

- AdamW：Adam 的解耦权重衰减版本，最常用的深度学习优化器
- SGD with Momentum：更简单，有时泛化效果更好
- LION：新型优化器，内存占用小，Google 在某些训练中使用
- 8-bit Adam：量化优化器状态，降低显存

### 训练策略

- 学习率：远小于预训练（通常 1e-5 ~ 5e-4 量级），过大容易灾难性遗忘
- 预热（Warmup）：训练初期线性增加学习率，避免梯度不稳定
- 批大小：受显存限制，结合梯度累积模拟大 batch
- Epoch 数：通常 1 ~ 5 个 epoch，过多容易过拟合

### 数据准备

- 质量 > 数量：1000 条高质量样本往往优于 10000 条噪声样本
- 指令多样性：覆盖多种表达方式和使用场景
- 格式一致性：确保所有样本都使用相同的 chat template
- 长度分布：包含不同长度的样本，避免模型在推理时的长度偏好
- 数据清洗：重复检测、质量过滤、去污染（防止测试数据泄露到训练集中）

## 微调效果评估

**自动化评估**

- 任务特定指标：分类用 F1、BLEU/ROUGE（NLP 生成任务）、HumanEval pass@k（代码）
- 验证集困惑度（Perplexity）：衡量模型对评估集的语言建模质量
- 与基线模型对比测试：在相同测试集上对比微调前后的指标

**人工评估**

- 盲测对比：隐藏模型来源，让标注者比较多个模型的回答质量
- 多维度打分：准确性、相关性、流畅性、安全性
- 领域专家评估：对专业领域的回答由专家鉴定

**评估最佳实践**

- 构建专属评估集：自动化指标不一定反映真实业务需求，需要结合你的实际场景构建评估数据集
- 分层评估：按问题类型、难度分层评估，避免总体指标掩盖特定短板
- 回归检查：确保新模型在原有擅长的任务上没有退化
- A/B 测试：生产环境中新旧模型对照，用真实反馈数据判断微调效果

**判断微调是否达到预期**

- 效果是否有统计显著的提升（而非随机波动）
- 提升幅度是否值得投入的成本
- 是否引入了新的问题（如灾难性遗忘、过度适应训练集分布）
- 推理延迟是否有变化（LoRA 合并后无影响，Adapter 会有少量影响）

## 微调策略的优缺点对比

| 策略 | 优点 | 缺点 |
|------|------|------|
| 全量微调 | 效果上限最高 | 资源开销极大，灾难性遗忘风险高 |
| LoRA | 高效轻量，推理延迟零增加 | 效果可能略低于全量微调 |
| Q-LoRA | 支持超大模型在消费卡上微调 | 量化可能引入精度损失 |
| Adapter | 多任务灵活切换 | 推理时额外计算开销 |
| Prefix/Prompt Tuning | 极低参数 | 表达能力有限，仅适合大模型 |
