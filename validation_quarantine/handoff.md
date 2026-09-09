# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 1920
- Cumulative: PASS 1468 / FIX 174 / REVIEW 261 / IMAGE_TEST_REQUIRED 17
- Batch 1-19 R2 acceptance gates: PASS
- Batch 20: checkpoint 1/5 durable (1901-1920)
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 1921
- Production/main modified: NO

## Batch 20 checkpoint 1
1901-1920: PASS 20 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0.

A-risk IDs1912 `box tie`, 1914 `frogtie`, 1915 `hogtie`, and1919 `legs bound apart` were deep-reviewed. Pose requirement metadata remains structural only; no automatic support insertion was inferred. Stage10 material was treated as scoped evidence and not promoted to production truth.

`candidate_fixes.csv` and `revalidation_queue.csv` checked unchanged. Semantic support remains55/58; common/rare statistics were not conflated with semantic support.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 1921. Checkpoint every20. Do not modify production/main.
