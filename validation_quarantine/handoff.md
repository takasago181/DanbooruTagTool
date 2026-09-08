# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass accepted through: 700
- Cumulative effective verdicts: PASS 619 / FIX 58 / REVIEW 7 / IMAGE_TEST_REQUIRED 16
- Batch 1-7 R2 acceptance gates: PASS
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 701
- Production modified: NO

## Batch 7 acceptance
Batch 7 range 601-700 is durably stored in five 20-row result blocks.

Final Batch7 distribution:
- PASS 76
- FIX 24
- REVIEW 0
- IMAGE_TEST_REQUIRED 0

`pass_sampling_batch7_r2.csv` rechecked 16 / 76 PASS rows (21.05%), including every surviving A-risk PASS; new false-PASS: 0. `batch7_integrity_r2.md` records 100/100 reconciliation with no gaps or duplicates. Batch7 R2 acceptance gate: PASS.

Notable correction:
- ID680 `autocunnilingus` -> proposed `SELF_ACTION` + `GFR_SELF_ACTION` + `ActorRequirementOverride=true` + `SELF_ACTOR_ROLE`. This remains quarantine-only.

Other Batch7 fixes are predominantly explicit bodypart/target and on-target spatial requirements in genital-contact/restraint tags, recorded in the five `candidate_fix_blocks/` files.

Candidate-fix durable representation for this batch is layered: the pre-Batch7 consolidated `candidate_fixes.csv` remains through ID600, and all Batch7 deltas are append-only in `candidate_fix_blocks/0601_0620.csv` through `0681_0700.csv`. This avoids stale aggregate overwrite while preserving every candidate. Revalidation-queue delta is zero.

Semantic-support coverage remains 53/58; remaining frozen rows belong to later Special IDs 1159, 1823, and 1839.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 701. Process at most 100 Specials, checkpoint every 20, and run the next 100-level integrity + deterministic PASS resampling gate before accepting sequence800. Do not modify production/main.
