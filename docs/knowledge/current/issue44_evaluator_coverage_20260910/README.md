# Issue #44 — Special 2,788 evaluator coverage desk analysis

> Desk/vocabulary coverage only. This is not image-level accuracy proof and not Danbooru semantic authority.

- rows classified: 2788 / 2788
- relation/binding review required by structural heuristic: 910 / 2788 (32.64%)

## Evaluator vocabulary coverage
- WD14: status=OK, vocab=10824, direct=658 (23.6%), direct+alias=658 (23.6%)
- Kagami: status=OK, vocab=23952, direct=1412 (50.65%), direct+alias=1412 (50.65%)
- CL: status=UNAVAILABLE_GATED, vocab=None, direct=0 (0.0%), direct+alias=0 (0.0%)

## Combined confirmed coverage
- verified evaluators: wd14_class, kagami_class
- direct union: 1423 (51.04%)
- direct+alias union: 1423 (51.04%)
- including component predicates: 1712 (61.41%)
- exact 3-evaluator result available: False

## Provisional routing
- AUTO_CANDIDATE: 754 (27.04%)
- REVIEW_REQUIRED: 958 (34.36%)
- BLOCKED: 1076 (38.59%)

## Boundary
- AUTO_CANDIDATE means only: at least one verified evaluator has direct/alias vocabulary support, and no structural relation/binding requirement was detected. It still requires real-image calibration before Stage10 automatic use.
- REVIEW_REQUIRED includes relation/binding/body-site/spatial/count/compound cases even when a unary tag exists.
- BLOCKED has no useful verified direct/alias/component observation, or relation is required with no useful observation.
- CL gated vocabulary access failure, if present, is an access blocker and must not be misreported as model incapability.

## Files
- `special2788_evaluator_coverage.csv`
- `representative_calibration_cases.csv`
- `summary.json`

No `data/**` file was modified by this analysis.
