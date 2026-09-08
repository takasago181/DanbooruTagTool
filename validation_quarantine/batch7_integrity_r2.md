# Batch 7 R2 Integrity / Acceptance Gate

Issue: #32
Branch: `dict-validation/quarantine`
Range: sequences 601-700
Rule: R2

## Exact row reconciliation
Five append-only result blocks exist:
- `results_blocks/0601_0620.csv`
- `results_blocks/0621_0640.csv`
- `results_blocks/0641_0660.csv`
- `results_blocks/0661_0680.csv`
- `results_blocks/0681_0700.csv`

Reconciliation result: 100 / 100 unique sequences, contiguous 601-700, no gaps, no duplicates.

Batch7 first-pass distribution:
- PASS 76
- FIX 24
- REVIEW 0
- IMAGE_TEST_REQUIRED 0
- total 100

All five checkpoint ranges also have append-only candidate-fix and revalidation-queue delta files. Effective revalidation queue delta is 0.

## Candidate-fix representation
The pre-Batch7 consolidated aggregate `candidate_fixes.csv` remains frozen through ID600 (blob at Batch6: `e2ac8ee06aeebf2d3f54aa7bb8362b60de6b15c8`). Batch7 changes are append-only in:
- `candidate_fix_blocks/0601_0620.csv`
- `candidate_fix_blocks/0621_0640.csv`
- `candidate_fix_blocks/0641_0660.csv`
- `candidate_fix_blocks/0661_0680.csv`
- `candidate_fix_blocks/0681_0700.csv`

This layered representation avoids stale full-file overwrite during long-running checkpointing and preserves every Batch7 candidate. Production data is untouched.

## Deterministic PASS re-audit
Effective Batch7 PASS rows: 76.
Sample: 16 / 76 = 21.05%, satisfying the >=20% R2 requirement.

Selection rule: include every surviving A-risk PASS, then deterministic spread controls across the ordered surviving PASS set, including alias, implement, scene-context, reaction, and boundary-adjacent controls.

Sample artifact: `pass_sampling_batch7_r2.csv`.

Surviving A-risk PASS explicitly included:
- 645 `pantyshot`
- 679 `female masturbation`
- 697 `multiple penis fellatio`
- 699 `male penetrated`

Re-audit result:
- new false-PASS: 0
- escalation required: NO
- full-batch revalidation required: NO

## Acceptance
Batch7 R2 acceptance gate: **PASS**.

Cumulative effective totals through sequence700:
- PASS 619
- FIX 58
- REVIEW 7
- IMAGE_TEST_REQUIRED 16

Semantic-support coverage remains 53 / 58 frozen rows; the remaining rows belong to later Special IDs 1159, 1823, and 1839.

Next safe first-pass restart: sequence 701.
Main / production modified: NO.
