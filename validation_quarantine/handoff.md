# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass reached: 500
- Effective first-pass counts remain: PASS 453 / FIX 26 / REVIEW 5 / IMAGE_TEST_REQUIRED 16
- Batch 1-4 R2 acceptance gates: PASS
- Batch 5 R2 acceptance gate: FAIL
- Batch 5 full revalidation completed: 20 / 100 (sequences 401-420)
- Effective pending revalidation after checkpoint overlay: 80 (421-500)
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- First-pass sequence 501 is BLOCKED until Batch5 full revalidation passes
- Exact next work: Batch5 R2 full revalidation starting at sequence 421
- Production modified: NO

## Durable revalidation checkpoint 401-420
- Results: `revalidation_blocks/0401_0420.csv`
- Queue-resolution overlay: `revalidation_queue_blocks/0401_0420.csv`
- Candidate fixes: `candidate_fixes.csv` already contains the retained ID420 correction
- Progress: `progress.json`
- This handoff file records the checkpoint restart state

Verdicts after revalidation:
- IDs401-419: retain PASS under R2.
- ID420 `nipple torture`: retain FIX; `BodypartRequirementOverride=true` remains the minimal quarantined structural correction. No implement or spatial promotion.
- No additional false-PASS was found in this 20-row checkpoint.
- Semantic support rows47-50 attached to ID416 remain covered with their existing scoped verdicts; no production promotion occurs.

`revalidation_queue.csv` is the original active Batch5 queue snapshot. For completed blocks, append-only `revalidation_queue_blocks/` overlays are authoritative; therefore rows401-420 must not be processed again. Effective pending count is 80 even though the original snapshot still lists all 100 rows.

## Batch 5 first-pass findings still active
- ID488 `xray sex` -> IMAGE_TEST_REQUIRED. Controlled generation remains required for x-ray/default additive behavior.
- ID490 `bestiality` -> FIX candidate `ActorRequirementOverride=true`.
- ID493 `mating (animal)` -> FIX candidate `ActorRequirementOverride=true`.
- ID479 `skull fucking` -> known A-risk false-PASS; candidate `BodypartRequirementOverride=true` + `SpatialAssignmentOverride=true`; still pending full revalidation at its sequence.

## Critical interpretation rules
- Blank/None is not automatically missing data.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Camera/visibility, broad+specific, canonical/Alias/Semantic generation response remain image-test/model-scope questions where applicable.
- Special2788 exact identity remains first-class.

## Exact restart
Read Issue #32, R2 rules, `progress.json`, `candidate_fixes.csv`, the original `revalidation_queue.csv`, all completed `revalidation_queue_blocks/` overlays, the five Batch5 first-pass result blocks, and `revalidation_blocks/0401_0420.csv`. Resume at sequence421. Persist the next 20-row revalidation checkpoint before continuing. Do not start sequence501 and do not modify production/main.
