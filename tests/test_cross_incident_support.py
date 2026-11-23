"""Falsifiable cross-incident leakage diagnostic; not an independent benchmark."""
import unittest
from traceqa.evidence import evaluate_evidence


class CrossIncidentSupportTests(unittest.TestCase):
    def test_same_incident_positive_control(self):
        query = "What was measured P95 retrieval latency after rank fusion RET-110?"
        text = "RET-110 rank fusion incident. Measured P95 retrieval latency was 42 ms."
        self.assertTrue(evaluate_evidence(query, text).supported)

    def test_other_incident_measurement_must_not_support_requested_incident(self):
        # Regression: another incident's numeric value must not be accepted.
        query = "What was measured P95 retrieval latency after rank fusion RET-110?"
        text = (
            "RET-110 rank fusion incident: no measured P95 latency was recorded. "
            "RET-999 rank fusion incident: measured P95 retrieval latency was 42 ms."
        )
        self.assertFalse(evaluate_evidence(query, text).supported)

    def test_other_incident_precedes_target_without_measurement(self):
        query = "What was measured P95 retrieval latency after rank fusion RET-110?"
        text = ("RET-999 rank fusion incident: measured P95 retrieval latency was 42 ms. "
                "RET-110 rank fusion incident: no measured P95 latency was recorded.")
        self.assertFalse(evaluate_evidence(query, text).supported)

    def test_explicitly_unmeasured_p95_not_rescued_by_slo_target(self):
        query = "What was measured P95 retrieval latency after rank fusion RET-110?"
        text = (
            "RET-110 rank fusion: no measured P95 retrieval latency was recorded. "
            "The proposed SLO target for P95 retrieval latency is 42 ms."
        )
        self.assertFalse(evaluate_evidence(query, text).supported)

    def test_positive_measured_p95_remains_accepted(self):
        query = "What was measured P95 retrieval latency after rank fusion RET-110?"
        text = "RET-110 rank fusion: measured P95 retrieval latency was 42 ms."
        self.assertTrue(evaluate_evidence(query, text).supported)

    def test_requested_incident_missing_entirely(self):
        query = "What was measured P95 retrieval latency after rank fusion RET-110?"
        text = "RET-999 rank fusion incident: measured P95 retrieval latency was 42 ms."
        self.assertFalse(evaluate_evidence(query, text).supported)


if __name__ == "__main__":
    unittest.main()
