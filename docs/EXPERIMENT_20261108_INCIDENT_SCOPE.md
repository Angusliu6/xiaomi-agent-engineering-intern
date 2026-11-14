# TRACEQA-20261108-INCIDENT-SCOPE-003

Status: unverified code change; Draft PR #6 only. Champion main remains d292346c49402141112d3f11a3fb293fd22df83c.

## Falsifiable hypothesis
For explicit RET-nnn measurement questions, restricting typed numeric evidence to the text after the matching incident identifier and before the next RET identifier rejects other-incident P95 values without rejecting the same-incident positive control.

## Change and controls
Start: bfa8b7ce1f6f75f9ddf16dc311be616d6cdb767c.
Production change: 627b48af48fa8eb93cce3bd3100d2c70cee60475.
Tests: c098d9715f4513460000eba3bac763d6111ae325.
Changed only optional B3 evidence policy and diagnostic tests. Removed expectedFailure and added reversed-order and missing-target negative controls. Existing same-incident positive control remains.

## Measurement plan and limits
Run `python -m unittest discover -s tests -v`, then paired `python -m traceqa eval --cases data/stress_hard_negative.jsonl --variant b2 --out reports/stress-b2.json` and analogous b3, followed by `python -m traceqa compare reports/stress-b2.json reports/stress-b3.json`. CI must be checked on final head. No performance delta is claimed before runs complete.

The rule assumes incident-labelled sequential text. It may reject valid evidence appearing before the first identifier, or miss facts split across sections; it is not NLI, span-level entailment, or a general incident entity resolver. The authored fixture is seen development data, NOT independent public holdout. Human-reviewed licensed public incident evaluation remains P0.

Cost: no paid API/GPU used. Decision: no merge or Champion promotion.
