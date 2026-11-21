# TRACEQA-20261117-PUBLIC-URL-PREFLIGHT-012

## Hypothesis and scope
Start: `d43d7b1599296c266a23114a6a54e746acb460e5`. Frozen main B2 Champion: `d292346c49402141112d3f11a3fb293fd22df83c`. Draft PR #6 only.

The public benchmark preflight previously accepted HTTPS URLs pointing to private/loopback/link-local/reserved literal IP addresses and subdomains of localhost. **Falsifiable hypothesis:** rejecting non-global IP literals and malformed URL authorities makes the metadata preflight fail closed without rejecting an ordinary public HTTPS URL. This does not authenticate source content, licensing, reviewers or supporting-span semantics.

## Minimal changes and controls
- Code: `b58d3c01309f906eec4877184f6114be87e24eb8`; reject non-global IP literals using standard-library `ipaddress`, localhost variants, malformed ports/IPv6 and whitespace.
- Synthetic test: `be2aa6b6d35fac7898b02aead598bf68c9babddc`; valid `example.org` positive, source IP/localhost negatives, license IP/malformed authority negatives.
- No production Evidence Gate change. No real public incident cases added.
- Trade-off: syntactic IP-global classification can conservatively reject some publicly routed special-use IP addresses; DNS resolution, redirect destinations, and domain ownership are not checked. Never fetch arbitrary provenance URLs without separate network safety controls.

## Validation and decision
Prior head `d43d7b1` workflow `43804121271` completed SUCCESS on 2026-11-17 check; this is not evidence for the new code. New commits require CI on Python 3.11/3.12, all existing tests, and fixed B2/B3 paired development evaluation. No independently annotated public holdout; no performance/generalization gain claimed. Paid API/GPU cost: zero. Keep B2 Champion unchanged and PR #6 Draft; Issue #1 public benchmark remains P0.
