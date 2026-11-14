# TRACEQA-20261112-TARGET-ONLY-007

Status: B3 Draft PR research patch; **not Champion promotion**.

## Hypothesis
For an explicit RET incident measured-P95 question, a bare P95 number or SLO target without a negation sentence is not sufficient candidate evidence. An explicitly measured P95 observation in a separate sentence should remain eligible.

## Intervention
Starting Challenger `af6ee2c3b1a95bb061f3f5bd6d458817cd55119d`. Evidence patch `7fabd2026340a6d14a58229f17de60cfd8080699`; paired regression tests `f3af8b6199502b0b52e296dca46b23a4b9ce562d`. Scope limited to optional B3, explicit single-RET measured-performance questions. The default B2 policy remains unchanged.

## Controls and falsification
Negative: target-only P95 42 ms with no explicit denial. Negative: proposed P95 42 ms without observation. Positive: separate target 20 ms and measured P95 42 ms. Retain earlier temporal denial, other-incident, and ambiguous-sentence regression controls. Fail the hypothesis if any new test fails or the frozen B2/B3 development comparison regresses without explanation.

## Research quality and limitations
All new cases are authored development diagnostics, not independent holdout. This sentence-level heuristic can still fail on mixed target/measurement sentences, punctuation, table layouts, implicit observations, or attribution. CI success is not evidence of independent claim entailment. Need licensed public incident documents and human-reviewed supporting spans, with frozen holdout and error analysis before promotion. No paid API or GPU spend. Keep main/B2 Champion unchanged.
