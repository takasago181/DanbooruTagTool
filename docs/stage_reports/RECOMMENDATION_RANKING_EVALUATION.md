# Stage 6 — Recommendation Ranking Evaluation

Status: **FINAL DECISION REQUIRED**.  This report compares methods and does not
select a production default.  It uses the Stage 5 population of 11,218,362
posts from `nyanko-devs/danbooru2026@ebb02a630201c7b51487e45fb90b3fcf4cbedc20:metadata/posts-snapshot.parquet`.

## Scope and data contract

For each selected multi-Special Core, the logical current-canonical overlay
performs true AND on the Core postings, then candidate aggregation over only
those `base_posts`.  A logical canonical with multiple source tags is unioned
and deduplicated per post for both global and co-counts.  Current dictionary
`post_count` is never read for statistics or ranking.

Normal recommendations are restricted to current General canonicals available
through the overlay.  Core inputs are excluded.  Runtime-only identities,
category mismatches, ambiguous aliases, and Semantic Bridge terms remain in
the data layer but are not silently promoted into the normal candidate list.
No role score is applied; no role mapping is supplied in this stage, so the
safe displayed role is `other`.

Raw fields retained on every `RecommendationCandidate` are:

- `base_count`, `co_count`, `conditional_rate = co_count / base_count`
- `runtime_global_count`, `global_rate = runtime_global_count / total_posts`
- `raw_lift = conditional_rate / global_rate`

## Compared presentation orders

| Method | Ranking score | Intended behavior |
|---|---|---|
| Conditional rate | `co / base` | Shows commonly accompanying tags. |
| Raw lift | `(co / base) / global_rate` | Highlights association relative to dataset prevalence. |
| Wilson lower bound | 95% lower confidence bound of `co / base` | Penalizes uncertain small-support rates. |
| Support-aware shrunk lift | `((co + 20*global_rate)/(base + 20))/global_rate` | Pulls small bases toward the snapshot global rate while retaining unusual candidates. |

The shrinkage prior is deliberately a visible constant (20 pseudo-observations),
not learned data or an ML model.  All scores affect sort order only; displayed
raw values are unchanged.

## Actual Special Core evaluation

Six Stage-5-recorded Core conditions were rerun: two each for 2, 3, and 5
Specials.  Canonicals are retained below so the runs are reproducible; their
Special provenance is in Stage 5's workload audit.

| Case | Core canonicals | base_count | ranking overhead (ms) |
|---|---|---:|---:|
| two_special_small | clothed_female_nude_male + genderswap | 101 | 27.9 |
| two_special_medium | erection + open_clothes | 8,805 | 288.0 |
| three_special_small | bare_legs + completely_nude + uncensored | 92 | 60.8 |
| three_special_medium | ass + facial + penis | 3,902 | 226.9 |
| five_special_small | drooling + ejaculation + hetero + see-through_clothes + sex | 21 | 128.2 |
| five_special_medium | breasts + covered_nipples + groping + pussy + spread_legs | 275 | 1,440.6 |

The complete human-review table—20 rows per method and case, including raw
statistics and score—is [top20_by_method.csv](benchmarks/stage6/top20_by_method.csv).
The machine-readable evidence, diagnostic values, and fixed input hashes are
in [ranking_evaluation.json](benchmarks/stage6/ranking_evaluation.json) and
[input_hashes.json](benchmarks/stage6/input_hashes.json).

## Rare-support behavior and stability

Conditional rate and Wilson produced no `co_count <= 10` rows in top20 for
the two medium-size cases.  Raw lift and shrunk lift frequently did: raw lift
had 20/20 such rows for `three_special_small` and `five_special_small`; shrunk
lift had the same 20/20 in those tiny-base conditions.  With a base of 21,
the 20-observation shrinkage prior is insufficient by itself to prevent
rare-support dominance when global frequency is very low.

A deterministic post-ID parity split measured top20 overlap between halves.
Across the six cases, conditional/Wilson overlap ranged 0.80–1.00; raw and
shrunk lift ranged 0.25–0.45.  This is a stability diagnostic, not a claim
that frequent tags are more useful.  It does show the unresolved tradeoff:
lift exposes narrow combinations but is much more sample-sensitive.

## Drop-one and combination specificity

Every evaluation case records full-Core base count and the count after omitting
each Core item in `ranking_evaluation.json`; no item is automatically removed.
Combination specificity is also diagnostic-only.  For example, the five-Special
small Core's raw-lift leader `strapless_dildo` has full conditional rate
4.76%, versus its largest singleton rate 0.011% (`ejaculation`).  This makes
the combination-specific signal inspectable without injecting it into any
ranking score.

## Performance and limitations

`ranking_overhead_ms` includes logical candidate aggregation and calculation
of all eligible candidate statistics for a warm mapped index.  It is not a UI
latency guarantee and does not replace Stage 5's large-base aggregation work.
The 1.44s case is an important reminder that ranking adds work after the
existing candidate traversal.

No generic suppression blacklist, role boost, model-specific knowledge,
negative recommendation, prompt completion, UI, or Stage 7+ work was added.
Before deciding a default, the user should review the linked top20 lists for
prompt usefulness and decide whether shrinkage needs a larger prior or an
explicit minimum-support presentation rule.
