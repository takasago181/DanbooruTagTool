# Special2788 Product-Fit Implementation Contract — 2026-09-12

## Purpose

Implement the completed 2,788-entry product-fit audit as a non-destructive product-facing eligibility layer.

This is not a semantic re-audit and must not mutate protected Special identity.

## Authoritative input

- audit branch: `audit/special2788-product-fit-20260912`
- audit log: `docs/audit/SPECIAL2788_PRODUCT_FIT_AUDIT_20260912.md`
- machine-readable verdict authority: `docs/audit/SPECIAL2788_PRODUCT_FIT_VERDICT_MANIFEST_20260912.json`
- manifest commit: `eff5c41a479062cb9f785fb9905111aeb4d1223b`
- audit log registration commit: `b04fbcfdcb644095d9c61a86be9e665e435b5697`

Expected verdict counts:
- KEEP 1618
- KEEP_REFERENCE_ONLY 1133
- OUT_OF_SCOPE_PRODUCT 12
- REVIEW 25
- total 2788

## Required implementation

1. Start from latest live `main` on a new task branch.
2. Import the authoritative manifest without semantic reinterpretation.
3. Deterministically expand it to `data/special2788/product_fit_verdicts.csv` with exactly:
   - `special_id`
   - `product_fit_verdict`
4. Validate:
   - exactly 2,788 rows
   - IDs unique and contiguous 1..2788
   - no overlap between explicit verdict sets
   - counts exactly 1618 / 1133 / 12 / 25
5. Load product-fit verdicts as a sidecar keyed by Special ID. Do not overwrite existing canonical Special rows.
6. Add the minimum product-facing eligibility behavior:
   - `KEEP`: normal product-facing Special candidate; browse/search/recommendation eligibility remains available.
   - `KEEP_REFERENCE_ONLY`: retained for exact/alias/reference/search access, but do not treat as an independent default recommendation/browse candidate when the canonical/product-facing concept already exists.
   - `OUT_OF_SCOPE_PRODUCT`: keep historical/source data intact but exclude from normal product-facing candidate/recommendation/browse surfaces.
   - `REVIEW`: retain and make inspectable, but do not silently normalize, auto-promote, or auto-recommend as a resolved product-facing concept.
7. Prefer a small central eligibility function/service over duplicated verdict checks throughout UI code.
8. Add focused tests for all four verdict classes and representative alias/reference behavior.

## Hard boundaries

- No Special ID deletion or renumbering.
- No canonical English identity mutation.
- No Alias/canonical relation mutation.
- No provenance/layer/source mutation.
- No reclassification based on age, sexual strength, non-consent, R18G, niche intensity, or extremity.
- No semantic re-audit by Codex.
- No #34 fuzzy/substring ranking redesign in this task.
- No Stage10 production A/B.
- No runtime LLM dependency.

## Search boundary

This task may alter candidate eligibility because product-facing status now exists, but it must not redesign fuzzy/substring ranking.

After this implementation is accepted/merged, Issue #34 should test/fix bilingual search relevance against the final product-facing eligibility layer. Representative `anal -> piano/analog...` behavior remains owned by #34.

## Acceptance

- deterministic manifest -> 2,788-row CSV generation succeeds
- counts and ID coverage match exactly
- production canonical dictionary remains unchanged
- runtime/UI can query product-fit verdict by Special ID
- normal product-facing candidate flow respects verdict semantics above
- reference-only entries remain discoverable as reference/search assets where appropriate
- OUT/REVIEW are not silently promoted to normal resolved recommendations
- applicable unit/integration/regression tests pass
- implementation report records changed files, tests, and any UI behavior affected

## Handoff after implementation

Return to DEV/AUDIT before merge. Do not self-approve semantic changes. After accepted integration, route next to Issue #34 bilingual search relevance/noise, then resume remaining #42 product-purpose narrowing.
