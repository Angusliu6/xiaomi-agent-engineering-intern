# TRACEQA-20261122-SEALED-SPLIT-017

## Hypothesis
Starting Challenger: `0aa32700b8bde32546d4c9702ad55c77619a4dba`. Frozen main Champion: `d292346c49402141112d3f11a3fb293fd22df83c`.

**Falsifiable hypothesis:** The existing audit returns ready=true for a correctly shaped but unpartitioned synthetic fixture. A caller intending sealed independent evaluation must fail closed if either dev or holdout is absent, while a disjoint dev/holdout pair passes. Legacy development-only auditing must remain backwards compatible.

## Minimal intervention
- Add keyword-only `require_holdout=False` to `audit_public_cases`.
- When enabled, require at least one dev and one holdout and require every case to carry a valid split. This is a structural precondition only; it does not establish a genuinely independent or frozen holdout.
- Add three test methods: unpartitioned legacy fixture negative, one-sided split negatives, disjoint pair positive.
- No inference gate, Champion or default behavior changes.

## Verification boundary
Local repository clone failed due to github.com DNS resolution. GitHub Actions for the new head must confirm tests and fixed B2/B3 dev-set comparisons; a CI command succeeding is not itself evidence of numeric improvement. This run collected no licensed real incident cases, no independent human supporting-span review, and no measured generalization gain.

## Costs and decision
No paid API or GPU requested. Keep PR #6 Draft and B2 Champion frozen. The next P0 milestone is a licensed public corpus with independent reviewed spans, frozen holdout and paired refusal metrics; do not claim the audit switch alone achieves that milestone.
