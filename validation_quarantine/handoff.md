# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Completed Special-level first pass: 100
- PASS: 85
- FIX: 9
- REVIEW: 3
- IMAGE_TEST_REQUIRED: 3
- Last completed Special: ID 100 (`after fellatio`)
- Last completed batch: 0 (Batch 1 first-pass complete but R2 acceptance gate pending)
- Next Special sequence position: 101 (BLOCKED until Batch 1 R2 gate passes)
- R2 revalidation/backfill pending: 60 Special entries
- Semantic-support frozen target: 58 data rows
- Semantic-support rows covered: 0
- False-PASS samples checked: 0
- Production modified: NO

## Fixed audit input
See `AUDIT_INPUT_SNAPSHOT.md`. The first pass uses the frozen production revision captured at setup. Do not silently switch to a later main revision.

## Active R2 method
- 100 Specials per external batch; checkpoint every 20
- static integrity + semantic screening
- mandatory deep review for S/A risk and all non-PASS findings
- mandatory deep review for `CORE_SUPPORT + ADDITIVE`
- full 58-row frozen semantic-support coverage
- generation-evidence cross-check for high-impact claims
- deterministic PASS sampling at each 100-Special boundary

## Current findings
Historical R1 sequences 1-60 remain preserved and queued for R2-only backfill.

Sequences 1-20:
- IDs16,17,19 -> IMAGE_TEST_REQUIRED for default-on `CORE_SUPPORT + ADDITIVE` behavior.

Sequences 21-40:
- IDs34,36 -> FIX candidate `ActorRequirementOverride=true` only; earlier spatial/separation proposals withdrawn.
- IDs22,40 -> REVIEW.

Sequences 41-60:
- FIX: ID49 pose/composition alignment; ID50 actor requirement; ID57 pose/composition + actor; ID58 multi-actor structure; ID59 implement requirement.
- REVIEW: ID55 simulated-vs-implied classification.

Sequences 61-80 (direct R2):
- 20 PASS.
- ID65 pose structure deep-reviewed and accepted without automatic support injection.
- IDs66/67 Alias-preserve policy accepted; canonical/Alias model-response equivalence remains Stage10 HOLD.
- IDs68-80 semantic-only entries remain conservative UNMAPPED search/support concepts.

Sequences 81-100 (direct R2):
- 18 PASS, 2 FIX.
- ID92 `pillow humping` -> candidate `ImplementRequirementOverride=true` because the pillow is intrinsic to the action.
- ID94 `table humping` -> candidate `ImplementRequirementOverride=true` because the table/surface is intrinsic to the action.
- ID95 tail masturbation remains PASS after sibling check against tailjob; no speculative BodypartRequirement promotion.

## Batch 1 gate
Do not start sequence 101 yet. Before Batch 1 can be accepted:
1. Resolve the 60-entry R2 backfill obligation for sequences 1-60.
2. Cover applicable frozen semantic-support rows and update `semantic_support_results.csv`.
3. Run deterministic 20% PASS false-PASS sampling with R2 escalation thresholds.
4. Cross-check the new object-mediated humping implement pattern against prior/sibling rows.
5. Update progress and Issue #32 with the gate result.

## Critical interpretation rules
- Blank/None is not automatically missing data.
- UNKNOWN / NOT ASSERTED may be correct.
- Requirement metadata is structure, not an instruction to inject support tags.
- common/rare/co-occurrence statistics are separate from semantic support.
- Stage10 HOLD knowledge is not production truth.
- model-family-specific knowledge remains scoped.
- Special2788 identity remains first-class.

## Durable ledgers
- `RESULT_LEDGER_INDEX.csv` + `results_blocks/`
- `candidate_fixes.csv`
- `revalidation_queue.csv`
- `semantic_support_results.csv`
- `progress.json`
- this `handoff.md`

## Exact restart
Read Issue #32 and durable files, confirm R2, then perform Batch 1 R2 gate work. Do not process sequence 101 until the gate is accepted. Do not overwrite historical R1 verdicts.

## Automation safety
Do not run scheduled and manual GitHub writes concurrently.
