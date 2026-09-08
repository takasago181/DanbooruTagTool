# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Completed Special-level first pass: 40
- PASS: 33
- FIX: 2
- REVIEW: 2
- IMAGE_TEST_REQUIRED: 3
- Last completed Special: ID 40 (`hug and suck`)
- Last completed batch: 0 (Batch 1 is partial)
- Next batch: 1
- Next Special sequence position: 41
- R2 revalidation/backfill pending: 40 Special entries
- Semantic-support row coverage: ledger created; frozen snapshot total must be populated/reconciled
- Production modified: NO

## Fixed audit input
See `AUDIT_INPUT_SNAPSHOT.md`.
The first pass uses the frozen production revision captured at setup. Do not silently switch to a later main revision.

## Rule history
- R1 governed sequences 1-40.
- R2 is active after sequence 40.
- Existing R1 Special-level verdicts remain historical and are not silently rewritten.
- Sequences 1-40 are queued for the additional R2 obligations only: row-complete semantic-support coverage where applicable and mandatory generation-evidence cross-checks.
- R2 backfill must be resolved before Batch 1's 100-Special false-PASS gate is accepted.

## Active R2 method
- 100 Specials per external batch
- 20 x 5 internal blocks
- checkpoint to GitHub every 20 completed Specials
- static integrity pass + fast semantic screening
- mandatory deep review for S/A risk and all non-PASS findings
- mandatory deep review for `CORE_SUPPORT + ADDITIVE`
- full frozen `semantic_support_profiles.csv` row coverage recorded in `semantic_support_results.csv`
- generation-evidence cross-check required for high-impact claims: S/A, default-on support, model-family-sensitive behavior, camera/pose/visibility/geometry, unusual anatomy/Negative interaction, broad+specific, canonical/Alias/Semantic response, multiple Special, LoRA/prompt-density behavior
- relevant KNOWLEDGE handoff / PROMPT evidence must be consulted when available; neither is automatic production truth
- unresolved generation behavior -> `REVIEW` or `IMAGE_TEST_REQUIRED`, not guessed PASS
- PASS sampling every 100 with R2 numeric escalation thresholds
- rule changes remain versioned and create revalidation work

## R2 false-PASS gate
Per completed 100-Special batch:
- sample 20% of PASS, min 10, max 20, deterministic/reproducible and stratified where practical
- 0 false-PASS -> batch accepted
- exactly 1 B/C false-PASS -> expand sample up to 40 and enqueue affected pattern
- >=2 false-PASS -> batch invalid; root-cause + full current-batch revalidation
- any S/A false-PASS -> batch invalid regardless of count
- repeated root cause across batches -> systemic retroactive revalidation

## Current findings
Checkpoint 1 (sequence 1-20, R1):
- Generation Profile classifications acceptable for all 20 rows under R1.
- IDs 16 `cooperative footjob`, 17 `cooperative handjob`, 19 `cuddling handjob` -> `IMAGE_TEST_REQUIRED` because enabled CORE_SUPPORT+ADDITIVE is semantically plausible but NOT_TESTED and currently default-on in Composer.

Checkpoint 2 (sequence 21-40, R1):
- IDs 34 `grabbing another's ass` and 36 `guided crotch grab` -> `FIX` candidates in quarantine. Their identities intrinsically require distinct actor ownership and spatial target assignment, but ActorRequirementOverride / SpatialAssignmentOverride / ACTOR_SEPARATION_REQUIRED are absent. Candidate fixes are recorded; production remains untouched.
- ID22 `ear sex` -> `REVIEW`: internal gloss indicates insertion semantics and may conflict with generic ACTION_INTERACTION, but independent authoritative definition was not recovered yet.
- ID40 `hug and suck` -> `REVIEW`: evidence suggests a compound multi-actor/spatial act, but exact authoritative definition remains insufficient for a static correction.
- ID21 `double handjob` remains ACTION_INTERACTION under R1 because multiplicity can describe participants or hands; R2 now requires the added generation-evidence cross-check for this A-priority decision.

## Critical interpretation rules
- Blank/None is not automatically missing data.
- UNKNOWN / NOT ASSERTED may be the correct state.
- Promote missing tag-level structure only when semantic ownership/geometry is independently high-confidence and generation-relevant; do not fill every blank for completeness.
- Generation requirements are structural metadata, not automatic support insertion commands.
- common/rare/co-occurrence statistics are separate from semantic support.
- Stage10 HOLD knowledge is not production truth.
- model-family-specific knowledge must remain scoped.
- Special2788 identity remains first-class and is never replaced by support.
- Danbooru semantic correctness alone does not prove that automatic prompt support improves image generation.

## Durable files
- `README.md`
- `VALIDATION_RULES.md`
- `AUDIT_INPUT_SNAPSHOT.md`
- `progress.json`
- `results.csv`
- `semantic_support_results.csv`
- `candidate_fixes.csv`
- `revalidation_queue.csv`
- this `handoff.md`

## Exact restart
Read Issue #32 and all durable files. Confirm active rule version R2. Resume Special sequence 41 from the frozen input under R2. Process the queued R1 sequences 1-40 for R2-only backfill before accepting Batch 1's false-PASS sampling gate. Do not erase or relabel historical R1 Special-level verdicts merely because R2 added new obligations.

## Chat migration rule
Before leaving any future validation chat, update at minimum:
1. `progress.json`
2. `handoff.md`
3. `results.csv`
4. `semantic_support_results.csv`
5. `candidate_fixes.csv` if FIX exists
6. `revalidation_queue.csv` if rule/evidence changes require revisit

Never rely on conversational memory alone for restart.
