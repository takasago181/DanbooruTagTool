# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2160
- Cumulative: PASS 1706 / FIX 174 / REVIEW 263 / IMAGE_TEST_REQUIRED 17
- Batch 1-21 R2 acceptance gates: PASS
- Batch 22: partial through 2160; 100-row gate not yet run
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 2161
- Production/main modified: NO

## Batch 22 partial summary
Range 2101-2160: PASS 60 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0.

Durable result blocks:
- `results_blocks/2101_2120.csv`
- `results_blocks/2121_2140.csv`
- `results_blocks/2141_2160.csv`

A-risk deep review: IDs2137-2141 camera/composition rows. CameraRequirementOverride remains structural visibility/composition metadata only. Stage10 knowledge keeps exact camera tuning/model-family effectiveness on HOLD; no automatic support or production tuning was promoted.

Alias rows preserve exact Special identity with canonical linkage statistics-only. Semantic-role rows remain search/support-only. Scene-context SUPPORT rows remain contextual metadata and do not become CORE_SUPPORT/default-on behavior. Blank structural requirements remain UNKNOWN rather than auto-filled.

Restart-time ledger reconciliation repaired `RESULT_LEDGER_INDEX.csv` through 2100 before new work. `candidate_fixes.csv` and `revalidation_queue.csv` were checked at each checkpoint and received no new entries. Semantic support remains 55/58.

## Exact restart
Resume first-pass at sequence 2161 (Batch 22). Checkpoint every 20. Do not modify production/main.
