# Hard-negative 压力测试数据卡与标注协议

## 目的和分布

`data/stress_hard_negative.jsonl` 是第二轮审计专门设计的 **16 道合成对抗测试**：6 道文档里有相关信息的问题、10 道高度词面重合但**当前 corpus 没有支持答案的事实**的问题。它与 `data/benchmark.jsonl` 采用相同的 corpus，但不等价于公开真实任务、不代表生产问答质量。它由工程作者标注，只能用于回归测试与定位失败，不得声称是独立 holdout。

例子：`hn003` 询问“真实生产环境的 P95 延迟”，但 `rank-fusion.md` 只有 RRF 的算法定义、没有真实 P95；`hn005` 询问 QueuePool 故障修复的精确 UTC 时间，文档没有具体事故恢复时刻。两题都应拒绝捏造具体数字，即使检索文档看起来很相关。

## 人工审核必须分三层

1. **Document relevance**：哪些文档与问题的实体或主题相关？（可以有相关但不能回答的文档）
2. **Claim support**：文档中是否有精确支持答案的句子/数据？如果问题要求金额、日期、负责人、性能数字，需要该类型证据，不能把“提及同一主题”当作蕴含。
3. **Answerability**：对当前允许使用的材料，是否能够给出有证据的答案？“文档外可能有人知道”不能转化为 corpus answerable。

当前 JSONL 的 `gold_docs` 仅用于**有答案任务的检索评价**。无答案时为 `[]`，不记录“主题相关但不支持”的文档；因此它不能作为完整的 claim-support 标注格式。完整版应新增 `topically_relevant_docs`, `supporting_spans`, `requested_fact_type`, `gold_answer`, `annotation_confidence`, `reviewer_id`, `split` 并由独立标注者审核。

## 本地复现

```bash
python -m pip install -e .
traceqa eval --cases data/stress_hard_negative.jsonl --variant b0 --out reports/stress-b0.json
traceqa eval --cases data/stress_hard_negative.jsonl --variant b1 --out reports/stress-b1.json
traceqa eval --cases data/stress_hard_negative.jsonl --variant b2 --out reports/stress-b2.json
traceqa compare reports/stress-b0.json reports/stress-b2.json
```

本轮实测 B2 只正确拒答 4/10 道无答案题，即无答案压力集上**失败 6/10**。没有模型生成答案的阶段，因此这个指标只是当前 `evidence_gate` 的离线决策表现，而非公开 RAG 正确拒答率。

## 下一步避免污染的协议

- 用真实公共资料构造任务前审查许可证，不加入私有企业日志或个人秘密。
- 先冻结真实文档和正确证据片段，盲标并复核一部分题；先预注册失败类别与评价公式，再做优化。
- Dev 数据允许用来定位错误，Holdout 的 gold 不允许在优化中泄漏；同一 Issue 或代码库跨 split 应考虑信息泄漏。
- 实验比较必须包含 `dataset_sha256`, `corpus_sha256`, `k`, `model_id`, `prompt_version`, `git_sha`, `run_id`；本项目的离线评估已经强制比较前两项与 `k`，其余元数据需要在真实模型研究时补齐。

## 思考题

1. 为什么 `rank-fusion.md` 是 hn003 的相关文档，却不是有用的答案证据？
2. 如果 `hn005` 被 B1 检索到 QueuePool 文档、B2 引用了它，但文档里没有具体时间，Hit@5 应该如何定义？
3. B0/B1 的无答案“拒答率”为什么只是 no-retrieval proxy？
4. 什么情况下 hard negative 会被模型通过胡乱补全回答“正确”，但事实支持仍然为零？
5. 如果开发者自己创造了所有 gold/doc，怎样阻止为自己的方法量身定做测试题？
