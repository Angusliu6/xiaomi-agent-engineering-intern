# TRACEQA-20261109-NEGATED-MEASUREMENT-004

Status: Draft PR #6 only; CI and paired fixture results must be verified at final head. Champion main unchanged.

## Falsifiable hypothesis
An explicit denial of a measured P95 in the requested RET incident must override a nearby P95 numeric SLO target. The previous incident-scoped type-presence rule could accept a target value as an observed measurement.

Negative control: "RET-110 ... no measured P95 retrieval latency was recorded. The proposed SLO target for P95 retrieval latency is 42 ms." Expected reject.
Positive control: "RET-110 ... measured P95 retrieval latency was 42 ms." Expected accept.

## Minimal change and risk
Only the optional B3 incident-scoped measurement gate was changed: reject an incident segment that explicitly negates a P95/P99 measurement, even when a matching numeric value occurs. Two paired unit controls were added. This conservative pattern can false-reject mixed prose (a denied historical measurement followed by a genuine newer measurement in the same incident segment), and cannot resolve target/observed values in general. It is NOT claim-level entailment.

## Reproducibility and promotion guard
Start Challenger: be4e64096e54fc093ceba48810fa2e21593760fc.
Code: acae9d28f7c93d6a986bda1af317558a47ac724d.
Tests: 0b8131d18475674b978ea0575eacaf578d3f65f2.
Run unittest on Python 3.11/3.12, B2/B3 fixed stress evaluation and compare, inspect final-head CI. Authored fixture is seen development data, not independent holdout. No measured generalization gain or regression can be claimed without independent public corpus and human-reviewed supporting spans. Keep B2 Champion and PR Draft.

Cost: no paid API or GPU usage; GitHub Actions free/plan allocation not independently priced.
