# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass accepted through: 600
- Cumulative effective verdicts: PASS 543 / FIX 34 / REVIEW 7 / IMAGE_TEST_REQUIRED 16
- Batch 1-6 R2 acceptance gates: PASS
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 601
- Production modified: NO

## Batch 6 acceptance
Batch 6 range 501-600 is durably stored in five 20-row result blocks.

Final Batch6 distribution:
- PASS 92
- FIX 6
- REVIEW 2
- IMAGE_TEST_REQUIRED 0

Non-PASS:
- ID503 `unbirthing` -> REVIEW
- ID535 `straddling paizuri` -> FIX `PoseRequirementOverride=true`
- ID545 `vaginal object insertion` -> FIX `ImplementRequirementOverride=true`
- ID569 `clitoris torture` -> FIX `BodypartRequirementOverride=true`
- ID570 `cunt busting` -> REVIEW
- ID571 `cervix punching` -> FIX `BodypartRequirementOverride=true`
- ID573 `vibrator on clitoris` -> FIX `BodypartRequirementOverride=true` + `SpatialAssignmentOverride=true`
- ID600 `sounding` -> FIX `ImplementRequirementOverride=true`

`pass_sampling_batch6_r2.csv` rechecked 18 / 92 PASS rows, including every A-risk PASS plus deterministic spread controls; new false-PASS: 0. `batch6_integrity_r2.md` records 100/100 reconciliation with no gaps or duplicates.

`candidate_fixes.csv` is consolidated through ID600; candidate-fix blob identity: `e2ac8ee06aeebf2d3f54aa7bb8362b60de6b15c8`. `revalidation_queue.csv` has no new Batch6 item and effective pending remains 0.

Semantic-support coverage remains 53/58; the remaining frozen rows belong to later Special IDs 1159, 1823, and 1839, so no coverage advancement occurred in Batch6.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 601. Process at most 100 Specials, checkpoint every 20, and run the next 100-level integrity + deterministic PASS resampling gate before accepting sequence700. Do not modify production/main.
