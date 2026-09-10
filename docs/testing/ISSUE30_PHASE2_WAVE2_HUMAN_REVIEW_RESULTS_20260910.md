# Issue #30 Phase 2 Wave 2 human review — 2026-09-10

User reviewed all 8 numbered images (4 fixed-seed A/B pairs). These observations are authoritative for the declared visible predicates. Machine evaluators remain assistive triage only.

## Image observations

| # | Case | Condition | Seed | Observation | Predicate judgment |
|---:|---|---|---:|---|---|
| 1 | P2-004 | B `dildo` | 42001 | 女の子なし、ディルドのみ | broader object present; requested subject context absent |
| 2 | P2-004 | A `double dildo` | 42001 | ディルド2本のみ、女の子なし | intended double-ended single-object shape not realized; model appears to interpret `double` as two objects |
| 3 | P2-004 | B `dildo` | 42002 | ディルドにまたがっている | broader object present with subject interaction |
| 4 | P2-004 | A `double dildo` | 42002 | 同様だが、ディルドが2本 | intended double-ended single-object shape not realized; two separate objects appear |
| 5 | P2-005 | B `anal penetration` | 42011 | アナルと膣の両方に挿入 | anal penetration realized, but extra vaginal penetration also appears |
| 6 | P2-005 | A `anal` | 42011 | 男性なし。性交ではなく、アナルが広がっているだけ | anal penetration not realized |
| 7 | P2-005 | B `anal penetration` | 42012 | アナルのアップ | anal penetration not realized |
| 8 | P2-005 | A `anal` | 42012 | 男性がいて挿入 | anal penetration realized, but `1girl, solo` subject constraint is violated |

## Pair-level interpretation

### P2-004 — `double dildo` vs `dildo`

This comparison does **not** cleanly answer exact-count retention. `double dildo` denotes a double-ended/dual-ended object shape, not necessarily two visible dildo instances. Human review shows both A images produced two separate dildos rather than a single double-ended object.

Decision:
- `HOLD_HUMAN_REVIEW_ONLY`
- reclassify the useful evidence as `SHAPE_SPECIFIC_REALIZATION_FAILURE / LEXICAL_DOUBLE_TO_COUNT_COLLAPSE`
- do not claim `EXACT_COUNT_RETENTION` was answered
- if exact-count behavior remains product-relevant, use a future case whose intended semantics explicitly require an exact count rather than using `double dildo` as a proxy

### P2-005 — `anal` vs `anal penetration`

Visible target for this test is: **肛門に何かが実際に挿入されていること**.

- Seed 42011: A `anal` FAIL, B `anal penetration` PASS (with extra vaginal insertion)
- Seed 42012: A `anal` PASS (with male/solo violation), B `anal penetration` FAIL

Pair results:
- 42011: `B_ONLY_PASS`
- 42012: `A_ONLY_PASS`

Decision:
- `HOLD_HUMAN_REVIEW_ONLY`
- no evidence that canonical and alias surfaces are stably equivalent under this WAI17 profile
- result is strongly seed-sensitive
- subject/composition violations must be recorded separately from target-relation realization

## Evaluator implication

This review reinforces the existing evaluator boundary: machine taggers can detect related objects/body regions and may return positive-looking signals while the actual relation predicate is wrong or absent. Exact shape, body-site relation, insertion relation, ownership/binding, and composition constraints remain human-protected.

## Review UX correction

Future Japanese review questions must state the visible success condition directly, e.g.:
- `1本の両端型ディルドとして見えるか？`
- `肛門に何かが実際に挿入されているか？`

Avoid abstract wording such as `同じ視覚的対象を誘発するか` when a concrete visible predicate can be stated instead.

## Boundary

- Additional generation: not performed in this review record
- `data/**`: unchanged
- #32 verdicts: unchanged
- canonical dictionary values: unchanged
- Stage10 production A/B: not started
