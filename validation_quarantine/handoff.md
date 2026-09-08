# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass accepted through: 600
- Batch 7 partial checkpoint durably completed through: 660
- Cumulative effective verdicts through 660: PASS 593 / FIX 44 / REVIEW 7 / IMAGE_TEST_REQUIRED 16
- Batch 1-6 R2 acceptance gates: PASS
- Batch 7 acceptance gate: PENDING until sequence700 integrity + PASS sampling
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 661
- Production modified: NO

## Batch 7 partial checkpoints
- 601-620: PASS13 / FIX7
- 621-640: PASS17 / FIX3
- 641-660: PASS20 / FIX0
- Current Batch7 delta through660: PASS50 / FIX10 / REVIEW0 / IMAGE_TEST_REQUIRED0
- Revalidation queue deltas: none

Append-only candidate-fix blocks are authoritative partial deltas; aggregate `candidate_fixes.csv` remains consolidated through ID600 until the Batch7 gate reconciliation.

Semantic-support coverage remains 53/58; remaining frozen rows belong to later Special IDs 1159, 1823, and 1839.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 661. Continue checkpointing every20. At sequence700 run exact100-row reconciliation, deterministic 20% PASS re-audit with A-risk preference, consolidate candidate-fix deltas, and only then accept Batch7. Do not modify production/main.
