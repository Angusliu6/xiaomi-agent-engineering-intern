"""Pre-registered checks: typed value presence is a weak proxy, not entailment."""
import unittest
from pathlib import Path

from traceqa.evidence import evaluate_evidence, requested_fact_type
from traceqa.retrieval import Corpus
from traceqa.runtime import Agent, ReadOnlyTools
from traceqa.evaluation import measure, load_cases, paired_compare

ROOT = Path(__file__).resolve().parents[1]


class TypedEvidenceGateTests(unittest.TestCase):
    def test_all_stress_requests_are_classified_as_non_explanatory(self):
        cases = load_cases(ROOT / "data/stress_hard_negative.jsonl")
        for case in cases[:10]:
            with self.subTest(case=case["id"]):
                self.assertNotEqual(requested_fact_type(case["query"]), "explanation")

    def test_typed_value_present_does_not_mean_entailed(self):
        examples = [
            ("What was measured P95 retrieval latency after rank fusion RET-110?",
             "Ticket RET-110. Measured P95 retrieval latency was 42 ms after rank fusion."),
            ("How many customers were impacted by the async incident?",
             "The async incident impacted 350 customers."),
            ("Who approved the MCP production override?",
             "MCP production override approved by Ada Lovelace."),
            ("What exact UTC timestamp was the queuepool incident fixed?",
             "QueuePool incident fixed at 2026-11-04T18:03:00Z UTC."),
            ("What exact context_window value was configured?",
             "context_window: 8192 was configured correctly"),
            ("What exact dollar amount was lost in duplicated payments?",
             "Duplicated payments caused a loss of $18,300 dollars."),
        ]
        for query, text in examples:
            with self.subTest(query=query):
                decision = evaluate_evidence(query, text)
                self.assertTrue(decision.supported, decision)

    def test_topic_only_is_rejected_for_specific_question(self):
        queries = [
            ("How many customers were impacted by the async incident?",
             "The async incident stalled the event loop. No customer impact data was provided."),
            ("What was measured P95 retrieval latency after rank fusion RET-110?",
             "RET-110 uses rank fusion; no measured P95 retrieval latency figures are available."),
            ("Who approved the MCP production override?",
             "MCP production override approval is pending, approver not recorded."),
            ("What exact context_window value was configured?",
             "The configured context_window value was not recorded."),
        ]
        for query, text in queries:
            with self.subTest(query=query):
                self.assertFalse(evaluate_evidence(query, text).supported)

    def test_credentials_are_not_exposed_as_evidence(self):
        d = evaluate_evidence("What is the actual API_KEY token?",
                              "An example contains an API_KEY token placeholder.")
        self.assertEqual(d.reason, "credential_disclosure_not_supported")

    def test_b3_pressure_test_and_cost(self):
        corpus = Corpus.from_dir(ROOT / "data/corpus")
        cases = load_cases(ROOT / "data/stress_hard_negative.jsonl")
        baseline = measure(cases, corpus, variant="b2")
        challenger = measure(cases, corpus, variant="b3")
        # This is development-set *diagnostic* only, never a blind holdout claim.
        self.assertEqual(baseline["metrics"]["correct_abstention_unanswerable"], 0.4)
        self.assertEqual(challenger["metrics"]["correct_abstention_unanswerable"], 1.0)
        self.assertEqual(challenger["metrics"]["candidate_acceptance_answerable"],
                         baseline["metrics"]["candidate_acceptance_answerable"])
        self.assertGreater(challenger["metrics"]["mean_calls"], baseline["metrics"]["mean_calls"])
        paired = paired_compare(baseline, challenger, iterations=300)
        self.assertEqual(len(paired["paired_abstention"]["gain_case_ids"]), 6)
        self.assertEqual(paired["paired_abstention"]["regression_case_ids"], [])

    def test_trace_has_explicit_gate_decision(self):
        corpus = Corpus.from_dir(ROOT / "data/corpus")
        state = Agent(ReadOnlyTools(corpus), evidence_policy="typed").run(
            "What was measured P95 retrieval latency after RRF rank fusion RET-110?")
        self.assertEqual(state.status, "insufficient_evidence")
        self.assertEqual(state.outcome_reason, "budget_exhausted_without_support")
        gate_events = [e for e in state.events if e.kind == "evidence_gate"]
        self.assertTrue(gate_events)
        self.assertEqual(gate_events[0].payload["intent"], "measurement")
        self.assertIn("rejections", gate_events[0].payload)

    def test_tool_failure_not_mislabeled_as_evidence_absence(self):
        corpus = Corpus.from_dir(ROOT / "data/corpus")
        state = Agent(ReadOnlyTools(corpus, fail_first=True)).run("MCP timeout", budget=1)
        self.assertEqual(state.status, "tool_failed")
        self.assertEqual(state.outcome_reason, "tool_error_without_successful_search")

    def test_checkpoint_policy_cannot_change_on_resume(self):
        import tempfile
        from traceqa.runtime import CheckpointStore
        with tempfile.TemporaryDirectory() as directory:
            corpus = Corpus.from_dir(ROOT / "data/corpus")
            store = CheckpointStore(Path(directory) / "checkpoints.sqlite")
            run = Agent(ReadOnlyTools(corpus), store=store, evidence_policy="typed").run(
                "RRF fusion")
            with self.assertRaisesRegex(ValueError, "policy mismatch"):
                Agent(ReadOnlyTools(corpus), store=store, evidence_policy="lexical").run(
                    "RRF fusion", resume=run.run_id)

    def test_bad_policy_is_rejected(self):
        corpus = Corpus.from_dir(ROOT / "data/corpus")
        with self.assertRaises(ValueError):
            Agent(ReadOnlyTools(corpus), evidence_policy="magic")


if __name__ == "__main__":
    unittest.main()
