# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 1740
- Cumulative: PASS 1290 / FIX 174 / REVIEW 259 / IMAGE_TEST_REQUIRED 17
- Batch 1-17 R2 acceptance gates: PASS
- Batch 18: partial through 1740
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 1741
- Production/main modified: NO

## Batch 18 partial
1701-1740: PASS 40 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0. Both 20-row append-only blocks are durable and indexed.

Semantic/search rows remain non-generative support/search metadata. Alias rows preserve exact Special prompt identity and do not claim model-response equivalence. ID1739 `defloration` was treated as A-risk because ActorRequirementOverride=true is asserted; deep review retained it as an intrinsic structural requirement only, not a support insertion or model-family behavior claim.

`candidate_fixes.csv` and `revalidation_queue.csv` were checked at each checkpoint and remain unchanged.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 1741. Checkpoint every20. Do not modify production/main.
