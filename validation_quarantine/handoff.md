# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 1720
- Cumulative: PASS 1270 / FIX 174 / REVIEW 259 / IMAGE_TEST_REQUIRED 17
- Batch 1-17 R2 acceptance gates: PASS
- Batch 18: partial through 1720
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 1721
- Production/main modified: NO

## Batch 18 partial
1701-1720: PASS 20 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0. The append-only result block is durable and indexed.

1701-1719 are APPROVED_SEMANTIC_ROLE and remain search/support-only without direct model-recognition claims. 1720 `clitoris clamp` is APPROVED_STATIC RESTRAINT_IMPLEMENT/DIRECT; blank requirement overrides are treated as NOT ASSERTED and no redundant support insertion is inferred.

`candidate_fixes.csv` and `revalidation_queue.csv` were checked at this checkpoint and remain unchanged.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 1721. Checkpoint every20. Do not modify production/main.
