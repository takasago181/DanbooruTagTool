# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2500
- Cumulative: PASS 2015 / FIX 174 / REVIEW 294 / IMAGE_TEST_REQUIRED 17
- Batch 1-25 R2 acceptance gates: PASS
- Batch 25: complete; integrity/false-PASS gate PASS
- Active revalidation pending pointer: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 2501
- Production/main modified: NO

## Batch 25 summary
Range 2401-2500: PASS 74 / FIX 0 / REVIEW 26 / IMAGE_TEST_REQUIRED 0.

Durable result blocks:
- `results_blocks/2401_2420.csv`
- `results_blocks/2421_2440.csv`
- `results_blocks/2441_2460.csv`
- `results_blocks/2461_2480.csv`
- `results_blocks/2481_2500.csv`

Static integrity: 100 contiguous unique sequences, missing 0, duplicate 0.

R2 high-risk handling:
- Material PROVISIONAL restraint/pose/bodypart/spatial/interaction concepts remain REVIEW where exact project family/requirements are not independently established.
- Approved rows 2451 `bound puppy pose`, 2459 `tentacle between breasts`, 2471 `holding blindfold`, 2495 `hand on own tentacles`, and 2497 `holding with tentacle` were escalated to A-risk REVIEW because explicit structural meaning is not fully asserted and R2 forbids production self-certification.
- Cosmetic/state-only PROVISIONAL rows remain PASS only where audit-only blanks make no execution claim.
- Blank/None was not treated as an automatic error.

R2 PASS re-audit: 15/74 PASS rows, deterministic sample, all re-PASS; new false-PASS 0. Details: `pass_sampling_batch25_r2.csv` and `batch25_integrity_r2.md`.

`candidate_fixes.csv` and `revalidation_queue.csv` were inspected at every 20-row checkpoint; Batch25 adds no new candidate fix or revalidation item. Semantic support remains 55/58. No Stage10 HOLD knowledge was promoted to production truth.

## Exact restart
Resume first-pass at sequence 2501 (Batch 26). Checkpoint every 20. Do not modify production/main.
