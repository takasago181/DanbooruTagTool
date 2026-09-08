# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass checkpointed through: 900
- Cumulative effective verdicts: PASS 713 / FIX 113 / REVIEW 58 / IMAGE_TEST_REQUIRED 16
- Batch 1-9 R2 acceptance gates: PASS
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 901
- Production modified: NO

## Batch 9 complete
Ranges 801-820, 821-840, 841-860, 861-880, and 881-900 are durably stored with matching result, candidate-fix, and revalidation-queue checkpoint blocks.

Batch9 distribution:
- PASS 36
- FIX 27
- REVIEW 37
- IMAGE_TEST_REQUIRED 0

Deterministic PASS re-audit:
- Sampled 10 / 36 PASS rows (R2 minimum 10), prioritizing surviving A-risk PASS rows.
- New false-PASS: 0
- Batch9 acceptance gate: PASS
- Evidence: `pass_sampling_batch9_r2.csv`, `batch9_integrity_r2.md`

Notable quarantine-only findings in the 841-900 continuation include implement/bodypart/spatial/camera requirement candidates only where intrinsic structure was directly encoded by the canonical; ambiguous PROVISIONAL or family-mismatch rows remain REVIEW rather than guessed corrections.

Semantic-support coverage remains 53/58; remaining frozen rows belong to later Special IDs 1159, 1823, and 1839.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 901 (Batch10). Checkpoint every 20; do not modify production/main.
