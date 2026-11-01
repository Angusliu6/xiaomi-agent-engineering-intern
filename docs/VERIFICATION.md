# 验收证据与已知限制（2026-11-02）

## 本次真实运行的验证

1. Python 包安装：本地 `python -m pip install -e . --no-build-isolation` 成功；不需要 GPU 和 API Key。
2. 自动测试：`python -m unittest discover -s tests -q` → **25 tests / OK**。
3. 离线检索：`traceqa eval --variant b0/b1/b2` → 各处理 23 条合成样本，真实 JSON 输出保存在 `examples/`。
4. 配对比较：`traceqa compare examples/b0_sample.json examples/b1_sample.json` → gains=1, regressions=0, unchanged=19，bootstrap 区间包含 0。
5. 演示幻灯：`slides/build_slides.js` 实际生成 29 页 PPTX；经 LibreOffice 导出 PDF 检查首页和抽样页面，无明显字体乱码或裁切。
6. 学习文档：已生成 28 页中文 PDF 手册，抽样渲染检查排版。
7. GitHub：项目源码、PPTX 与 PDF 通过连接器提交到 `main` 并检查文件树存在。

## 严格禁止推广为已完成的项目成果

- 未完成真实企业生产数据测试或行业公开真实 benchmark。
- 未验证远程真实 LLM 模型工具调用输出；只实现了显式 opt-in 的查询计划器适配。
- 未完成 MCP SDK v2 的 live interop 测试；仅有适配代码示例。
- 无真正神经 Dense Retriever、Reranker、分布式 Agent Runtime 或生产安全门控。
- 当前“证据门”仅是 lexical coverage 弱启发式，它不是自然语言蕴含证明。
- 小样本上的 100% Hit@5 仅来自作者构造的合成 fixtures，不能在简历中写“问答准确率 100%”。

## 逐步转成可投递的最终旗舰工程作品，需要补完的证据

- S1：公共许可真实文档/Issues，约 80–120 条任务和冻结 holdout ≥25，人工复核。
- S2：模型驱动多轮检索与真正 Embedding/Rerank，记录 Token/Latency/Costs。
- S3：证据门控、hard negatives、no-answer correctness、claim-level 人审标注。
- S4：MCP 真正互操作测试、5 个故障注入点恢复实验与权限/幂等审查。
- S5：消融、对照、回归报告、技术演示和简历 bullet 的数字验证。

详见 `docs/HR_REVIEW.md` 的 P0/P1 缺口和 `docs/PROJECT_SPEC.md` 的实验矩阵。
