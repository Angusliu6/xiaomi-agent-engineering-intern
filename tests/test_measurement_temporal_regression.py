"""Development-only diagnostic: historical denial versus later measurement.

This is not an independent benchmark. It exercises a narrow B3 fix,
not general claim entailment.
"""
import unittest

from traceqa.evidence import evaluate_evidence


QUERY = "What was measured P95 retrieval latency after rank fusion RET-110?"


class MeasurementTemporalRegressionTests(unittest.TestCase):
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

    def test_target_without_explicit_denial_is_not_observation(self):
        text = "RET-110 rank fusion: the P95 latency SLO target is 42 ms."
        self.assertFalse(evaluate_evidence(QUERY, text).supported)

    def test_unqualified_p95_number_is_not_observation(self):
        text = "RET-110 rank fusion: P95 retrieval latency 42 ms was proposed."
        self.assertFalse(evaluate_evidence(QUERY, text).supported)

    def test_separate_target_and_observation_remain_accepted(self):
        text = (
            "RET-110 rank fusion: P95 SLO target was 20 ms. "
            "Measured P95 retrieval latency was 42 ms."
        )
        self.assertTrue(evaluate_evidence(QUERY, text).supported)

    def test_explicit_post_value_not_observed_is_rejected(self):
        text = "RET-110 rank fusion: measured P95 retrieval latency 42 ms was not observed."
        self.assertFalse(evaluate_evidence(QUERY, text).supported)

    def test_explicit_post_value_not_measured_is_rejected(self):
        text = "RET-110 rank fusion: P95 retrieval latency 42 ms was not measured."
        self.assertFalse(evaluate_evidence(QUERY, text).supported)

    def test_post_value_negation_then_later_observation_is_accepted(self):
        text = (
            "RET-110 rank fusion: P95 retrieval latency 42 ms was not observed. "
            "After instrumentation, measured P95 retrieval latency was 38 ms."
        )
        self.assertTrue(evaluate_evidence(QUERY, text).supported)

    def test_only_measured_observation_remains_accepted(self):
        text = "RET-110 rank fusion: measured P95 retrieval latency was 42 ms."
        self.assertTrue(evaluate_evidence(QUERY, text).supported)


    def test_historical_denial_then_only_target_still_rejected(self):
        text = (
            "RET-110 rank fusion: initially no measured P95 latency was recorded. "
            "After instrumentation, proposed P95 SLO target was 42 ms."
        )
        self.assertFalse(evaluate_evidence(QUERY, text).supported)

    def test_other_incident_later_observation_still_rejected(self):
        text = (
            "RET-110 rank fusion: no measured P95 latency was recorded. "
            "RET-999 rank fusion: measured P95 retrieval latency was 42 ms."
        )
        self.assertFalse(evaluate_evidence(QUERY, text).supported)

    def test_same_sentence_ambiguous_denial_remains_rejected(self):
        text = (
            "RET-110 rank fusion: no measured P95 latency was recorded, "
            "although measured P95 retrieval latency 42 ms was proposed."
        )
        self.assertFalse(evaluate_evidence(QUERY, text).supported)


if __name__ == "__main__":
    unittest.main()
