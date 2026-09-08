# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Completed Special-level first pass: 200
- Effective counts: PASS 174 / FIX 14 / REVIEW 4 / IMAGE_TEST_REQUIRED 8
- Batch 1 R2 acceptance gate: PASS
- Batch 2 (101-200) acceptance gate: PASS
- Batch 2 deterministic PASS sample: 18 / 90 effective PASS; new false-PASS 0
- Revalidation queue pending: 0
- Semantic-support frozen target: 58 rows; covered: 24
- Next first-pass Special sequence: 201
- Next external batch: 3 (201-300)
- Production modified: NO

## Batch 2 results
Effective Batch2 delta: PASS 90 / FIX 5 / REVIEW 1 / IMAGE_TEST_REQUIRED 4.

### FIX candidates
- ID149 `anal object insertion`: ImplementRequirementOverride=true
- ID153 `pegging`: ImplementRequirementOverride=true
- ID177 `food insertion`: ImplementRequirementOverride=true
- ID182 `object insertion`: ImplementRequirementOverride=true
- ID194 `large insertion`: ImplementRequirementOverride=true

### REVIEW
- ID197 `self fisting`: self-directed identity is explicit, but current INSERTION_STRUCTURED profile lacks `SELF_ACTOR_ROLE`. Existing SELF_ACTION convention is insufficient evidence to force that flag across families, so this remains REVIEW rather than guessed FIX.

### IMAGE_TEST_REQUIRED
- ID122 `missionary`: four enabled CORE_SUPPORT+ADDITIVE rows are NOT_TESTED.
- ID129 `sitting on face`: enabled `sitting` CORE_SUPPORT+ADDITIVE is NOT_TESTED.
- ID161 `anal training`: enabled `anus` CORE_SUPPORT+ADDITIVE is NOT_TESTED.
- ID173 `double penetration`: enabled `object_insertion` and `multiple_penetration` CORE_SUPPORT+ADDITIVE rows are NOT_TESTED.

## Semantic-support coverage
Frozen support rows1-24 are now audited. Contextual/optional rows were accepted only as non-default choices; default-on generation effects were not promoted without image evidence. Global coverage: 24/58.

## Batch 2 sampling gate
`pass_sampling_batch2_r2.csv` records 18/90 effective PASS rows (20%), prioritizing A-risk structural rows across all five checkpoints plus spread B semantic controls. New false-PASS: 0. Therefore Batch2 gate PASS.

## Exact restart
Resume first-pass at sequence201 under R2. Process Batch3 with 20-row append-only checkpoints. Audit any associated semantic-support rows before accepting Special verdicts. At 300 run the next 100-row consistency and deterministic false-PASS sampling gate. Do not modify main/production.
