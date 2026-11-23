"""Fail-closed provenance and claim-span audit for future public benchmarks.

This is a data quality gate, NOT an evaluation result. No corpus is bundled.
"""
from __future__ import annotations

from urllib.parse import urlparse
from ipaddress import ip_address


def _public_url(value: object) -> bool:
    """Syntax-only public HTTPS preflight; not a license or DNS verification."""
    if not isinstance(value, str):
        return False
    try:
        u = urlparse(value)
        host = (u.hostname or "").rstrip(".").lower()
        # Literal private, loopback, link-local and documentation IPs cannot
        # serve as independently verifiable public source/permission URLs.
        try:
            literal = ip_address(host)
        except ValueError:
            literal = None
        return (
            u.scheme == "https" and bool(host) and "." in host
            and host != "localhost" and not host.endswith(".localhost")
            and not host.endswith(".local")
            and (literal is None or literal.is_global)
            and u.port != 0 and not u.username and not u.password
            and not any(ch.isspace() for ch in value)
        )
    except ValueError:
        # urlparse().hostname / .port can raise for malformed IPv6/ports.
        return False


def audit_public_cases(cases: list[dict], documents: dict[str, dict], *, require_holdout: bool = False) -> dict:
    """Validate independent public evidence labels without scoring a model.

    Document schema: id -> {text, source_url, license_url, license_id}.
    Case schema: id, query, answerable, gold_docs, supporting_spans,
    review_status='human_reviewed', reviewer_ids (>=2 distinct).
    supporting_spans: [{doc_id, start, end, quote}], exact offsets into text.
    Unanswerable cases must have no gold docs or supporting spans.
    """
    if not isinstance(cases, list) or not isinstance(documents, dict):
        return {"ready": False, "cases": 0, "documents": 0, "errors": ["invalid_container_types"]}
    errors: list[str] = []
    if not cases:
        errors.append("empty_cases")
    if not documents:
        errors.append("empty_documents")
    for doc_id, doc in documents.items():
        if not isinstance(doc, dict):
            errors.append(f"document:{doc_id}:invalid")
            continue
        if not isinstance(doc.get("text"), str) or not doc["text"].strip():
            errors.append(f"document:{doc_id}:empty_text")
        if not _public_url(doc.get("source_url")):
            errors.append(f"document:{doc_id}:source_url")
        if not _public_url(doc.get("license_url")) or not isinstance(doc.get("license_id"), str) or not doc["license_id"].strip():
            errors.append(f"document:{doc_id}:license_unverified")
    # A declared holdout must not share queries or gold documents with development.
    # Unlabelled legacy synthetic fixtures retain their existing behavior.
    split_mode = any(isinstance(c, dict) and "split" in c for c in cases)
    if require_holdout:
        # A legacy synthetic fixture must never silently qualify as sealed evaluation.
        counts = {label: sum(isinstance(c, dict) and c.get("split") == label for c in cases)
                  for label in ("dev", "holdout")}
        if not counts["dev"] or not counts["holdout"]:
            errors.append("missing_dev_or_holdout_split")
        split_mode = True
    seen_queries: dict[str, str] = {}
    seen_gold_docs: dict[str, str] = {}
    seen_gold_texts: dict[str, str] = {}
    seen_source_urls: dict[str, str] = {}
    seen: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"case:{index}:invalid")
            continue
        cid = case.get("id")
        if not isinstance(cid, str) or not cid.strip() or cid in seen:
            errors.append(f"case:{index}:duplicate_or_empty_id")
            cid = str(index)
        seen.add(cid)
        if not isinstance(case.get("query"), str) or not case["query"].strip():
            errors.append(f"case:{cid}:query")
        reviewers = case.get("reviewer_ids")
        if case.get("review_status") != "human_reviewed" or not isinstance(reviewers, list) or len(reviewers) < 2 or any(not isinstance(r, str) or not r.strip() for r in reviewers) or len({r.strip().casefold() for r in reviewers if isinstance(r, str)}) < 2:
            errors.append(f"case:{cid}:independent_review_missing")
        if split_mode:
            split = case.get("split")
            if split not in ("dev", "holdout"):
                errors.append(f"case:{cid}:invalid_split")
            else:
                query = case.get("query")
                if isinstance(query, str) and query.strip():
                    key = " ".join(query.split()).casefold()
                    if key in seen_queries and seen_queries[key] != split:
                        errors.append(f"case:{cid}:cross_split_query_leakage")
                    seen_queries[key] = split
                gold_candidate = case.get("gold_docs")
                if isinstance(gold_candidate, list):
                    for doc_id in gold_candidate:
                        if isinstance(doc_id, str):
                            if doc_id in seen_gold_docs and seen_gold_docs[doc_id] != split:
                                errors.append(f"case:{cid}:cross_split_gold_doc_leakage")
                            seen_gold_docs[doc_id] = split
                            doc = documents.get(doc_id)
                            if isinstance(doc, dict) and isinstance(doc.get("text"), str):
                                # Different IDs cannot disguise identical gold evidence.
                                text_key = doc["text"]
                                if text_key in seen_gold_texts and seen_gold_texts[text_key] != split:
                                    errors.append(f"case:{cid}:cross_split_gold_text_leakage")
                                seen_gold_texts[text_key] = split
                            if isinstance(doc, dict) and isinstance(doc.get("source_url"), str):
                                # The same source report cannot be independently held out
                                # merely by changing its document ID or extracted text.
                                source = urlparse(doc["source_url"].strip())
                                # URL fragments are client-side anchors, not different source reports.
                                # Hostnames and schemes are case-insensitive; keep path/query intact.
                                source_key = ((source.scheme.lower(), (source.hostname or "").lower().rstrip("."),
                                               source.port or 443, source.path or "/", source.query)
                                              if _public_url(doc["source_url"]) else doc["source_url"].strip())
                                if source_key in seen_source_urls and seen_source_urls[source_key] != split:
                                    errors.append(f"case:{cid}:cross_split_source_url_leakage")
                                seen_source_urls[source_key] = split
        answerable = case.get("answerable")
        gold = case.get("gold_docs")
        spans = case.get("supporting_spans")
        if not isinstance(answerable, bool) or not isinstance(gold, list) or not isinstance(spans, list):
            errors.append(f"case:{cid}:invalid_labels")
            continue
        if any(not isinstance(d, str) or d not in documents for d in gold) or len({d for d in gold if isinstance(d, str)}) != len(gold):
            errors.append(f"case:{cid}:invalid_gold_docs")
        if answerable != bool(gold) or answerable != bool(spans):
            errors.append(f"case:{cid}:answerability_span_mismatch")
        span_docs: set[str] = set()
        for j, span in enumerate(spans):
            if not isinstance(span, dict):
                errors.append(f"case:{cid}:span:{j}:invalid")
                continue
            doc_id = span.get("doc_id")
            start, end, quote = span.get("start"), span.get("end"), span.get("quote")
            doc = documents.get(doc_id) if isinstance(doc_id, str) else None
            if (not isinstance(doc, dict) or not isinstance(doc.get("text"), str) or
                not isinstance(start, int) or isinstance(start, bool) or
                not isinstance(end, int) or isinstance(end, bool) or
                start < 0 or end <= start or end > len(doc["text"]) or
                not isinstance(quote, str) or not quote or doc["text"][start:end] != quote):
                errors.append(f"case:{cid}:span:{j}:offset_or_quote_mismatch")
            else:
                span_docs.add(doc_id)
        if span_docs != {d for d in gold if isinstance(d, str)}:
            errors.append(f"case:{cid}:gold_span_coverage_mismatch")
    return {"ready": not errors, "cases": len(cases), "documents": len(documents), "errors": errors}
