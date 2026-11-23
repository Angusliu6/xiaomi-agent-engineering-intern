# TRACEQA-20261123-SOURCE-URL-ALIAS-018

## Scope and hypothesis
Starting Challenger: `6bf0a95` (2026-11-22 end); frozen main Champion: `d292346c49402141112d3f11a3fb293fd22df83c`.
Hypothesis: a dev gold document and a holdout gold document from the same public report can evade exact URL comparison using a different fragment or hostname case. Canonicalizing scheme/hostname/default HTTPS port and discarding fragment should reject the alias, while malformed source URLs fail closed without raising an exception.

## Intervention and controls
Only `src/traceqa/public_audit.py` and `tests/test_public_audit.py` changed. Source identity is compared as (scheme, host, port, path, query), retaining path/query to avoid collapsing genuinely distinct reports. The invalid URL path remains a metadata error, and must not crash split checking. Added two unittest methods: cross-split fragment/case alias negative and malformed port negative. Existing disjoint-source positive and within-dev duplicate positive are regression controls.

## Verification and limitations
The GitHub connector was used to read current main, PR, Issues, research state, ledger, and prior report. Local git clone is BLOCKED by `Could not resolve host: github.com`. New GitHub Actions run and fixed B2/B3 numeric outputs must be verified separately; committed tests are not proof of passing. No independent public cases, human reviews, or licensed corpus were added. This is a narrow syntactic leakage guard, not semantic source deduplication, license verification, or evidence entailment. The old source URL comparison also missed redirects, mirrors and URL aliases.

## Decision and costs
No paid API or GPU used. Keep PR #6 Draft and main B2 Champion unchanged. Do not claim task-level improvement or generalization from synthetic controls. P0 remains licensed real incidents with independent span review and sealed holdout.
