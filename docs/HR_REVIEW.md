# 模拟招聘审核：严苛 HR + Agent Engineer 双审

## 第一眼会看到什么

**优势**：企业 LLM Agent 实习经历，与这份 JD 高度匹配；项目有真实 Python 工程源码、文档、自动测试、可运行命令和明确的研究问题。检索/运行时/评测的分层体现出工程认知，不是只做了聊天页面。

**立即质疑**：这是不是一个只有 12 篇合成文档、23 道题、结果过于容易的教程仓库？所谓 Agentic 是否真的由模型自主规划？“Hybrid” 是不是伪装成 embedding？任意输入是否能误检？能否独立解释 checkpoint 崩溃重放？

**当前审查结论**：作为教学可运行原型合格，作为“研究级/HR 一眼认定候选人”的**最终旗舰作品尚不合格**。必须完成以下 P0 项，且有新数据支撑后才建议将它放在简历主项目位。

## 风险级别和必须补齐的项目

| 优先 | 现状缺口 | 对方会怎么追问 | 必须交付的修补证据 |
|---|---|---|---|
| P0 | 实际多轮/LLM 规划未端到端验证 | “为什么称 Agent？” | 真实 LLM Tool Call trace + 对照规则策略 + 错误恢复测试 |
| P0 | 合成数据太简单 | “换真实库有效吗？” | 公开许可数据 ≥80，holdout ≥25，人工双人抽检 |
| P0 | B1 只是 lexical fusion | “有没有做 Embedding？” | Dense 模型 + reranker + 同条件消融 |
| P0 | Answer correctness 未测 | “没回答对有什么用？” | Gold answer、claim-support 标注、正确拒答独立评分 |
| P0 | Evidence gate 过弱 | “搜到无关文档也算成功？” | 可解释的判据、near-miss 负例、校准曲线 |
| P1 | SQLite 不是完整 durable runtime | “crash 半途怎么续？” | 五个时点 fault injection 与幂等性/恢复测试 |
| P1 | MCP 只在学习说明中 | “真正接过 MCP 吗？” | SDK Server/Client 可复现互操作测试 |
| P1 | 未统计 API token/成本 | “线上成本呢？” | P50/P95、tokens/call、预算 tradeoff |
| P2 | Post-training 无独立成果 | “SFT/DPO 经验？” | 小模型合法数据训练对照与日志，若时间/算力可用 |

## 具体下一次研究如何决策

1. 将 `unanswerable` 错误单独作为最先研究瓶颈（B0/B1 以“检索无结果”为拒答的代理指标仍为 0；B2 的弱词法门对这 3 道合成负例能拒答，但很可能过拟合）。
2. 建立更难的 `hard negative` 集：词高度重叠但根因不同的文档。
3. 让模型选择 search/rewrite/stop，强制每个计划动作都记录 schema 与轨迹。
4. 人工核验 100 条任务，并用冻结集看是否出现回归。
5. 用 paired delta + latency + token cost 共同判断是否提升，不要单凭分数替换 Champion。

## 招聘流程角度的包装

- Resume headline：**Agent Engineering / Agentic Search / Evaluation**，不称“LLM Training Expert”。
- 2 分钟演示：一次有据可查的成功 + 一次失败 + 一次 A/B（含不确定性）。
- 报告 1 页摘要：问题、主假设、数据、主结果、失败类型、局限、下一实验。
- 如果无法完成完整旗舰项，诚实把 repo 命名为 independent engineering lab，不伪装正式科研成果。

## 2026-11-05 独立复审：Typed Gate Challenger（TRACEQA-20261105-EVIDENCE-TYPE-001）

**加分项**：候选人主动发现单纯词面匹配无法证明具体事实支持；将 B2/B3 方案隔离，建立 pairwise no-answer eval，保存 refusal 原因、成本和失败反例，未擅自将 Challenger 替换 Champion。

**减分项**：规则依赖英语查询形式与简单的金额、时间、姓名、数值模式；看到开发负例后实现的规则容易产生 in-sample 过拟合。没有 Claim Span 对齐、独立标注、真实模型多轮推理，也没有完整端到端正确率证据。

**不会认可的简历话术**：“Agent 拒答准确率提升至 100%”、“成功解决 LLM 幻觉”、“实现工业级 Evidence Verification”。

**可以认可的表述**：“在可重复的自建开发压力集上比较词法门与类型值门，记录无答案负例的逐题变化、仍漏掉的正例、额外调用成本和方法局限；保留可靠基线。”

**晋级要求**：先完成公开数据、盲标 Claim Support、Cost/Latency 对照，再讨论 B3 的招聘级价值。
