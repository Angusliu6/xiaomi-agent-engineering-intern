# TRACE-QA Baseline Experiment Report · First reproducible fixture

**Date:** 2026-11-02. **Status:** confirmed local execution, not an independent field benchmark.

## Question

Does combining BM25 and character 3-gram lexical rankings using reciprocal rank fusion improve retrieval Hit@5 on our **authored synthetic engineering incident fixture**?

## Experiment design

- Data: 12 handcrafted synthetic incident notes; 23 handcrafted queries (20 answerable and 3 unanswerable).
- Baseline B0: BM25 Top-5; Challenger B1: BM25 + character 3-gram overlap RRF Top-5.
- Same corpus, query list, K, code revision, machine environment. **No neural embedding was used**.
- Gold ID annotation was performed while constructing the corpus; therefore strong author/test-set bias exists.
- Evaluation metric: doc-level Hit@5 and MRR; **not** answer correctness, model task success, or independent incident resolution.

## Measured results (local execution)

| Metric | B0 | B1 | Interpretation |
|---|---:|---:|---|
| Hit@5, answerable 20 queries | 0.95 | 1.00 | +1/20 query became a hit |
| MRR, answerable | 0.95 | 0.9667 | Several ranking changes, not all strictly positive |
| Unanswerable correct abstention, 3 cases | 0.0 | 0.0 | **Both baselines fail to abstain** by empty-search proxy |
| Mean retrieval time, ms, local CPU | ~0.02 | ~0.58 | Lexical fusion costs more, machine-specific |

Paired analysis: **gains=1, regressions=0, unchanged=19**. Approximate paired bootstrap 95% CI for difference in Hit@5: **[0.00, 0.15]**; includes zero, so no robust generalized improvement claim.

The single recovered case is `q008`, a paraphrased “tools keep retrying the same search and use all the budget”; B0's top five missed `agent-loop.md`, whereas B1 ranked it third. This is a concrete example of an observed synthetic benefit, **not proof of a model's reasoning improvement**.

## Critical failure revealed

An always-return-top-K retriever returned documents for all 3 deliberately unanswerable queries. The original rule-based planner had a similar weakness: it could treat any retrieved hit as sufficient evidence. As a first engineering response, we added a **weak lexical evidence gate** to the offline runtime. It is intentionally not a calibrated factual entailment test. B2 will be scored separately after the change, and because it alters both search strategy and abstention logic, it cannot isolate which component improves performance.

## Next falsifiable experiments

1. **Hard-negative**: add 30 contrastive incidents with lexical overlap but conflicting causes; test evidence gate false positives.
2. **Dense semantic search**: freeze data and add embedding model as a genuinely new retriever; compare both absolute and cost-adjusted ranking.
3. **Independent gold set**: label publicly licensed issues with heldout tasks independent from code authors; measure answer correctness/abstention.
4. **LLM query planner**: compare same retriever with model-driven vs deterministic query selection, with identical budgets and trace metrics.
5. **Crash/replay**: instrument checkpoint at five boundaries; prove idempotent read-only replay and deny non-idempotent tools without approval.

The result is valuable mainly because it establishes the scientific workflow: same-input comparison, failure localization, isolated hypotheses, uncertainty, and honest limitations.


## Second audit / stress suite (2026-11-03; not a held-out production benchmark)

We added `data/stress_hard_negative.jsonl` (16 authored cases; 6 answerable and 10 deliberately unanswerable despite high topic overlap). B0/B1 each hit 6/6 answerable and had 0/10 no-result proxy abstentions. B2 hit 6/6 answerable but correctly abstained on **only 4/10 unanswerable** cases. Thus the previous 3/3 abstentions on easy negatives were misleadingly optimistic.

Evaluation v0.2 now includes SHA-256 of full label-bearing benchmark and full corpus; paired comparisons reject mismatches and return explicit gain/regression case IDs. Older `examples/` were regenerated with v0.2 metadata to keep copy-paste commands working. This does not provide independent data or answer correctness.

The next falsifiable experiment should focus on **requested fact type vs supporting spans** (date/amount/person/actual production metric) instead of adding more generic lexical keyword thresholds. See `docs/AUDIT_2026-11-03.md` and `docs/HARD_NEGATIVE_PROTOCOL.md`.
