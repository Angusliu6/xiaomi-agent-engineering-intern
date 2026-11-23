# TRACEQA-20261111-TEMPORAL-OBSERVATION-006

Status: narrow B3 Challenger patch submitted to Draft PR #6; **not Champion promotion**.

## Falsifiable hypothesis
When a RET incident section states an earlier absence of P95 measurements and then explicitly reports a later measured P95 in a separate sentence, B3 should accept the later observation. A section containing only an SLO target, a cross-incident measurement, or an ambiguous single-sentence denial should remain rejected.

## Intervention and controls
Starting head: `8d023b9a7b810cab72a8d1a8ec9d92cdf8245195`.
Patch commits: `43d525be0110c77ef77eda7d9f8a62197c49397d`, `23856c243dabb1bfdb0cfdca8c50ee8836d25b18`.
Test commit: `097aae2193a7ee0b0ff8c52042c88dc57376721b`.
Changed only optional B3 measurement evidence check and focused tests. When incident-level denial exists, allow a non-denied sentence containing an explicit measured/observed P95 value. Retain conservative refusal for ambiguous or target-only sentences. Removed the prior expectedFailure.

## Verification and research limits
Previous head `8d023b9`: Actions run 42755111453 completed SUCCESS (Python 3.11/3.12 unit tests, fixed stress evaluation commands, deck). This **does not** verify the patch. Final-head CI and paired metrics must be checked separately; a passing CI command alone does not provide a quantitative gain. The authored fixture is development data, not a blind independent holdout.

Known limitations: sentence punctuation, tables, explicit contradicting later claims, numerical value attribution, and unmeasured phrasing variants remain unhandled. This is heuristic evidence presence, not claim entailment. No licensed real public human-reviewed corpus or independent supporting-span audit exists yet. No paid API or GPU costs authorized. Keep B2 Champion and Draft PR.
