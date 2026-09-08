# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Completed Special-level first pass: 180
- Effective counts: PASS 157 / FIX 12 / REVIEW 3 / IMAGE_TEST_REQUIRED 8
- Batch 1 R2 acceptance gate: PASS
- Batch 2 checkpoints complete: 101-120, 121-140, 141-160, 161-180
- Revalidation queue pending: 0
- Semantic-support frozen target: 58 rows; covered: 24
- Next first-pass Special sequence: 181
- Production modified: NO

## Batch 2 findings so far
- ID122 `missionary`, ID129 `sitting on face`, ID161 `anal training`, ID173 `double penetration` -> IMAGE_TEST_REQUIRED due enabled NOT_TESTED CORE_SUPPORT+ADDITIVE behavior.
- FIX candidates: ID149 `anal object insertion`, ID153 `pegging`, ID177 `food insertion` -> ImplementRequirementOverride=true.
- Semantic-support rows10-24 are audited. Contextual/optional rows remain static PASS only as non-default choices.

## Exact restart
Resume first-pass at sequence181 under R2. Complete 181-200, then run Batch2 static consistency checks and deterministic PASS false-PASS sampling before sequence201. Do not modify main/production.
