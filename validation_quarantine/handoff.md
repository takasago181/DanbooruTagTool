# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 1220
- Cumulative: PASS 782 / FIX 173 / REVIEW 248 / IMAGE_TEST_REQUIRED 17
- Batch 1-12 R2 acceptance gates: PASS
- Batch 13: partial 1201-1220 checkpointed
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 1221
- Production/main modified: NO

## Batch 13 partial
1201-1220: PASS 5 / FIX 0 / REVIEW 15 / IMAGE_TEST_REQUIRED 0. Result block, candidate-fix block, empty revalidation queue block, progress and handoff are durable. PROVISIONAL / REVIEW_REQUIRED rows without exact source authority remain REVIEW; approved context/direct rows were kept conservative without inventing blank requirement overrides.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 1221. Checkpoint every20. Do not modify production/main.
