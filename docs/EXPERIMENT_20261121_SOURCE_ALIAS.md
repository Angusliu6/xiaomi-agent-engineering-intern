# TRACEQA-20261121-SOURCE-ALIAS-016

## Hypothesis and scope
Start Challenger: `316d23070f451e3d1747fa5b4f9182212d42d9f7`. Frozen main Champion: `d292346c49402141112d3f11a3fb293fd22df83c`. Draft PR #6 remains unmerged.

**Falsifiable hypothesis:** A dev gold document and a holdout gold document that originate from the exact same `source_url` must fail the public benchmark audit, even if their IDs and extracted text differ. Disjoint sources with different evidence should remain eligible.

## Minimal change and controls
- `src/traceqa/public_audit.py`: track source URL of gold documents across declared splits; flag `cross_split_source_url_leakage`.
- `tests/test_public_audit.py`: add a negative test with same URL/different text and adjust the existing disjoint positive to use a different URL.
- Only the audit helper changed; B2/B3 inference behavior is unchanged.
- Scope is **exact URL equality**; redirect aliases, tracking parameters, mirrored reports, near-duplicates, semantic leakage and underlying retrieval-corpus contamination remain undetected.
- URL preflight checks syntax only, not actual licensing or source ownership. Review identifiers do not prove real independent human review.

## Validation and decision
CI and fixed B2/B3 development-set numeric comparisons must be checked on the final head. Local clone was blocked by GitHub DNS resolution. No new real licensed cases, no sealed holdout, no measured generalization gain. No paid API/GPU was used. Keep B2 Champion unchanged and PR #6 Draft.
