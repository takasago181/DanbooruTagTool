# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass checkpointed through: 940
- Cumulative effective verdicts: PASS 722 / FIX 121 / REVIEW 81 / IMAGE_TEST_REQUIRED 16
- Batch 1-9 R2 acceptance gates: PASS
- Batch 10: partial (901-940 checkpointed)
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 941
- Production modified: NO

## Batch 9 complete
Batch 9 (801-900) is accepted under R2: PASS 36 / FIX 27 / REVIEW 37 / IMAGE_TEST_REQUIRED 0. Five 20-row blocks reconcile exactly 100 unique contiguous sequences. Deterministic PASS re-audit sampled 10 / 36 with surviving A-risk PASS priority and found 0 new false-PASS. Evidence: `pass_sampling_batch9_r2.csv` and `batch9_integrity_r2.md`.

## Batch 10 partial
Ranges 901-920 and 921-940 are durably stored with matching result, candidate-fix, and revalidation-queue checkpoint blocks.

Partial Batch10 distribution:
- PASS 9
- FIX 8
- REVIEW 23
- IMAGE_TEST_REQUIRED 0

Notable quarantine-only findings include narrowly supported bodypart / implement / spatial corrections at IDs901,905,909,915,921,925,928,929. Ambiguous PROVISIONAL rows and possible family mismatches remain REVIEW rather than guessed corrections.

Semantic-support coverage remains 53/58; remaining frozen rows belong to later Special IDs 1159, 1823, and 1839.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 941. Batch10 gate remains pending until sequence1000. Checkpoint every 20. Do not modify production/main.
