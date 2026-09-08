# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Completed Special-level first pass: 80
- PASS: 67
- FIX: 7
- REVIEW: 3
- IMAGE_TEST_REQUIRED: 3
- Last completed Special: ID 80 (`penetrative sex`)
- Last completed batch: 0 (Batch 1 is partial)
- Next batch: 1
- Next Special sequence position: 81
- R2 revalidation/backfill pending: 60 Special entries
- Semantic-support frozen target: 58 data rows
- Semantic-support rows covered: 0
- Production modified: NO

## Fixed audit input
See `AUDIT_INPUT_SNAPSHOT.md`.
The first pass uses the frozen production revision captured at setup. Do not silently switch to a later main revision.

## Rule / concurrency history
- R1 governed the historical Special-level results through sequence 60.
- The scheduled task activated R2 after sequence 40 while the active chat had already loaded R1 and was validating 41-60.
- A stale progress write failed with HTTP 409; no force overwrite occurred.
- Execution reconciliation is recorded in `CONCURRENCY_RECONCILIATION_2026-09-08.md`.
- R2 remains active; direct R2 first-pass processing began at sequence 61.
- Sequences 1-60 are queued for R2-only backfill; their R1 verdicts are not silently relabelled.

## Active R2 method
- 100 Specials per external batch
- 20 x 5 internal blocks
- checkpoint to GitHub every 20 completed Specials
- static integrity pass + fast semantic screening
- mandatory deep review for S/A risk and all non-PASS findings
- mandatory deep review for `CORE_SUPPORT + ADDITIVE`
- full frozen `semantic_support_profiles.csv` row coverage in `semantic_support_results.csv` (58 rows exactly)
- generation-evidence cross-check for high-impact claims per R2
- unresolved generation behavior -> REVIEW or IMAGE_TEST_REQUIRED
- PASS sampling every 100 with R2 escalation thresholds

## Current findings
Sequences 1-20 (R1):
- IDs 16 `cooperative footjob`, 17 `cooperative handjob`, 19 `cuddling handjob` -> IMAGE_TEST_REQUIRED for NOT_TESTED default-on CORE_SUPPORT+ADDITIVE behavior.

Sequences 21-40 (R1):
- IDs 34 `grabbing another's ass`, 36 `guided crotch grab` -> FIX candidates narrowed to ActorRequirementOverride=true only after sibling falsification. Earlier Spatial/ACTOR_SEPARATION proposals are explicitly withdrawn in `candidate_fixes.csv`.
- ID22 `ear sex`, ID40 `hug and suck` -> REVIEW.

Sequences 41-60 (historical R1 due concurrency; queued for R2 backfill):
- FIX: ID49 `presenting own body` -> pose/composition alignment candidate based on sibling ID514 and Danbooru evidence.
- FIX: ID50 `reach-around` -> ActorRequirementOverride=true candidate.
- REVIEW: ID55 `simulated footjob` -> simulated action vs implied/context classification unresolved.
- FIX: ID57 `take your pick` -> POSE_COMPOSITION + multiple-participant structure candidate from Danbooru definition.
- FIX: ID58 `teamwork (sexual)` -> MULTI_ACTOR_INTERACTION candidate; cooperative tag evidence implicates teamwork_(sexual).
- FIX: ID59 `teddy bear sex` -> ImplementRequirementOverride=true candidate; Danbooru identifies sex acts with stuffed toys.

Sequences 61-80 (direct R2):
- All 20 -> PASS.
- ID65 `upright 69`: A-risk deep review confirms POSE_COMPOSITION + pose requirement is intrinsic structure; no automatic support claim added.
- IDs66 `fuck`, 67 `fucking`: A-risk Alias review confirms identity-preserving policy; model response equivalence remains Stage10 HOLD.
- IDs68-80 semantic-only entries match UNMAPPED semantic-bridge state and remain search/support concepts without direct recognition claims.
- No candidate-fix or revalidation-queue changes were required for 61-80; those ledgers remain unchanged by policy.

## Critical interpretation rules
- Blank/None is not automatically missing data.
- UNKNOWN / NOT ASSERTED may be correct.
- Promote missing structure only when independently high-confidence and generation-relevant.
- Generation requirements are structural metadata, not automatic support insertion commands.
- common/rare/co-occurrence statistics are separate from semantic support.
- Stage10 HOLD knowledge is not production truth.
- model-family-specific knowledge remains scoped.
- Special2788 identity remains first-class.
- Danbooru semantic correctness alone does not prove automatic prompt support improves generation.
- Sibling comparison can invalidate an earlier proposed fix; preserve withdrawn proposals rather than erasing audit history.

## Durable files
- `README.md`
- `VALIDATION_RULES.md`
- `AUDIT_INPUT_SNAPSHOT.md`
- `CONCURRENCY_RECONCILIATION_2026-09-08.md`
- `RESULT_LEDGER_INDEX.csv`
- `results_blocks/`
- `progress.json`
- `results.csv` (legacy consolidated snapshot through sequence 60)
- `semantic_support_results.csv`
- `candidate_fixes.csv`
- `revalidation_queue.csv`
- this `handoff.md`

## Exact restart
Read Issue #32 and all durable files. Confirm active rule R2. Resume frozen Special sequence 81. Sequences 1-60 remain R2 backfill work and must be resolved before Batch 1 false-PASS gate is accepted. Do not overwrite historical R1 verdicts.

## Automation safety
Do not run scheduled and manual GitHub writes concurrently. During a manual validation run, pause the scheduled task; re-enable it only after the current checkpoint is fully persisted.

## Chat migration rule
Before moving chats, persist progress, handoff, results, semantic support coverage, candidate fixes, and revalidation queue. Never rely on conversational memory alone.
