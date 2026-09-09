# Batch 16 integrity / R2 false-PASS audit

Range: 1501-1600
Rule: R2

## Internal consistency
- 5 checkpoint blocks x 20 rows = 100 rows
- contiguous sequences: PASS
- duplicate sequences: 0
- missing sequences: 0
- candidate_fixes additions: 0
- revalidation_queue additions: 0
- semantic-support rows encountered: 0

## Batch verdict counts
- PASS: 100
- FIX: 0
- REVIEW: 0
- IMAGE_TEST_REQUIRED: 0

## PASS re-audit
Deterministic sample: every fifth sequence across the 100-row batch.

Sampled sequences: 1505, 1510, 1515, 1520, 1525, 1530, 1535, 1540, 1545, 1550, 1555, 1560, 1565, 1570, 1575, 1580, 1585, 1590, 1595, 1600.

Sample size: 20 / 100 PASS rows (20%).
S/A PASS rows in batch: 0.
New false-PASS findings: 0.

All sampled rows remain acceptable as APPROVED_IDENTITY_ONLY / ALIAS_TARGET_RESOLVED / ALIAS_PRESERVE identity-preservation records. The audit does not infer generation equivalence from canonical_target and does not mix statistical alias linkage with semantic support.

## Gate
Batch16 R2 acceptance gate: PASS.
Next safe first-pass sequence: 1601.
Production/main modified: NO.
