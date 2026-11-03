# LAB 07 · 独立审计：从“分数漂亮”到“证据充足”

**目标时长 2–3 小时；前置：LAB 04 已能跑固定评测。**

## Step 1：先预测

不运行代码，写出你的答案：

- 同样的 case ID，改掉第一道题的 `gold_docs`，还能直接比较旧/新版本吗？为什么？
- 两个检索结果都包含 `RRF`，但一个问 RRF 原理、一个问“线上 P95 是多少”，系统是否都应该回答？
- 模型 API 请求报错，`insufficient_evidence` 和 `planning_failed` 在产品意义上有什么差别？

## Step 2：亲自复现

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
traceqa eval --variant b0 --out reports/audit-b0.json
traceqa eval --variant b1 --out reports/audit-b1.json
traceqa compare reports/audit-b0.json reports/audit-b1.json
traceqa eval --cases data/stress_hard_negative.jsonl --variant b2 --out reports/hard-b2.json
```

看每个报告的 `dataset_sha256`, `corpus_sha256`, `settings` 和 `rows`。手工定位 `hn003`、`hn005`，说出支持答案缺了哪种类型的事实，不要只看分数。

## Step 3：故意制造评测污染

拷贝 `data/benchmark.jsonl`，只改一条 gold 标签。保持 corpus 和全部 ID 不变，生成第二份报告，与原报告 `compare`。

**验收：** 工具必须拒绝跨不同 `dataset_sha256` 的比较；而不是输出一个看起来精确的 ΔHit@5。然后恢复文件，重复同样的实验，确认对照能够执行。

## Step 4：设计下一版证据门（禁止写死题号）

为 `hn003` / `hn005` 提出一个可证伪的规则或可标注模型：先识别问题要找的事实类型，再检查文档是否含该类型证据。明确至少两个可能误伤有答案题的反例。

**不能做：** 因为知道 `hn005` 的 gold 就把此题特判为拒答，或让模型在 Prompt 里直接看 benchmark 标注。

## Exit Gate（100 分）

- 25 分：能正确说明数据/标注/答案层评测的边界。
- 35 分：代码可以复现原报告，并能触发比较拒绝；包含至少一项新自动化测试。
- 25 分：对 `hn003`, `hn005` 的假阳性给出可证伪解释。
- 15 分：交付路径、测试命令、配置哈希、反例列表齐全。

**最低 80 分；代码、数据完整性或安全问题未解决不能毕业。**
