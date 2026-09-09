# Batch 28 final-partial integrity — R2

Range: 2701-2788 (final 88 Specials)
Rule: R2

## Coverage
- Expected rows: 88
- Durable rows: 88
- Contiguous sequences: YES
- Missing: 0
- Duplicates: 0

## Verdict distribution
- PASS: 79
- FIX: 0
- REVIEW: 9
- IMAGE_TEST_REQUIRED: 0

REVIEW IDs: 2734, 2736, 2737, 2747, 2749, 2753, 2763, 2764, 2770.

## R2 PASS re-audit
- PASS population: 79
- Required 20% sample: ceil(79 * 0.20) = 16
- Sampled: 16
- A-risk PASS included preferentially: 2742, 2743, 2746, 2786, 2787
- New false-PASS: 0
- Gate: PASS

Sample ledger: `pass_sampling_batch28_r2.csv`.

## Boundary checks
- Alias/canonical linkage remained statistics-only; model response equivalence not asserted.
- Statistical common/rare and semantic support were not conflated.
- Blank/None and PROVISIONAL states were not auto-filled merely for completeness.
- Camera/pose/visibility structure was accepted only where intrinsic and did not promote Stage10 model-family tuning or automatic support.
- No candidate fixes or revalidation items were added by Batch28.
- Production/main modified: NO.

## Remaining non-first-pass obligations
- Frozen semantic-support row coverage remains 55/58.
- Active revalidation pending pointer remains 0 according to progress state; unresolved REVIEW/IMAGE_TEST_REQUIRED findings remain quarantined.
- Pre-freeze completeness reconciliation and separate final promotion audit remain required by Issue #32 before production promotion.
