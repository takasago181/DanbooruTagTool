# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2140
- Cumulative: PASS 1686 / FIX 174 / REVIEW 263 / IMAGE_TEST_REQUIRED 17
- Batch 1-21 R2 acceptance gates: PASS
- Batch 22: partial through 2140; 100-row gate not yet run
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 2141
- Production/main modified: NO

## Batch 22 partial summary
Range 2101-2140: PASS 40 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0.

Durable result blocks:
- `results_blocks/2101_2120.csv`
- `results_blocks/2121_2140.csv`

A-risk deep review:
- 2137 `downblouse`
- 2138 `downpants`
- 2139 `upskirt`
- 2140 `ass focus`

These POSE_COMPOSITION/camera rows keep CameraRequirementOverride=true as structural visibility/composition metadata only. Stage10 knowledge supports minimal role-separated camera/visibility handling but keeps exact family-specific tuning on HOLD; no automatic support tag or production tuning was inferred.

Alias rows preserve exact Special identity with canonical linkage statistics-only. Semantic-role rows remain search/support-only and do not assert direct model recognition.

Restart-time ledger reconciliation repaired `RESULT_LEDGER_INDEX.csv` from 2000 through authoritative blocks at 2100 before new work. `candidate_fixes.csv` and `revalidation_queue.csv` were checked at each checkpoint and received no new entries. Semantic support remains 55/58.

## Exact restart
Resume first-pass at sequence 2141 (Batch 22). Checkpoint every 20. Do not modify production/main.
