# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 1780
- Cumulative: PASS 1330 / FIX 174 / REVIEW 259 / IMAGE_TEST_REQUIRED 17
- Batch 1-17 R2 acceptance gates: PASS
- Batch 18: partial through 1780
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 1781
- Production/main modified: NO

## Batch 18 partial
1701-1780: PASS 80 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0. Four 20-row append-only blocks are durable and indexed.

A-risk ID1739 and IDs1745-1756 were deep-reviewed. Pose/actor requirements remain structural metadata only; Stage10 experimental knowledge was not promoted to production truth. Damage-state rows 1765-1779 retain broad structural grouping with blank requirements left NOT ASSERTED. Semantic and alias lanes remain separated from generation-response equivalence.

`candidate_fixes.csv` and `revalidation_queue.csv` were checked at every checkpoint and remain unchanged.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 1781. Checkpoint every20. Do not modify production/main.
