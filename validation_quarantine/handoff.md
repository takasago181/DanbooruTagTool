# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R1

## Current position
- Target: 2,788 Specials
- Completed: 40
- PASS: 33
- FIX: 2
- REVIEW: 2
- IMAGE_TEST_REQUIRED: 3
- Last completed Special: ID 40 (`hug and suck`)
- Last completed batch: 0 (Batch 1 is partial)
- Next batch: 1
- Next sequence position: 41
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
- Generation Profile classifications acceptable for all 20 rows under R1.
- IDs 16 `cooperative footjob`, 17 `cooperative handjob`, 19 `cuddling handjob` -> `IMAGE_TEST_REQUIRED` because enabled CORE_SUPPORT+ADDITIVE is semantically plausible but NOT_TESTED and currently default-on in Composer.

Checkpoint 2 (sequence 21-40):
- IDs 34 `grabbing another's ass` and 36 `guided crotch grab` -> `FIX` candidates in quarantine. Their identities intrinsically require distinct actor ownership and spatial target assignment, but ActorRequirementOverride / SpatialAssignmentOverride / ACTOR_SEPARATION_REQUIRED are absent. Candidate fixes are recorded; production remains untouched.
- ID22 `ear sex` -> `REVIEW`: internal gloss indicates insertion semantics and may conflict with generic ACTION_INTERACTION, but independent authoritative definition was not recovered yet.
- ID40 `hug and suck` -> `REVIEW`: evidence suggests a compound multi-actor/spatial act, but exact authoritative definition remains insufficient for a static correction.
- ID21 `double handjob` remains ACTION_INTERACTION because multiplicity can describe participants or hands; same conservative logic as ID20 `double footjob`.

## Critical interpretation rules
- Blank/None is not automatically missing data.
- UNKNOWN / NOT ASSERTED may be the correct state.
- Promote missing tag-level structure only when semantic ownership/geometry is independently high-confidence and generation-relevant; do not fill every blank for completeness.
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
Read Issue #32 and durable files. Confirm active rule version R1. Resume Batch 1 at frozen Generation Profile sequence 41. Do not re-count sequence 1-40 unless a revalidation trigger is recorded.

## Chat migration rule
Before leaving any future validation chat, update at minimum:
1. `progress.json`
2. `handoff.md`
3. `results.csv`
4. `candidate_fixes.csv` if FIX exists
5. `revalidation_queue.csv` if rule/evidence changes require revisit

Never rely on conversational memory alone for restart.
