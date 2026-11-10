"""Development-only diagnostic: historical denial versus later measurement.

This is not an independent benchmark. expectedFailure tracks a known B3
false-rejection risk without implying that the bug has been fixed.
"""
import unittest

from traceqa.evidence import evaluate_evidence


QUERY = "What was measured P95 retrieval latency after rank fusion RET-110?"


class MeasurementTemporalRegressionTests(unittest.TestCase):
    @unittest.expectedFailure
    def test_old_missing_measurement_then_new_valid_measurement(self):
        # Current segment-wide 'denied' check rejects even the later observation.
        text = (
            "RET-110 rank fusion: initially no measured P95 latency was recorded. "
            "After instrumentation, measured P95 retrieval latency was 42 ms."
        )
        self.assertTrue(evaluate_evidence(QUERY, text).supported)

    def test_only_unmeasured_target_remains_rejected(self):
        text = (
            "RET-110 rank fusion: no measured P95 latency was recorded. "
            "The proposed P95 SLO target is 42 ms."
        )
        self.assertFalse(evaluate_evidence(QUERY, text).supported)

    def test_only_measured_observation_remains_accepted(self):
        text = "RET-110 rank fusion: measured P95 retrieval latency was 42 ms."
        self.assertTrue(evaluate_evidence(QUERY, text).supported)


if __name__ == "__main__":
    unittest.main()
