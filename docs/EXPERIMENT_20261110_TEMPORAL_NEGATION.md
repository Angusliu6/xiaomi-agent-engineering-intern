# TRACEQA-20261110-TEMPORAL-NEGATION-005

Status: diagnostic submitted on Draft PR #6; **not a production fix**. Champion main unchanged.

## Falsifiable hypothesis
B3's segment-wide denial regex rejects a valid *later* measured P95 when the same RET incident segment also mentions an *earlier* absence of measurements. A temporal/claim-span-aware verifier should accept a later explicit observation, while rejecting a document containing only an unmeasured SLO target.

## Fixed development controls
- Negative: RET-110 has no measured P95, only a 42 ms proposed SLO target => reject.
- Positive: RET-110 measured P95 latency 42 ms => accept.
- Mixed temporal: initially no measured P95, after instrumentation measured P95 latency 42 ms => **accept** (currently expectedFailure).

New file: `tests/test_measurement_temporal_regression.py`. The expectedFailure explicitly tracks a known gap; a green CI does **not** mean it is solved. Before changing production logic, distinguish historical denial, target and observed claim spans, add conflicting and cross-incident negatives, and run fixed B2/B3 paired evaluation. Do not remove expectedFailure until a genuine fix passes.

## Evidence and limits
Previous head `7a74e950290ffaf02864bba107786c31cbb3a2ba`: Actions run 42558234250 completed success (Python 3.11, 3.12, deck; stress B2/B3 commands). This confirms execution, not independent validity. This run's test commit: `53aa2d2fea48c4881d57f70ff4bfa151924b7702`. Final-head CI is not yet established in this report.

No independent licensed public corpus, human-reviewed supporting spans, or new quantitative generalization evidence. No paid API or GPU use. Keep Draft PR and B2 Champion.
