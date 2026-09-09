# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 1760
- Cumulative: PASS 1310 / FIX 174 / REVIEW 259 / IMAGE_TEST_REQUIRED 17
- Batch 1-17 R2 acceptance gates: PASS
- Batch 18: partial through 1760
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 1761
- Production/main modified: NO

## Batch 18 partial
1701-1760: PASS 60 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0. Three 20-row append-only blocks are durable and indexed.

ID1739 `defloration` and IDs1745-1756 POSE_COMPOSITION were deep-reviewed as A-risk. PoseRequirementOverride/composition ownership remain structural metadata only. Stage10 evidence supports separating pose/geometry/visibility roles but remains experimental; no automatic support insertion, camera default, or model-family generation response was promoted.

`candidate_fixes.csv` and `revalidation_queue.csv` were checked at each checkpoint and remain unchanged.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 1761. Checkpoint every20. Do not modify production/main.
