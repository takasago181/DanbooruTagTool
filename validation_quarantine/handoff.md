# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass checkpointed through: 1120
- Cumulative effective verdicts: PASS 765 / FIX 159 / REVIEW 180 / IMAGE_TEST_REQUIRED 16
- Batch 1-11 R2 acceptance gates: PASS
- Batch 12: IN_PROGRESS (1101-1120 durable)
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 1121
- Production modified: NO

## Batch 12 partial
1101-1120: PASS 4 / FIX 5 / REVIEW 11 / IMAGE_TEST_REQUIRED 0. Results, candidate-fix block, empty queue block, progress and this handoff are durably checkpointed before continuing.

PROVISIONAL / REVIEW_REQUIRED rows without exact source authority remain REVIEW. Concrete fixes are limited to explicit actor/bodypart/object/spatial relations supported by the frozen identity and reviewed sibling conventions.

Semantic-support coverage remains 53/58; remaining rows belong to Special IDs 1159, 1823 and 1839.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 1121. Checkpoint every20. Do not modify production/main.
