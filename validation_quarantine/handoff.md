# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass reached: 500
- Effective counts after completed Batch5 revalidation checkpoints: PASS 452 / FIX 27 / REVIEW 5 / IMAGE_TEST_REQUIRED 16
- Batch 1-4 R2 acceptance gates: PASS
- Batch 5 R2 acceptance gate: FAIL
- Batch 5 full revalidation completed: 40 / 100 (401-440)
- Effective pending revalidation: 60 (441-500)
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- First-pass sequence 501 is BLOCKED until Batch5 full revalidation passes
- Exact next work: Batch5 R2 full revalidation starting at sequence 441
- Production modified: NO

## Durable revalidation checkpoints
- `revalidation_blocks/0401_0420.csv`
- `revalidation_blocks/0421_0440.csv`
- matching queue-resolution overlays in `revalidation_queue_blocks/`
- `candidate_fixes.csv` updated when findings changed

### 401-420
- IDs401-419 retain PASS.
- ID420 `nipple torture` retains FIX: `BodypartRequirementOverride=true`.

### 421-440
- ID422 `torture instruments` is a newly discovered A-risk false-PASS.
- Production family `GFR_RESTRAINT_IMPLEMENT` has blank/UNKNOWN requirement defaults; the Special itself is explicitly an implement/object concept, so `ImplementRequirementOverride=true` is required as quarantined structural metadata.
- ID425 `genital torture` remains PASS because this production row is SEMANTIC_SUPPORT/SUPPORT, not a direct structural profile; direct-profile requirement rules are not promoted into the semantic/search-only lane.
- Remaining rows421,423-440 retain PASS.

`revalidation_queue.csv` is the original Batch5 queue snapshot. Completed append-only queue overlays in `revalidation_queue_blocks/` are authoritative for restart, so 401-440 must not be processed again. Effective pending count is 60.

## Batch 5 still-active findings ahead
- ID479 `skull fucking` -> FIX candidates `BodypartRequirementOverride=true` + `SpatialAssignmentOverride=true` (known A-risk false-PASS; pending revalidation).
- ID488 `xray sex` -> IMAGE_TEST_REQUIRED.
- ID490 `bestiality` -> FIX `ActorRequirementOverride=true`.
- ID493 `mating (animal)` -> FIX `ActorRequirementOverride=true`.

## Critical interpretation rules
- Blank/None is not automatically missing data; in family rules blank explicitly means UNKNOWN/not asserted.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Read Issue #32, R2 rules, `progress.json`, `candidate_fixes.csv`, original `revalidation_queue.csv`, completed `revalidation_queue_blocks/`, the five Batch5 first-pass result blocks, and both completed Batch5 revalidation blocks. Resume at sequence441. Persist the next 20-row revalidation checkpoint before continuing. Do not start sequence501 and do not modify production/main.
