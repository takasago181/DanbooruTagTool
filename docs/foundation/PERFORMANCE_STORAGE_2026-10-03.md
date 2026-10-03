# #254 Performance / Storage optimization

Base: live main `239e7b518dd0b169d22e8d758a721c41239c8882`. Lane #254 only.
Implementation and local verification complete; PR review/CI is the next gate.
No production promotion, UserData migration, semantic change, or #255/#230/#256 work.
Raw measurements, variance, allocation counts, ordered-result hashes, query plans,
and validation summary: [results](PERFORMANCE_RESULTS_2026-10-03.json).

## Evidence reused and measurement conditions

Reused the Foundation audit, metadata boundary/parity results, 142-row external
reuse matrix, #114/#199 catalog harness, #223 HOME tests, #226 5,000-image/20,000-row
Library fixture, and #229 1,000-LoRA fixture. No second repository-wide audit.
The #226 historical performance artifact already measures 124,895 entries;
#114's 33,688-entry practical evidence is historical context, not a comparable SLA.

Measurements use this Windows workstation, .NET 10.0.12, Release, and the unchanged
149,344,256-byte installed catalog opened read-only. Current main code is the
post-Foundation baseline. Three separated load samples and 3 warmups + 11 query
samples capture median, observed p95 (maximum of 11), allocation and ordered
ID/rank SHA256. Workstation benchmarks run in a nonparallel xUnit collection.
An initial search measurement concurrent with the Library fixture was discarded;
the recorded before/after search runs are isolated. Cold OS-cache/boot behavior
is not controlled and no machine-specific result becomes a product SLA.

Population: General 30,629; Special 3,059; Character 35,278; Copyright 7,616;
Artist 48,313. All accepted rows stay intact, including hidden Artist data.

## Accepted changes

1. Remove query/word allocation repeated inside search scoring. Split query and
   detect Japanese once; enumerate term words using the existing .NET
   [Span Split](https://learn.microsoft.com/ja-jp/dotnet/api/system.memoryextensions.split?view=net-10.0)
   and compare whole-word boundaries without padded temporary strings. Rank,
   global strong-hit suppression, canonical deduplication and ordering stay intact.
   No search engine, cache, persistent search index or new dependency.
2. Build `entries_ordinal` once after bulk insertion into **new** catalogs. The
   measured `SELECT payload FROM entries ORDER BY ordinal` formerly used a temporary
   B-tree. SQLite now scans the ordinal index. Existing catalog Open stays read-only;
   no existing DB receives an index/migration. Payload/schema version 1 stays compatible.

| Workload | Before median | After median | Allocation before → after |
| --- | ---: | ---: | ---: |
| canonical `blue_hair` | 59.10 ms | 29.06 ms | 164.72 → 46.03 MB |
| strong `anal` | 40.98 ms | 20.89 ms | 98.79 → 19.01 MB |
| Japanese `青い髪` | 39.14 ms | 19.69 ms | 96.35 → 18.99 MB |
| short Japanese `髪` | 34.71 ms | 16.57 ms | 88.71 → 15.55 MB |
| broad `breast` | 39.75 ms | 19.88 ms | 98.70 → 19.07 MB |
| mixed `blue_hair 青い髪` | 58.42 ms | 29.02 ms | 180.19 → 50.02 MB |
| alias `exclamation mark` | 53.71 ms | 25.77 ms | 171.47 → 45.96 MB |
| .NET full catalog Open, ordinal candidate | 1,453.29 ms | 1,067.35 ms | unchanged steady allocation (~716 MB) |
| actual WPF title + input idle | 3,440.59 ms | 2,960.45 ms | working set ~424 → 423 MB |

All 17 measured queries, including the typing sequence `b → bl → blu → blue →
blue_h → blue_ha → blue_hai`, retain identical ordered ID/rank hashes and counts.
Search allocation falls roughly 72–86%; latency about 49–54%. Managed retained
catalog + UnifiedBrowse heap remains ~203 MB; startup memory is effectively unchanged.
Raw catalog SQL read/decode (Python, excluding JSON/index construction) falls
470.24 → 120.91 ms. This is separate from the .NET Open measurement; do not add
these improvements together. Ordinal index costs 1,449,984 bytes (~0.97%) per new
catalog. Query plans and all three samples are retained in the JSON result.

## Other paths and rejected candidates

- Full JSON read/deserialization and the one RuntimeCatalogIndex construction
  remain the bulk of startup (~0.86 s and ~0.50 s in warm samples). Retain the
  in-memory design; lazy projections/new storage formats/serializer rewrites add
  compatibility and maintenance costs not justified after the bounded improvement.
- Category-first scoring could change **global** strong-intent suppression and
  deduplication (including hidden Artist collisions). Reject this shortcut;
  eliminate scoring allocations without altering the search population.
- Unified Browse neutral/facet ~1–2 ms; HOME/group indexed navigation below
  meaningful timer resolution; HOME search improves through the same Rank change.
  No extra caches or HOME/index rewrite.
- Existing 20k Library text/favorite/last-page queries ~2–7 ms. `image_date`,
  annotation favorite and parameter indexes serve representative plans. Favorite
  still sorts a small matched set; leading-wildcard text still scans. FTS would
  alter matching; extra composite indexes/cache invalidation complexity have
  insufficient current UI benefit. Full-suite fixture timings are observational,
  not isolated cold/warm scan claims: 5,000 images warm scan ~0.4–0.5 s, zero rereads.
- PNG metadata read ~0.071 ms; 100 pure parses ~0.392 ms. No parser-result cache
  (would require reliable external-file invalidation). Metadata fidelity unchanged.
- 1,000-LoRA synthetic header fixture: cold scan ~440 ms; warm scan ~190 ms,
  **zero hashes**, 1,000 unchanged; name lookup ~0.646 ms, last page ~1.55 ms.
  Insertability safety check ~1.15 ms. No public hash-query API was added;
  existing SQLite `lora_hash` lookup plan was inspected. No scanner/cache rewrite.
- Real Library 90,112 bytes, LoRA DB 32,768 bytes, thumbnail cache 7 files/551,452
  bytes; zero free pages in all inspected real DBs. 20k fixture ~11.36 MB.
  No evidence warrants VACUUM, PRAGMA writes, deletion, deduplicating raw metadata,
  UserData migration or obsolete-artifact cleanup. Raw Prompt/unknown parameters
  are intentionally preserved. No copied UserData in validation packages.
- Standard SQLite and .NET suffice; reused existing adoption matrix. No broad OSS
  survey, unsafe cache, architectural rewrite or speculative parallelization.

## Verification and artifact disposition

- Targeted search/HOME: 11 PASS; supporting fixture: 1 PASS; ordinal measurement:
  1 PASS; storage/authority tests: 7 PASS, 2 explicit migration-oracle skips.
- Final clean Release solution build: 0 warnings/errors. Full Release regression:
  **360 PASS, 25 opt-in skips, 0 failures** (385 total). First full pass preceded
  discovering the storage candidate; one justified final rerun includes it.
- Maintenance Python: 22 PASS, 1 skip; workspace contracts: 2 PASS.
- Accepted authority compiled into a fresh isolated output. All 124,895 complete
  payloads, including ordering, have identical normalized JSON SHA256 against
  the unchanged installed catalog. Small fixture verifies index plan, payload
  bytes/order and read-only compatibility with old catalogs lacking the index.
- Self-contained win-x64 single-file publish succeeds; payload ~326.68 MB.
  Baseline/search-candidate publish ~4.80/3.59 s are one-run incremental observations,
  not an optimization claim. Final package adds the catalog index bytes.
- Three real Windows Hidden title/input-idle launches plus a launch after copying
  the executable/catalog/ForgeBridge to another location succeed. Only disposable
  per-package UserData is created. This is startup/copy validation, not manual UI
  interaction testing or a second-PC claim. Initial final timing overlapping a
  build was discarded before the recorded sequential measurement.
- Environment retries: missing RID assets were restored; final clean build passed.
  Bounded `-m:1 -nr:false` avoids workstation MSBuild worker/pipe overhead. No
  product change for transient build/sandbox measurement failures.
- Production executable/manifest/catalog/ForgeBridge + UserData: **19/19 files
  unchanged**, same file count and hashes (includes 14 UserData files). No legacy
  Python or existing data trees moved/deleted. Canonical authority files untouched.
- `.local/issue254/` contains ignored measurement-only baseline archive, scripts,
  logs/TRX, scratch index DB, newly compiled catalog and startup/copy packages.
  They are not production-ready promotion packages; no runtime-manifest claim,
  automatic installation or broad cleanup. Durable evidence is this doc/JSON;
  the opt-in harness remains test-only, disabled in normal CI.

Reproduce full measurement with `DTT_PERF_CATALOG` pointing to a full read-only
catalog and `DTT_PERF_REPORT` to a scratch JSON destination, then run:
`dotnet test src/DanbooruTagTool.Tests -c Release --filter FullyQualifiedName~Issue254PerformanceTests -m:1 -nr:false`.
Ordinal comparison additionally requires `DTT_PERF_INDEX_CATALOG` pointing to a
separately generated indexed catalog. CI must not set workstation benchmark envs.

Rollback: revert the product changes/PR. Old catalogs work unchanged; a newly
indexed catalog is compatible with the baseline reader, so no UserData rollback
or DB migration is required. Normal catalog rebuilds require an explicit fresh
destination, as before. Production stays on the #245 LKG.

Stop at #254 PR acceptance. After accepted CI/review, #254 can complete and the
user can decide whether #255 history cleanup is warranted. Do not start #255,
#230, #256 or Foundation production/LKG promotion automatically.
