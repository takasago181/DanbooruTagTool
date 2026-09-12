# CURRENT DEV TASK — ISSUE #63 MIRROR

> The live GitHub Issue is the executable task authority. Read `CURRENT_STATE.md`, then fetch Issue #63 and its latest checkpoint before implementation. If this mirror differs from the live Issue, fail closed and do not guess from chat history.

最終同期: 2026-09-12

## Source

- Source Issue: **#63**
- Issue title: **[SPECIAL-DICT][PRODUCT-FIT][DEV] Integrate audited product-fit verdict sidecar**
- Issue state: **OPEN / CURRENT CORE DEV until accepted/merged**
- DEV state: **PRODUCT_FIT_VERDICT_INTEGRATION**
- Stage10 production A/B: **NOT A v1 BLOCKER / NOT STARTED**

## Authoritative inputs

Audit branch: `audit/special2788-product-fit-20260912`

Read after live Issue preflight:
1. `docs/audit/SPECIAL2788_PRODUCT_FIT_IMPLEMENTATION_CONTRACT_20260912.md`
2. `docs/audit/SPECIAL2788_PRODUCT_FIT_VERDICT_MANIFEST_20260912.json`
3. `docs/audit/SPECIAL2788_PRODUCT_FIT_AUDIT_20260912.md`
4. `docs/audit/CODEX_PROMPT_PRODUCT_FIT_IMPLEMENTATION_20260912.md`

Expected verdict counts:
- KEEP 1618
- KEEP_REFERENCE_ONLY 1133
- OUT_OF_SCOPE_PRODUCT 12
- REVIEW 25
- total 2788

## Scope

1. Import the audited verdict manifest without semantic re-judgment.
2. Deterministically generate `data/special2788/product_fit_verdicts.csv` with one row per Special ID.
3. Validate 2,788 contiguous unique IDs, no overlap, exact verdict counts.
4. Load verdicts as a Special-ID-keyed sidecar; do not overwrite canonical Special data.
5. Centralize product-facing eligibility behavior.
6. Apply:
   - KEEP = normal product-facing candidate
   - KEEP_REFERENCE_ONLY = retained for exact/alias/reference/search access, not independent default recommendation/browse candidate
   - OUT_OF_SCOPE_PRODUCT = source/history retained, normal product-facing candidate surfaces excluded
   - REVIEW = inspectable but not silently normalized/auto-promoted
7. Add focused tests and implementation report.
8. Stop for DEV/AUDIT before merge.

## Hard boundaries

- No Special ID deletion/renumbering.
- No canonical identity or Alias relation mutation.
- No provenance/source/layer mutation.
- No semantic re-audit of 2,788 rows.
- Do not invent filters based on age, sexual strength, non-consent, R18G, niche intensity, or extremity.
- Do not implement Issue #34 fuzzy/substring ranking changes here.
- Do not implement #42/#64 UI/product-scope changes here.
- No runtime LLM dependency.

## Completion / return contract

Codex must provide:
- task branch and commit SHA
- changed files
- generated CSV counts/coverage validation
- tests and results
- product-facing behavior changes
- canonical/protected data unchanged confirmation
- unresolved items

Do not self-merge. Return to DEV/AUDIT.

## Post-#63 route

After accepted integration:

`#63 -> #64 General 30,629 practical taxonomy -> #34 bilingual search relevance/noise -> #42 v1 scope lock -> v1 UI integration / Windows acceptance`

Issue #5 / Stage10 is a future generation-effectiveness lane only if an adopted feature later requires empirical image evidence.
