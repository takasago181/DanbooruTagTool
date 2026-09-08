# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass checkpointed through: 820
- Cumulative effective verdicts: PASS 686 / FIX 92 / REVIEW 26 / IMAGE_TEST_REQUIRED 16
- Batch 1-8 R2 acceptance gates: PASS
- Batch 9: partial (801-820 checkpointed)
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 821
- Production modified: NO

## Batch 9 partial
Range 801-820 is durably stored with matching result, candidate-fix, and revalidation-queue checkpoint blocks.

Partial Batch9 distribution:
- PASS 9
- FIX 6
- REVIEW 5
- IMAGE_TEST_REQUIRED 0

Notable quarantine-only findings:
- explicit bodypart/spatial omissions were corrected narrowly for direct positional canonicals;
- ID808 `oyakodon (sex)` remains REVIEW because frozen evidence does not safely resolve relation/participant structure beyond generic ACTION_INTERACTION;
- PROVISIONAL rows 802/804/811/814 remain REVIEW rather than guessed promotion.

Semantic-support coverage remains 53/58; remaining frozen rows belong to later Special IDs 1159, 1823, and 1839.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 821. Continue Batch9 only after the 801-820 checkpoint is accepted as durable. Checkpoint every 20; run Batch9 integrity + deterministic PASS resampling before acceptance. Do not modify production/main.
