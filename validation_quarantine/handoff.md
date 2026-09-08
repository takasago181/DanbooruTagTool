# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Completed Special-level first pass: 100
- Effective counts: PASS 84 / FIX 9 / REVIEW 3 / IMAGE_TEST_REQUIRED 4
- Batch 1 first-pass: COMPLETE
- Batch 1 full R2 revalidation: 100 / 100 COMPLETE
- Batch 1 R2 acceptance gate: PASS
- Revalidation queue pending: 0 (all 100 entries resolved or evidence-parked)
- PASS false-PASS sample: 20 checked, 0 new false-PASS after revalidation
- Historical false-PASS: 1 (ID88, S risk; explicitly superseded)
- Semantic-support frozen target: 58 rows; covered: 9
- Next first-pass Special sequence: 101
- Next external batch: 2 (101-200)
- Production modified: NO

## Batch 1 root cause and correction
ID88 `masturbation` originally recorded PASS while enabled CORE_SUPPORT+ADDITIVE `solo` was omitted from the Special-level sidecar-aware verdict. R2 correctly classified this as an S-risk false-PASS. The immutable first-pass block remains unchanged; `revalidation_results.csv` / `revalidation_blocks/0081_0100.csv` supersede effective ID88 state to IMAGE_TEST_REQUIRED pending controlled A/B.

The root cause was addressed by full R2 sidecar-aware revalidation of sequences1-100. No additional false-PASS was found.

## Revalidation checkpoints
- 1-20: complete. IDs16/17/19 remain IMAGE_TEST_REQUIRED; ID20 A-priority PASS retained.
- 21-40: complete. IDs22/40 remain REVIEW; IDs34/36 narrowed ActorRequirement FIX retained.
- 41-60: complete in `revalidation_blocks/0041_0060.csv`. ID55 REVIEW retained; IDs49/50/57/58/59 FIX candidates retained.
- 61-80: complete in `revalidation_blocks/0061_0080.csv`. No new false-PASS/FIX; A-priority structure/alias rows retained without generation overclaim.
- 81-100: complete in `revalidation_blocks/0081_0100.csv`. ID88 -> IMAGE_TEST_REQUIRED; IDs92/94 ImplementRequirement FIX retained.

## PASS sampling gate
`pass_sampling_batch1_r2.csv` records the deterministic 20-row audit:
- all 13 effective A-priority PASS rows in Batch1
- 7 fixed spread B-priority PASS controls
- new false-PASS: 0

Therefore Batch1 acceptance gate is PASS and sequence101 may begin.

## Effective unresolved/candidates after Batch1
- IMAGE_TEST_REQUIRED: IDs16,17,19,88
- REVIEW: IDs22,40,55
- FIX candidates: IDs34,36,49,50,57,58,59,92,94
These are explicitly parked/resolved in `revalidation_queue.csv`; they do not block first-pass continuation.

## Semantic-support coverage
Frozen rows1-9 are audited:
- IDs16/17/19 CORE_SUPPORT+ADDITIVE -> IMAGE_TEST_REQUIRED
- ID88 `solo` CORE_SUPPORT+ADDITIVE -> IMAGE_TEST_REQUIRED
- ID88 optional pose alternatives -> static PASS as optional choices only
Global coverage remains 9/58. Continue row-complete sidecar audit as associated Specials are encountered; final promotion remains blocked until 58/58.

## Exact restart
Resume first-pass at sequence101 under R2. Process 101-200 with 20-row checkpoints. For any associated semantic-support row, record it in `semantic_support_results.csv` before accepting the Special-level verdict. At 200, run the full 100-row consistency + deterministic PASS sampling gate. Do not modify main/production.

## Durable ledgers
`RESULT_LEDGER_INDEX.csv`, `results_blocks/`, `revalidation_results.csv`, `revalidation_blocks/`, `pass_sampling_batch1_r2.csv`, `candidate_fixes.csv`, `revalidation_queue.csv`, `semantic_support_results.csv`, `progress.json`, `handoff.md`.
