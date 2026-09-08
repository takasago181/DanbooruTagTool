# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass reached: 500
- Effective counts after completed Batch5 revalidation checkpoints: PASS 451 / FIX 28 / REVIEW 5 / IMAGE_TEST_REQUIRED 16
- Batch 1-4 R2 acceptance gates: PASS
- Batch 5 R2 acceptance gate: FAIL
- Batch 5 full revalidation completed: 80 / 100 (401-480)
- Effective pending revalidation: 20 (481-500)
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- First-pass sequence 501 is BLOCKED until Batch5 full revalidation and final acceptance gate pass
- Exact next work: Batch5 R2 full revalidation starting at sequence 481
- Production modified: NO

## Durable revalidation checkpoints
- `revalidation_blocks/0401_0420.csv`
- `revalidation_blocks/0421_0440.csv`
- `revalidation_blocks/0441_0460.csv`
- `revalidation_blocks/0461_0480.csv`
- matching queue-resolution overlays in `revalidation_queue_blocks/`
- `candidate_fixes.csv` updated whenever a new finding changed the candidate set

## Confirmed/new Batch5 corrections during full revalidation
- ID420 `nipple torture` -> retain FIX, `BodypartRequirementOverride=true`.
- ID422 `torture instruments` -> new FIX, `ImplementRequirementOverride=true`; family defaults are UNKNOWN and do not encode the intrinsic implement requirement.
- ID469 `peeing on penis` -> new FIX, `BodypartRequirementOverride=true` + `SpatialAssignmentOverride=true`; cross-consistent with reviewed fixed-bodypart contact sibling ID265.
- ID479 `skull fucking` -> retain FIX, `BodypartRequirementOverride=true` + `SpatialAssignmentOverride=true`.

Rows441-460 produced no new false-PASS. Semantic/search-only rows continue to be kept separate from direct structural profiles; no direct requirement metadata is promoted solely from phrase decomposition in that lane.

`revalidation_queue.csv` is the original Batch5 queue snapshot. Completed append-only queue overlays in `revalidation_queue_blocks/` are authoritative for restart, so 401-480 must not be processed again. Effective pending count is 20.

## Remaining first-pass findings at 481-500
- ID488 `xray sex` -> IMAGE_TEST_REQUIRED.
- ID490 `bestiality` -> FIX `ActorRequirementOverride=true`.
- ID493 `mating (animal)` -> FIX `ActorRequirementOverride=true`.
- Other A-risk rows 491/492/496 require revalidation cross-check before Batch5 can be accepted.

## Critical interpretation rules
- Blank/None is not automatically missing data; family-rule blanks explicitly mean UNKNOWN/not asserted.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Read Issue #32, R2 rules, `progress.json`, `candidate_fixes.csv`, original `revalidation_queue.csv`, completed queue overlays, the five Batch5 first-pass result blocks, and four completed Batch5 revalidation blocks. Resume at sequence481. Persist the 481-500 checkpoint, then run the full Batch5 integrity and false-PASS acceptance checks before sequence501. Do not modify production/main.
