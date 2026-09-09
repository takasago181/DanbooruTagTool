# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: HOLD_PROMOTION_PENDING_LOCAL_COMPLETENESS_SCAN
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
- Local protected-asset completeness: PENDING
- Promotion-readiness verdict: HOLD_PROMOTION
- Production/main modified: NO

## Completed post-first-pass work

### Semantic support 58/58
Final rows are durably recorded in:
- `semantic_support_blocks/0056_0058.csv`
- consolidated `semantic_support_results.csv`

Rows 56-58:
- ID1823 `cuffs-to-collar` -> `cuffs`: IMAGE_TEST_REQUIRED
- ID1823 `cuffs-to-collar` -> `collar`: IMAGE_TEST_REQUIRED
- ID1839 `spreader bar` -> `restraints`: IMAGE_TEST_REQUIRED

Reason: semantic constituent/parent compatibility does not certify default-on additive generation benefit. Relation/device identity remains first-class and model-scoped generation behavior remains controlled-test work.

### Candidate FIX consistency
See:
`CANDIDATE_FIX_CROSS_CONSISTENCY_R2_20260910.md`

Result: PASS_WITH_STATUS_FILTER.

Important promotion constraint: historical `WITHDRAWN_AFTER_SIBLING_CHECK` / superseded candidate rows are evidence only. Final implementation must select the effective active candidate set and apply multi-field fixes atomically without inferring generation support behavior.

### Unresolved disposition
See:
`UNRESOLVED_DISPOSITION_R2_20260910.md`

Result: PASS_AS_EXPLICITLY_PARKED.

Special-level IMAGE_TEST_REQUIRED 17 are intentionally parked generation-evidence questions. REVIEW 305 are fail-closed evidence-insufficient/provisional/unknown cases and are not active revalidation. Do not force them to PASS/FIX for numerical cleanliness.

## Pre-freeze completeness reconciliation

GitHub-visible scan is recorded in:
`PRE_FREEZE_COMPLETENESS_RECONCILIATION_20260910.md`

Findings:
- current main `special2788_generation_profile.csv` blob remains `ac6c1d24e1c6ce04b238cc0b16d788f9d0965a05`, the same frozen audit profile;
- current main frozen semantic-support blob remains `e666e4efd5c3aabf22410d75e04ff51d826c9b0e`;
- no GitHub-visible artifact was found that independently proves a still-missing Special identity.

However, D-009/D-012 require ignored/local protected historical candidate/search/support assets to be reconciled. GitHub is intentionally not a full backup of those assets, so `missing=0` cannot yet be certified from this environment.

Required local execution contract:
`PRE_FREEZE_LOCAL_PROTECTED_ASSET_SCAN_TASK_20260910.md`

Allowed local outcomes:
- `LOCAL_COMPLETENESS_PASS_MISSING_0`
- `LOCAL_COMPLETENESS_DELTA_FOUND`
- `LOCAL_COMPLETENESS_BLOCKED_INVENTORY_UNKNOWN`

## Promotion package

See:
`PROMOTION_READINESS_PACKAGE_20260910.md`

Current enum: **HOLD_PROMOTION**.

This is an evidence-completeness hold only. It does not invalidate the completed 2,788 audit or mean a missing Special was found.

## Next safe action

Do NOT rerun first-pass work.
Do NOT modify production `data/**`.

Run the local protected-asset completeness scan using the tracked contract above.

If `LOCAL_COMPLETENESS_PASS_MISSING_0`, record the evidence in quarantine/Issue #32, set final Special count 2,788, change readiness to `READY_FOR_FINAL_PROMOTION_AUDIT`, and start a separate independent final promotion audit.

If a genuine delta is found, validate only that delta under applicable #32 R2 rules; keep all completed 2,788 results.
