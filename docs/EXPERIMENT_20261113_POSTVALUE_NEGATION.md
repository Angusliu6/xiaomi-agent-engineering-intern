# TRACEQA-20261113-POSTVALUE-NEGATION-008

Status: B3 Draft PR only; B2 Champion unchanged.

## Baseline and CI
Start: `0202005ef3be27d432b82b4c275b76db824f960e`.
Prior Actions run 43150268183: Python 3.11, 3.12, and deck jobs succeeded, including fixed authored development evaluation commands. These are command-success results, not extracted paired task metrics or independent evaluation.

## Falsifiable hypothesis
A sentence asserting "measured P95 ... 42 ms was not observed" must not count as an observed P95 measurement, while a separate later affirmative measurement must remain eligible. Previously the gate rejected pre-value negation but could accept post-value "not observed".

## Intervention and controls
Evidence change: `0b0343f6f375b9b7ff65f792b3698df99a382c59`.
Test change: `cb5e36d115d5a829c6479771babe13f3e49ccd6a`.
New negatives: "measured P95 ... was not observed"; "P95 ... was not measured".
New positive: historical "not observed" followed by separate measured 38 ms.
Prior same-incident, cross-incident, target-only and temporal controls remain.
Failure criterion: any new or existing test fails, or paired fixed-development regression is unexplained.

## Validity and boundaries
These are authored development diagnostics, NOT blind holdout or independent public data. The regex is limited to explicit single-RET measured P95/P99 questions, and does not prove entailment or extract supporting spans. Sentence boundaries, negation scope, multiple measurements and public-document provenance remain open. No paid API/GPU authorized. Do not merge or promote Champion.

## Verification
Local clone unavailable (DNS resolution failure). New head CI must be checked independently; do not infer success from prior run. Fixed dataset metrics and independent public evaluation not measured this run.
