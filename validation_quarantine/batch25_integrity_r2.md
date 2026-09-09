# Batch 25 R2 integrity / false-PASS gate

Range: 2401-2500
Rule: R2

## Static integrity
- Expected sequences: 100
- Covered sequences: 100
- Missing: 0
- Duplicates: 0
- Durable checkpoints: 5 x 20

## Verdict counts
- PASS: 74
- FIX: 0
- REVIEW: 26
- IMAGE_TEST_REQUIRED: 0

## High-risk handling
Material PROVISIONAL restraint, pose, bodypart, spatial, and interaction rows were deep-reviewed and kept REVIEW where independent evidence was insufficient for exact project structure. Blank/None was not treated as an automatic error. Cosmetic or state-only audit-only rows received PASS only when they asserted no execution behavior and preserved exact identity.

Approved rows 2451, 2459, 2471, 2495, and 2497 were escalated to A-risk REVIEW because explicit pose/bodypart/implement/spatial meaning was not fully represented by current structural metadata and R2 forbids self-certification from production metadata alone.

## PASS re-audit
- PASS population: 74
- Required 20% sample: 15
- Deterministic sampled: 15
- New false-PASS: 0
- Gate: PASS

Sampling details: `pass_sampling_batch25_r2.csv`

## Lane / scope checks
- Statistical common/rare evidence was not used as semantic support.
- Semantic/search-only meaning was not promoted to direct model-recognition truth.
- Stage10 HOLD/unvalidated knowledge was not promoted to production truth.
- No production/main files changed.

Batch 25 acceptance: PASS.
