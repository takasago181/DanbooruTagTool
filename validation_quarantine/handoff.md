# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass reached: 500
- Effective counts after Batch5 gate: PASS 453 / FIX 26 / REVIEW 5 / IMAGE_TEST_REQUIRED 16
- Batch 1-4 R2 acceptance gates: PASS
- Batch 5 R2 acceptance gate: FAIL
- Revalidation queue pending: 100 (Batch5 sequences 401-500)
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Semantic-support IMAGE_TEST_REQUIRED rows: 29
- First-pass sequence 501 is BLOCKED until Batch5 full revalidation passes
- Exact next work: Batch5 R2 full revalidation starting at sequence 401
- Production modified: NO

## Batch 5 first-pass checkpoints
- `results_blocks/0401_0420.csv`
- `results_blocks/0421_0440.csv`
- `results_blocks/0441_0460.csv`
- `results_blocks/0461_0480.csv`
- `results_blocks/0481_0500.csv`

Initial first-pass delta for 401-500: PASS97 / FIX2 / REVIEW0 / IMAGE_TEST_REQUIRED1.

First-pass non-PASS findings:
- ID488 `xray sex` -> IMAGE_TEST_REQUIRED. Semantic support row51 `x-ray` is a CORE_SUPPORT visualization choice with NOT_TESTED camera/visibility behavior; row53 broad `sex` is default additive and NOT_TESTED. Row52 `cross-section` remains optional PASS.
- ID490 `bestiality` -> FIX candidate `ActorRequirementOverride=true`; independent meaning requires a human/animal participating counterpart. No spatial/separation flag inferred.
- ID493 `mating (animal)` -> FIX candidate `ActorRequirementOverride=true`; mating intrinsically involves participating counterparts. No spatial/separation flag inferred.

## Batch 5 false-PASS gate
PASS population before sampling: 97. Deterministic sample size: 19 with A-risk preference (`pass_sampling_batch5_r2.csv`).

Two A-risk false-PASSes were found:
- ID420 `nipple torture`: independent meaning fixes the target body part as nipple. Candidate: `BodypartRequirementOverride=true`. No implement/spatial promotion.
- ID479 `skull fucking`: independent meaning is sexual insertion targeting the skull. Candidates: `BodypartRequirementOverride=true` and `SpatialAssignmentOverride=true`. No camera/pose support promotion.

Because R2 says any A/S false-PASS or >=2 false-PASSes invalidates the current 100-row batch, Batch5 gate is FAIL. Sequence501 must not begin until full 401-500 revalidation completes and a new acceptance gate is run.

Effective Batch5 state after sampling supersession: PASS95 / FIX4 / REVIEW0 / IMAGE_TEST_REQUIRED1.

## Semantic-support coverage
- Consolidated `semantic_support_results.csv` remains through source row46.
- Durable append-only semantic deltas:
  - `semantic_support_blocks/0047_0050.csv`: ID416 BDSM optional/contextual rows, all scoped PASS.
  - `semantic_support_blocks/0051_0053.csv`: ID488; x-ray and broad sex parked IMAGE_TEST_REQUIRED, cross-section PASS.
- Durable total coverage: 53/58. Remaining rows54-58 occur at later Specials 1159/1823/1839.

## Revalidation queue
`revalidation_queue.csv` now represents the active pending queue and contains Batch5 sequences401-500 as PENDING_R2. Earlier resolved Batch1 queue history is preserved in Git history and `revalidation_blocks/`.

## Candidate fixes added in Batch5
- 420 nipple torture -> BodypartRequirementOverride=true
- 479 skull fucking -> BodypartRequirementOverride=true
- 479 skull fucking -> SpatialAssignmentOverride=true
- 490 bestiality -> ActorRequirementOverride=true
- 493 mating (animal) -> ActorRequirementOverride=true

All remain quarantine-only. No production/main data was modified.

## Critical interpretation rules
- Blank/None is not automatically missing data.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Camera/visibility, broad+specific, canonical/Alias/Semantic generation response remain image-test/model-scope questions where applicable.
- Special2788 exact identity remains first-class.

## Exact restart
Read Issue #32, R2 rules, `progress.json`, `candidate_fixes.csv`, active `revalidation_queue.csv`, and the five Batch5 result blocks. Revalidate sequence401 first. Persist each 20-row revalidation checkpoint before continuing. Do not start sequence501 and do not modify production/main.
