# Batch 23 R2 integrity / false-PASS gate

Range: 2201-2300
Rule: R2

## Integrity
- Five durable 20-row result blocks present: 2201-2220, 2221-2240, 2241-2260, 2261-2280, 2281-2300.
- Expected sequences: 100
- Unique sequences: 100
- Missing: 0
- Duplicates: 0
- Verdicts: PASS 100 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0

## R2 boundary checks
- CLOTHING_EXPOSURE rows are structural visual-state/direct metadata only; blanks are not auto-errors and no redundant support is inserted.
- Alias rows 2265-2268 and 2279 preserve Special prompt identity. Canonical linkage remains statistics-only and is not promoted to generation equivalence.
- Semantic-role rows 2269-2278 remain semantic/search support only and do not assert direct model recognition or automatic inclusion.
- No Stage10 HOLD item was promoted to production truth.
- candidate_fixes.csv and revalidation_queue.csv were inspected at each checkpoint; Batch23 adds no new candidate or active revalidation item.

## Deterministic PASS re-audit
Sampling rule for this batch: every fifth sequence in the fixed 100-row range, giving exactly 20/100 PASS rows.

Sampled sequences: 2205, 2210, 2215, 2220, 2225, 2230, 2235, 2240, 2245, 2250, 2255, 2260, 2265, 2270, 2275, 2280, 2285, 2290, 2295, 2300.

This deliberately includes clothing cutout/manipulation, one Alias row (2265), semantic/search-only rows (2270, 2275), and naked-clothing states.

False-PASS found: 0
Escalation required: NO
Batch23 acceptance gate: PASS

Production/main modified: NO
Next safe first-pass sequence: 2301
