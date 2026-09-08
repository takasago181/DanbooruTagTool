# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Completed Special-level first pass: 160
- Effective counts: PASS 140 / FIX 11 / REVIEW 3 / IMAGE_TEST_REQUIRED 6
- Batch 1 R2 acceptance gate: PASS
- Batch 2 checkpoints complete: 101-120, 121-140, 141-160
- Revalidation queue pending: 0
- Semantic-support frozen target: 58 rows; covered: 15
- Next first-pass Special sequence: 161
- Production modified: NO

## Batch 2 findings so far
- ID122 `missionary` -> IMAGE_TEST_REQUIRED due four enabled NOT_TESTED CORE_SUPPORT+ADDITIVE rows.
- ID129 `sitting on face` -> IMAGE_TEST_REQUIRED due enabled NOT_TESTED CORE_SUPPORT+ADDITIVE `sitting`.
- ID149 `anal object insertion` -> FIX candidate: ImplementRequirementOverride=true.
- ID153 `pegging` -> FIX candidate: ImplementRequirementOverride=true.
- Alias/Semantic rows remain conservative; no model-response equivalence promoted.

## Exact restart
Resume first-pass at sequence161 under R2. Continue through 200 with 20-row checkpoints. Audit associated semantic-support rows before accepting each Special-level verdict. At 200 run full Batch2 consistency and deterministic PASS sampling gate. Do not modify main/production.
