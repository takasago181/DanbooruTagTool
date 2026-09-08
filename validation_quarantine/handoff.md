# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R1

## Current position
- Target: 2,788 Specials
- Completed: 20
- PASS: 17
- FIX: 0
- REVIEW: 0
- IMAGE_TEST_REQUIRED: 3
- Last completed Special: ID 20 (`double footjob`)
- Last completed batch: 0 (Batch 1 is partial)
- Next batch: 1
- Next sequence position: 21
- Revalidation pending: 0
- Production modified: NO

## Fixed audit input
See `AUDIT_INPUT_SNAPSHOT.md`.
The first pass uses the frozen production revision captured at setup. Do not silently switch to a later main revision.

## Active method
- 100 Specials per external batch
- 20 x 5 internal blocks
- checkpoint to GitHub every 20 completed Specials
- static integrity pass + fast semantic screening
- mandatory deep review for S/A risk and all non-PASS findings
- mandatory deep review for `CORE_SUPPORT + ADDITIVE`
- PASS sampling every 100 to detect false-PASS drift
- rule changes are versioned and create revalidation work

## Current findings
Checkpoint 1 (sequence 1-20):
- Generation Profile classifications were acceptable for all 20 rows under R1.
- IDs 16 `cooperative footjob`, 17 `cooperative handjob`, and 19 `cuddling handjob` have enabled `CORE_SUPPORT + ADDITIVE` rows that are semantically plausible but have `generation_test_status=NOT_TESTED`.
- Because Stage9 Composer default-selects CORE_SUPPORT+ADDITIVE, these three are parked as `IMAGE_TEST_REQUIRED` until controlled Stage10 comparison decides whether default broad/constituent reinforcement helps versus a minimal Special-only baseline.
- ID20 `double footjob` remains ACTION_INTERACTION rather than MULTI_ACTOR_INTERACTION because its reference meaning permits either multiple participants or use of both feet; no unsupported actor-count assertion was added. Recheck against sibling `double handjob` / `two-footed footjob` during cross-family review.

## Critical interpretation rules
- Blank/None is not automatically missing data.
- UNKNOWN / NOT ASSERTED may be the correct state.
- Generation requirements are structural metadata, not automatic support insertion commands.
- common/rare/co-occurrence statistics are separate from semantic support.
- Stage10 HOLD knowledge is not production truth.
- model-family-specific knowledge must remain scoped.
- Special2788 identity remains first-class and is never replaced by support.

## Durable files
- `README.md`
- `VALIDATION_RULES.md`
- `AUDIT_INPUT_SNAPSHOT.md`
- `progress.json`
- `results.csv`
- `candidate_fixes.csv`
- `revalidation_queue.csv`
- this `handoff.md`

## Exact restart
Read Issue #32 and the durable files above. Confirm active rule version R1. Resume Batch 1 at frozen Generation Profile sequence 21. Do not re-count sequence 1-20 unless a revalidation trigger is recorded.

## Chat migration rule
Before leaving any future validation chat, update at minimum:
1. `progress.json`
2. `handoff.md`
3. `results.csv`
4. `candidate_fixes.csv` if FIX exists
5. `revalidation_queue.csv` if rule/evidence changes require revisit

Never rely on conversational memory alone for restart.
