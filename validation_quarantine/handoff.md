# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass accepted through: 500
- Batch 6 first-pass checkpointed through: 520 (100-level gate not yet run)
- Cumulative provisional/effective verdicts through 520: PASS 470 / FIX 28 / REVIEW 6 / IMAGE_TEST_REQUIRED 16
- Batch 1-5 R2 acceptance gates: PASS
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 521
- Production modified: NO

## Batch 6 partial

Checkpoint `results_blocks/0501_0520.csv` is durably stored. Delta: PASS 19 / REVIEW 1.

- ID503 `unbirthing` -> REVIEW. The exact body-site/spatial relation appears meaning-relevant, but current independent evidence is insufficient to promote Bodypart/Spatial overrides safely. Fail closed; no candidate fix created.
- IDs501-502 and 504-520 remain PASS under R2 using existing sibling conventions.
- `candidate_fixes.csv` unchanged at blob `dbffff800ea67ef4250d261a5fb01e5a95fab2cb` for this checkpoint.
- `revalidation_queue.csv` has no new queue item; effective pending remains 0.
- No semantic-support source row belongs to 501-520; coverage remains 53/58.

## Critical interpretation rules
- Blank/None is not automatically missing data; family-rule blanks explicitly mean UNKNOWN/not asserted.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 521. Continue 20-row durable checkpoints. Batch 6 must not be accepted through 600 until 100-row integrity and deterministic PASS resampling complete. Do not modify production/main.
