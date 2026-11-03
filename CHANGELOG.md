# Changelog

## v0.2 · Independent audit (2026-11-03)

- Harden paired evaluation with benchmark and corpus SHA-256 provenance and strict label consistency checks; expose exact gained/regressed case IDs.
- Add 19 adversarial audit tests and 7 CLI contracts (total offline tests: 51; measured `traceqa` line coverage: 93%).
- Distinguish optional provider/planner failures (`planning_failed`) from genuine insufficient evidence, and include bounded untrusted tool observations for planner context.
- Reject URL userinfo, fragments, query parameters, redirects, oversized provider responses in opt-in planner.
- Add authored stress set: 10 high-overlap unanswerable / 6 answerable; measured B2 abstention proxy 4/10 for negatives, exposing a major weakness.
- Rebuild 31-slide deck, revise course priorities, expand PDF manual, include audit/HN data card and LAB 07.

**Still not done:** public independent benchmark, real provider end-to-end run, semantic dense retrieval/reranker, actual MCP client/server interop, human claim-supported answer accuracy, production hardened runtime. Do not claim otherwise.

## v0.1 · Initial learning prototype (2026-11-02)

- Standard-library Python runtime, keyword retrieval/fusion, SQLite checkpoint demonstration, JSONL retrieval evaluator, 25 tests, initial PPT/manual/labs.
