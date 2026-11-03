# 学习路线说明书 · 面向小米 A09799 大模型应用实习生

> 版本 v0.2 · 目标：以可复现的技术能力而非记忆名词来通过技术面试。规划总量约 65–85 小时，6–8 周，每周 8–12 小时；“两周投递版”与“完整作品版”分离。时间为建议，不代表任何能力保证。

## 0. 先定终点：毕业式验收（Goal/Definition of Done）

完成者必须在不查看答案的条件下，能：

1. **解释和实现**：从空白文件实现一个带工具接口、状态/预算、停止条件、异常处理的 Agent Tool Loop，并能比较规则计划器和模型计划器的责任边界。
2. **搭建检索**：实现 BM25、混合检索、至少一个独立 rerank 模块；对长代码符号、短语、无答案、多跳检索分别提出预测。
3. **评价**：设计经过人工审核的 gold-doc/answerability/answer correctness，计算 Hit@k、MRR、拒答率和任务成功率；对齐版本、模型、prompt、数据集、配置及成本。
4. **诊断**：对失败 trace 说清“检索没命中、证据有但推理错、工具调用失败、预算耗尽、恢复失败”中的哪类瓶颈，执行单变量对照。
5. **工程化**：写自动测试、CLI、README、部署/恢复手册；能明确什么没有验证、哪些数据不可公示。
6. **展示**：自己录制 2–3 分钟演示，现场 20 分钟带问题代码 walkthrough，回答反事实追问而非背定义。

阶段性门槛：两周版本能独立运行 Tool Loop + 检索 + 最小 eval；完整版本至少有公开可复现数据、独立 holdout、真实模型调用、故障注入、对照实验、报告。当前仓库属于**工作型原型**，尚未达到完整研究验收门槛。

## 1. 基于既有背景的学习诊断（只使用已有可核实经历）

| 已有经历 | 可复用长板 | 无法从简历直接推定的能力 |
|---|---|---|
| 华来科技 LLM 研发中心 Agent 实习 | Dify workflow / 多轮对话 / 微调数据准备 / Python 后端 | 独立 Python Runtime、测试覆盖、可复现 eval、DPO 独立实验 |
| DataWhale 微信智能回复 RAG | RAG 流程和业务问答 | Gold labels、混合检索、拒答/引用真实性评价 |
| Kaggle Gemma 4 Developer Agent | Tool Loop、检索、版本控制和评测策略的真实研究素材 | 本人独立手写所有模块；不能混淆自动化团队成果和个人贡献 |
| 无人机跨视角图像检索 | 特征检索、Recall/mAP 指标、嵌入式部署与性能权衡 | 文本 RAG 一样的错误分布；两者检索任务不同 |
| SemiValley Python GUI / 系统联调 | 系统接口与调试耐心 | 并发服务、CI、权限隔离全栈熟练度 |

**求职叙事目标：** “真实企业 Agent 开发经历 + 独立工程的可测量 Agentic Search 项目”。不把全部时间投在 LLM 后训练上：JD 第四项是参与后训练，当前最小补强成本和最高迁移收益在前 1–3 项。

## 2. 全套节奏与交付物

| 阶段 | 时间 | 必修资源 | 动手交付 | 通过条件 |
|---|---:|---|---|---|
| P0 Python+Runtime | 10h | LangGraph 课程前 3 节；HF Agents Unit 1 | 无框架 loop + checkpoint/fault tests | 能在白板解释状态转移，并手写处理无效参数 |
| P1 Tool/Skill/MCP | 8h | MCP 官方架构、Skills 规范 | schema 校验+只读 MCP server+回放日志 | 说清 Host/Client/Server、Skills 运行时定位 |
| P2 Search | 14h | Advanced RAG + Hugging Face Agentic RAG | BM25、Hybrid、Rerank + query rewrite | 用同一测试集列出新增成功与退步 |
| P3 Evaluation | 15h | Evaluating AI Agents、Ragas metrics docs | 真实评测协议、gold set、错误归因 | 不能把检索 Hit@5 冒充回答正确率 |
| P4 Reliability | 10h | LangGraph durable execution、故障复盘 | crash replay、tool timeout、安全注入 | 有失败/通过的自动化测试和恢复限制说明 |
| P5 Post-training & research | 8–12h | HF TRL SFT / DPO | 数据卡、轨迹标注、可选小模型 LoRA | 解释何时不需要微调、训练与评测隔离 |
| Final | 8–12h | 本项目实现说明与答辩题库 | Benchmark、独立报告、Demo、简历 | 可回答 10 个陌生 case + 真实日志证据 |

### 两周投递优先版

- **天 1–2：** 核对华来实习本人贡献；运行本仓库，画出 `Runtime→Tool→Retriever→Trace`；做 P0 口试。
- **天 3–4：** 不看实现，手写 `search_docs` schema 与 bounded Tool Loop；注入非法 top_k / timeout。
- **天 5–6：** 对现有 RAG 做 gold-data 修订；手算 Hit@5、MRR；观察 B0/B1 的逐题 gains/regressions。
- **天 7–9：** 实现更真实的 query rewrite 和 reranker；用**公开文档**补测试集。
- **天 10–12：** 针对两个最严重失败归因设计单变量实验；做 2min Demo。
- **天 13–14：** 正式整理投递简历与 20min 技术答辩；不要等待完整研究版才投递。

## 3. 每节课的学习方法

1. **预注册预测**：在看实现前写 “如果 X 失败，系统应 Y”；示例：“第三次 Tool Call 进程崩溃，重启是否重复？”
2. **只看针对性的讲解**：概念 15–30 分钟，用自己语言画状态图。
3. **动手制造故障**：例如把 `top_k=5` 改成 `top_k=-100`，观察 schema 在哪里拒绝。
4. **记录 Trace**：保存输入、动作、结果、停止原因、耗时、配置哈希。
5. **口试**：先说预期，再解释反例，最后指出怎样证伪自己的结论。
6. **结课 Gate**：通过正确性 + 代码 + 失败归因 + 验证，分数 80/100；安全/正确性缺陷不能靠平均分抵消。

## 4. 每阶段推荐的认知碰撞案例

- Runtime：Tool Loop 运行 12 轮却从未结束，是 planner 还是 runtime 的责任？
- MCP：Server 挂了，Tool Schema 仍在模型上下文中，是否意味着工具可执行？
- Skill：构建包静态包含脚本，却没在运行时 materialize，为何功能为零？
- Search：`ContextWindowExceededError` 稀有符号用 BM25 反而能更准；什么条件下 Dense 更优？
- Evaluation：B1 命中 19/20，B2 命中 20/20，bootstrap 区间跨 0，如何写结论？
- Reliability：checkpoint 发生在写操作前和后，各有什么重复执行风险？
- Post-training：如果是 tool argument schema 失败，先修数据/接口还是训模型？

## 5. 每周复盘模板

```text
Week / Commit / Runtime configuration:
我原来的预测：
本周最反直觉的一条 trace：
失败类型及证据：
最小可证伪假设：
控制变量与数据集：
观测指标与区间：
新增成功 / 原有成功回归：
下周继续 / 停止的原因：
本人独立实现的代码：
我还解释不清的东西：
```

## 6. 简历上什么可以说、什么不可以说

- **可以**：使用 Python 构建只读检索 Agent 原型、任务 checkpoint、自动化检索 Benchmark，在固定合成集上评估 BM25/lexical hybrid。
- **不可以**：称当前代码已经实现真实 Embedding 混合检索、全面 MCP 集成、SFT/DPO 训练、实证生产质量或 Kaggle 冲榜成绩。
- **等验证后才能说**：真实模型 Agent 任务成功率、端到端事实正确率、显著性能提升、生产就绪故障恢复。


## 7. 审计专题（最小必修）

完成 `docs/AUDIT_2026-11-03.md` 的两项手动验证：故意修改 `gold_docs` 导致 paired compare 拒绝；运行 10 道高重叠无答案 stress case，解释为何当前系统只正确拒答其中 4 道。能用自己的话解释这两个失败模式后，方可宣称具有基本 Evaluation/Abstention 意识。
