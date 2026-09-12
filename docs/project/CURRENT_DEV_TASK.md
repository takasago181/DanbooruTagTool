# CURRENT DEV TASK — ISSUE #63 MIRROR

> The live GitHub Issue is the executable task authority. Read `CURRENT_STATE.md`, then fetch Issue #63 and its latest checkpoint before implementation. If this mirror differs from the live Issue, fail closed and use neither stale content nor chat history to guess the contract.

最終同期: 2026-09-12

## Source

- Source Issue: **#63**
- Issue title: **[SPECIAL-DICT][PRODUCT-FIT][DEV] Integrate audited product-fit verdict sidecar**
- Issue state: **OPEN / READY / CURRENT CORE DEV**
- DEV state: **PRODUCT_FIT_VERDICT_INTEGRATION_READY**
- Working branch: **Codex must create a dedicated feature branch from latest live main**
- Stage10 production A/B: **NOT STARTED**

## Authoritative inputs

Audit branch: `audit/special2788-product-fit-20260912`

Read after live Issue preflight:
1. `docs/audit/SPECIAL2788_PRODUCT_FIT_IMPLEMENTATION_CONTRACT_20260912.md`
2. `docs/audit/SPECIAL2788_PRODUCT_FIT_VERDICT_MANIFEST_20260912.json`
3. `docs/audit/SPECIAL2788_PRODUCT_FIT_AUDIT_20260912.md`
4. `docs/audit/CODEX_PROMPT_PRODUCT_FIT_IMPLEMENTATION_20260912.md`

Audit commits:
- manifest `eff5c41a479062cb9f785fb9905111aeb4d1223b`
- audit registration `b04fbcfdcb644095d9c61a86be9e665e435b5697`
- implementation contract `487076db7e22f0b7fdbead7afa19428ede56c285`
- Codex prompt `63d01b2c11b64568464e27522e171b934efd9b08`

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
   - OUT_OF_SCOPE_PRODUCT = historical/source data retained, normal product-facing candidate surfaces excluded
   - REVIEW = inspectable but not silently normalized/auto-promoted as resolved recommendation
7. Add focused tests and implementation report.
8. Stop for DEV/AUDIT before merge.

## Hard boundaries

- No Special ID deletion/renumbering.
- No canonical identity or Alias relation mutation.
- No provenance/source/layer mutation.
- No semantic re-audit of 2,788 rows.
- Do not invent filters based on age, sexual strength, non-consent, R18G, niche intensity, or extremity.
- Do not implement Issue #34 fuzzy/substring ranking changes here.
- Do not start Stage10 production A/B.
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

Do not merge. Return to DEV/AUDIT.

After accepted integration the route is:
`#63 -> #34 bilingual search relevance/noise -> remaining #42 product-purpose narrowing -> #5 -> Stage10 prep`.
