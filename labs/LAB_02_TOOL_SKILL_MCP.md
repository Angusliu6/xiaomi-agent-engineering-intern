# LAB 02 · Tool / Skill / MCP 不能混为一谈

**前置：** PPT 09–10；读 [MCP SDK first steps](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/get-started/first-steps.md)。

## 预测题

- Skill 文件存在且被打包，运行时缺少 materialize，该功能能否成功？
- MCP 可列出 `search_docs`，调用时却返回超时，哪一层该决定重试？
- Tool Schema 控制输入类型，谁控制工具真正能不能读取秘密文件？

## 实验步骤

1. 看 `skills/incident-triage/SKILL.md`，指出哪些段落是指导模型，哪些必须由 Runtime 代码强制执行。
2. `python -m pip install mcp`（联网环境、可选）；按 README 说明运行 `mcp dev integrations/mcp_server.py`。当前仓库未完成 live MCP SDK 互操作验证，亲自完成后记录 SDK 版本及输出。
3. 先 `top_k=5`，再 `top_k=-100`，然后故意关闭 Server，区分 schema/transport 错误。
4. 设计一个 canary，证明被引入的 Skill/Tool 被真正调用，不能仅凭清单存在判断。

## 验收

记录 MCP server 的真实版本/日志或将结果标注为 NOT RUN；一张 Host/Client/Server 图；至少两个独立失败分类。
