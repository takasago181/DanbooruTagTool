# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 1800
- Cumulative: PASS 1349 / FIX 174 / REVIEW 260 / IMAGE_TEST_REQUIRED 17
- Batch 1-18 R2 acceptance gates: PASS
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 1801
- Production/main modified: NO

## Batch 18 complete
1701-1800: PASS 99 / FIX 0 / REVIEW 1 / IMAGE_TEST_REQUIRED 0. Five 20-row append-only blocks are durable and indexed with no gaps or duplicates.

A-risk ID1739 and IDs1745-1756 were deep-reviewed. Pose/actor requirements remain structural metadata only; Stage10 experimental knowledge was not promoted to production truth. ID1787 `vaginal prolapse` remains S-risk REVIEW because its BODY_ATTRIBUTE/body_target_or_attribute classification conflicts with sibling ID1759 `prolapse` BODY_STATE/body_state and retrieved frozen evidence is insufficient to choose a concrete correction safely.

Deterministic R2 PASS re-audit checked 20/99 PASS rows, including all 13 A-risk PASS rows. New false-PASS: 0. Batch18 acceptance gate: PASS.

`candidate_fixes.csv` and `revalidation_queue.csv` were checked at every checkpoint and remain unchanged. Semantic support remains 55/58; common/rare statistics were not conflated with semantic support.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 1801. Checkpoint every20. Do not modify production/main.
