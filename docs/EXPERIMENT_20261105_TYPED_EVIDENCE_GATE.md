# Experiment TRACEQA-20261105-EVIDENCE-TYPE-001

**类别**：Offline gate ablation on authored development stress fixture（绝非独立 Blind Holdout）  
**Champion**：`main` @ `d292346c49402141112d3f11a3fb293fd22df83c`，B2 旧词法门控。  
**Challenger**：PR [#6](https://github.com/Angusliu6/xiaomi-agent-engineering-intern/pull/6)，B3 类型约束门控。  
**成本**：0 API/GPU，CPU + GitHub CI。  
**研究范围**：候选证据接受或拒绝的代理行为；不产生生成式答案，不测蕴含与 Task Success。

## 问题与假设

已观察到 B2 在 `data/stress_hard_negative.jsonl` 里 10 个“话题相关但缺少具体事实”的样本只拒答了 4 个。例：RET-110 文档介绍了 RRF，却没有给出“实测 P95 延迟”的值。

**H1**：对显式要求金额、UTC 时刻、责任人、数量、精确配置和性能测量的问题，检查候选文档是否至少**包含该事实类型的值**，可减少误将相关文档视为答案依据的情况。

**可能的失败**：规则不适用于中文、改写问题、隐式数字、表格、相对时间；同段落中的错误数值也可能触发接受；更严格的拒答可能伤害正例，并增加搜索成本。

## 改动的唯一主要变量

- B2：原有 lexical overlap gate。
- B3：同 Retriever、同 Rule Planner、同 5 个候选、同 3 次预算，但增加 `requested_fact_type` 和类型值存在性检查。
- 保留原 B2 默认运行路径，避免未经验证的策略影响 Champion。

## 预注册观测

- Primary (dev-only)：10 道无答案题中 `correct_abstention_unanswerable`，并报告逐题新增正确拒答/丢失拒答。
- Guardrail：6 道可回答题中 `candidate_acceptance_answerable`；不能让全部拒答的策略虚假获胜。
- Resource：`mean_calls`，以便发现较高拒答带来的额外工具成本。
- Retrieval-only Hit@5 保持单列，不混为答案正确率。

## 开发阶段的初步复现实验

本地基于 GitHub 中 12 篇公开仓库合成文档、相同 BM25 / 字符 n-gram 检索逻辑及 Rule Planner 逐题重放，得到：

| 指标 | B2 词法门 | B3 类型门 | 解读 |
|---|---:|---:|---|
| 无答案题正确拒答 | **4/10** | **10/10** | 6 道开发集新增正确拒答，**非泛化证明** |
| 可回答题候选接受 | **4/6** | **4/6** | 没发生新增拒答，但两种策略均遗漏两个正例 |
| 平均工具调用次数 | **1.75** | **2.50** | 更严格的门控导致成本增加约 0.75 calls/题 |
| 真实答案正确率 | **未评测** | **未评测** | 只有 extractive candidate，没有完整回答 |
| 独立 Holdout | **无** | **无** | 不能报告“真实提升 60 个百分点” |

**实验有效性声明**：压力集预先存在并已用于查错，因此属于训练/开发型诊断数据。提升可能来自特定问题措辞。上表是本地逻辑复现结果，完整工程 CI 的结论应以 PR 验证记录为准。

## 逐题与统计

运行：
```bash
python -m traceqa eval --cases data/stress_hard_negative.jsonl --variant b2 --out reports/b2.json
python -m traceqa eval --cases data/stress_hard_negative.jsonl --variant b3 --out reports/b3.json
python -m traceqa compare reports/b2.json reports/b3.json
```

新版 `paired_compare` 将 **`paired_abstention`** 与原始 **`delta_hit_at_5`** 分开报告。Bootstrap 95% CI 只是探索性估计；样本太小、人工作者同源，不足以支持统计显著或产业收益结论。

## 失败归类

1. **topic_match_without_requested_fact**：能检索相关文档，但缺特定数值、人物或时刻。
2. **no_candidate_found**：Tool 成功运行但无候选。
3. **budget_exhausted_without_support**：检索发生但规则认为未找到可接受证据。
4. **planner_error**：计划端点或计划格式异常，不等同证据不足。
5. **tool_error_without_successful_search**：工具整体失败，不能报告“无文档证据”。

## Reviewer 提出的红旗

- B3 的“有同类型值”**不是文本蕴含**；相同文档中的其他事故数值可触发误接受。
- 由于 query rewriting 仍是规则拆词，B3 在部分负例上把 1 次调用变成 3 次。
- 原始 tokenizer 在英文标识符句尾标点时存在边界问题，已经记录为下一个独立 correctness 实验，不与本轮混合修改。
- 需要引入事实支持片段、时间/单位对齐、来源可信度、独立真实数据，才能研究下一版 Gate。
- 不能在简历上写“提升真实 Agent 任务成功率”或“完成 NLI”。

## 判定

**保留 B2 为 Champion，B3 为 Research Challenger。** PR 通过 CI 后仍保持 Draft，直到 S1 真实公开任务与独立标注阶段可以评估泛化效果为止。
