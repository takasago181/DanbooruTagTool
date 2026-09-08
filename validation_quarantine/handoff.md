# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass checkpointed through: 960
- Cumulative effective verdicts: PASS 728 / FIX 128 / REVIEW 88 / IMAGE_TEST_REQUIRED 16
- Batch 1-9 R2 acceptance gates: PASS
- Batch 10: partial (901-960 checkpointed)
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 961
- Production modified: NO

## Batch 10 partial
Ranges 901-960 are durably stored in 20-row blocks with matching candidate-fix and revalidation-queue checkpoint blocks.

941-960 delta:
- PASS 6
- FIX 7
- REVIEW 7
- IMAGE_TEST_REQUIRED 0

New quarantine-only structural candidates in 941-960: IDs942,944,946,947,957,959,960. Ambiguous PROVISIONAL rows remain REVIEW rather than guessed corrections. No revalidation item was added.

Semantic-support coverage remains 53/58; remaining frozen rows belong to later Special IDs 1159, 1823, and 1839.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 961. Batch10 gate remains pending until sequence1000. Checkpoint every20. Do not modify production/main.
