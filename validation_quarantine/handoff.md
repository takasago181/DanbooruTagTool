# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2640
- Cumulative: PASS 2153 / FIX 174 / REVIEW 296 / IMAGE_TEST_REQUIRED 17
- Batch 1-26 R2 acceptance gates: PASS
- Batch 27: in progress; checkpoint 2/5 saved (2601-2640)
- Active revalidation pending pointer: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 2641
- Production/main modified: NO

## Batch 27 checkpoint summary
Range 2601-2640: PASS 40 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0.

Durable result blocks:
- `results_blocks/2601_2620.csv`
- `results_blocks/2621_2640.csv`

All 40 rows are `ALIAS_PRESERVE`. R2 canonical/Alias boundary checked: exact Prompt identity remains preserved; canonical linkage remains statistics-only; no model-response equivalence or automatic support behavior was promoted. Unusual-anatomy wording at 2620-2622 and 2630 was not used to infer anatomy-negative behavior.

`candidate_fixes.csv` and `revalidation_queue.csv` inspected at each checkpoint; no Batch27 delta. Semantic support remains 55/58. No Stage10 HOLD knowledge promoted to production truth.

`RESULT_LEDGER_INDEX.csv` is still lagging durable blocks from a pre-existing state. Durable result blocks + `progress.json` + this handoff remain the restart source until index reconciliation is completed; no checkpointed block is being treated as lost.

## Exact restart
Resume first-pass at sequence 2641 (Batch 27). Checkpoint every 20. Do not modify production/main.
