# Batch 14 Integrity / False-PASS Audit (R2)

Range: 1301-1400
Rule: R2

## Reconciliation
- Five append-only result blocks present: 1301-1320, 1321-1340, 1341-1360, 1361-1380, 1381-1400.
- Exactly 100 contiguous unique sequences.
- Missing sequences: 0.
- Duplicate sequences: 0.
- Batch verdict delta: PASS 100 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0.
- Frozen generation profile classification for all 100 rows: APPROVED_IDENTITY_ONLY / ALIAS_TARGET_RESOLVED / ALIAS_PRESERVE.
- No enabled semantic-support row in this batch; semantic support coverage remains 55/58.
- candidate_fixes.csv: no Batch14 additions.
- revalidation_queue.csv: no Batch14 additions; pending count remains 0.

## R2 PASS re-audit
Deterministic 20% sample of PASS rows (20/100):
1301, 1306, 1311, 1316, 1321, 1326, 1331, 1336, 1341, 1346, 1351, 1356, 1361, 1366, 1371, 1376, 1381, 1386, 1391, 1396.

All sampled rows were rechecked against the frozen generation profile and the R2 identity-preservation guardrails. No S/A PASS rows exist in this batch. No sampled row asserted canonical/model-response equivalence or automatic support insertion; each preserves exact Special prompt identity and keeps canonical_target statistics-only.

New false-PASS found: 0.
Batch14 acceptance gate: PASS.

## Safety boundary
No production/main data changed. Stage10 material was not promoted to production truth.
