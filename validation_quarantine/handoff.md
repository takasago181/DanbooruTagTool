# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2700
- Cumulative: PASS 2213 / FIX 174 / REVIEW 296 / IMAGE_TEST_REQUIRED 17
- Batch 1-26 R2 acceptance gates: PASS
- Batch 27: 100-row first pass complete; integrity/false-PASS gate pending
- Active revalidation pending pointer: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 2701 only after Batch27 gate is saved
- Production/main modified: NO

## Batch 27 first-pass summary
Range 2601-2700: PASS 100 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0.

Durable result blocks:
- `results_blocks/2601_2620.csv`
- `results_blocks/2621_2640.csv`
- `results_blocks/2641_2660.csv`
- `results_blocks/2661_2680.csv`
- `results_blocks/2681_2700.csv`

All 100 rows are `ALIAS_PRESERVE`. Exact Prompt identity is retained, canonical linkage remains statistics-only, and no canonical/Alias model-response equivalence is promoted. Alias wording that suggests actor, geometry, camera, restraint, visibility, or unusual anatomy was not used to infer unasserted production metadata. Blank requirement fields remain valid NOT ASSERTED states.

`candidate_fixes.csv` and `revalidation_queue.csv` inspected at every 20-row checkpoint; no Batch27 delta. Semantic support remains 55/58. No Stage10 HOLD knowledge promoted to production truth.

`RESULT_LEDGER_INDEX.csv` remains a lagging secondary index from a pre-existing state; durable blocks + progress + handoff are the restart source pending reconciliation.

## Gate boundary
Do not start sequence 2701 until Batch27 static integrity and PASS re-audit are completed and persisted.
