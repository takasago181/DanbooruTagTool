# Coverage Rules — Issue #36

## R1 baseline contract

1. Read production/protected inputs only; do not modify or copy them into GitHub.
2. Preserve canonical strings exactly.
3. Measure Japanese `display` and Japanese `search` coverage separately.
4. Record lane membership for each canonical tag:
   - General/runtime search universe or an explicitly documented deterministic proxy
   - statistical recommendation universe
   - semantic-support candidate canonicals
   - manually addable auxiliary universe when deterministically derivable
5. Count a display as covered only when the Japanese display value is nonblank and not an English-only placeholder.
6. Count a search entry separately; display coverage must not be inferred from search synonyms or vice versa.
7. One canonical may belong to multiple lanes. Union totals deduplicate by canonical while lane memberships remain explicit.
8. Priority queue:
   - P0: recommendation/semantic-support surfaced tags and common/high-usage General tags
   - P1: remaining recommendation/auxiliary reachable tags
   - P2: remaining General/runtime universe
9. Existing post_count/reference frequency/lane count may order translation work but must not alter production recommendation/search ranking.
10. Ambiguous meaning stays REVIEW; do not guess a production Japanese label.

## Boundary with Issue #32

If a canonical also appears in #32 semantic/generation validation:
- #32 owns support/generation correctness.
- #36 owns only Japanese display/search wording coverage.
- Japanese wording is not evidence that a support relation or generation assertion is correct.

## Known screenshot checks

Coverage inventory must classify at least:
- `1girl`
- `penis`
- `sex`
- `blush`
- `nipples`

`piano`, `analog_clock`, `analogous_colors` appearing for query `anal` are a search-relevance defect, not a translation-coverage defect. They may still be missing translations, but #36 must not fix why they were retrieved.
