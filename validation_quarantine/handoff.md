# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2120
- Cumulative: PASS 1666 / FIX 174 / REVIEW 263 / IMAGE_TEST_REQUIRED 17
- Batch 1-21 R2 acceptance gates: PASS
- Batch 22: partial through 2120; 100-row gate not yet run
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 2121
- Production/main modified: NO

## Batch 22 partial summary
Range 2101-2120: PASS 20 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0.

Durable result block:
- `results_blocks/2101_2120.csv`

This block is CLOTHING_EXPOSURE/DIRECT only. Identity and exposure-state semantics remain explicit; no bodypart/pose support was inferred from cutout/asides/transparency wording.

Restart-time ledger reconciliation: `progress.json` correctly showed 2100 complete while `RESULT_LEDGER_INDEX.csv` stopped at 2000. Authoritative append-only blocks 2001-2100 were confirmed present and the index was repaired through 2100 before creating new work.

`candidate_fixes.csv` and `revalidation_queue.csv` were checked and received no new entries. Semantic support remains 55/58.

## Exact restart
Resume first-pass at sequence 2121 (Batch 22). Checkpoint every 20. Do not modify production/main.
