# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 1980
- Cumulative: PASS 1528 / FIX 174 / REVIEW 261 / IMAGE_TEST_REQUIRED 17
- Batch 1-19 R2 acceptance gates: PASS
- Batch 20: checkpoints 1-4/5 durable (1901-1980)
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 1981
- Production/main modified: NO

## Batch 20 so far
1901-1980: PASS 80 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0.
A-risk pose/spatial restraint rows were deep-reviewed. Alias canonical linkage remains statistics-only. Semantic-role rows remain search/support-only without direct model-recognition claims. Fluid/action rows preserve exact Special identity without unsupported support insertion.

`candidate_fixes.csv` and `revalidation_queue.csv` checked unchanged at checkpoints. Semantic support remains55/58; common/rare statistics were not conflated with semantic support.

## Exact restart
Resume first-pass at sequence 1981. Checkpoint every20. Do not modify production/main.
