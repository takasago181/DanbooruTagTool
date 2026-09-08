# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass durably checkpointed through: 800
- Cumulative effective verdicts: PASS 677 / FIX 86 / REVIEW 21 / IMAGE_TEST_REQUIRED 16
- Batch 1-7 R2 acceptance gates: PASS
- Batch 8 first-pass: complete; integrity/PASS-sampling gate pending
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 801, BLOCKED until Batch8 gate result
- Production modified: NO

## Batch 8 first-pass
701-800 is stored in five 20-row result blocks with matching candidate-fix and revalidation-queue checkpoint blocks.

Batch8 first-pass delta: PASS 58 / FIX 28 / REVIEW 14 / IMAGE_TEST_REQUIRED 0.

High-risk handling: explicit bodypart/implement/actor/self/spatial omissions were recorded as narrow quarantine-only candidates; PROVISIONAL or exact-meaning gaps remain REVIEW. ID738 `animal penis` is a static body-attribute correction aligned to approved horse/dog siblings; ID779 `tweaking own nipple` is a self-action structural correction. No Stage10 generation hypothesis was promoted.

Semantic-support coverage remains 53/58; remaining frozen rows belong to later Special IDs 1159, 1823, and 1839.

## Exact restart
Run Batch8 integrity reconciliation and deterministic 20% PASS re-audit now. Do not start sequence801 unless that gate passes. Main/production remain read-only.
