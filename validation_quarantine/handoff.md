# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2040
- Cumulative: PASS 1586 / FIX 174 / REVIEW 263 / IMAGE_TEST_REQUIRED 17
- Batch 1-20 R2 acceptance gates: PASS
- Batch 21: partial checkpoint through 2040; 100-Special gate not yet run
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 2041
- Production/main modified: NO

## Batch 21 partial checkpoint
2001-2020: PASS 20 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0. Result block `results_blocks/2001_2020.csv` is durable.

2021-2040: PASS 18 / FIX 0 / REVIEW 2 / IMAGE_TEST_REQUIRED 0. Result block `results_blocks/2021_2040.csv` is durable.

IDs 2029 `grabbing another's breast` and 2031 `guided breast grab` are A-risk REVIEW. Existing sibling audit history (ID34 another-person grab; ID36 guided crotch grab) suggests ActorRequirementOverride=true may be warranted, but R2 does not allow the production row plus analogous prior metadata to self-certify a FIX. Exact row-specific independent evidence was not attached at this checkpoint, so both remain unresolved rather than guessed.

ID2028 `cooperative breast smother` deep-review PASS: MULTI_ACTOR_INTERACTION, ActorRequirementOverride=true, SpatialAssignmentOverride=true, and ACTOR_SEPARATION_REQUIRED are internally consistent. This remains structural metadata only and does not authorize support-tag insertion.

`candidate_fixes.csv` and `revalidation_queue.csv` were checked and require no new entries at this checkpoint. Semantic support remains 55/58.

## Exact restart
Resume first-pass at sequence 2041. Checkpoint every 20. Do not modify production/main.
