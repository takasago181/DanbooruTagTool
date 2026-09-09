# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2600
- Cumulative: PASS 2113 / FIX 174 / REVIEW 296 / IMAGE_TEST_REQUIRED 17
- Batch 1-26 R2 acceptance gates: PASS
- Batch 26: complete; integrity/false-PASS gate PASS
- Active revalidation pending pointer: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 2601
- Production/main modified: NO

## Batch 26 summary
Range 2501-2600: PASS 98 / FIX 0 / REVIEW 2 / IMAGE_TEST_REQUIRED 0.

Durable result blocks:
- `results_blocks/2501_2520.csv`
- `results_blocks/2521_2540.csv`
- `results_blocks/2541_2560.csv`
- `results_blocks/2561_2580.csv`
- `results_blocks/2581_2600.csv`

Static integrity: 100 contiguous unique sequences, missing 0, duplicate 0.

Non-PASS:
- 2503 `mutual impregnation` — S-risk REVIEW; reciprocal/multi-actor structure is plausible but exact family/role/actor requirements lack sufficient independent evidence.
- 2504 `vine bondage` — S-risk REVIEW; restraint+vine implement structure is plausible but exact project family/role/requirements lack sufficient independent evidence.

Alias-preserve rows were checked against the R2 canonical/Alias HOLD boundary. Exact Prompt identity remains preserved; canonical linkage remains statistics-only; no model-response equivalence was promoted.

R2 PASS re-audit: 20/98 PASS rows, deterministic/stratified; all re-PASS; new false-PASS 0. Details: `pass_sampling_batch26_r2.csv` and `batch26_integrity_r2.md`.

`candidate_fixes.csv` and `revalidation_queue.csv` were inspected at every 20-row checkpoint; Batch26 adds no new candidate fix or revalidation item. Semantic support remains 55/58. No Stage10 HOLD knowledge was promoted to production truth.

`RESULT_LEDGER_INDEX.csv` remains a secondary index and is lagging pre-existing durable blocks; do not treat that lag as loss of checkpointed work. Durable result blocks + `progress.json` + this handoff are the restart source until index reconciliation is separately performed.

## Exact restart
Resume first-pass at sequence 2601 (Batch 27). Checkpoint every 20. Do not modify production/main.
