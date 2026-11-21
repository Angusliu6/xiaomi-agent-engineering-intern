# LAB 08 · 从词面相似到事实证据（B2 vs B3）

**时间**：60–90 分钟。**先预测再运行**。这不是模型微调、自然语言推理（NLI）或真实 Holdout 研究。

## 目标

理解：检索能命中主题相关文档，不代表该文档能回答查询中的具体数字、时间、负责人或配置值。通过固定同一个 corpus 与检索器比较两种 evidence gate 的拒答和代价。

## 先不要看代码，回答

1. 问题“RET-110 的真实生产环境 P95 延迟是多少？”检索到了 RRF 定义文档，但没有延迟数值，应归类为 `no_result`、`topic_match_without_fact` 还是 `tool_error`？
2. 一套策略把所有请求都拒答，能获得多高的无答案正确拒答率？为什么这不是好系统？
3. 如果 `hn006` 的文档中有“GPU throughput gain of 30%”，就一定回答了该问题吗？该数值是否可能属于别的测试？
4. 若门控更严格导致工具调用从 1.75 增加到 2.50 次，如何评价它是否值得？
5. 为什么开发阶段知道 `hn001`–`hn010` 的正确标签之后，不能再把它们当成独立 Holdout？

## 实验步骤

```bash
python -m pip install -e .
python -m unittest discover -s tests -v

python -m traceqa eval --cases data/stress_hard_negative.jsonl --variant b2 --out reports/lab08-b2.json
python -m traceqa eval --cases data/stress_hard_negative.jsonl --variant b3 --out reports/lab08-b3.json
python -m traceqa compare reports/lab08-b2.json reports/lab08-b3.json
```

查看 `paired_abstention.gain_case_ids`、`paired_abstention.regression_case_ids`、`candidate_acceptance_answerable` 与 `mean_calls`。

接着执行：

```bash
python -m traceqa ask "What was measured P95 retrieval latency after RRF rank fusion RET-110?" --evidence-policy lexical
python -m traceqa ask "What was measured P95 retrieval latency after RRF rank fusion RET-110?" --evidence-policy typed
```

注意 JSON 的 `events`：`evidence_gate.policy`、`intent`、`rejections` 与 `outcome_reason`。

## 故障注入与反例（必须亲自做）

- 在一条不相关文档中添加 `P95 retrieval latency 1 ms`，观察 Typed Gate 是否可能错误接受。注意只改你自己的临时 corpus，**不要篡改原始 Benchmark 的真值标注**。
- 把已明确给出 `context_window: 8192` 的文档修改成自然语言表达“上下文长度八千多”，测试规则是否漏检。
- 改变 `max_steps/budget`，记录拒答和调用成本是否一起变化。
- 模拟 Tool 返回错误，解释 `tool_failed` 与 `insufficient_evidence` 不能混同。
- 研究 tokenizer 把 `configured.` 作为一个整体 token 的边界 Bug：先编失败测试，再作为**独立**实验修复，不混入本轮 PR。

## 通过标准

不能只回答“B3 100%”。必须说出：10 个无答案样本是已见开发集、正例仅接受 4/6、平均调用增加，类型值存在不是 Entailment，真实改善必须通过盲标新数据验证。

## 面试 90 秒表达

“我们先观察到词面匹配把技术相关文档误当作事实依据。我把 Evidence Gate 拆成可选策略，加入问题所需事实类型判断，并保留原始方案作对照。在开发压力集上拒答行为变得更保守，但它并不等于已实现 Claim Verification，也增加了工具调用成本，因此我没有晋级 Champion。下一步要做独立人工标注的 supporting spans，并且在新数据上验证拒答和答案覆盖的取舍。”

**评分**：机制 25、实验复现 30、失败与反事实分析 30、诚实局限 15。
