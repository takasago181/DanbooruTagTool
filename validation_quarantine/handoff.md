# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2460
- Cumulative: PASS 1985 / FIX 174 / REVIEW 284 / IMAGE_TEST_REQUIRED 17
- Batch 1-24 R2 acceptance gates: PASS
- Batch 25: checkpoints 1-3/5 complete (2401-2460)
- Active revalidation pending pointer: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 2461
- Production/main modified: NO

## Batch 25 current summary
Range 2401-2460: PASS 44 / FIX 0 / REVIEW 16 / IMAGE_TEST_REQUIRED 0.

Durable result blocks:
- `results_blocks/2401_2420.csv`
- `results_blocks/2421_2440.csv`
- `results_blocks/2441_2460.csv`

R2 deep review keeps material provisional restraint/interaction rows unresolved rather than guessing. Approved rows with explicit pose/spatial meaning but missing structural assertion (2451/2459) are REVIEW pending independent generation evidence. Cosmetic audit-only variants preserve valid blank metadata.

candidate_fixes/revalidation_queue inspected at each checkpoint with no Batch25 delta. No Stage10 HOLD knowledge promoted.

## Exact restart
Resume first-pass at sequence 2461. Checkpoint every 20. Do not modify production/main.
