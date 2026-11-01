"""Gold-ID retrieval evaluation. No LLM judge and no answer correctness claims."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import random
import statistics
from .retrieval import Corpus
from .runtime import Agent, ReadOnlyTools


def load_cases(path: Path) -> list[dict]:
    cases = [json.loads(s) for s in path.read_text(encoding="utf-8").splitlines() if s.strip()]
    ids = [x["id"] for x in cases]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate case ids")
    for c in cases:
        if not isinstance(c.get("gold_docs"), list) or not isinstance(c.get("answerable"), bool):
            raise ValueError("missing gold_docs / answerable")
        if c["answerable"] != bool(c["gold_docs"]):
            raise ValueError("inconsistent answerability labels")
    return cases


def measure(cases: list[dict], corpus: Corpus, *, variant: str = "b0") -> dict:
    if variant not in ("b0", "b1", "b2"):
        raise ValueError("choose b0, b1, or b2")
    rows = []
    for c in cases:
        mode = "bm25" if variant == "b0" else "hybrid"
        if variant == "b2":
            state = Agent(ReadOnlyTools(corpus)).run(c["query"], mode=mode, budget=3)
            predicted = state.retrieved[:5]
            calls = state.step
            elapsed = state.elapsed_ms
            abstained = state.status == "insufficient_evidence"
        else:
            import time
            begin = time.perf_counter()
            predicted = [h.id for h in corpus.search(c["query"], 5, mode)]
            elapsed = round((time.perf_counter() - begin) * 1000, 3)
            calls = 1
            abstained = not predicted  # fixed-search baseline only; absence of hits is a crude abstention proxy
        gold = set(c["gold_docs"])
        first = next((i for i, doc in enumerate(predicted, 1) if doc in gold), 0)
        rows.append({"id": c["id"], "category": c.get("category", "general"),
                     "answerable": c["answerable"], "gold_docs": sorted(gold),
                     "retrieved": predicted, "hit_at_5": bool(first),
                     "reciprocal_rank": 1 / first if first else 0.,
                     "recall_at_5": len(set(predicted) & gold) / len(gold) if gold else None,
                     "correct_abstention": abstained if not gold else None,
                     "calls": calls, "latency_ms": elapsed})
    def mean(key, keep=lambda r: True):
        vals = [r[key] for r in rows if keep(r) and r[key] is not None]
        return round(statistics.mean(vals), 4) if vals else None
    return {"variant": variant, "count": len(rows), "scope": "retrieval_only",
            "metrics": {"hit_at_5_answerable": mean("hit_at_5", lambda r:r["answerable"]),
                        "mrr_answerable": mean("reciprocal_rank", lambda r:r["answerable"]),
                        "recall_at_5_answerable": mean("recall_at_5", lambda r:r["answerable"]),
                        "correct_abstention_unanswerable": mean("correct_abstention", lambda r:not r["answerable"]),
                        "mean_calls": mean("calls"), "mean_latency_ms": mean("latency_ms")},
            "rows": rows}


def paired_compare(a: dict, b: dict, iterations: int = 2000, seed: int = 42) -> dict:
    x, y = {r["id"]:r for r in a["rows"]}, {r["id"]:r for r in b["rows"]}
    if x.keys() != y.keys():
        raise ValueError("different evaluation cases")
    ids = sorted(k for k in x if x[k]["answerable"])
    if not ids:
        raise ValueError("no answerable tasks")
    improvements = [int(y[i]["hit_at_5"]) - int(x[i]["hit_at_5"]) for i in ids]
    rng = random.Random(seed)
    samples = sorted(sum(rng.choice(improvements) for _ in ids) / len(ids) for _ in range(iterations))
    return {"baseline": a["variant"], "challenger": b["variant"],
            "paired_n": len(ids), "delta_hit_at_5": round(statistics.mean(improvements), 4),
            "bootstrap_95pct_ci": [round(samples[int(.025*(iterations-1))],4),round(samples[int(.975*(iterations-1))],4)],
            "gains": improvements.count(1), "regressions": improvements.count(-1),
            "both_same": improvements.count(0), "note": "descriptive bootstrap; small synthetic samples do not establish production gains"}
