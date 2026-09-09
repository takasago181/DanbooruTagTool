# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2260
- Cumulative: PASS 1806 / FIX 174 / REVIEW 263 / IMAGE_TEST_REQUIRED 17
- Batch 1-22 R2 acceptance gates: PASS
- Batch 23: checkpoint 3/5 complete (2201-2260)
- Active revalidation pending pointer: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 2261
- Production/main modified: NO

## Batch 23 checkpoint summary
2201-2260: PASS 60 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0.

Durable result blocks:
- `results_blocks/2201_2220.csv`
- `results_blocks/2221_2240.csv`
- `results_blocks/2241_2260.csv`

All rows validated so far are CLOTHING_EXPOSURE/DIRECT. Clothing/exposure state and garment manipulation remain structural visual-state metadata only. Blank structural requirements remain UNKNOWN/not asserted. No automatic support insertion or Stage10 camera/pose/visibility behavior is promoted.

`candidate_fixes.csv` and `revalidation_queue.csv` were inspected at each checkpoint and remain unchanged for this range. Semantic support remains 55/58.

## Exact restart
Resume first-pass at sequence 2261 (Batch 23 checkpoint 4). Checkpoint every 20. Do not modify production/main.
