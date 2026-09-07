# Stage 4 review — 2026-09-05

## Real Special-only exact coverage

All 2,788 real Special terms were passed to `TagKnowledgeCore.resolve_exact`.
Results: canonical 1,674, alias 778, semantic 336; none 0.
The existing Special-only fallback requires `match_type == "none"` and mapped
Special targets. No current real term satisfies that precondition. Therefore a
real-data test asserting search `match_type == "special"` cannot be supplied
without changing the data or resolution behavior. Neither was changed.
`tests/test_stage4_special_coverage.py` records this snapshot coverage explicitly;
it is not a claim that the Special-only result branch has been exercised.

## Performance

Command: `python -m tools.stage4_search_benchmark` from the project root.
Windows 11 build 26200, Python 3.12.14. Full current Stage 3 knowledge:
124,016 canonicals, 34,416 normalized alias keys, 2,788 Special records,
336 Semantic rows, 0 optional translations, 164,071 search entries.
The Japanese query uses the real Special Japanese label for ID 1.

Each query: 20 warmups, 200 measured calls, interleaved query order,
GC enabled, default limit 50. Full `search_one`, including scan, aggregation,
ranking, and result formatting. Initialization excluded. Median and nearest-rank
p95 in milliseconds; two sequential runs, not controlled isolated CPU trials.

| Type / query | Before median | Before p95 | After median | After p95 |
|---|---:|---:|---:|---:|
| canonical exact / twintails | 5.582 | 6.190 | 5.433 | 6.069 |
| alias exact / sole_female | 4.499 | 4.997 | 4.741 | 5.344 |
| Japanese exact / 肛門 | 2.403 | 2.956 | 2.732 | 3.451 |
| prefix / long h | 4.969 | 5.565 | 5.115 | 5.707 |
| partial / ng hai | 5.505 | 6.044 | 5.653 | 6.312 |
| broad match / hair | 9.054 | 9.981 | 6.781 | 7.498 |
| one-character stress / a | 565.840 | 625.198 | 211.167 | 240.321 |

After-run knowledge load: 548.705 ms; search initialization: 241.897 ms.
The representative partial scan is fast enough for interactive search under
these conditions. Broad one-character queries remain noticeably slower and are
not proven suitable for per-keystroke UI rendering. No GUI or Forge concurrency
measurement was performed; these timings are not universal latency guarantees.

## Minimal implementation change and validation

The stress case justified a small optimization: select top K deduplicated groups
with the existing ranking fields before creating presentation records. This
avoids formatting every match. Prefix/partial matching, ranking priorities,
ambiguity, dedup identities, provenance, and output fields are unchanged. No new
search index, engine, dependencies, or architecture was introduced.

`tests/test_stage4_topk.py` compares full result records against the previous
full-sort procedure, for nine real queries and limits 1, 50, and 100.
Full pytest: **56 passed in 7.62s**, using `-p no:cacheprovider -q`.

Backup: `backups/stage4_review/search.before_topk.py`.
The existing handoff ZIP was not regenerated and predates this review.
Stage 3 inputs/invariants and decision documents are unchanged. Stage 5 was not
started. Handoff: use this report with docs/architecture/SEARCH_ENGINE_DECISION.md; the requested
real-data Special-only exact case remains unavailable in the current snapshot.
