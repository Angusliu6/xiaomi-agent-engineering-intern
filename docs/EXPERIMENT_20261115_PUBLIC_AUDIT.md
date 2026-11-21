# TRACEQA-20261115-PUBLIC-AUDIT-010

Status: audit scaffold submitted on Draft PR #6; **no public benchmark evaluated**. Champion B2 remains frozen at `d292346c49402141112d3f11a3fb293fd22df83c`.

## Bottleneck and falsifiable hypothesis
The current authored stress fixture cannot establish generalization, and Issue #1 requires public provenance and independently reviewed supporting spans. Hypothesis: a fail-closed preflight audit will reject missing or inconsistent provenance/labels before an external benchmark can be scored, while accepting internally consistent positive and abstention controls.

## Changes and controls
Start head: `cfd4892c694b06a6b2dd6190a8c4f32fecdf40a8`.
Audit code: `6fac0ca2e5e88418de9a04f73c139bafd28df3f7`.
Unit controls: `2bcc90736160a6e4879c7c188143fad0e29be0a1`.
The validator checks declared HTTPS source and license URLs, license ID, two distinct reviewer IDs, answerability/gold consistency, exact quoted supporting-span offsets, gold/span coverage and duplicate IDs. Negative controls perturb offsets, license metadata, reviewer IDs, gold coverage and case uniqueness; positive controls cover answerable and abstention labels.

## Important limitations
The validator **does not visit URLs, authenticate human reviewers, establish legal licensing, assess semantic entailment, or create a blind holdout**. `example.org` in tests is a synthetic placeholder, not a vetted source. An independent reviewer must manually verify licensing and claim support before any public dataset is declared ready. No real cases were added. Do not claim independent performance or a measured gain.

## Verification
GitHub writes succeeded. Local full-repository clone/test is BLOCKED by `Could not resolve host: github.com`. CI for the test commit and final head must be checked separately. No fixed B2/B3 paired scores were generated this run; production gate was not changed. Any CI failure or false acceptance of malformed annotations falsifies the proposed data-quality control.

## Decision
Keep B2 Champion, PR #6 Draft. Next: confirm CI, source a small legally verified public incident pilot, double-review supporting spans and no-answer labels, then freeze holdout before paired evaluation. No paid API/GPU spending.
