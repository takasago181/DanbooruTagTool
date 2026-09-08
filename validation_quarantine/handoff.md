# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass checkpointed through: 920
- Cumulative effective verdicts: PASS 719 / FIX 117 / REVIEW 68 / IMAGE_TEST_REQUIRED 16
- Batch 1-9 R2 acceptance gates: PASS
- Batch 10: partial (901-920 checkpointed)
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 921
- Production modified: NO

## Batch 10 partial
Range 901-920 is durably stored with matching result, candidate-fix, and revalidation-queue checkpoint blocks.

Partial Batch10 distribution:
- PASS 6
- FIX 4
- REVIEW 10
- IMAGE_TEST_REQUIRED 0

Notable quarantine-only findings:
- ID901 `biting nipple` -> bodypart requirement candidate.
- ID905 `cum in footwear` -> spatial requirement candidate.
- ID909 `condom on nipples` -> bodypart + implement + spatial requirement candidates.
- ID915 `nipple stimulation (female on male)` -> actor + bodypart requirement candidates.
- Ambiguous PROVISIONAL rows remain REVIEW.

Semantic-support coverage remains 53/58; remaining frozen rows belong to later Special IDs 1159, 1823, and 1839.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 921. Checkpoint every 20; Batch10 gate remains pending until 1000. Do not modify production/main.
