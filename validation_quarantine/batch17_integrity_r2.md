# Batch 17 integrity / R2 false-PASS audit

Range: 1601-1700
Rule: R2

## Internal consistency
- 5 checkpoint blocks x 20 rows = 100 rows
- contiguous sequences: PASS (1601-1700)
- duplicate sequences: 0
- missing sequences: 0
- candidate_fixes additions: 0
- revalidation_queue additions: 0
- enabled semantic-support rows encountered: 0

## Batch verdict counts
- PASS: 100
- FIX: 0
- REVIEW: 0
- IMAGE_TEST_REQUIRED: 0

The first 90 rows are APPROVED_IDENTITY_ONLY / ALIAS_TARGET_RESOLVED / ALIAS_PRESERVE. Exact Special prompt identity is preserved and canonical_target is kept as statistical linkage only. Rows 1691 and 1694-1700 are APPROVED_SEMANTIC_ROLE records and remain search/support-only without asserting direct model recognition or canonical equivalence. Rows 1692-1693 are APPROVED_STATIC META_CONTEXT/SUPPORT records. No automatic expansion or Stage10 generation truth is inferred.

## PASS re-audit
Deterministic sample: every fifth sequence across the 100-row batch.

Sampled sequences: 1605, 1610, 1615, 1620, 1625, 1630, 1635, 1640, 1645, 1650, 1655, 1660, 1665, 1670, 1675, 1680, 1685, 1690, 1695, 1700.

Sample size: 20 / 100 PASS rows (20%).
S/A PASS rows in batch: 0.
New false-PASS findings: 0.

The sample intentionally reaches the semantic-role tail (1695, 1700). Those rows remain acceptable only as search/support-role metadata; the audit does not promote a model-recognition/generation-response claim. Statistical alias/canonical linkage remains separate from semantic support.

## Gate
Batch17 R2 acceptance gate: PASS.
Next safe first-pass sequence: 1701.
Production/main modified: NO.
