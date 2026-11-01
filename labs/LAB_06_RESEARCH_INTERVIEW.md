# LAB 06 · 科研消融 + 20 分钟技术答辩

**前置：** PPT 18–29；全套代码、问题清单与 baseline report。

## 实验问题

“Evidence-aware Query Budgeting 在多步工程故障任务中，能否以可接受的 P95 代价提高正确证据的覆盖与正确拒答率？”

## 执行

1. 预注册 B0/B1/B2/B3 的**单一关键改动**，固定数据和 Prompt。
2. 分配 dev/holdout，至少 80 条公开可许可的技术任务（最终目标，当前未完成），保留 hard negatives、no-answer 和复杂多跳案例。
3. 做一次真实 LLM 模型策划器端到端评测，保存 tool call trace 与成本；若无 API / GPU 则明确标记 NOT RUN。
4. 给每条失败案例贴 taxonomy：retrieval / reasoning / tool / budget / unsafe / unknown。
5. 录 2 分钟演示：成功、失败、A/B 对照、尚未实现的模块。

## 现场面试模拟

- 为什么你一定要把搜索器和 agent policy 的贡献分开？
- 你认为最大的虚假高分风险是什么？
- 什么证据能证明你的代码具有工程质量而不是脚本演示？
- 如果 B3 更复杂、慢两倍但没有显著提高成功率，你是否发布？

## 毕业条件

报告可复现、测试可运行、贡献可归属、失败可以解释，不伪造显著性或生产指标。
