# LAB 01 · Runtime 与 Tool Schema 的错误边界

**前置：** 看 PPT 07–08，课程 LangGraph Build Agent from Scratch；运行 `python -m unittest discover -s tests -v`。

## 实验前预测

1. `top_k=True` 与 `top_k=1` 在 Python 参数类型上有什么意外关系？
2. 工具 `search_docs` 第一次失败、第二次成功：status、attempted、events 会怎样变化？
3. 如果预算为 1，出现 ToolError 后是否会重试？为什么？

## 操作

- 阅读 `ReadOnlyTools.search_docs`，把三个非法参数单独输入；写 `unittest`。
- 调用 `Agent(ReadOnlyTools(corpus, fail_first=True)).run('MCP timeout', budget=3)`；完整打印 `events`。
- 把预算改成 1，用日志解释终止。
- 任选一个 `tool_start` 事件手工写进 SQLite，再调用 `--resume`（或参考自动测试）。

## 提交物与验收

`labs/evidence/lab01-notes.md`（预测→实际→解释）、新增或引用的测试名、一个 20 行以内的执行状态图。**晋级门槛：** 说清模型负责决策、Python 负责执行和校验、只读重试与有副作用工具区别。
