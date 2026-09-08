# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Completed Special-level first pass: 140
- Effective counts: PASS 122 / FIX 9 / REVIEW 3 / IMAGE_TEST_REQUIRED 6
- Batch 1 R2 acceptance gate: PASS
- Batch 2 checkpoints: 101-120 COMPLETE; 121-140 COMPLETE
- Revalidation queue pending: 0
- Semantic-support frozen target: 58 rows; covered: 15
- Next first-pass Special sequence: 141
- Production modified: NO

## Batch 2 findings so far
- 101-120: no new non-PASS findings.
- ID122 `missionary`: profile structure retained, but four enabled CORE_SUPPORT+ADDITIVE rows are NOT_TESTED -> IMAGE_TEST_REQUIRED.
- ID129 `sitting on face`: enabled CORE_SUPPORT+ADDITIVE `sitting` is NOT_TESTED and may dilute the intrinsic spatial relation -> IMAGE_TEST_REQUIRED.
- Semantic-support rows10-15 are now audited; optional/contextual camera variation remains static PASS only as optional choice.

## Prior unresolved/candidates
- IMAGE_TEST_REQUIRED: IDs16,17,19,88,122,129
- REVIEW: IDs22,40,55
- FIX candidates: IDs34,36,49,50,57,58,59,92,94

## Exact restart
Resume first-pass at sequence141 under R2. Continue Batch2 through 200 with 20-row checkpoints. For any associated semantic-support row, update `semantic_support_results.csv` before accepting the Special-level verdict. At 200 run consistency checks and deterministic PASS false-PASS sampling. Do not modify main/production.

## Durable ledgers
`RESULT_LEDGER_INDEX.csv`, `results_blocks/`, `revalidation_results.csv`, `revalidation_blocks/`, `pass_sampling_batch1_r2.csv`, `candidate_fixes.csv`, `revalidation_queue.csv`, `semantic_support_results.csv`, `progress.json`, `handoff.md`.
