"""Synthetic audit controls; not an independent public benchmark."""
import copy
import unittest
from traceqa.public_audit import audit_public_cases

TEXT = "Measured P95 was 42 ms."
DOCS = {"d1": {"text": TEXT, "source_url": "https://example.org/report",
               "license_url": "https://example.org/license", "license_id": "CC-BY-4.0"}}
CASE = {"id": "c1", "query": "What was measured P95?", "answerable": True,
        "gold_docs": ["d1"], "supporting_spans": [
            {"doc_id": "d1", "start": 0, "end": len(TEXT), "quote": TEXT}],
        "review_status": "human_reviewed", "reviewer_ids": ["reviewer-a", "reviewer-b"]}


class PublicAuditTests(unittest.TestCase):
    def test_positive_and_abstention_controls(self):
        self.assertTrue(audit_public_cases([CASE], DOCS)["ready"])
        no_answer = dict(CASE, id="c2", answerable=False, gold_docs=[], supporting_spans=[])
        self.assertTrue(audit_public_cases([no_answer], DOCS)["ready"])

    def test_rejects_span_mismatch(self):
        c = copy.deepcopy(CASE)
        c["supporting_spans"][0]["start"] = 1
        self.assertFalse(audit_public_cases([c], DOCS)["ready"])

    def test_rejects_missing_license_and_single_reviewer(self):
        d = copy.deepcopy(DOCS)
        d["d1"]["license_url"] = ""
        c = dict(CASE, reviewer_ids=["reviewer-a", "reviewer-a"])
        result = audit_public_cases([c], d)
        self.assertFalse(result["ready"])
        self.assertTrue(any("license_unverified" in e for e in result["errors"]))
        self.assertTrue(any("independent_review_missing" in e for e in result["errors"]))

    def test_reviewer_identity_aliases_are_not_independent(self):
        for reviewers in (["reviewer-a", " Reviewer-A "],
                          ["REVIEWER-A", "reviewer-a"]):
            with self.subTest(reviewers=reviewers):
                c = dict(CASE, reviewer_ids=reviewers)
                result = audit_public_cases([c], DOCS)
                self.assertFalse(result["ready"])
                self.assertIn("case:c1:independent_review_missing", result["errors"])

    def test_distinct_reviewer_ids_remain_eligible(self):
        c = dict(CASE, reviewer_ids=[" reviewer-a ", "reviewer-b"])
        self.assertTrue(audit_public_cases([c], DOCS)["ready"])

    def test_sealed_holdout_rejects_cross_split_query_and_document(self):
        dev = dict(CASE, id="dev", split="dev")
        holdout = dict(CASE, id="holdout", split="holdout")
        result = audit_public_cases([dev, holdout], DOCS)
        self.assertFalse(result["ready"])
        self.assertIn("case:holdout:cross_split_query_leakage", result["errors"])
        self.assertIn("case:holdout:cross_split_gold_doc_leakage", result["errors"])

    def test_sealed_holdout_accepts_disjoint_cases(self):
        dev = dict(CASE, id="dev", split="dev")
        other_text = "Measured P99 was 88 ms."
        docs = dict(DOCS, d2=dict(DOCS["d1"], text=other_text,
                                      source_url="https://example.org/independent-report"))
        holdout = dict(CASE, id="holdout", split="holdout",
                       query="What was measured P99?", gold_docs=["d2"],
                       supporting_spans=[{"doc_id": "d2", "start": 0,
                                          "end": len(other_text), "quote": other_text}])
        self.assertTrue(audit_public_cases([dev, holdout], docs)["ready"])

    def test_sealed_holdout_rejects_same_text_under_different_doc_ids(self):
        dev = dict(CASE, id="dev", split="dev")
        docs = dict(DOCS, d2=dict(DOCS["d1"]))
        holdout = dict(CASE, id="holdout", split="holdout",
                       query="Report the observed retrieval latency.",
                       gold_docs=["d2"],
                       supporting_spans=[{"doc_id": "d2", "start": 0,
                                          "end": len(TEXT), "quote": TEXT}])
        result = audit_public_cases([dev, holdout], docs)
        self.assertFalse(result["ready"])
        self.assertIn("case:holdout:cross_split_gold_text_leakage", result["errors"])

    def test_sealed_holdout_rejects_same_source_with_different_text(self):
        dev = dict(CASE, id="dev", split="dev")
        other_text = "Observed timeout count was 3."
        docs = dict(DOCS, d2=dict(DOCS["d1"], text=other_text))
        holdout = dict(CASE, id="holdout", split="holdout",
                       query="How many timeouts were observed?",
                       gold_docs=["d2"],
                       supporting_spans=[{"doc_id": "d2", "start": 0,
                                          "end": len(other_text), "quote": other_text}])
        result = audit_public_cases([dev, holdout], docs)
        self.assertFalse(result["ready"])
        self.assertIn("case:holdout:cross_split_source_url_leakage", result["errors"])
        self.assertNotIn("case:holdout:cross_split_gold_text_leakage", result["errors"])

    def test_sealed_holdout_rejects_source_url_fragment_and_host_alias(self):
        dev = dict(CASE, id="dev", split="dev")
        other_text = "Observed timeout count was 3."
        docs = copy.deepcopy(DOCS)
        docs["d1"]["source_url"] = "https://EXAMPLE.org/report#section-a"
        docs["d2"] = dict(DOCS["d1"], text=other_text,
                          source_url="https://example.org/report#section-b")
        holdout = dict(CASE, id="holdout", split="holdout",
                       query="How many timeouts were observed?",
                       gold_docs=["d2"],
                       supporting_spans=[{"doc_id": "d2", "start": 0,
                                          "end": len(other_text), "quote": other_text}])
        result = audit_public_cases([dev, holdout], docs, require_holdout=True)
        self.assertFalse(result["ready"])
        self.assertIn("case:holdout:cross_split_source_url_leakage", result["errors"])

    def test_invalid_source_url_port_fails_closed_without_exception(self):
        docs = copy.deepcopy(DOCS)
        docs["d1"]["source_url"] = "https://example.org:not-a-port/report"
        dev = dict(CASE, id="dev", split="dev")
        holdout = dict(CASE, id="holdout", split="holdout")
        result = audit_public_cases([dev, holdout], docs, require_holdout=True)
        self.assertFalse(result["ready"])
        self.assertIn("document:d1:source_url", result["errors"])

    def test_sealed_holdout_same_text_within_dev_is_allowed(self):
        dev1 = dict(CASE, id="dev1", split="dev")
        docs = dict(DOCS, d2=dict(DOCS["d1"]))
        dev2 = dict(CASE, id="dev2", split="dev",
                    query="Report the observed retrieval latency.",
                    gold_docs=["d2"],
                    supporting_spans=[{"doc_id": "d2", "start": 0,
                                       "end": len(TEXT), "quote": TEXT}])
        self.assertTrue(audit_public_cases([dev1, dev2], docs)["ready"])

    def test_sealed_holdout_requires_complete_split_labels(self):
        dev = dict(CASE, id="dev", split="dev")
        holdout = dict(CASE, id="holdout", query="Different question?")
        result = audit_public_cases([dev, holdout], DOCS)
        self.assertIn("case:holdout:invalid_split", result["errors"])

    def test_sealed_mode_rejects_legacy_unpartitioned_fixture(self):
        self.assertTrue(audit_public_cases([CASE], DOCS)["ready"])
        result = audit_public_cases([CASE], DOCS, require_holdout=True)
        self.assertFalse(result["ready"])
        self.assertIn("missing_dev_or_holdout_split", result["errors"])
        self.assertIn("case:c1:invalid_split", result["errors"])

    def test_sealed_mode_rejects_only_dev_or_only_holdout(self):
        for split in ("dev", "holdout"):
            with self.subTest(split=split):
                case = dict(CASE, split=split)
                result = audit_public_cases([case], DOCS, require_holdout=True)
                self.assertFalse(result["ready"])
                self.assertIn("missing_dev_or_holdout_split", result["errors"])

    def test_sealed_mode_accepts_disjoint_dev_and_holdout(self):
        dev = dict(CASE, id="dev", split="dev")
        text = "Observed timeout count was 3."
        docs = dict(DOCS, d2=dict(DOCS["d1"], text=text,
                                   source_url="https://example.org/other-report"))
        holdout = dict(CASE, id="holdout", split="holdout",
                       query="How many timeouts?", gold_docs=["d2"],
                       supporting_spans=[{"doc_id": "d2", "start": 0,
                                          "end": len(text), "quote": text}])
        self.assertTrue(audit_public_cases([dev, holdout], docs,
                                            require_holdout=True)["ready"])

    def test_rejects_gold_without_support(self):
        c = dict(CASE, supporting_spans=[])
        self.assertFalse(audit_public_cases([c], DOCS)["ready"])

    def test_rejects_duplicate_ids(self):
        self.assertFalse(audit_public_cases([CASE, CASE], DOCS)["ready"])


if __name__ == "__main__":
    unittest.main()
