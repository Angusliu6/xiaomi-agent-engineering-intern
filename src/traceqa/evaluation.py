"""Auditable document-retrieval evaluation, *not* an answer-quality benchmark.

The dataset and corpus are hashed so that paired comparisons cannot quietly
compare different benchmarks. The B2 diagnostic remains an offline, heuristic
reference policy: it is not a trained LLM agent or an industrial RAG result.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import hashlib
import json
import random
import statistics
import time

from .retrieval import Corpus
from .runtime import Agent, ReadOnlyTools

EVALUATION_VERSION = "retrieval-v2"


def _digest(data: object) -> str:
    blob = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _validate_cases(cases: list[dict]) -> None:
    if not cases:
        raise ValueError("empty benchmark")
    seen: set[str] = set()
    for n, case in enumerate(cases, 1):
        if not isinstance(case, dict):
            raise ValueError(f"case {n}: expected object")
        case_id = case.get("id")
        query = case.get("query")
        gold = case.get("gold_docs")
        answerable = case.get("answerable")
        if not isinstance(case_id, str) or not case_id.strip() or case_id in seen:
            raise ValueError(f"case {n}: empty or duplicate id")
        seen.add(case_id)
        if not isinstance(query, str) or not 0 < len(query.strip()) <= 1000:
            raise ValueError(f"case {n}: invalid query")
        if not isinstance(gold, list) or any(not isinstance(d, str) or not d for d in gold):
            raise ValueError(f"case {n}: invalid gold_docs")
        if len(set(gold)) != len(gold):
            raise ValueError(f"case {n}: duplicate gold_docs")
        if not isinstance(answerable, bool) or answerable != bool(gold):
            raise ValueError(f"case {n}: inconsistent answerability labels")


def load_cases(path: Path) -> list[dict]:
    cases: list[dict] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            cases.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSONL line {line_no}") from exc
    _validate_cases(cases)
    return cases


def measure(cases: list[dict], corpus: Corpus, *, variant: str = "b0") -> dict:
    """Score document IDs only, on the *same* labeled cases for every variant.

    B2 'first five' documents are the first five UNIQUE IDs encountered across
    its tool calls. This is not the same as a reranked global top five; report
    it as `first_seen_across_hops` to avoid silently claiming equivalent ranks.
    """
    _validate_cases(cases)
    if variant not in ("b0", "b1", "b2"):
        raise ValueError("choose b0, b1, or b2")
    corpus_ids = {d.id for d in corpus.docs}
    if not corpus_ids:
        raise ValueError("empty corpus")
    for case in cases:
        missing = set(case["gold_docs"]) - corpus_ids
        if missing:
            raise ValueError(f"{case['id']}: gold document missing from corpus: {sorted(missing)}")

    rows: list[dict] = []
    mode = "bm25" if variant == "b0" else "hybrid"
    for case in cases:
        if variant == "b2":
            state = Agent(ReadOnlyTools(corpus)).run(case["query"], mode=mode, budget=3)
            predicted = state.retrieved[:5]
            all_retrieved = state.retrieved
            calls = state.step
            elapsed = state.elapsed_ms
            abstained = state.status == "insufficient_evidence"
        else:
            start = time.perf_counter()
            predicted = [h.id for h in corpus.search(case["query"], 5, mode)]
            elapsed = (time.perf_counter() - start) * 1000
            all_retrieved = predicted
            calls = 1
            # This is a *no-result proxy*, NOT an evidence-calibrated answer refusal.
            abstained = not predicted
        gold = set(case["gold_docs"])
        first = next((i for i, doc_id in enumerate(predicted, 1) if doc_id in gold), 0)
        rows.append({"id": case["id"], "category": case.get("category", "general"),
                     "answerable": case["answerable"], "gold_docs": sorted(gold),
                     "retrieved": predicted, "all_retrieved": all_retrieved,
                     "hit_at_5": bool(first), "reciprocal_rank": 1 / first if first else 0.,
                     "recall_at_5": len(set(predicted) & gold) / len(gold) if gold else None,
                     "correct_abstention": abstained if not gold else None,
                     "calls": calls, "latency_ms": round(elapsed, 3)})

    def mean(key, keep=lambda r: True):
        values = [r[key] for r in rows if keep(r) and r[key] is not None]
        return round(statistics.mean(values), 4) if values else None

    return {"evaluation_version": EVALUATION_VERSION,
            "dataset_sha256": _digest(cases),
            "corpus_sha256": _digest([{"id": d.id, "text": d.text} for d in corpus.docs]),
            "settings": {"k": 5, "mode": mode, "strategy":
                         "first_seen_across_hops" if variant == "b2" else "single_ranked_query",
                         "planner": "deterministic_reference" if variant == "b2" else None},
            "variant": variant, "count": len(rows), "scope": "retrieval_only",
            "metrics": {"hit_at_5_answerable": mean("hit_at_5", lambda r: r["answerable"]),
                        "mrr_answerable": mean("reciprocal_rank", lambda r: r["answerable"]),
                        "recall_at_5_answerable": mean("recall_at_5", lambda r: r["answerable"]),
                        "correct_abstention_unanswerable": mean("correct_abstention", lambda r: not r["answerable"]),
                        "mean_calls": mean("calls"),
                        "mean_latency_ms": mean("latency_ms")},
            "rows": rows}


def paired_compare(a: dict, b: dict, iterations: int = 2000, seed: int = 42) -> dict:
    if not isinstance(iterations, int) or isinstance(iterations, bool) or iterations < 100:
        raise ValueError("iterations must be >= 100")
    for label, report in (("baseline", a), ("challenger", b)):
        if report.get("evaluation_version") != EVALUATION_VERSION or report.get("scope") != "retrieval_only":
            raise ValueError(f"{label}: unsupported or legacy evaluation format")
        if not isinstance(report.get("rows"), list) or len(report["rows"]) != report.get("count"):
            raise ValueError(f"{label}: inconsistent report row count")
    for field in ("dataset_sha256", "corpus_sha256"):
        if a.get(field) != b.get(field):
            raise ValueError(f"cannot compare different {field}")
    if a.get("settings", {}).get("k") != b.get("settings", {}).get("k"):
        raise ValueError("cannot compare different top-k settings")
    x = {r["id"]: r for r in a["rows"]}
    y = {r["id"]: r for r in b["rows"]}
    if len(x) != len(a["rows"]) or len(y) != len(b["rows"]) or x.keys() != y.keys():
        raise ValueError("different or duplicated evaluation cases")
    for case_id in x:
        if (x[case_id]["gold_docs"], x[case_id]["answerable"]) != (y[case_id]["gold_docs"], y[case_id]["answerable"]):
            raise ValueError(f"mismatched labels for case {case_id}")
    ids = sorted(k for k in x if x[k]["answerable"])
    if not ids:
        raise ValueError("no answerable tasks")
    gains = [k for k in ids if not x[k]["hit_at_5"] and y[k]["hit_at_5"]]
    regressions = [k for k in ids if x[k]["hit_at_5"] and not y[k]["hit_at_5"]]
    differences = [int(y[i]["hit_at_5"]) - int(x[i]["hit_at_5"]) for i in ids]
    rng = random.Random(seed)
    samples = sorted(statistics.mean(rng.choice(differences) for _ in ids) for _ in range(iterations))
    lo, hi = int(.025 * (iterations - 1)), int(.975 * (iterations - 1))
    return {"baseline": a["variant"], "challenger": b["variant"],
            "dataset_sha256": a["dataset_sha256"], "corpus_sha256": a["corpus_sha256"],
            "paired_n": len(ids), "delta_hit_at_5": round(statistics.mean(differences), 4),
            "bootstrap_95pct_ci": [round(samples[lo], 4), round(samples[hi], 4)],
            "gains": len(gains), "regressions": len(regressions),
            "gain_case_ids": gains, "regression_case_ids": regressions,
            "both_same": differences.count(0),
            "note": "Exploratory paired bootstrap, not evidence of production benefit; small, authored fixture."}
