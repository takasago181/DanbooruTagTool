# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass durably checkpointed through: 780
- Cumulative effective verdicts: PASS 668 / FIX 80 / REVIEW 16 / IMAGE_TEST_REQUIRED 16
- Batch 1-7 R2 acceptance gates: PASS
- Batch 8: partial (701-780 saved; gate pending)
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 781
- Production modified: NO

## Batch 8 partial checkpoint
701-780 is stored in four 20-row result blocks with matching candidate-fix and revalidation-queue checkpoint blocks.

Current Batch8 delta: PASS 49 / FIX 22 / REVIEW 9 / IMAGE_TEST_REQUIRED 0.

Notable findings: explicit bodypart/implement/actor omissions remain narrow quarantine-only FIX candidates; ID738 animal-penis correction aligns to approved horse/dog penis siblings; ID779 `tweaking own nipple` is a self-action structural correction. PROVISIONAL rows without exact source evidence remain REVIEW rather than guessed promotion.

Semantic-support coverage remains 53/58; remaining frozen rows belong to later Special IDs 1159, 1823, and 1839.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 781. Process through 800, persist the fifth checkpoint, then run Batch8 integrity + deterministic PASS resampling before acceptance. Do not modify production/main.
