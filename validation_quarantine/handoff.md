# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2080
- Cumulative: PASS 1626 / FIX 174 / REVIEW 263 / IMAGE_TEST_REQUIRED 17
- Batch 1-20 R2 acceptance gates: PASS
- Batch 21: partial checkpoint through 2080; 100-Special gate not yet run
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 2081
- Production/main modified: NO

## Batch 21 partial checkpoint
2001-2020: PASS 20 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0.
2021-2040: PASS 18 / FIX 0 / REVIEW 2 / IMAGE_TEST_REQUIRED 0.
2041-2060: PASS 20 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0.
2061-2080: PASS 20 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0.

IDs 2029 `grabbing another's breast` and 2031 `guided breast grab` remain A-risk REVIEW because exact row-specific independent evidence was not attached. ID2028 `cooperative breast smother` deep-review PASS with explicit multi-actor/actor/spatial/separation structure; structural only, no support insertion.

Semantic-role IDs2063-2067 remain search/support-only; alias ID2068 preserves exact Special identity with canonical linkage statistics-only. `candidate_fixes.csv` and `revalidation_queue.csv` were checked and require no new entries. Semantic support remains 55/58.

## Exact restart
Resume first-pass at sequence 2081. Checkpoint every 20. Do not modify production/main.
