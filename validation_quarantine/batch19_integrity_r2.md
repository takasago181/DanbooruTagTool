# Batch 19 Integrity Audit — R2

Range: 1801-1900
Rule: R2
Acceptance gate: PASS

## Reconciliation
- Expected Special rows: 100
- Checkpoint blocks: 5 x 20
- Contiguous sequence coverage: 1801-1900
- Missing sequences: 0
- Duplicate sequences: 0
- Batch verdicts: PASS 99 / FIX 0 / REVIEW 1 / IMAGE_TEST_REQUIRED 0
- Cumulative after batch: PASS 1448 / FIX 174 / REVIEW 261 / IMAGE_TEST_REQUIRED 17

## Deep review
- ID1834 `pillory`: A-risk PASS. `COMPOSITION_OWNER_CANDIDATE` is structural scene ownership metadata only; no automatic support insertion.
- ID1840 `stocks`: A-risk PASS under the same structural-only interpretation.
- ID1844 `wooden horse`: A-risk PASS under the same structural-only interpretation.
- ID1895 `arms bound apart`: A-risk PASS. Pose/spatial requirements are intrinsic structural metadata only; no automatic support insertion.
- ID1864 `convenient tentacle`: S-risk REVIEW. Frozen row is `REVIEW_REQUIRED` / `TARGETED_NO_AUTHORITATIVE_DEFINITION`; insufficient independent evidence for a safe GenerationFamily/GenerationRole assignment.

## False-PASS audit
Deterministic sample: 20 / 99 PASS rows (R2 maximum), including every A-risk PASS in the batch.
Sampled sequences: 1805, 1810, 1815, 1820, 1825, 1830, 1834, 1835, 1840, 1844, 1845, 1850, 1855, 1860, 1870, 1875, 1880, 1885, 1890, 1895.
New false-PASS findings: 0.
R2 false-PASS gate: PASS.

## Guardrails checked
- Blank/None not treated as automatic error.
- Semantic/search-only rows not promoted to direct model recognition.
- Statistical common/rare not conflated with semantic support.
- Stage10 evidence used only as scoped evidence, not production truth.
- Candidate fixes and revalidation queue checked unchanged.
- Production/main modified: NO.

Next safe first-pass restart: 1901.
