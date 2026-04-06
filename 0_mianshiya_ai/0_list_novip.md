
### begin
最近 OpenClaw 这么火，你知道它的原理吗？
简单
AI
OpenClaw
大模型应用开发
Agent 开发
AI 应用开发
### end
### begin
（OpenClaw前置知识）什么是 AI Agent？它和直接调用大模型 API 做一次问答有什么本质区别？
简单
AI
OpenClaw
大模型应用开发
AI 应用开发
Agent 开发
### end
### begin
（OpenClaw前置知识）请解释 Tool Calling（工具调用）的完整链路：工具是怎么定义的、LLM 怎么调用它、结果怎么回传?
简单
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
（OpenClaw前置知识）System Prompt 在 Agent 系统中承载了哪些职责？如果 System Prompt 越来越长，你会怎么处理？
简单
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
（OpenClaw前置知识）什么是 Agent 的 Context Window？为什么它是 Agent 工程中最核心的约束之一？
简单
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
OpenClaw 是什么？它要解决什么问题？它的核心能力有哪些？
简单
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
如果一个 Agent 系统要同时接入 Telegram、飞书、钉钉等渠道，你会怎么设计抽象层？OpenClaw 的 Channel Plugin 接口是怎么设计的？
简单
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
什么是 AI Agent 中的 Skills？它有什么用？
简单
NEW
AI
大模型
Agent
Skills
### end
### begin
MCP 和 Skills 有什么区别？分别适用于什么场景？
简单
NEW
AI
大模型
Agent
Skills
### end

### begin
（OpenClaw前置知识）解释「短期记忆」和「长期记忆」在 Agent 系统中的区别，分别适合怎么存储和检索？
中等
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
OpenClaw 的核心组件有哪些？请描述它们之间的关系
中等
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
LLM 的 Context Window 有上限，长对话时如何保证 Agent 仍然能正常工作？OpenClaw 是怎么做的？
中等
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
Agent 调用工具可能返回超大结果（比如代码搜索返回 50KB），这会带来什么问题？你会怎么处理？OpenClaw 是怎么做的？
中等
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
当对话历史实在太长、裁剪也不够用时，还有什么办法？什么是 Compaction？OpenClaw 的 Compaction 策略是怎样的？
中等
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
OpenClaw 把 Context 管理抽象成了可插拔的 Context Engine，为什么要做这层抽象？这个设计能支持哪些不同的策略？
中等
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
如何设计和管理 AI Agent 的 Skills 体系？在实际项目中有哪些挑战？
中等
NEW
AI
大模型
Agent
Skills
### end
### begin
同一个系统里可能有多个 Agent，不同渠道/用户/群组的消息需要路由到不同的 Agent。你会怎么设计这个路由？OpenClaw 的路由匹配优先级是怎样的？
中等
NEW
AI
OpenClaw
大模型应用开发
Agent开发
AI应用开发
### end
### begin
同一个用户在 Telegram 私聊和 Discord 群组里和 Agent 对话，应该共享会话还是隔离？OpenClaw 是怎么设计会话隔离粒度的？
中等
NEW
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
同一个工具（比如「执行命令」）在不同场景下应该有不同的权限。你会怎么设计工具的权限控制？OpenClaw 的工具策略管道是怎么分层的？
中等
NEW
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
不同的 LLM Provider 对 Tool Schema 的支持不完全一致，你会怎么处理这种差异？OpenClaw 是怎么做 Schema 适配的？
中等
NEW
AI
OpenClaw
大模型应用开发
AI应用开发
### end
### begin
Agent 系统中 Hook/中间件模式有什么用？能举几个典型场景吗？OpenClaw 的 Hook 系统是怎么设计的？
中等
NEW
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
什么场景下需要多 Agent 协作而不是单个 Agent 解决？OpenClaw 是怎么支持子 Agent（Subagent）的？
中等
NEW
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
父 Agent spawn 子 Agent 时，有哪些边界问题需要考虑？OpenClaw 做了哪些限制和保护？
中等
NEW
AI
大模型应用开发
AI应用开发
Agent开发
### end
### begin
多 Agent 之间如何通信和协调？OpenClaw 的 Gateway 在其中扮演什么角色？
中等
NEW
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
OpenClaw 采用插件架构，第三方可以注册新渠道、工具、Hook。设计一个插件系统需要考虑哪些关键问题？OpenClaw 的插件 API 长什么样？
中等
NEW
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
OpenClaw 的 Gateway 对 Agent 请求做了幂等性处理。为什么 Agent 系统特别需要幂等性？工具已经产生副作用时怎么办？
中等
NEW
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
如果让你基于 OpenClaw 的设计理念从零搭建一个 Agent 框架，你会先做哪三个模块？为什么？
中等
NEW
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end

### begin
在 OpenClaw 中，一条用户消息从进入系统到收到回复，完整链路是怎样的？
困难
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end
### begin
OpenClaw 的 Agent Runner 是如何工作的？一次 Agent 运行经历了哪些阶段？
困难
AI
OpenClaw
大模型应用开发
AI应用开发
Agent开发
### end