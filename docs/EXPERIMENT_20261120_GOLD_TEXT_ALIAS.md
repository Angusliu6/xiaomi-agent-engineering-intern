# TRACEQA-20261120-GOLD-TEXT-ALIAS-015

## Hypothesis and scope
Starting Challenger: `771368eb9148f5e89fb7ef2a4fd019ca7493fd67`. Frozen main Champion: `d292346c49402141112d3f11a3fb293fd22df83c`. PR #6 remains Draft.

**Falsifiable hypothesis:** Dev and holdout gold evidence with identical full text but different document IDs must be rejected by the public benchmark audit. Same-text reuse inside a single split must remain valid. This closes a concrete bypass of the 2026-11-19 ID-only split guard.

## Change and controls
- Code commit `289bb8e`: track exact gold document text across declared splits in `public_audit.py`; report `cross_split_gold_text_leakage` when a text is reused across splits, independent of ID.
- Test commit `b5cc66e`: one cross-split alias negative and one within-dev positive. Existing disjoint dev/holdout and cross-ID tests remain.
- This is an exact-text guard only; paraphrases, partial overlaps, duplicated source URLs, and contamination of the underlying model or retrieval corpus remain undetected.
- The metadata auditor does not verify legal license validity, human reviewer independence, or semantic entailment.

## Validation and decision
Previous head `771368e` CI: SUCCESS (unit-tests run 44458430074). New commits require their own CI; no task-level improvement or regression is claimed until frozen paired numeric outputs are examined. Actual licensed public cases: 0; independent holdout: absent. Paid API/GPU: 0. B2 Champion unchanged; PR #6 stays Draft.