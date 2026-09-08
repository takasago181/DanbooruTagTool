# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Completed Special-level first pass: 400
- Effective counts: PASS 358 / FIX 22 / REVIEW 5 / IMAGE_TEST_REQUIRED 15
- Batch 1 R2 acceptance gate: PASS
- Batch 2 R2 acceptance gate: PASS
- Batch 3 R2 acceptance gate: PASS
- Batch 4 R2 acceptance gate: PASS
- Revalidation queue pending: 0
- Semantic-support frozen target: 58 rows; covered: 46
- Semantic-support IMAGE_TEST_REQUIRED rows: 27
- Next first-pass Special sequence: 401
- Current external batch: 5 (401-500)
- Production modified: NO

## Batch 4 final
301-400 delta: PASS 92 / FIX 0 / REVIEW 1 / IMAGE_TEST_REQUIRED 7.

20-Special result checkpoints were saved as:
- 0301_0320.csv
- 0321_0340.csv
- 0341_0360.csv
- 0361_0380.csv
- 0381_0400.csv

Non-PASS findings:
- ID309 `mecha on girl` -> REVIEW. It remains PROVISIONAL_CORRECTION with broad technology-group evidence and no settled family/role; blanks were not auto-filled.
- ID312 `sex machine` -> IMAGE_TEST_REQUIRED because default-on CORE_SUPPORT+ADDITIVE `machine` / `sex_toy` rows are NOT_TESTED.
- ID313 `sybian` -> IMAGE_TEST_REQUIRED because default-on `vibrator` / `sex_toy` reinforcement is NOT_TESTED for the specific machine identity.
- ID314 `robot sex` -> IMAGE_TEST_REQUIRED because default-on broad constituents `robot` / `sex` require controlled broad+specific A/B.
- ID325 `tentacle sex` -> IMAGE_TEST_REQUIRED because default-on `tentacles` / `sex` reinforcement is NOT_TESTED.
- ID362 `cum swap` -> IMAGE_TEST_REQUIRED because default-on broad `cum` reinforcement may dilute the transfer relation.
- ID365 `ejaculating while penetrated` -> IMAGE_TEST_REQUIRED because broad `ejaculation` reinforcement may dilute the simultaneous-state relation.
- ID385 `cumdrip from penis` -> IMAGE_TEST_REQUIRED because `penis` / `cum` / `dripping` are all default-on and their combined generation effect is NOT_TESTED.

No new static FIX candidate was supported in Batch4, so `candidate_fixes.csv` remains unchanged. No new backfill pattern was triggered, so `revalidation_queue.csv` remains unchanged.

## Semantic-support coverage
Source rows 25-46 were audited in this batch. Global coverage is now 46/58. Optional/contextual variations were statically resolved when their scope was explicit. Every CORE_SUPPORT+ADDITIVE row in this range was deep-reviewed and unresolved default-on generation value was parked as IMAGE_TEST_REQUIRED rather than guessed PASS.

## Batch 4 false-PASS gate
PASS population: 92. Deterministic sample: 18 PASS rows with A-risk preference. New false-PASS: 0. Batch4 gate PASS. Audit ledger: `pass_sampling_batch4_r2.csv`.

## Critical interpretation rules
- Blank/None is not automatically missing data.
- UNKNOWN / NOT ASSERTED may be correct.
- Requirement metadata is structural and does not itself command support insertion.
- common/rare/co-occurrence statistics remain separate from semantic support.
- Stage10 HOLD knowledge is evidence for experiment design, not production truth.
- CORE_SUPPORT+ADDITIVE default-on effects require generation evidence under R2.
- Exact Special identity remains first-class; broad constituents do not replace it.

## Exact restart
Resume sequence 401 under R2 from the frozen audit order. Read `progress.json`, `RESULT_LEDGER_INDEX.csv`, and `semantic_support_results.csv` first. Do not modify production/main.
