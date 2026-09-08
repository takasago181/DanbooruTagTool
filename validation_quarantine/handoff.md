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
- Next Special sequence position: 101 (BLOCKED)
- Full Batch 1 revalidation pending: 100 Special entries
- Semantic-support frozen target: 58 data rows
- Semantic-support rows covered: 9
- Semantic-support IMAGE_TEST_REQUIRED: 6
- False-PASS found: 1 (S risk)
- Production modified: NO

## Why Batch 1 failed
During the mandatory semantic-support sidecar audit, ID88 `masturbation` was found to have an enabled `CORE_SUPPORT + ADDITIVE` row for `solo` that was not incorporated into the Special-level 81-100 verdict. The immutable checkpoint block had recorded ID88 as PASS.

Under R2 this is an S-risk false-PASS because default-on additive support must receive deep review and the row is `NOT_TESTED`. The original block is not rewritten. `revalidation_results.csv` explicitly supersedes ID88 to `IMAGE_TEST_REQUIRED` pending controlled image A/B.

R2 requires any S/A false-PASS to invalidate the current 100-Special batch. Therefore sequences 1-100 are now queued for full sidecar-aware revalidation, and sequence 101 must not begin until that gate passes.

## Newly completed direct R2 work
Sequences 61-80:
- 20 PASS after R2 screening.
- ID65 pose structure deep-reviewed and retained without automatic support injection.
- IDs66/67 Alias-preserve policy retained; canonical/Alias model-response equivalence remains Stage10 HOLD.
- IDs68-80 semantic-only concepts remain conservative UNMAPPED search/support entries.

Sequences 81-100:
- Initial checkpoint: 18 PASS, 2 FIX.
- New FIX ID92 `pillow humping` -> `ImplementRequirementOverride=true`.
- New FIX ID94 `table humping` -> `ImplementRequirementOverride=true`.
- ID88 initial PASS is superseded after sidecar audit; effective state is IMAGE_TEST_REQUIRED.

## Semantic-support coverage completed so far
Frozen data rows 1-9 have explicit records in `semantic_support_results.csv`:
- ID16: three CORE_SUPPORT+ADDITIVE rows -> IMAGE_TEST_REQUIRED
- ID17: one CORE_SUPPORT+ADDITIVE row -> IMAGE_TEST_REQUIRED
- ID19: one CORE_SUPPORT+ADDITIVE row -> IMAGE_TEST_REQUIRED
- ID88: `solo` CORE_SUPPORT+ADDITIVE -> IMAGE_TEST_REQUIRED
- ID88 optional pose alternatives `sitting`, `on_back`, `kneeling` -> static PASS as optional alternatives; no generation-benefit claim

## Historical findings preserved
- IDs16,17,19: IMAGE_TEST_REQUIRED
- IDs22,40,55: REVIEW
- IDs34,36: ActorRequirement FIX candidates
- ID49: pose/composition FIX candidate
- ID50: actor requirement FIX candidate
- ID57: pose/composition + actor FIX candidate
- ID58: multi-actor FIX candidate
- ID59: implement requirement FIX candidate
- IDs92,94: implement requirement FIX candidates

## Active R2 rules
- Every frozen semantic-support row must be audited.
- `CORE_SUPPORT + ADDITIVE` gets mandatory deep review.
- S/A and generation-behavior claims require knowledge/PROMPT cross-check.
- Image-dependent uncertainty is not guessed PASS.
- Any S/A false-PASS invalidates the current 100-Special batch.
- Historical blocks remain immutable; corrections use explicit revalidation records.

## Durable ledgers
- `RESULT_LEDGER_INDEX.csv` + `results_blocks/`
- `revalidation_results.csv`
- `candidate_fixes.csv`
- `revalidation_queue.csv`
- `semantic_support_results.csv`
- `progress.json`
- this `handoff.md`

## Exact restart
1. Read Issue #32 and all durable ledgers.
2. Confirm Batch 1 R2 gate is FAILED because of ID88 S-risk false-PASS.
3. Revalidate sequences 1-100 under full sidecar-aware R2, preserving historical records and using explicit supersession records where needed.
4. Re-run deterministic PASS false-PASS sampling only after full-batch revalidation stabilizes.
5. Do not process sequence 101 until the Batch 1 gate passes.

## Automation safety
Do not run scheduled and manual GitHub writes concurrently.
