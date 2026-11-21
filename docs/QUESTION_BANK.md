# 口试题库 + 故障卡片 + 评分 Rubric

**教练用法：** 每个 Part 先随机挑 2 道让学生预测执行行为；让学生直接修改代码复现后，再问“反过来会怎样”。评分四维：机制 25、代码 35、故障诊断 25、证据 15。**不在学生第一次作答前展示参考方向**。标准答案不是背诵模板，而是必须说清验证路线。

## Part 0 · Python 工程与接口（L0–L2）

1. `isinstance(True, int)` 为什么为真？如何防止 `top_k=True` 穿过输入验证？
2. `async def` 内调用 `time.sleep` 会怎样？怎么测 event-loop latency？
3. `pytest` 和一次手动运行成功相比，具体防止了什么回归？
4. 重复 `run_id` 的两次请求如何避免覆盖非同一配置的状态？
5. 当 Python 脚本异常退出，`finally` 能保证所有外部副作用被撤销吗？

**实验：** 将 `top_k=-100`、`top_k=True`、`top_k=100000` 分别发送给工具；写三个失败测试；解释每一种 bug 可能如何破坏线上系统。

## Part 1 · Runtime & Memory（L1–L3）

1. 什么是 Agent Runtime？为什么不是 GPU Runtime？
2. Dify 的固定路径 workflow 与模型自主选择下一 Tool Call 何处不同？
3. 工具返回的巨大日志造成 context overrun，应在模型、Runtime、Tool 哪层截断？有什么信息丢失风险？
4. Memory、checkpoint、缓存、conversation history 分别解决什么问题？
5. Agent 在第 3 次工具调用时崩溃，checkpoint 写在调用之前与之后，两种恢复策略分别有何风险？
6. `MAX_STEPS=5` 能保证任务可靠结束吗？如何定义失败终止与善后？
7. 为什么同一 Tool Call 重试安全与否取决于 side effect 和 idempotency？

**实验：** 在 `tool_start` 事件后故意抛进程异常；重启读取 SQLite，观察 `attempted` 与 `step`；解释为何本原型不是完整 crash-safe replay。

## Part 2 · Tool / Skill / MCP（L1–L3）

1. Skill 与 Python function Tool 相比，多了哪些可复用材料？
2. MCP Host/Client/Server 分别处于哪里？MCP Server 是否直接决定模型的下一个 token？
3. Server 暴露出 Tool Schema 等于当前 Tool 可用吗？如何做健康检查？
4. 工具返回非法 JSON，应该让模型自由猜测还是让 Tool Adapter 报 structured error？
5. 为什么系统 prompt 不应信任检索文档里的“忽略一切规则”？
6. Tool 的输入 schema 与权限许可分别属于哪一层？

**实验：** 把 README 中的 MCP 示例连接到本地读-only 数据；故意关闭 Server；写断连恢复日志（严禁重试会产生外部写操作的工具）。

## Part 3 · Retrieval/Agentic Search（L1–L3）

1. BM25 IDF 为什么在精确错误标识符检索中经常有价值？
2. RRF 融合是概率吗？为什么不能把 char-gram 当 Embedding？
3. Query Rewrite 把 `ContextWindowExceededError` 改写成“上下文太长”，可能发生什么？
4. Hit@5 提高但 Answer Accuracy 下降的三个可能原因？
5. 为什么一个最终答案有 citation 不代表这些 citation 支持每一条事实？
6. 哪些检索信号允许 Agent 停止？如果最相关文档也不可靠，如何正确拒答？
7. 为什么 Tool Call 的次数变少不一定说明性能提升？

**实验：** 人为改变一个 rare symbol，比较 B0、B1 的排名；保存每题排序和错误归因，不要只报告总分。

## Part 4 · Evaluation（L1–L3）

1. 旧版 18/30，新版 21/30，如何知道是不是旧对新错互相抵消？
2. bootstrap 95% 区间跨 0 能作什么结论，不能作什么结论？
3. 人工构造 query 和 gold doc，会使实验评价偏向哪些方法？
4. 训练开发集、holdout 集、线上分布有什么本质差别？
5. 何时用 Recall@K，何时用 MRR，何时看正确拒答？
6. 检索得到正确文档但答案仍错误，属于哪层失败？
7. LLM-as-Judge 应如何检查一致性和评分偏差？
8. 模型 A 是 90% 准确率、14s，B 是 88%、5s，如何根据产品约束选择？

**实验：** 用 `examples/b0_sample.json` 与 `b1_sample.json`，找到唯一的新增命中题，查看 bootstrap 区间；重算不同 K 的结果并解释 sensitivity。

## Part 5 · Reliability/Security（L1–L3）

1. 工具超时应该以什么规则重试？与权限拒绝的处理有何不同？
2. 假设报告包含 `IGNORE PREVIOUS INSTRUCTIONS`，怎样证明系统仅把它作为 DATA？
3. 模型输出任意 shell command 的时候为什么需要 allowlist 和人类审批？
4. 恢复 checkpoint 能否保证外部支付恰好一次？需要什么额外设计？
5. 如果缓存里残存测试集的 gold label，研究结果还可信吗？如何防止？
6. 如何通过 trace_id 将一次用户任务的 5 次检索关联起来？

**实验：** 运行注入文档用例，验证没有任何 shell 执行入口；手动向 checkpoint 写入不合法状态并提出数据库 schema 版本迁移方案。

## Part 6 · Post-training/项目答辩（L1–L3）

1. SFT 和 DPO 需要的数据标签分别是什么？
2. 一组 SFT 轨迹包含私有日志时，应该怎样合法处理？
3. 如果 Tool Schema 有 bug，SFT 能修复吗？
4. LoRA loss 降低而 Agent 成功率不变，怎么找原因？
5. 你的项目真正的 innovation 在哪里？如果没有统计显著提升还能发在简历上吗？
6. 你曾让另一个 Agent 自主实现模块，哪些贡献是你亲自设计/编写/验证的？
7. 你这个项目相比于 ordinary RAG Demo 到底多了什么？

## 三张面试官压力测试卡

**Card A — Public score 0.06 → 0.13：** V1/V2 有 thinking、output limit、retrieval 改动混杂。问：能否说 thinking 使得成功率翻倍？你要设计什么对照组？

**Card B — Skill present but failed:** 编译静态把 skill 打进包，但是运行时未实际安装。问：如何构造 smoke canary，证明 Skill 真的执行？

**Card C — Context budget overrun:** max_output_tokens = max_model_len，第一轮即异常。问：推理 token budget 的固定开销由哪几项组成？如何做 fail-fast？

## 口试复盘模板

```text
题号 / 初始判断 / 信心(0-100)
我写的最小测试或运行记录：
结果与预测冲突：
我调整过的假设：
现在我能解释的最小因果链：
如果换一组参数，我预计：
验证证据文件和 commit：
```


## Part 7 · v0.2 独立审计追问（先预测，再实测）

1. 两份 JSON 的 task IDs 完全相同，但其中一份的 `gold_docs` 被改动，你怎样阻止错误的 paired compare？
2. 为什么 `dataset_sha256` 与 `corpus_sha256` 都需要？只有前者是否够？
3. 模型 API 超时和“没有找到证据”是不是相同的业务状态？用户界面应如何分别反馈？
4. 明明检索到了 RRF 的文档，为什么 `hn003` 的真实生产 P95 仍属于无答案问题？
5. 为什么在 10 个高重叠无答案题中，B2 只拒答 4 个，比原来 3 道容易负例 100% 更值得研究？
6. 如果你打算引入 LLM-as-a-Judge，如何建立人工审核与盲验流程，防止评分器奖励更流畅但无依据的答案？

**执行证据**：完整复现实验及破坏标签反例参考 `labs/LAB_07_AUDIT_AND_HARD_NEGATIVES.md`；该实验是学习材料，不允许看到 gold 后硬编码特殊判断。

## Part 8 · Evidence Sufficiency（TRACEQA-20261105-EVIDENCE-TYPE-001）

1. 为什么一个包含 `p95`、`RRF` 关键词的文档，仍然可能不支持“真实生产 P95 延迟是多少”？
2. B2 在 10 道不可回答题上拒答 4 道，B3 拒答 10 道；如果另有 6 道可回答题，为什么必须同时检查 B3 的候选接受率？
3. 在文档里任意添加一个 `P95 = 1 ms` 就会让某些类型门通过。这说明 Typed Gate 最本质的限制是什么？
4. 10 道题都来自开发者已见过的合成集，怎样设计新的不泄漏 Holdout 来验证？
5. B3 多消耗 0.75 次工具调用/题，若接入付费 LLM 和 API，每次调用成本的权衡应如何评估？
6. `tool_failed`、`planner_error`、`budget_exhausted_without_support` 和 `candidate_evidence_only` 为什么不能都归入“无答案”？
7. Checkpoint 是用 lexical 策略创建的，恢复时改成 typed，应如何处理？为什么？
8. `configured.` 被旧 tokenizer 当作整体 token，属于哪类 bug？如何编写回归测试？

**动手关卡**：完成 [LAB 08](../labs/LAB_08_TYPED_EVIDENCE_GATE.md)。不要把该实验描述为模型完成了自然语言蕴含推理。
