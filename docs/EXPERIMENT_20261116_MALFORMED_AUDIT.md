# TRACEQA-20261116-MALFORMED-AUDIT-011

## Scope and hypothesis
Starting Draft PR #6 head: `934f489ec88b58787e0baf89f20a793de2c67611`. Frozen main Champion: `d292346c49402141112d3f11a3fb293fd22df83c`. The public benchmark preflight audit is a fail-closed quality gate, but malformed nested labels (e.g., unhashable lists in gold_docs, reviewer_ids or span doc_id) could raise TypeError instead of returning `ready=false`. Hypothesis: defensive type checks eliminate these crashes while preserving acceptance of valid answerable and abstention controls.

## Minimal change and controls
Code commits: `6ff555040422371eed14cfdcaa8c1faf453d27ba`, `192d41f222c86f45e6dc5143bb31949983d4d053`.
Test commit: `78a911b1221822e1a53d2ce7e019aeb67c57d122`.
Tests cover invalid top-level containers, unhashable gold IDs, span doc IDs and reviewers, plus valid positive/abstention controls. Expected outcome: invalid cases return structured errors without exceptions. This is a synthetic robustness test, **not independent public-data evaluation**.

## Verification, limitations and decision
Prior head `934f489` unit-tests workflow completed SUCCESS (run 43677470535). That does not verify the new commits. New head CI and fixed B2/B3 paired metrics must be checked separately. No public documents or reviewed labels were added, no production evidence policy was changed, and no measured quality gain or generalization is claimed. Metadata-only URL/license/reviewer checks do not verify authenticity, legal rights, or semantic entailment.

Cost: zero paid API and GPU. Keep PR #6 Draft and B2 Champion unchanged. Next: confirm new CI, then prioritize a license-verified public incident pilot with independently reviewed supporting spans and frozen holdout.
