# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass accepted through: 600
- Batch 7 partial checkpoint durably completed through: 620
- Cumulative effective verdicts through 620: PASS 556 / FIX 41 / REVIEW 7 / IMAGE_TEST_REQUIRED 16
- Batch 1-6 R2 acceptance gates: PASS
- Batch 7 acceptance gate: PENDING until sequence700 integrity + PASS sampling
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 621
- Production modified: NO

## Batch 7 partial checkpoint 601-620
Durable files:
- `results_blocks/0601_0620.csv`
- `candidate_fix_blocks/0601_0620.csv`
- `revalidation_queue_blocks/0601_0620.csv` (no delta)

Delta: PASS 13 / FIX 7 / REVIEW 0 / IMAGE_TEST_REQUIRED 0.

FIX candidates in this block:
- ID604 `vibrator on penis`: bodypart + spatial
- ID614 `tentacle on penis`: bodypart + spatial
- ID616 `ball busting`: bodypart
- ID617 `cbt`: bodypart
- ID618 `denki anma`: bodypart
- ID619 `squeezing testicles`: bodypart
- ID620 `biting penis`: bodypart

These are structural requirement candidates only; they do not authorize support-tag injection or production writes. `candidate_fixes.csv` remains consolidated through ID600 during the partial batch; append-only candidate-fix blocks are authoritative deltas until Batch7 reconciliation.

Semantic-support coverage remains 53/58; remaining frozen rows belong to later Special IDs 1159, 1823, and 1839.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 621. Continue checkpointing every20. At sequence700 run exact100-row reconciliation, deterministic 20% PASS re-audit with A-risk preference, consolidate candidate-fix deltas, and only then accept Batch7. Do not modify production/main.
