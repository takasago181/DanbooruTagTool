# Batch 26 R2 integrity / false-PASS gate

Range: 2501-2600
Rule: R2

## First-pass reconciliation
- Expected rows: 100
- Durable result blocks: 5 x 20
- Observed rows: 100
- Missing sequence: 0
- Duplicate sequence: 0
- PASS: 98
- FIX: 0
- REVIEW: 2
- IMAGE_TEST_REQUIRED: 0

Non-PASS rows:
- 2503 `mutual impregnation` — S-risk REVIEW; exact reciprocal/multi-actor family/role/actor requirements lack sufficient independent evidence.
- 2504 `vine bondage` — S-risk REVIEW; exact restraint/implement family and requirement structure lack sufficient independent evidence.

## R2 boundary checks
- Blank/None was not treated as an automatic error.
- Statistical/canonical linkage was not treated as semantic or model-response equivalence.
- Alias rows preserve exact Prompt identity; canonical target use remains statistics-only.
- Stage10 canonical/Alias response knowledge remains HOLD and was not promoted to production truth.
- No support tag was auto-inserted from requirement metadata.
- `candidate_fixes.csv` and `revalidation_queue.csv` were inspected at every 20-row checkpoint; Batch26 adds no delta.
- Semantic support coverage remains 55/58 and is a separate lane from Special first-pass coverage.

## PASS re-audit
R2 target: 20% of 98 PASS rows = 19.6, rounded to 20 and capped at 20.

Deterministic/stratified sample: 20 PASS rows. Alias/HOLD boundary rows were intentionally represented heavily because they dominate this batch. See `pass_sampling_batch26_r2.csv`.

Result:
- Re-audited PASS: 20
- New false-PASS: 0
- S/A false-PASS: 0

## Gate
**PASS** — Batch26 may advance to sequence 2601.

Note: `RESULT_LEDGER_INDEX.csv` remains a secondary index and was already lagging the durable result-block/progress checkpoint before this batch. No main/production artifact was modified; durable block files + progress/handoff remain the restart source for this run. Index reconciliation should be performed separately without rewriting historical validation results.
