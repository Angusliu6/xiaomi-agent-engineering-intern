# 学习配套资料库 · 课程选择、知识点、深度与阅读作业

> 链接截至 2026-11-02 查验。课程访问形式或付费政策可能变化。只学指定章节，跳过与 A09799 目标低相关的泛化内容。

## C1 · Runtime、Tool Loop、状态持久化

**主课：** [DeepLearning.AI · AI Agents in LangGraph](https://www.deeplearning.ai/courses/ai-agents-in-langgraph)（约 1h32m）；必看 Build an Agent from Scratch、LangGraph Components、Persistence and Streaming、Human in the Loop；Essay Writer 作为选修。**辅助课：** [Hugging Face Agents Unit 1](https://huggingface.co/learn/agents-course/unit1/introduction) 的 Tools/Actions/Messages/Agent Workflow。

- **L1 解释：** Workflow 是预定义有向路径；Agent 的“下一步动作”可由模型/策略动态决定；Runtime 负责安全执行、预算和状态，不等于底层 GPU Runtime。
- **L2 代码：** `while steps < max_steps`、状态类型、工具 schema、超时/结果回传、终止条件、idempotent 只读重试。
- **L3 调试：** 在写前 checkpoint 和外部副作用之间发生 crash，理解 exactly-once 不是 SQLite 能自动保证的。
- **本仓库作业：** 阅读 `runtime.py`，画 State→ToolStart→ToolResult→Finish 状态图；改变 budget 和故障注入开关，解释 trace 变化。
- **出口题：** 如果模型把 `top_k` 设成 `true`，Python 的 `bool` 属于 `int` 子类，工具 schema 应如何避免通过？

## C2 · Skill 和 MCP

**主资源：** [Agent Skills Specification](https://agentskills.io/specification)；[MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)；[MCP 官方 Python first steps](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/get-started/first-steps.md)。

- **L1 解释：** Tool 是受控动作，Skill 是含说明、脚本和资源的可复用任务包；MCP 的 Host/Client/Server 分工；MCP 有 Tool/Resource/Prompt 三类原语。
- **L2 代码：** 带类型标注的只读 MCP 工具，序列化、异常映射、接口契约测试。
- **L3 调试：** 构建时有 skill≠运行时可访问；服务端工具可被列出≠每次调用都成功；无法恢复的副作用不自动重试。
- **作业：** 为 `skills/incident-triage/` 写一个回归测试，独立启动 MCP Server，把输入 schema 错误与服务端超时分别标记。

## C3 · RAG 与 Agentic Search

**主课：** [Building and Evaluating Advanced RAG](https://www.deeplearning.ai/short-courses/building-evaluating-advanced-rag/)（约 1h55m）；必看 Advanced RAG Pipeline、RAG Triad、Sentence-window Retrieval、Auto-merging Retrieval。**配套：** [Hugging Face Agentic RAG](https://huggingface.co/learn/agents-course/en/unit3/agentic-rag/agentic-rag)。

- **L1 解释：** 分清 chunking、candidate retrieval、reranking、evidence grounding、answer generation 五个模块；Agentic Search 还允许自主决定是否/如何继续检索。
- **L2 代码：** 手写 BM25 TF/IDF、RRF、TopK、人工 gold-doc 标注；知道 Sparse 与 Dense 的互补性。
- **L3 研究：** 查询改写可能伤害精确代码符号；RRF 可能在高度相关的两个 Lexical Retriever 上带来很小增益。
- **本仓库注意：** `hybrid` 现在是 BM25 + char-gram overlap，**不是 embedding hybrid**。后续一定增加独立 embedding baseline，不能把 RRF 结果写成 Dense 模型效果。
- **出口题：** 为什么 Hit@5 更好但 Answer Accuracy 更差？如何从 Trace 区分召回错/排序错/生成错？

## C4 · Eval 与科研方法（最高优先）

**主课：** [Evaluating AI Agents](https://www.deeplearning.ai/courses/evaluating-ai-agents)；**技术阅读：** [Ragas Context Precision](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/context_precision/) 与其他指标定义。

- **L1 解释：** offline gold set 与 online 用户反馈；可回答 vs 不可回答；检索层、答案层、Agent trajectory 层、运行成本层不能混同。
- **L2 代码：** 每题 `gold_docs`、`answerable`、类别与难度，逐题 paired A/B 输出；Bootstrap 只是描述性不确定性估计，不能自动证明显著性。
- **L3 研究：** 预先锁定 holdout；优化同一小集会过拟合。延迟均值不能替代 P95；抽样时必须保留失败案例。
- **出口题：** 旧版 18/30、新版 21/30，为什么必须看逐题匹配而不只是“多三题”？

## C5 · Reliability、Memory、Planning、安全

**主文档：** [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) 和 [durable execution](https://docs.langchain.com/oss/python/langgraph/durable-execution)。

- **L1 解释：** session memory/store、checkpoint、tool call log、replay 不一样；简单的保存字典≠可靠恢复。
- **L2 代码：** 故障注入、执行预算、timeout/backoff、schema failure fail-fast、允许列表、只读工具与副作用分级。
- **L3 安全：** 检索文档是 untrusted content，注入文本只能作为证据显示，不是高优先级指令；绝不把 API key 交给外部文档。
- **出口题：** Crash 后如何证明没有重复扣费？能否仅凭 SQLite 事务做到？

## C6 · Post-training（了解 + 可选小规模实验）

**技术文档：** [Hugging Face TRL SFTTrainer](https://huggingface.co/docs/trl/sft_trainer)、[DPOTrainer](https://huggingface.co/docs/trl/main/dpo_trainer)。

- **L1 解释：** SFT 的监督轨迹格式 vs DPO chosen/rejected 偏好数据；LoRA 的低秩更新并不是任务成功率保证。
- **L2 实验准备：** 从 Agent trace 采集**已合法授权且脱敏**的成功/失败数据；过滤重复、错误标签、泄漏。
- **L3 评测：** 同架构、同 Prompt/Tool Schema、同冻结 holdout，比较未微调与微调模型；保存训练配置、seed、GPU 时间。
- **出口题：** 错误来自 schema 还是模型策略？为什么很多情况下先调工具和评测比 SFT 更值得？

## 工具清单与推荐顺序

- 必装：Python 3.11+、Git、编辑器（VS Code）、pytest/unittest、基础 sqlite3（Python 标准库）。
- 推荐：`ruff`、`mypy`、`coverage`、`pre-commit`，用于工程质量控制。
- 进阶：LangGraph、MCP Python SDK、SentenceTransformers（真实 Embedding）、FAISS/Chroma、Ragas、LangSmith/Arize（需检查隐私/成本）。
- 可选训练：Transformers、TRL、PEFT、Accelerate。只在数据标注、伦理与机器资源允许后做。
