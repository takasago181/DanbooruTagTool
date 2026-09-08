# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass accepted through: 500
- Cumulative effective verdicts: PASS 451 / FIX 28 / REVIEW 5 / IMAGE_TEST_REQUIRED 16
- Batch 1-5 R2 acceptance gates: PASS
- Batch 5 full R2 revalidation: COMPLETE (401-500)
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 501
- Production modified: NO

## Batch 5 final acceptance

Full revalidation used five append-only 20-row blocks and matching queue-resolution overlays covering 401-500 exactly once. Effective Batch5 verdicts after revalidation:
- PASS 93
- FIX 6
- REVIEW 0
- IMAGE_TEST_REQUIRED 1

Confirmed corrections in quarantine:
- ID420 `nipple torture` -> `BodypartRequirementOverride=true`
- ID422 `torture instruments` -> `ImplementRequirementOverride=true`
- ID469 `peeing on penis` -> `BodypartRequirementOverride=true` + `SpatialAssignmentOverride=true`
- ID479 `skull fucking` -> `BodypartRequirementOverride=true` + `SpatialAssignmentOverride=true`
- ID490 `bestiality` -> `ActorRequirementOverride=true`
- ID493 `mating (animal)` -> `ActorRequirementOverride=true`

ID488 `xray sex` remains IMAGE_TEST_REQUIRED. Stage10 HOLD/model-dependent visibility evidence was not promoted to production truth.

`pass_sampling_batch5_r2_revalidation.csv` sampled 19 of 93 effective PASS rows with deterministic spread and all surviving A-risk PASS included. New false-PASS found: 0. `batch5_revalidation_integrity_r2.md` records the 100-row integrity check and PASS gate decision.

A-risk ID491 `knotting`, ID492 `animal insertion`, and ID496 `zoophilia` remain PASS after prompt-reference, full revalidation, and post-revalidation sampling cross-check. ID492 specifically permits insertion using animal body parts or similar; this does not universally establish a live animal actor or fixed target, so no speculative override is promoted.

`revalidation_queue.csv` remains the original Batch5 queue snapshot; completed append-only overlays under `revalidation_queue_blocks/` are authoritative for resolved state. Effective pending count is 0.

## Critical interpretation rules
- Blank/None is not automatically missing data; family-rule blanks explicitly mean UNKNOWN/not asserted.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Read Issue #32, R2 rules, `progress.json`, `candidate_fixes.csv`, semantic-support ledger, and this handoff. Resume first-pass at sequence501. Process at most 100 Specials, checkpoint every20, and perform the next 100-level integrity + PASS resampling gate before accepting sequence600. Do not modify production/main.
