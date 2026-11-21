# TRACE-QA · 可复现研发路线图（2026-11-05）

| 工作包 | 研究目的 | 关键验收 | 状态 |
|---|---|---|---|
| [S1](https://github.com/Angusliu6/xiaomi-agent-engineering-intern/issues/1) 公开 Benchmark | 真实泛化证据 | 数据许可、≥80 经核验问题、独立 Holdout、审稿抽查 | OPEN |
| [S2](https://github.com/Angusliu6/xiaomi-agent-engineering-intern/issues/2) Dense/Rerank | 真正语义检索 | sparse、dense、hybrid、rerank 配对消融及成本统计 | OPEN |
| [S3](https://github.com/Angusliu6/xiaomi-agent-engineering-intern/issues/3) Evidence-Aware Query Budgeting | 降低无支持答案，同时控制成本 | 人工 Claim-Span 标注、query/stop 模型策略、paired 结果 | **当前第一研究方向** |
| [S4](https://github.com/Angusliu6/xiaomi-agent-engineering-intern/issues/4) Reliability/MCP | 可重放且可审计运行 | MCP Server/Client 实测、五个 crash points、幂等边界 | OPEN |
| [S5](https://github.com/Angusliu6/xiaomi-agent-engineering-intern/issues/5) 科研作品集 | 面试可辩护 | 报告、演示、失败分析、简历合规描述 | OPEN |

## 阶段 H0：Typed-fact Evidence Gate（PR #6）

此阶段仅验证**词汇相关性与事实类型存在性**的区别，不宣称实现 entailment。
已知开发压力题 10 个不可回答 case 以前 B2 只能正确拒答 4 个；B3 实验是 in-sample 诊断，不能作为泛化指标。

### 下一轮预注册推荐

- 基于公共文档设计 `supporting_spans` 结构，含题目、允许引用的来源句、事实槽位、答案/拒答、标注人。
- 对数值错配、同一文档不同事故、单位换算、多跳引用做 20 条**新**测试；先冻结，再调门控算法。
- 观察“拒答更多”与“漏答更多”的 Pareto 曲线，不能以全部拒答刷高 no-answer 指标。
- 除正确率，还测 max calls、Token、P50/P95 延迟；记录每条任务的首次证据时间。
