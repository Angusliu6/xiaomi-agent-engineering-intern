# 技术手册 · 环境、CLI、调试、安全、排错

## 安装

```bash
git clone https://github.com/Angusliu6/xiaomi-agent-engineering-intern.git
cd xiaomi-agent-engineering-intern
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

无需 GPU、无需 API key 即可跑离线代码。核心用 Python 标准库；安装/运行命令在 Windows/macOS/Linux 应当兼容。当前没有 Docker 镜像或发布渠道的端到端验证。

## 复现示例

```bash
traceqa ask 'MCP search_docs top_k timeout' --budget 3
traceqa ask 'A completely unknown policy XZZZZ' --mode bm25
traceqa eval --variant b0 --out reports/b0.json
traceqa eval --variant b1 --out reports/b1.json
traceqa compare reports/b0.json reports/b1.json
```

输出 `run_id`, `events`, `retrieved`, `citations`, `status`。`evidence_found` 只表示找到相关候选，不代表因果诊断已验证。`insufficient_evidence` 是目前启发式规则，在部分无答案问题可能误判。

## Trace 字段读法

- `step`：此次任务中的第几次检索工具执行。
- `tool_start`：调用意图已经记入状态，不保证调用成功。
- `tool_result`：成功返回的候选 doc IDs。
- `tool_error`：类型化失败；当前 sample 支持注入一次 transient error。
- `finish`：状态终止，但证据充分性目前未做人类标注校准。
- `elapsed_ms`：本机本轮时间，不是线上 LLM 延迟，也不等价总任务响应 P95。

## 常见故障

| 症状 | 定位 | 解决 |
|---|---|---|
| `ModuleNotFoundError traceqa` | 未安装 package | `pip install -e .` 或 `PYTHONPATH=src` |
| `empty corpus` | 目录路径错误 | `--corpus data/corpus`；需要 `.md` 文档 |
| `invalid top_k` | 负数、过大、bool | 检查工具 schema 的输入范围 |
| `resume config mismatch` | 不同 query/mode/budget 复用了 run_id | 不能跨配置恢复，另起 run_id |
| `403/timeout` | 外部 LLM endpoint 未授权/不可用 | 先单独测试受信任 API，离线 eval 不依赖它 |
| 不可回答被错召回 | lexical overlap 引发误匹配 | 不可把“有结果”当“证据充分”；S3 修 evidence gate |

## 风险与安全政策

- `data/corpus/` 全为演示数据，不应包含工作单位私有材料。
- External LLM 必须显式 `--llm-url` + `--model`，并且只接受 HTTPS 或 localhost HTTP。
- 绝不将 API key 放在命令行或 `git add` 的文件；使用 `TRACEQA_API_KEY` 环境变量。
- 文档里注入的字符串不具有指令权限。当前模型不能调用 shell / write 工具。
- **SQLite 只提供事务式 checkpoint，不实现跨外部服务的 exactly-once；不要拿它执行支付或修改。**
- 如果后续扩展外部 URL 检索，需要防 SSRF、域名 allowlist、body 大小限制与内容净化。

## 自我学习调试路线

1. 在 `retrieval.Corpus.search` 打断点，亲手计算某个 term 的 `idf`。
2. 在 `runtime.Agent.run` 的 `tool_start` 前后设断点，说明先写事件的理由。
3. 在 `evaluation.measure` 对一题预测 retrieved doc IDs，再执行验证。
4. 修改一个函数，先运行 unit tests，再跑 B0/B1，并找逐题退步。
5. 将观测、预测、修复 commit、回归测试记录到研究日志。
