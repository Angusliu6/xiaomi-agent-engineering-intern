"""Conservative typed-fact evidence checks for *offline research*.

Separates topical similarity from superficial answer-type plausibility.  A
matching type is NOT entailment. This is neither a calibrated confidence model
nor a production safety policy; independent claim-support labels are required.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from .retrieval import tokenize


@dataclass(frozen=True)
class EvidenceDecision:
    supported: bool
    intent: str
    reason: str


STOPWORDS = frozenset({
    "what", "when", "where", "the", "from", "does", "with", "have",
    "about", "should", "could", "would", "after", "into", "your",
    "this", "that", "were", "there", "which", "many", "some", "other",
})


def lexical_relevance(query: str, text: str) -> bool:
    q = {t for t in tokenize(query) if len(t) >= 4 and t not in STOPWORDS}
    if not q:
        return False
    matching = q & set(tokenize(text))
    required = 1 if len(q) <= 2 else max(2, (len(q) + 2) // 3)
    return len(matching) >= required


def requested_fact_type(query: str) -> str:
    q = query.lower()
    if re.search(r"\b(api_key|password|access[_ -]?token|private[_ -]?key|secret[_ -]?token)\b", q) and re.search(r"\b(actual|real|exact|reveal|print|give|show|value|token|credential)\b", q):
        return "secret"
    if re.search(r"\b(?:dollar amount|how much money|payment amount|amount of money|\$\s*amount)\b", q):
        return "money"
    if re.search(r"\b(?:exact\s+utc|utc\s+timestamp|exact\s+(?:time|timestamp|date)|what\s+(?:time|date)\s+exactly)\b", q):
        return "timestamp"
    if re.search(r"\b(?:who\s+(?:approved|verified|signed)|which\s+(?:human|annotator|reviewer|person)|approver\s+name|give\s+the\s+approver\s+name|sign\s+off)\b", q):
        return "person"
    if re.search(r"\bhow\s+many\b", q):
        return "count"
    if re.search(r"\b(?:exact\s+\w+\s+value|what\s+exact\s+\w+\s+value|value\s+was\s+configured)\b", q):
        return "config"
    if re.search(r"\b(?:measured|actual|observed)\b", q) and re.search(r"\b(?:p95|p99|latency|throughput|gain|speedup|performance)\b", q):
        return "measurement"
    return "explanation"


def _has_typed_fact(query: str, text: str, intent: str) -> bool:
    t = text.lower()
    if intent == "money":
        return bool(re.search(r"(?:\$\s*\d[\d,]*(?:\.\d+)?|\b\d[\d,]*(?:\.\d+)?\s*(?:usd|dollars)\b)", t))
    if intent == "timestamp":
        return bool(re.search(r"\b\d{4}-\d{2}-\d{2}[t\s]\d{2}:\d{2}(?::\d{2})?(?:z|\s*utc|[+-]\d{2}:?\d{2})\b", t))
    if intent == "person":
        return bool(re.search(r"\b(?:approved|signed\s+off|verified|reviewed|annotated)\s+by\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}\b", text))
    if intent == "count":
        m = re.search(r"\bhow\s+many\s+([a-z]+)", query.lower())
        if not m:
            return False
        unit = m.group(1).rstrip("s")
        return bool(re.search(r"\b\d[\d,]*\s+" + re.escape(unit) + r"s?\b", t))
    if intent == "config":
        keys = [k for k in tokenize(query) if "_" in k and k != "api_key"]
        return any(re.search(r"\b" + re.escape(k) + r"\s*(?:=|:|was\s+set\s+to)\s*\d+(?:\.\d+)?\b", t) for k in keys)
    if intent == "measurement":
        if "p95" in query.lower() or "p99" in query.lower():
            percentile = "p95" if "p95" in query.lower() else "p99"
            return bool(re.search(r"\b" + percentile + r"\b.{0,60}?\d+(?:\.\d+)?\s*(?:ms|seconds?|s)\b", t))
        if "throughput" in query.lower():
            return bool(re.search(r"\b\d+(?:\.\d+)?\s*(?:tokens?/s|requests?/s|req/s|qps|%)\b", t))
        if "gain" in query.lower() or "speedup" in query.lower():
            return bool(re.search(r"\b\d+(?:\.\d+)?\s*(?:%|x|times)\b", t))
        return bool(re.search(r"\b\d+(?:\.\d+)?\s*(?:ms|seconds?|tokens?/s|req/s|%)\b", t))
    return False


def evaluate_evidence(query: str, document_text: str) -> EvidenceDecision:
    intent = requested_fact_type(query)
    if intent == "secret":
        return EvidenceDecision(False, intent, "credential_disclosure_not_supported")
    if not lexical_relevance(query, document_text):
        return EvidenceDecision(False, intent, "insufficient_topical_overlap")
    if intent == "explanation":
        return EvidenceDecision(True, intent, "lexical_candidate_only")
    if _has_typed_fact(query, document_text, intent):
        return EvidenceDecision(True, intent, "typed_value_present_not_entailed")
    return EvidenceDecision(False, intent, "requested_fact_type_absent")
