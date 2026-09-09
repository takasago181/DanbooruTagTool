# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: READY_FOR_FINAL_PROMOTION_AUDIT
Rule version: R2

## Current position
- Fixed first-pass target: 2,788 Specials
- First pass: 2788 / 2788 — COMPLETE
- Cumulative: PASS 2292 / FIX 174 / REVIEW 305 / IMAGE_TEST_REQUIRED 17
- Batch 1-28 acceptance gates: PASS
- Active revalidation pending: 0
- Frozen semantic support: 58 / 58 COMPLETE; IMAGE_TEST_REQUIRED rows 33
- Candidate FIX cross-consistency: PASS_WITH_STATUS_FILTER
- REVIEW / IMAGE_TEST_REQUIRED disposition: PASS_AS_EXPLICITLY_PARKED
- GitHub-visible pre-freeze completeness: PASS_VISIBLE_SCOPE
- Local protected-asset completeness: PASS_AFTER_DELTA_VALIDATION
- Local scan enum: LOCAL_COMPLETENESS_DELTA_FOUND
- Local delta: 5 rows validated under R2; GENUINE_MISSING_SPECIAL = 0
- Final evidence-derived Special count: 2,788
- Promotion-readiness verdict: READY_FOR_FINAL_PROMOTION_AUDIT
- Production/main modified: NO

## Completed post-first-pass work

### Semantic support 58/58
Final rows are durably recorded in:
- `semantic_support_blocks/0056_0058.csv`
- consolidated `semantic_support_results.csv`

Rows 56-58 remain IMAGE_TEST_REQUIRED because semantic constituent/parent compatibility does not certify default-on additive generation benefit. Relation/device identity remains first-class and model-scoped generation behavior remains controlled-test work.

### Candidate FIX consistency
See:
`CANDIDATE_FIX_CROSS_CONSISTENCY_R2_20260910.md`

Result: PASS_WITH_STATUS_FILTER.

Historical `WITHDRAWN_AFTER_SIBLING_CHECK` / superseded candidate rows remain evidence only. Final implementation must select the effective active candidate set and apply multi-field fixes atomically without inferring generation-support behavior.

### Unresolved disposition
See:
`UNRESOLVED_DISPOSITION_R2_20260910.md`

Result: PASS_AS_EXPLICITLY_PARKED.

Special-level IMAGE_TEST_REQUIRED 17 remain intentional generation-evidence questions. REVIEW 305 remain fail-closed evidence-insufficient/provisional/unknown cases and are not active revalidation. Do not force them to PASS/FIX for numerical cleanliness.

## Pre-freeze completeness reconciliation

GitHub-visible scan:
`PRE_FREEZE_COMPLETENESS_RECONCILIATION_20260910.md`

Local protected/ignored scan:
`PRE_FREEZE_LOCAL_PROTECTED_ASSET_SCAN_RESULT_20260910.md`

Local scan result:
- `LOCAL_COMPLETENESS_DELTA_FOUND`
- evidence-pending candidate rows: 5
- genuine missing Special at scan time: 0
- production `data/**`: unchanged

Delta ledger:
`PRE_FREEZE_LOCAL_PROTECTED_ASSET_SCAN_DELTA_20260910.csv`

R2 delta-only validation:
`PRE_FREEZE_DELTA_R2_VALIDATION_20260910.md`

Result:
- 5 / 5 candidate rows dispositioned
- all retain `DO_NOT_PROMOTE`
- `GENUINE_MISSING_SPECIAL`: 0
- final Special count: 2,788
- completed 2,788 first-pass was not rerun or altered

The historical candidate labels remain provenance. They were not converted into Special identity merely because the phrases are meaningful, searchable, or model-reactive. `spread_eagle` is not established as a separate first-class Special; independent Danbooru-derived references use the general pose tag `spread_eagle_position`. The four `*_removal` strings also lack independent first-class Special authority.

## Promotion package

See:
`PROMOTION_READINESS_PACKAGE_20260910.md`

Current enum: **READY_FOR_FINAL_PROMOTION_AUDIT**.

This state does not authorize production promotion. A separate independent final promotion audit is still mandatory.

## Next safe action

Do NOT rerun first-pass work.
Do NOT modify production `data/**`.
Do NOT merge to `main` from this lane.

Start a separate independent final promotion audit against the frozen #32 quarantine package. That audit may approve or reject promotion, but #32 must not self-promote its candidate fixes.
