# TRACE-QA | Evidence-first Agentic Search Engineering Lab

**A09799-aligned portfolio engineering project | Status: working research prototype, not production-ready**

> *Every retrieval change needs a failure hypothesis, a paired benchmark, and an honest regression report.*

TRACE-QA is a bilingual learning + engineering repository built to demonstrate skills relevant to a Shanghai **LLM Application / Agent Engineering Intern** role: Python engineering, bounded agent runtime, read-only tools, retrieval, checkpoints, evidence tracing, evaluation, and experiment review.

**Read this before you judge the repository:** the included `data/` is a small **authored synthetic fixture**, not a real industrial dataset; `b0/b1/b2` evaluate **retrieval only**, not task resolution or answer correctness. Offline `Agent` uses a deterministic reference policy (no learned model). A real model planner is **optional**, requires an explicitly supplied OpenAI-compatible endpoint, and has not been validated here against a live provider. This separation is intentional: no fake performance claims.

## 60-second demo (Python 3.11+)

```bash
python -m pip install -e .
traceqa ask "ContextWindowExceededError max_output_tokens max_model_len"
traceqa eval --variant b0 --out reports/b0.json
traceqa eval --variant b1 --out reports/b1.json
traceqa eval --variant b2 --out reports/b2.json
traceqa compare reports/b0.json reports/b1.json
python -m unittest discover -s tests -v
```

Without installation, set `PYTHONPATH=src` and run `python -m traceqa` instead of `traceqa`.

Optional model planner (sends query and task history to your own configured provider; not needed for tests):

```bash
export TRACEQA_API_KEY="..."  # never commit secrets
traceqa ask "Why does this search tool time out?" \
  --llm-url https://YOUR_APPROVED_ENDPOINT/v1 --model YOUR_MODEL
```

Use only a trusted endpoint, and do not send private company documents. In the demo the model can **plan a search query only**; runtime does not give it a shell or a write-capable tool. The final answer is a short **extractive evidence preview**, not a generated causal diagnosis.

## Architecture

```text
User query ──> Bounded Runtime ──> Planner (offline rules / optional LLM)
                   │                     │
                   │                 next query
                   ▼                     ▼
            Tool schema & validation ─> ReadOnlyTools.search_docs
                                           │
                                      Corpus / BM25
                                      Lexical char-gram
                                      Hybrid reciprocal-rank fusion
                                           │
               SQLite checkpoints <── events & evidence ids
                           │
                       evidence excerpts + citations / abstain
                           │
                      Retrieval-only evaluator
                           │
                 per-item result / paired bootstrap / error report
```

## Repository guide

| Path | Purpose |
|---|---|
| `src/traceqa/retrieval.py` | BM25, lexical character overlap, rank fusion, input validation |
| `src/traceqa/runtime.py` | Planner protocol, finite execution budget, tool trace, SQLite checkpoints, safe extractive answer |
| `src/traceqa/llm.py` | Optional external OpenAI-compatible query planner (opt-in) |
| `src/traceqa/evaluation.py` | Retrieval-only Hit@5, Recall@5, MRR, paired bootstrap |
| `data/corpus/` | 12 authored synthetic incident notes; source text is **untrusted data** |
| `data/benchmark.jsonl` | 23 handcrafted examples, 20 answerable + 3 deliberately unanswerable |
| `tests/` | Automated validation and fault-injection tests |
| `docs/LEARNING_PATH.md` | Six-phase job-aligned curriculum + learning gates |
| `docs/KNOWLEDGE_MAP.md` | Knowledge graph and conceptual distinctions |
| `docs/COURSE_NOTES.md` | All learning resources and targeted lesson checkpoints |
| `docs/QUESTION_BANK.md` | Socratic interview questions + graded rubrics and experiments |
| `docs/PROJECT_SPEC.md` | PRD, architecture, experiments, success criteria, data protocol |
| `docs/OPERATIONS.md` | setup, commands, troubleshooting, limitations and security |
| `docs/INTERVIEW_GUIDE.md` | 2-minute demo, truthful resume bullets and difficult cross-examination |
| `docs/HR_REVIEW.md` | skeptical hiring-manager review and hardening roadmap |
| `skills/incident-triage/SKILL.md` | Skill example and safety boundaries |
| `slides/` | Slide source file and exported PPTX inside downloadable distribution |

## Research baseline: what the current numbers mean

Command examples in `examples/` are outputs from the **synthetic fixture** in this repository, not a benchmark on authentic industry incidents. The sample dataset is small and has authored answers, hence it is **not evidence of generalization**. The project deliberately logs both gains and regressions; observe whether confidence intervals include zero.

**No** text generation model quality has been measured. **No** live MCP interoperability test, distributed recovery test, retrieval abuse red-team, or real GitHub Issue benchmark has been completed. Those are explicit next milestones, not hidden claims.

## What makes this JD-relevant?

1. **Agent Runtime** — bounded loops, typed tool interface, checkpointing and fault-injection exercise.
2. **Agentic Search** — deterministic B0/B1 baselines, planned search tool calls, evidence provenance.
3. **Evaluation** — task-level gold labels, reproducible comparisons, regression inspection.
4. **Engineering writing** — a research protocol, runbooks, honest evidence ledger and interview notes.
5. **Post-training** — companion theory-and-experiment plan, intentionally *not* presented as completed model training.

## First things to improve

1. Replace the synthetic notes with a **licensed/public** held-out engineering corpus; freeze an independent test set.
2. Integrate a real neural embedding retriever and reranker, with the same fixed candidates and budget; add proper query planning and evidence-based stopping.
3. Test a live LLM-based tool selection policy and score **end-to-end answer quality** with human labels.
4. Add actual MCP client/server integration tests; add failure-resume replay and idempotency validation.
5. Expand adversarial and security evaluation; add rate limits, observability and versioned configs.

**Claiming these features already exist would misrepresent the project.** The included docs identify precisely how to implement and validate them.

## Attribution & confidentiality

Designed as an independent learning exercise from a public job description. Not affiliated with or endorsed by Xiaomi. Synthetic corpus is newly authored for this repository; no employer data or private repository content is included. Technical inspiration from earlier personal Kaggle / RAG work is described in `docs/LEARNING_PATH.md` without asserting personal authorship of automatically generated competition changes.

License: MIT (see LICENSE). Feedback and experiments welcome.
