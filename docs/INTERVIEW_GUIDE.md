# 技术面试与简历实战手册

## 90 秒项目陈述（只能在本人真正掌握后使用）

“我本科主要做智能感知和深度学习，也在企业 LLM 研发中心接触过 Dify Agent 工作流与 Python 后端。为了补齐可评测的 Agent 工程能力，我做了 TRACE-QA：一个面向工程故障资料的证据驱动检索系统。它把工具输入校验、任务执行预算、SQLite checkpoint、关键词检索和结构化 trace 分开处理。我首先构建了完全离线可复现的 BM25/RRF 对照以及 23 条合成测试样本。关键是我没有把检索命中率包装成回答正确率；我会区分三类不同的失败：找不到依据、有依据但不会推理、工具执行与恢复出错。目前它还是研究原型，接下来重点验证真正的 LLM 多轮检索、语义检索和独立人工评测。”

## 2–3 分钟 Demo 演示顺序

1. `traceqa ask 'max_output_tokens equals max_model_len'` → 展示 citations 和 trace；提醒回答是候选证据而非根因判断。
2. `traceqa ask 'completely unknown policy XZZZZ'` → 展示没有证据时的失败行为；指出它仍然存在误召回风险。
3. `traceqa eval --variant b0 --out reports/b0.json` → 固定指标。
4. `traceqa eval --variant b1 --out reports/b1.json` → A/B，展示 `compare` 的 gains/regressions/95% 区间。
5. `python -m unittest discover -s tests -v` → 展示自动化失败测试。

## HR 或技术面试官会问的 8 个高压问题

| 问题 | 合格回答的结构 |
|---|---|
| “你会 Agent Runtime 吗？” | 区分决策与执行，画状态图，解释 bounded loop、schema、checkpoint；现场找到具体源码。 |
| “这个和 Dify 有什么不一样？” | 比较可视化流程与 Python 独立控制的 trace/test/错误处理；不要贬低 Dify。 |
| “你做的 hybrid 是 semantic retrieval 吗？” | 明确不是：当前 BM25 + lexical char-grams；embedding/reranker 尚是路线。 |
| “为什么得分提高？” | 检查同题配对、任务类型、改动变量、区间与反例；拒绝归因过度。 |
| “如何防止幻觉？” | 检索层/生成层分开、答案证据标注与无法回答策略；目前只输出 extractive evidence。 |
| “你做过 post-training 吗？” | 可坦诚说明参与微调数据处理，但未完成独立 DPO；不要说自己训练过未执行的模型。 |
| “Crash recovery 安全吗？” | 解释 SQLite checkpoint 的能力边界，副作用工具 exactly-once 不保证。 |
| “项目哪里最差？” | 小型合成数据、无真实模型结果、检索层 lexical、无生产安全；优先明确下一次实验。 |

## CV Bullet 规范（需要结果才填数）

- `Designed and implemented a read-only engineering-document retrieval agent in Python, including bounded tool execution, structured traces, and SQLite checkpoints; validated input schema and fault cases with automated unit tests.`
- `Built a reproducible retrieval-only benchmark with annotated document-level relevance labels; compared BM25 and lexical rank fusion with per-case paired analysis and bootstrap uncertainty estimates.`
- **未来完成以后才可补**：`Integrated model-driven search planning and semantic reranking ... achieved [real delta] ... on [held-out task count] ... with [cost/latency].`

## 个人贡献审查

Kaggle Gemma 4 项目若由 Muse 自动化开发，不应把所有 kernel、harness、LoRA 结果说成“本人独立实现”。面试时用三列：本人设计/理解与审核/其他工具自动生成。任何数字必须附实验配置和原始日志。面试官更重视你能重新复现和解释技术决策。


## v0.2 审计后的新增强制答辩

**面试官问：这个项目 Hit@5 有 100%，说明检索完美吗？**

不。那是 20 条作者自己构造的简单题里的 doc-level Hit@5，根本不是生成准确率；更难的 10 道无答案/高词面重合题里，B2 只正确拒答 4 道，说明“相关≠蕴含”。下一阶段必须做独立公共数据和人工 claim support 评分。

**面试官问：你如何保证没有通过换题抬高成绩？**

检索比较结果带 `dataset_sha256` 和 `corpus_sha256`，不同 gold、正文或 top-k 配置的报告 `compare` 会拒绝；同时公开逐题 gains/regressions 和样本限度。这个措施解决的是对照完整性，不是统计外部效度，仍需要冻结 holdout 与盲标。

**面试官问：模型 API 崩了，你为什么不返回“证据不足”？**

因为无法完成搜索和完成搜索但没有支持材料是两种状态。v0.2 用 `planner_error`/`planning_failed` 记录执行失败，并与检索上的拒答区分。实际远程模型交互尚未 live 验证。

**面试官问：哪些贡献是你亲自掌握的？**

只可声称本人能够复现、修改、测试并讲清的模块。将 AI 生成初稿、本人评审和亲手改进的 commit/测试证据分开，不能把所有自动生成代码冒充为个人原始创作。
