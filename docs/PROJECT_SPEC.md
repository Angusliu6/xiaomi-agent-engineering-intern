# TRACE-QA 工程研究实施说明书

## 1. 项目定位与成功定义

- **目标 JD**：上海大模型应用实习生 A09799，重点覆盖 Agent Runtime、Skill 开发、Agentic Search、技术方案与可复现实验。
- **用户画像**：研发工程师面对 Issue / traceback / 配置缺陷，需要在文档、故障记录和源码注释中找到**可引用证据**，而不是让模型编造根因。
- **范围内**：只读检索、多轮查询规划、证据出处、失败分类、预算控制、离线评测、可恢复状态、开发文档。
- **范围外（当前）**：自动执行 shell / 修改用户仓库 / 直接生产部署 / 私有数据上传 / 宣称训练了模型。
- **研究贡献目标（尚未完成）**：检验预算和证据门控下的动态检索，是否能以可接受成本改善多步工程任务的可靠性。

## 2. 总体架构及模块接口

```
CLI/API → Agent Runtime (run_id, max_calls, state, checkpoint)
    → Planner (deterministic replay / opt-in LLM decisions)
    → Tool Registry (strict schema, read-only allowlist)
    → Retrieval (BM25 -> char-gram lexical fusion -> future dense/rerank)
    → Evidence (doc_id + extract, source integrity)
    → Evaluation (gold labels, task success, traces, latency)
    → Reports (paired gains/regressions; champion-challenger decision)
```

**重要区别**：本仓库 `Agent` 现阶段只在首次命中后停止，证据充分性尚是很弱的代理条件；B2 不是成熟的 multi-hop Agentic Search。`hybrid` 是两个 lexical 排名，不是 sparse+dense。要实现研究愿景，必须新增独立真正的 embedding 检索和评测人工验证的停止门。

## 3. 技术栈与为什么这么选

- Python 3.11+, `sqlite3`：兼容招聘期待，轻量离线、清晰理解事务边界。
- 无依赖 BM25 + 字符 ngram：确保 benchmark 在无 GPU/无 API key 情况下可复现。**仅作为 Baseline，不应称 SOTA。**
- RRF rank fusion：用于可解释地融合两个排序器；并不能保证增益。
- JSONL Gold cases + unittest：构建最小科学实验基础。
- Optional OpenAI-compatible planner：LLM 只控制搜索 query；不允许变成 shell / write 权限升级。
- 后续 LangGraph/MCP：目标是对照验证，而不是框架堆砌；MCP 环节要独立真实互操作测试。

## 4. 仓库中的数据协议

每条 `benchmark.jsonl`：

```json
{"id":"q001","query":"QueuePool limit size 5 overflow 10 reached","category":"exact","answerable":true,"gold_docs":["connection-pool.md"]}
```

- `gold_docs` 不来自被测 Agent；由独立审核者依据可追溯信息确认。
- `answerable=false` 时 `gold_docs=[]`；其正确拒答不能用检索返回空列表完全替代（当前仅测 proxy）。
- 每种任务单独报告：精确符号、语义改述、多跳、负例、注入、超时、工具错误。
- 分割：dev 用于探索，holdout 冻结且不读 gold 调参；生产数据必须有公开许可并匿名化。

## 5. 实验矩阵：必须控制变量

| 组别 | 检索 | Planner | Evidence Gate | 研究问题 | 当前状态 |
|---|---|---|---|---|---|
| B0 | BM25 | 无 | 无 | 关键词基线 | 已实现、测试 |
| B1 | BM25 + char-gram RRF | 无 | 无 | Lexical rank fusion 效应 | 已实现、测试 |
| B2 | B1 | bounded rule planner | 弱（有候选即停止） | Tool Loop 的运行成本 | 原型实现；不代表成熟 Agentic Search |
| B3 | B1 + Dense / Rerank | LLM query planner | 引用充分性+终止预算 | 多轮动态检索效应 | 尚未实现 |
| B4 | B3 | 同 | + crash replay & robust safety | 可靠性增量 | 尚未实现 |
| B5 | B4 | 同 | 同 + SFT/DPO | 后训练是否值得 | 可选研究，尚未实现 |

**反对的研究方式**：同时改 top_k、Prompt、模型、chunk size，然后把总体提升归于 Prompt。每轮必须一条主假设，所有配置哈希与逐题输出保留。

## 6. 可量化评测指标与保护阈值

| 层级 | 核心指标 | 必须避免的错误解释 |
|---|---|---|
| Retrieval | Hit@5、Recall@5、MRR | 不等于 Answer Accuracy |
| Answer | 人审正确率、引用支持率、正确拒答率 | 当前未测 |
| Agent | task success、loop count、tool error / timeouts | 不能仅把少一次 call 当改善 |
| System | P50/P95 端到端时延、token/cost、成功/失败重试 | 小型合成任务的 CPU ms 无产业意义 |
| Safety | 注入成功率、schema 防御、权限违规次数 | 没有 shell 工具≠所有潜在风险已解决 |

**最低完整研究验收门槛（目标，非当前成绩）**：公开合法数据 ≥80 题，独立 heldout ≥25 题，多跳和不可回答各 ≥15 条；对照组设置一致；每项主要指标报告 paired delta、95% 不确定区间、失败例；高风险工具默认关闭；CI 通过；提供运行成本和可复现脚本。绝不预设结果必须上涨。

## 7. 最有可能产生研究价值的重点方向

**重点 A — Evidence-aware Query Budgeting（第一研究重点）**

1. 单条查询返回候选后，为每条候选估计与问题的证据匹配（非纯 top-score）。
2. 若 gold 任务要求多步关联，模型必须指出当前缺哪一条依据。
3. 根据“额外查询带来的预期信息增益”决定继续搜索或停止。
4. 将剩余 token、最大调用次数、P95 延迟预算作为停止约束。
5. 与 B1 直接配对比较 `Hit@5`、端到端正确率、成本；验证对高频无答案场景是否适得其反。

**重点 B — Failure-aware Tool Recovery（第二重点）**

持久化 `tool_intent`、`tool_result`、幂等键；中断后对只读工具重复尝试，对有副作用的操作请求人工确认。做断连、延迟、错误码注入及恢复成功率实验。

**重点 C — Calibration & Reliable Abstention（第三重点）**

对问题做 answerability 判别，校准置信度，避免低质量依据自信作答。单独设 unanswerable、near-miss、prompt injection 测试集。

**不推荐首攻 SFT/DPO**：训练很容易吞掉算力、时间、标注资源，却无法自动补齐工具 schema 与评测漏洞。先确认 error taxonomy 中“模型策略能力”占主要比例再决定微调。

## 8. 项目排期与交付验收

| Sprint | 范围 | 具体交付与评审 |
|---|---|---|
| S0 (已实现) | offline seed | Corpus、BM25/RRF、rule planner、checkpoint、CLI、23 fixture、23 tests、文档/PPT |
| S1 | 真正模型策略 | 真实模型 tool-planning trace、schema errors、预算统计、≥10 人工核验任务 |
| S2 | Retriever 增强 | Dense+Rerank；检索的独立 holdout；每题回归分析 |
| S3 | evidence gate | 证据门控与多轮 query；真实 human answer annotation |
| S4 | 故障恢复 | crash at 5 boundaries，MCP 互操作、idempotency tests |
| S5 | 冻结与包装 | ≥80 public tasks；完整报告、CI、GitHub Releases、Demo/video |

## 9. 科研日志要求

每个 Experiment ID 包含 `hypothesis, expected_failure, baseline_sha, challenger_sha, model_id, prompt_hash, corpus_version, eval_split, random_seed, paired_task_ids, scores, regressions, runtime/cost, threats_to_validity, decision`。

如果结果不升：写失败原理和反例，不修改 gold 标签寻找好看的分数。若证据缺失，填 `UNKNOWN`。
