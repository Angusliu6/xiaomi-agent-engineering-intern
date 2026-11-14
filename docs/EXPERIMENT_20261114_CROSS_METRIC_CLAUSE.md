# TRACEQA-20261114-CROSS-METRIC-CLAUSE-009

Status: development-only B3 Draft PR; B2 Champion unchanged.

## Baseline and falsifiable hypothesis
Start Challenger: `62b55f94ba2784c29e34f881da91b36afb26c5ab`.
The P95 evidence gate previously checked whether a whole sentence contained any `measured` or `observed` token plus a P95 numeric pattern. Thus a measured throughput clause could license a neighboring P95 SLO target in the same sentence. Hypothesis: requiring the observation marker and P95 value within the same comma/semicolon-delimited clause rejects this cross-metric false support without rejecting a separate affirmative P95 clause.

## Intervention and controls
Code: `75e4869e50584fed08f8b38da7a7123230ee2fd0`.
Tests: `5fc22ac12775abb2ed692e525e18b26dd1bd2927`.
Two negatives: measured throughput followed by P95 target, separated by semicolon or comma. One positive: measured throughput followed by explicitly measured P95 in another clause. Existing incident scoping, target-only, post-value denial and historical-then-later observation tests remain.

## Verification and falsification
Local clone and unittest BLOCKED: DNS could not resolve github.com. CI for new head must be checked; test submission is not test success. No new fixed-development paired metrics, no public independent evaluation, no measured gain or regression. Fail if any new or old unit test fails, or if fixed paired B2/B3 results show unexplained regression.

## Scope and risks
The clause split is heuristic: commas within numbers, tables, nested clauses and implicit references may cause false refusals; no claim entailment or supporting span extraction. Existing authored development fixtures are not blind holdout. No paid API/GPU. Keep Draft PR and B2 Champion; independent licensed public source review with human gold spans is the next P0.
