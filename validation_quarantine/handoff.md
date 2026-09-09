# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 1540
- Cumulative: PASS 1090 / FIX 174 / REVIEW 259 / IMAGE_TEST_REQUIRED 17
- Batch 1-15 R2 acceptance gates: PASS
- Batch 16: partial through 1540
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 1541
- Production/main modified: NO

## Batch 16 partial
1501-1540: PASS 40 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0. Two append-only 20-row result blocks are durable.

All rows are APPROVED_IDENTITY_ONLY / ALIAS_TARGET_RESOLVED / ALIAS_PRESERVE. Exact Special prompt identity is preserved; canonical_target is statistical linkage only, not a prompt replacement or generation-equivalence claim. No enabled semantic-support row occurs in these checkpoints.

`candidate_fixes.csv` and `revalidation_queue.csv` were checked at each 20-Special checkpoint; no additions were required.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 1541. Checkpoint every20. Do not modify production/main.
