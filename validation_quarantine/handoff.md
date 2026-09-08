# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass durably checkpointed through: 720
- Cumulative effective verdicts: PASS 629 / FIX 66 / REVIEW 9 / IMAGE_TEST_REQUIRED 16
- Batch 1-7 R2 acceptance gates: PASS
- Batch 8: partial (701-720 saved; gate pending)
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 721
- Production modified: NO

## Batch 8 partial checkpoint
701-720 is stored in `results_blocks/0701_0720.csv` with companion `candidate_fix_blocks/0701_0720.csv` and `revalidation_queue_blocks/0701_0720.csv`.

Delta: PASS 10 / FIX 8 / REVIEW 2 / IMAGE_TEST_REQUIRED 0.

Notable FIX patterns: explicit pectoral/prostate/testicle/penis bodypart targets and distinct female/futa/male actor roles. ID706 `penis sheath` and ID710 `covering anus` remain REVIEW because a family correction cannot be established safely from the frozen metadata alone.

Semantic-support coverage remains 53/58; remaining frozen rows belong to later Special IDs 1159, 1823, and 1839.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 721. Continue at most through 800, checkpoint every 20, then run Batch8 integrity + deterministic PASS resampling before acceptance. Do not modify production/main.
