# Batch 20 Integrity Audit — R2

Range: 1901-2000
Rule: R2
Acceptance gate: PASS

## Reconciliation
- Expected Special rows: 100
- Checkpoint blocks: 5 x 20
- Contiguous sequence coverage: 1901-2000
- Missing sequences: 0
- Duplicate sequences: 0
- Batch verdicts: PASS 100 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0
- Cumulative after batch: PASS 1548 / FIX 174 / REVIEW 261 / IMAGE_TEST_REQUIRED 17

## Deep review
A-risk PASS rows: IDs 1912 `box tie`, 1914 `frogtie`, 1915 `hogtie`, 1919 `legs bound apart`, 1926 `reverse prayer`, 1932 `shrimp tie`, 1935 `stationary restraints`, 1937 `strappado`, 1938 `suspension`, 1940 `wrists bound apart`.

All pose/spatial/composition assertions were reviewed as structural metadata only. No automatic support insertion, direct-model recognition, or model-family behavior was inferred. ID1935's official-definition evidence supports a fixed restraint-device scene concept while its composition/spatial metadata remains non-inserting. Stage10 material was used only as scoped evidence and was not promoted to production truth.

## False-PASS audit
Deterministic sample: 20 / 100 PASS rows (R2 maximum), including every A-risk PASS in the batch.
Sampled sequences: 1901, 1908, 1912, 1914, 1915, 1919, 1921, 1926, 1932, 1934, 1935, 1937, 1938, 1940, 1942, 1956, 1963, 1971, 1983, 1996.
New false-PASS findings: 0.
R2 false-PASS gate: PASS.

## Guardrails checked
- Blank/None not treated as automatic error.
- Alias canonical linkage kept statistics-only.
- Semantic/search-only rows not promoted to direct model recognition.
- Statistical common/rare not conflated with semantic support.
- Stage10 evidence used only as scoped evidence, not production truth.
- Candidate fixes and revalidation queue checked unchanged.
- Production/main modified: NO.

Next safe first-pass restart: 2001.
