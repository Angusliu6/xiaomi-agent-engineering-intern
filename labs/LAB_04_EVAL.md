# LAB 04 · 从感觉优化到可证伪评测

**前置：** PPT 13–14 / 23；Evaluating AI Agents。

## 先预测

B0=19/20、B1=20/20，能否说新方案在真实故障调查中更好？为什么？如果旧版命中 18，新版命中 21，是否还需要看逐题 paired 数据？

## 实验

```bash
traceqa eval --variant b0 --out reports/b0.json
traceqa eval --variant b1 --out reports/b1.json
traceqa eval --variant b2 --out reports/b2.json
traceqa compare reports/b0.json reports/b1.json
```

- 报告每一题 `retrieved`, `hit_at_5`, `reciprocal_rank`, `latency_ms`。
- 记录 `gains/regressions/same` 和 bootstrap 区间，解释它们不足以证明生产效果。
- 从未测过的问题中独立标注至少 10 个新的 gold 文档；打乱开发顺序，冻结 test split。
- 为不可回答问题定义**真正**的回答级人工审核标注，而非仅依赖“检索为空”。

## 验收

写一页实验决策报告：问题、基线、控制变量、结果、回归、威胁有效性、下一实验。
