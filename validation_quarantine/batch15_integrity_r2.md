# Batch 15 R2 integrity / acceptance gate

Range: 1401-1500
Rule: R2

## Result reconciliation
- Durable 20-row blocks: 1401-1420, 1421-1440, 1441-1460, 1461-1480, 1481-1500
- Expected rows: 100
- Reconciled rows: 100
- Unique sequences: 100
- Range contiguous: YES
- Gaps: 0
- Duplicates: 0

## Verdict distribution
- PASS: 100
- FIX: 0
- REVIEW: 0
- IMAGE_TEST_REQUIRED: 0

All 100 source rows are `APPROVED_IDENTITY_ONLY / ALIAS_TARGET_RESOLVED / ALIAS_PRESERVE`, with `PRESERVE_PROMPT_IDENTITY` handling and no enabled semantic-support records in this range. The audit therefore validates the narrow identity-preservation assertion only; it does not infer generation equivalence to canonical targets or promote statistical canonical targets into prompt replacements.

## R2 false-PASS audit
- PASS population: 100
- Deterministic sample: 20 (20%)
- S/A PASS population: 0
- New false-PASS: 0
- Sampling artifact: `pass_sampling_batch15_r2.csv`
- Gate result: PASS

## Side ledgers
- `candidate_fixes.csv`: checked, no Batch15 additions
- `revalidation_queue.csv`: checked, no Batch15 additions; pending remains 0
- semantic support coverage: unchanged at 55 / 58

## Acceptance
Batch15 R2 acceptance gate: PASS.
Production/main modified: NO.
Next safe first-pass sequence: 1501.
