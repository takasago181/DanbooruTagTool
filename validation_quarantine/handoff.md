# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Completed Special-level first pass: 100
- Effective PASS: 84
- FIX: 9
- REVIEW: 3
- IMAGE_TEST_REQUIRED: 4
- Last completed Special: ID 100 (`after fellatio`)
- Batch 1 first-pass: COMPLETE
- Batch 1 R2 acceptance gate: FAILED
- Batch 1 R2 revalidation checkpoint: 40 / 100
- Next Batch 1 revalidation position: 41
- Next new Special sequence position: 101 (BLOCKED)
- Revalidation queue remains pending until full Batch 1 gate acceptance: 100 entries
- Semantic-support frozen target: 58 data rows
- Semantic-support rows covered: 9
- Semantic-support IMAGE_TEST_REQUIRED: 6
- False-PASS found: 1 (S risk; ID88)
- Production modified: NO

## Why Batch 1 failed
ID88 `masturbation` had an enabled `CORE_SUPPORT + ADDITIVE` row for `solo` that was omitted from the immutable 81-100 Special-level verdict. R2 classifies this as an S-risk false-PASS because default-on additive generation value is NOT_TESTED. `revalidation_results.csv` supersedes ID88 to `IMAGE_TEST_REQUIRED`; sequence101 remains blocked until full Batch1 revalidation and the R2 gate pass.

## R2 revalidation checkpoints
### 1-20
- No new false-PASS.
- IDs16/17/19 remain IMAGE_TEST_REQUIRED because their default-on CORE_SUPPORT+ADDITIVE rows require controlled A/B.
- ID20 A-priority PASS retained after Stage10 cross-check; `double footjob` does not necessarily imply two actors.

### 21-40
- No new false-PASS.
- ID21 `double handjob`: A-priority PASS retained; two hands does not necessarily imply two actors.
- ID22 `ear sex`: REVIEW retained; independent authoritative meaning remains insufficient for insertion-family promotion.
- ID25 `footjob from behind`: A-priority PASS retained; viewpoint/spatial support is not auto-promoted from the Special name.
- ID34 `grabbing another's ass`: narrowed FIX retained for ActorRequirementOverride=true only. Spatial/ACTOR_SEPARATION proposals remain withdrawn.
- ID36 `guided crotch grab`: narrowed FIX retained for ActorRequirementOverride=true only.
- ID40 `hug and suck`: REVIEW retained; actor/spatial correction lacks sufficiently strong independent authority.
- Candidate-fix ledger unchanged; no new candidate added.

Queue entries intentionally remain pending until complete 1-100 R2 gate acceptance, so partial checkpoint completion cannot be mistaken for an accepted batch.

## Direct R2 first-pass work already completed
- 61-80: 20 PASS after R2 screening; ID65 deep-reviewed; IDs66/67 Alias response remains Stage10 HOLD.
- 81-100: initial 18 PASS, 2 FIX; ID92/94 ImplementRequirementOverride=true candidates; ID88 later superseded to IMAGE_TEST_REQUIRED by sidecar audit.

## Semantic-support coverage completed so far
Frozen rows 1-9 are recorded in `semantic_support_results.csv`:
- ID16 rows1-3 CORE_SUPPORT+ADDITIVE -> IMAGE_TEST_REQUIRED
- ID17 row4 -> IMAGE_TEST_REQUIRED
- ID19 row5 -> IMAGE_TEST_REQUIRED
- ID88 row6 `solo` -> IMAGE_TEST_REQUIRED
- ID88 rows7-9 optional pose alternatives -> PASS as optional alternatives only

## Historical findings preserved
- IMAGE_TEST_REQUIRED: IDs16,17,19,88
- REVIEW: IDs22,40,55
- FIX candidates: IDs34,36,49,50,57,58,59,92,94

## Active R2 rules
- Every frozen semantic-support row must be audited.
- `CORE_SUPPORT + ADDITIVE` gets mandatory deep review.
- S/A and generation-behavior claims require knowledge/PROMPT cross-check.
- Image-dependent uncertainty is not guessed PASS.
- Any S/A false-PASS invalidates the current 100-Special batch.
- Historical blocks remain immutable; revalidation/corrections use explicit ledgers.

## Durable ledgers
- `RESULT_LEDGER_INDEX.csv` + `results_blocks/`
- `revalidation_results.csv`
- `candidate_fixes.csv`
- `revalidation_queue.csv`
- `semantic_support_results.csv`
- `progress.json`
- this `handoff.md`

## Exact restart
Resume Batch1 R2 revalidation at sequence 41. Do not resolve the 100 queue entries, run final PASS sampling, or process sequence101 until the complete 1-100 revalidation gate is accepted.

## Automation safety
Do not run scheduled and manual GitHub writes concurrently.
