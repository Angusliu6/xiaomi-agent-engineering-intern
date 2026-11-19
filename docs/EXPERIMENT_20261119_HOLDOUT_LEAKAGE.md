# TRACEQA-20261119-HOLDOUT-LEAKAGE-014

## Hypothesis and scope
Starting Challenger: `3bde0e3`; frozen main Champion: `d292346c49402141112d3f11a3fb293fd22df83c`. Draft PR #6 remains unmerged.

**Falsifiable hypothesis:** When development and sealed holdout cases are declared, reusing a normalized question or the same gold document across splits must make the public-benchmark audit fail closed. A disjoint positive pair must pass. This is a split-integrity check, not a model-quality or real-world generalization result.

## Change and controls
- `d9a9cfd`: optional split-aware integrity checks in `src/traceqa/public_audit.py`. If any case declares `split`, every case must declare `dev` or `holdout`. Cross-split queries are compared after whitespace normalization and Unicode casefold; shared gold document IDs are rejected.
- `8c3548e`: three synthetic test methods: cross-split duplicate negative, disjoint positive, and missing split negative.
- Legacy cases with no split field retain existing audit behavior. No changes to production Evidence Gate or main.
- Limitations: exact/normalized query overlap is not semantic near-duplicate detection; gold-doc separation does not prevent other corpus leakage; no genuine holdout or human review was created. The audit still does not verify source licensing or semantic entailment.

## Validation and decision
The GitHub Actions run on the final head must be checked for Python 3.11/3.12 and frozen B2/B3 commands. No new task-level gain or regression is claimed without paired numeric outputs. Actual licensed public cases: 0. Independent public holdout: absent. Paid API/GPU cost: 0. Retain B2 Champion and keep Draft PR #6 open.
