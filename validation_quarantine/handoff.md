# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 1620
- Cumulative: PASS 1170 / FIX 174 / REVIEW 259 / IMAGE_TEST_REQUIRED 17
- Batch 1-16 R2 acceptance gates: PASS
- Batch 17: partial 1601-1620 checkpointed
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 1621
- Production/main modified: NO

## Batch 17 partial
1601-1620: PASS 20 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0. The append-only result block is durable. All rows are APPROVED_IDENTITY_ONLY / ALIAS_TARGET_RESOLVED / ALIAS_PRESERVE identity-preservation records. Exact Special prompt identity is preserved; canonical_target remains statistical linkage only and is not treated as prompt replacement or generation-equivalence evidence. No enabled semantic-support row occurs in this checkpoint.

`candidate_fixes.csv` and `revalidation_queue.csv` were checked and unchanged.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 1621. Checkpoint every20. Do not modify production/main.
