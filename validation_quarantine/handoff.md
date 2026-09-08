# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass reached: 500
- Effective counts after full Batch5 revalidation: PASS 451 / FIX 28 / REVIEW 5 / IMAGE_TEST_REQUIRED 16
- Batch 1-4 R2 acceptance gates: PASS
- Batch 5 full R2 revalidation: COMPLETE (401-500)
- Batch 5 acceptance gate: PENDING_FINAL_GATE
- Effective pending revalidation: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- First-pass sequence 501 remains BLOCKED until post-revalidation integrity + PASS-resampling gate completes
- Production modified: NO

## Durable Batch5 revalidation checkpoints
- `revalidation_blocks/0401_0420.csv`
- `revalidation_blocks/0421_0440.csv`
- `revalidation_blocks/0441_0460.csv`
- `revalidation_blocks/0461_0480.csv`
- `revalidation_blocks/0481_0500.csv`
- matching queue-resolution overlays under `revalidation_queue_blocks/`

## Corrections confirmed by full revalidation
- ID420 `nipple torture` -> FIX: `BodypartRequirementOverride=true`.
- ID422 `torture instruments` -> FIX: `ImplementRequirementOverride=true`.
- ID469 `peeing on penis` -> FIX: `BodypartRequirementOverride=true` + `SpatialAssignmentOverride=true`.
- ID479 `skull fucking` -> FIX: `BodypartRequirementOverride=true` + `SpatialAssignmentOverride=true`.
- ID490 `bestiality` -> FIX: `ActorRequirementOverride=true`.
- ID493 `mating (animal)` -> FIX: `ActorRequirementOverride=true`.
- ID488 `xray sex` -> retain IMAGE_TEST_REQUIRED; Stage10/model-dependent visibility behavior remains unpromoted.

A-risk ID491 `knotting`, ID492 `animal insertion`, and ID496 `zoophilia` remain PASS after prompt-reference and prior deterministic sampling cross-check. In particular, ID492's frozen reference says insertion using animal body parts or similar; this does not universally establish a live animal actor or one fixed insertion target, so no speculative actor/bodypart/implement override is promoted.

`revalidation_queue.csv` remains the original Batch5 queue snapshot. The five append-only queue overlays in `revalidation_queue_blocks/` are authoritative for completed state; effective pending count is 0.

## Critical interpretation rules
- Blank/None is not automatically missing data; family-rule blanks explicitly mean UNKNOWN/not asserted.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Run the Batch5 post-revalidation integrity check over the five 20-row revalidation blocks and five queue overlays. Then re-sample the effective PASS population under R2, with A-risk preference. Only if no new false-PASS is found may Batch5 acceptance become PASS and sequence501 be unblocked. Do not modify production/main.
