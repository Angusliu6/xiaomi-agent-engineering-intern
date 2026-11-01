# LAB 03 · 检索精确符号 vs 语义改述

**前置：** PPT 11–12；Advanced RAG 课程与 HF Agentic RAG 教程。

## 先预测

查询 `ContextWindowExceededError` 时，稀有词 BM25 和 char-gram overlap 谁可能更准？如果改写成“模型上下文不够”，哪个检索器会受到影响？

## 实验

1. 阅读 `retrieval.Corpus._bm25`，手算一篇文档中 rare symbol 的 IDF；用代码验证。
2. 运行 `traceqa eval --variant b0/b1`，观察 q008 原本没命中、融合后命中的对应文档位置。
3. 添加一个与目标文档重合大量词语却根因不同的 hard negative，重新执行；记录新增回归。
4. **进阶研究**：使用 SentenceTransformers/FAISS 添加真正的 embedding 检索；无环境就只写实验协议，不声称已完成。

## 验收

一份逐题检索命中列表，至少一个失败案例，以及为什么 char-grams 不能叫 Dense 的解释。
