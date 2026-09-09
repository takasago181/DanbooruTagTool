# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2060
- Cumulative: PASS 1606 / FIX 174 / REVIEW 263 / IMAGE_TEST_REQUIRED 17
- Batch 1-20 R2 acceptance gates: PASS
- Batch 21: partial checkpoint through 2060; 100-Special gate not yet run
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 2061
- Production/main modified: NO

## Batch 21 partial checkpoint
2001-2020: PASS 20 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0.
2021-2040: PASS 18 / FIX 0 / REVIEW 2 / IMAGE_TEST_REQUIRED 0.
2041-2060: PASS 20 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0.

IDs 2029 `grabbing another's breast` and 2031 `guided breast grab` remain A-risk REVIEW. Existing sibling audit history suggests ActorRequirementOverride=true may be warranted, but exact row-specific independent evidence was not attached, so R2 does not allow a guessed PASS/FIX.

ID2028 `cooperative breast smother` deep-review PASS: explicit multi-actor/actor/spatial/separation metadata is internally consistent and remains structural only.

`candidate_fixes.csv` and `revalidation_queue.csv` were checked and require no new entries. Semantic support remains 55/58.

## Exact restart
Resume first-pass at sequence 2061. Checkpoint every 20. Do not modify production/main.
