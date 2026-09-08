# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass accepted through: 500
- Batch 6 first-pass checkpointed through: 540 (100-level gate not yet run)
- Cumulative provisional/effective verdicts through 540: PASS 489 / FIX 29 / REVIEW 6 / IMAGE_TEST_REQUIRED 16
- Batch 1-5 R2 acceptance gates: PASS
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 541
- Production modified: NO

## Batch 6 partial

Durable blocks: `results_blocks/0501_0520.csv`, `results_blocks/0521_0540.csv`.

Findings so far:
- ID503 `unbirthing` -> REVIEW; meaning-relevant target/spatial structure unresolved, no guessed correction.
- ID535 `straddling paizuri` -> FIX candidate `PoseRequirementOverride=true`, sibling-calibrated against ID272.
- `candidate_fixes.csv` synchronized through ID535.
- `revalidation_queue.csv` unchanged; effective pending 0.
- No frozen semantic-support rows belong to 501-540; coverage remains 53/58.

## Critical interpretation rules
- Blank/None is not automatically missing data; family-rule blanks mean UNKNOWN/not asserted.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 541. Continue 20-row checkpoints. Do not accept Batch6 through600 until 100-row integrity + deterministic PASS resampling complete. Do not modify production/main.
