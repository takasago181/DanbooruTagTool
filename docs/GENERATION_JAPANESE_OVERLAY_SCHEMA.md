# Stage 6.5 Japanese Overlay

`data/japanese/japanese_terms.csv` is a reviewable sidecar with the fixed columns
`canonical_tag,ja_term,usage,source_id`. `usage` is one of `display`, `search`,
`candidate`, or `rejected`; duplicate `(canonical_tag, ja_term)` identities are
invalid and a canonical has at most one `display` row.

Only `display` and `search` rows are materialized into the local runtime file
`data/runtime/japanese_overlay.json`. A display value is also a search value.
Candidate and rejected rows remain audit data and cannot enter runtime search or
 presentation. Existing Special Core Dictionary snapshot Japanese text remains the first presentation
value and is never replaced by this overlay.

External imports use the current canonical set after only the project normalizer
and permitted space-to-underscore conversion. Alias-only, fuzzy, semantic, and
external metadata matches do not create canonical identity. The pinned source
manifest and import counts are recorded in `data/japanese/japanese_sources.json`
and `benchmarks/stage6_5/japanese_import_audit.json`. The audit includes
`source_term_usage_counts` for each source, counting terms before global identity
deduplication. Deterministic examples are selected by disposition and usage
bucket, so alias-only, unmatched, rejected, candidate, search, and ambiguous
records remain visible without random sampling.

The runtime loader is local and read-only. If the overlay is absent, the existing
canonical, alias, Special, semantic, and Stage 4 search behavior is available by
the same loader path.
