# Stage 6.5 Japanese Overlay Report

Stage 6.5 adds a local Japanese display/search sidecar while preserving the
Stage 0–6 dictionaries and runtime identities. `JapaneseOverlay` loads only the
runtime-safe rows; the builder never changes Special2788, canonical metadata,
aliases, semantic data, or Generation Profile data.

The pinned inputs and licenses are recorded in `data/japanese/japanese_sources.json`.
The Hugging Face dataset card for the pinned newtextdoc1111 revision confirms MIT:

- `PYU224/tagdb-updater` commit `b5da8f0141de06cbda3df864ef8afee66131052b`
- `boorutan/booru-japanese-tag` commit `cec5f7eefbe5c3addd8fb9338d11435518ae8ccf`
- `newtextdoc1111/danbooru-tag-csv` revision `fdf2772213f13d46bff60fc5ebd876e1a811a053`

The build produced 117,147 unique Japanese term rows: 25,140 `search`, 85,277
`candidate`, 6,730 `rejected`, and no automatic `display` rows. The runtime
overlay contains 15,228 canonical entries and 25,140 search terms. Candidate and
rejected terms are retained in the CSV and audit only. The audit records 1,337
ambiguous Japanese terms and 18,868 duplicate identities removed during merge.
The audit's per-source `source_term_usage_counts` are counted before global
`(canonical_tag, ja_term)` deduplication: pyu224 is 91,080 candidate; boorutan is
412 candidate; newtextdoc1111 is 25,140 search, 12,626 candidate, and 6,757
rejected. Global totals therefore can be lower after duplicate identity merging.

Exact canonical matches, alias-only records, unmatched records, category counts,
Special overlap, non-Special General coverage, and source-level usage counts are
recorded per source in `benchmarks/stage6_5/japanese_import_audit.json`.
`japanese_import_examples.csv` uses deterministic per-disposition/usage quotas so
search, candidate, rejected, alias-only, unmatched, and ambiguous examples remain
auditable after every rebuild. External category, count, and alias fields are
never copied into project metadata; alias-only records remain audit-only.

The runtime keeps the existing search order canonical → alias → Japanese →
semantic → prefix/partial. Existing Special Japanese text remains the first
display value. An absent overlay loads as an empty sidecar, restoring the
pre-Stage-6.5 search data path.

Validation completed:

- targeted Stage 6.5 tests: 5 passed
- full pytest: 111 passed in 19.91s
- two consecutive builds produced byte-identical terms CSV, runtime JSON, audit,
  and examples CSV
- Special2788 SHA-256 unchanged:
  `07584b365d5a68dbadd3f5e80859e768c2718b18746e32de02ce4b8bd60935e3`
- canonical, alias, linkage, and Generation Profile source hashes unchanged
- source acquisition is a development-time activity; the builder and runtime read
  only pinned local source files and require no network, LLM, or translation API

Stage 7 UI and automatic translation review are intentionally outside this stage.
