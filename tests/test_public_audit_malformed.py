"""Adversarial malformed-input controls for public benchmark preflight."""
import copy
import unittest

from traceqa.public_audit import audit_public_cases
from test_public_audit import CASE, DOCS


class PublicAuditMalformedTests(unittest.TestCase):
    def test_invalid_top_level_containers(self):
        for cases, docs in [(None, DOCS), ([CASE], None), ({}, DOCS)]:
            with self.subTest(cases=type(cases).__name__, docs=type(docs).__name__):
                result = audit_public_cases(cases, docs)
                self.assertFalse(result["ready"])
                self.assertIn("invalid_container_types", result["errors"])

    def test_unhashable_gold_doc_rejected_without_exception(self):
        case = copy.deepcopy(CASE)
        case["gold_docs"] = [["d1"]]
        result = audit_public_cases([case], DOCS)
        self.assertFalse(result["ready"])
        self.assertIn("case:c1:invalid_gold_docs", result["errors"])

    def test_unhashable_span_doc_id_rejected_without_exception(self):
        case = copy.deepcopy(CASE)
        case["supporting_spans"][0]["doc_id"] = ["d1"]
        result = audit_public_cases([case], DOCS)
        self.assertFalse(result["ready"])
        self.assertTrue(any("offset_or_quote_mismatch" in e for e in result["errors"]))

    def test_unhashable_reviewer_rejected_without_exception(self):
        case = copy.deepcopy(CASE)
        case["reviewer_ids"] = ["reviewer-a", ["reviewer-b"]]
        result = audit_public_cases([case], DOCS)
        self.assertFalse(result["ready"])
        self.assertIn("case:c1:independent_review_missing", result["errors"])

    def test_valid_controls_still_pass(self):
        self.assertTrue(audit_public_cases([CASE], DOCS)["ready"])
        abstention = dict(CASE, id="c2", answerable=False, gold_docs=[], supporting_spans=[])
        self.assertTrue(audit_public_cases([abstention], DOCS)["ready"])
