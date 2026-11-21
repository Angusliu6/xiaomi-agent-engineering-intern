"""Synthetic public-URL provenance controls; no live URL or license verification."""
import copy
import unittest

from traceqa.public_audit import audit_public_cases


class PublicUrlPreflightTests(unittest.TestCase):
    def setUp(self):
        self.text = "Measured P95 was 42 ms."
        self.documents = {"d1": {
            "text": self.text,
            "source_url": "https://example.org/incident",
            "license_url": "https://example.org/license",
            "license_id": "CC-BY-4.0",
        }}
        self.case = {
            "id": "c1", "query": "What was the measured P95?",
            "answerable": True, "gold_docs": ["d1"],
            "supporting_spans": [{"doc_id": "d1", "start": 0,
                                  "end": len(self.text), "quote": self.text}],
            "review_status": "human_reviewed",
            "reviewer_ids": ["reviewer-a", "reviewer-b"],
        }

    def test_valid_syntactic_public_urls_still_pass(self):
        self.assertTrue(audit_public_cases([self.case], self.documents)["ready"])

    def test_non_public_source_addresses_fail_closed(self):
        for url in (
            "https://10.0.0.1/report",
            "https://192.168.1.20/report",
            "https://169.254.169.254/latest/meta-data",
            "https://127.0.0.1/report",
            "https://localhost./report",
            "https://foo.localhost/report",
            "https://192.0.2.10/report",
            "https://[::1]/report",
        ):
            with self.subTest(url=url):
                docs = copy.deepcopy(self.documents)
                docs["d1"]["source_url"] = url
                result = audit_public_cases([self.case], docs)
                self.assertFalse(result["ready"])
                self.assertTrue(any("source_url" in e for e in result["errors"]))

    def test_non_public_license_and_malformed_url_fail_closed(self):
        for url in ("https://10.0.0.1/license",
                    "https://[::1/license",
                    "https://example.org:invalid/license",
                    "https://example.org:0/license",
                    "https://example.org/license with spaces"):
            with self.subTest(url=url):
                docs = copy.deepcopy(self.documents)
                docs["d1"]["license_url"] = url
                result = audit_public_cases([self.case], docs)
                self.assertFalse(result["ready"])
                self.assertTrue(any("license_unverified" in e for e in result["errors"]))


if __name__ == "__main__":
    unittest.main()
