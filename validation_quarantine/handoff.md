# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2680
- Cumulative: PASS 2193 / FIX 174 / REVIEW 296 / IMAGE_TEST_REQUIRED 17
- Batch 1-26 R2 acceptance gates: PASS
- Batch 27: in progress; checkpoint 4/5 saved (2601-2680)
- Active revalidation pending pointer: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 2681
- Production/main modified: NO

## Batch 27 checkpoint summary
Range 2601-2680: PASS 80 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0.

Durable result blocks:
- `results_blocks/2601_2620.csv`
- `results_blocks/2621_2640.csv`
- `results_blocks/2641_2660.csv`
- `results_blocks/2661_2680.csv`

All rows are `ALIAS_PRESERVE`. Exact Prompt identity is retained, canonical linkage remains statistics-only, and no canonical/Alias model-response equivalence is promoted. Spatial, actor, camera, restraint, visibility, and unusual-anatomy implications were not inferred merely from alias wording where the production row intentionally leaves those claims unasserted.

`candidate_fixes.csv` and `revalidation_queue.csv` inspected at each checkpoint; no Batch27 delta. Semantic support remains 55/58. No Stage10 HOLD knowledge promoted to production truth.

`RESULT_LEDGER_INDEX.csv` remains a lagging secondary index from a pre-existing state; durable blocks + progress + handoff are the restart source pending reconciliation.

## Exact restart
Resume first-pass at sequence 2681 (Batch 27). Checkpoint every 20. Do not modify production/main.
