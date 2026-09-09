# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 1260
- Cumulative: PASS 810 / FIX 174 / REVIEW 259 / IMAGE_TEST_REQUIRED 17
- Batch 1-12 R2 acceptance gates: PASS
- Batch 13: partial 1201-1260 checkpointed
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 1261
- Production/main modified: NO

## Batch 13 partial
1201-1260: PASS 33 / FIX 1 / REVIEW 26 / IMAGE_TEST_REQUIRED 0. Three append-only20-row result blocks, candidate-fix blocks, empty queue blocks, progress and handoff are durable. ID1241 `clitoral stimulation` is a quarantine-only structural FIX candidate for `BodypartRequirementOverride=true`; no support auto-insertion is implied.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 1261. Checkpoint every20. Do not modify production/main.
