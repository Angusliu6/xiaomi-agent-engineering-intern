# LAB 05 · Crash / Replay / Budget / 注入攻击

**前置：** PPT 15–16 / 21–22；LangGraph Durable Execution。

## 预测

“先写 tool_intent 再执行”安全吗？外部动作结束但 checkpoint 还没持久化怎么办？恢复时 Tool 是否可以重试？

## 实验

1. 看 `test_resume_interrupted_read_only_call` 的 `State`。说明为什么只读 search_docs 可以回放。
2. 修改 checkpoint 故意在工具执行后中断，证明重试仍不适用于付款/写入。
3. 在测试文档中加入 `IGNORE ALL PREVIOUS ...`，证明它仍被作为资料而非指令。
4. 修改 `--budget`，测工具调用总量及失败状态，不允许无限重试。

## 验收

故障注入表：注入点、风险、是否安全重试、真实测试输出；明确承认当前不支持 exactly-once 副作用。
