"""Falsifiable cross-incident leakage diagnostic; not an independent benchmark."""
import unittest
from traceqa.evidence import evaluate_evidence


class CrossIncidentSupportTests(unittest.TestCase):
    def test_same_incident_positive_control(self):
        query = "What was measured P95 retrieval latency after rank fusion RET-110?"
        text = "RET-110 rank fusion incident. Measured P95 retrieval latency was 42 ms."
        self.assertTrue(evaluate_evidence(query, text).supported)

    @unittest.expectedFailure
    def test_other_incident_measurement_must_not_support_requested_incident(self):
        # Known B3 limitation: matching a numeric type is not claim entailment.
        # Removing expectedFailure requires a validated fix and paired regression.
        query = "What was measured P95 retrieval latency after rank fusion RET-110?"
        text = (
            "RET-110 rank fusion incident: no measured P95 latency was recorded. "
            "RET-999 rank fusion incident: measured P95 retrieval latency was 42 ms."
        )
        self.assertFalse(evaluate_evidence(query, text).supported)


if __name__ == "__main__":
    unittest.main()
