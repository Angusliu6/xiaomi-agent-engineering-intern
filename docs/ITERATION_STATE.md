# TRACE-QA · 研发接续状态（2026-11-05）

> **研究分支**：`research/evidence-gate-typed-facts-20261105`，PR [#6](https://github.com/Angusliu6/xiaomi-agent-engineering-intern/pull/6)（Draft）。  
> **主分支 Champion**：`d292346c49402141112d3f11a3fb293fd22df83c`，保持不变；在独立评测前不得自动晋级 Challenger。  
> **当前研发假设**：候选文档的 lexical relevance 并不意味着文档中存在问题要求的具体数值、时间、责任人或配置值。  
> **状态数据以 GitHub 最新提交、PR CI 和实验台账为准，本文件是可复现的状态摘要，不代表后台持续运行。**

## 已有能力（上次核查）

- Python 规则式检索 Tool Loop，SQLite checkpoint 与可追踪事件。
- BM25 + 字符 n-gram rank fusion（两个都是词法检索；无 Dense Encoder）。
- B2 使用词法覆盖启发式作为“候选证据门”；**不是蕴含识别**。
- 12 篇自建文档、23 条合成查询以及 16 条 hard-negative/positive stress fixture。
- GitHub Actions 在 Python 3.11/3.12 执行核心测试与离线评测。

## 本轮 Challenger（仍需 PR Review）

- 可选 `typed` Evidence Gate，对请求类型采用保守的数值/时间/责任人/配置类存在性检查；默认 `lexical` 不变。
- `b3` challenger 与 `b2` 原始对照，报告不可回答题的配对拒答变化以及成本代价。
- Runtime 在 Trace 中记录拒绝原因，并区分 planner failure / tool failure / budget exhaustion。
- Checkpoint 保存证据策略名称，阻止不同策略之间复用同一任务状态。
- 课后实验可以通过 `traceqa eval --variant b2/b3` 复现，新增相关测试。

## 值得优先推进的三项问题

1. **P0：基于来源句子的 Claim Support**。现有 Typed Gate 只能发现某种类型数值/日期/姓名，不能证明数值回答的是指定问题；应设计 `supporting_spans` 与人工双审 gold。
2. **P0：真实公开 Benchmark**。当前 stress cases 在开发前已知，任何改善都是 in-sample diagnostic，不能当作独立 Holdout 或招聘简历的真实性能成绩。
3. **P1：更经济的动态预算**。对 hard negatives 反复尝试近似无意义的查询会增加调用次数。需要独立研究停止策略与成本/质量前沿。

## 当前阻断与资源

- 无经过核实且许可明确的真实工程 Incident 数据集和独立人工标注。
- 无可验证生产级 LLM API、Dense Retriever、MCP 真实互操作实验结果。
- **本轮不使用付费 API/GPU**，只允许只读公开资料和免费 CI。
- **不要将本分支中的合成实验结论直接替换 main / Champion**。

## 接续命令

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
python -m traceqa eval --cases data/stress_hard_negative.jsonl --variant b2 --out reports/stress-b2.json
python -m traceqa eval --cases data/stress_hard_negative.jsonl --variant b3 --out reports/stress-b3.json
python -m traceqa compare reports/stress-b2.json reports/stress-b3.json
python -m traceqa ask "What was measured P95 retrieval latency after RRF rank fusion RET-110?" --evidence-policy typed
```

## 教学重点

提问：“为什么 B3 只通过 *存在具体值* 判断候选，而不能证明该值**属于这一事故**？”  
答题时必须展示至少一个 typed Gate 错误接受的反例，并说明真实 Claim Verifier 所需证据粒度与人工审核程序。
