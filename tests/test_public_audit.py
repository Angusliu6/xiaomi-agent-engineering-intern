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

    def test_rejects_gold_without_support(self):
        c = dict(CASE, supporting_spans=[])
        self.assertFalse(audit_public_cases([c], DOCS)["ready"])

    def test_rejects_duplicate_ids(self):
        self.assertFalse(audit_public_cases([CASE, CASE], DOCS)["ready"])


if __name__ == "__main__":
    unittest.main()
