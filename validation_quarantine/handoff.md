# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass checkpointed through: 860
- Cumulative effective verdicts: PASS 699 / FIX 102 / REVIEW 43 / IMAGE_TEST_REQUIRED 16
- Batch 1-8 R2 acceptance gates: PASS
- Batch 9: partial (801-860 checkpointed)
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 861
- Production modified: NO

## Batch 9 partial
Ranges 801-820, 821-840, and 841-860 are durably stored with matching result, candidate-fix, and revalidation-queue checkpoint blocks.

Partial Batch9 distribution:
- PASS 22
- FIX 16
- REVIEW 22
- IMAGE_TEST_REQUIRED 0

Notable quarantine-only findings in 841-860:
- ID842 `sex toy pull` -> implement requirement candidate.
- ID844 `panties on penis` -> bodypart + spatial requirement candidates.
- ID850 `cum in panties` -> spatial requirement candidate.
- ID851 `foreskin pull` -> bodypart requirement candidate.
- ID845 `bouncing testicles`, ID852 `nipple tweak through clothes`, ID856 `chastity cage emission`, and PROVISIONAL rows remain REVIEW where family/meaning cannot be safely fixed from frozen evidence alone.

Semantic-support coverage remains 53/58; remaining frozen rows belong to later Special IDs 1159, 1823, and 1839.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 861. Continue Batch9 only after the 841-860 checkpoint is accepted as durable. Checkpoint every 20; run Batch9 integrity + deterministic PASS resampling before acceptance. Do not modify production/main.
