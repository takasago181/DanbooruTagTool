# Protected data rebuild assessment — 2026-09-10

## Scope and stop condition

This document records a read-only rebuildability assessment after the
protected-data recovery remained at `PROTECTED_DATA_RECOVERY_HOLD`.

No missing file was regenerated, re-acquired, copied, overwritten, deleted, or
substituted. No rebuild script was executed and no pytest was run. `#35`, `#49`,
and main merge were not started.

The previously requested recovery report was committed and pushed first:

- branch: `dict-validation/quarantine`
- pushed tip: `1304a42`
- recovery report: `docs/recovery/PROTECTED_DATA_RECOVERY_20260910.md`

## Assessment verdict

`PARTIAL_REBUILD_POSSIBLE`

This is an assessment only, not permission to rebuild. The six binary raw-index
arrays, `tags.json`, and `index_metadata.json` have a documented deterministic
build path that can reproduce the accident-before bytes only after the exact
approved Parquet is obtained and all input/code hashes are frozen. The original
Parquet and three pinned Japanese source files are externally re-acquirable by
exact revision and SHA-256. Build/audit metadata and the canonical overlay are
not expected to reproduce the accident-before file SHA because they contain
build timestamps and, for `build_report.json`, elapsed time. The surviving
evidence does not identify a unique project-local human-edited file among the
missing paths, but the complete accident-before per-file manifest is absent.

Therefore this is not `SAFE_TO_REBUILD_MISSING_ONLY`, and no rebuild is safe to
execute under the current task boundary.

## Count reconciliation

The user-provided delta is 14 files. The local pre-freeze inventory identifies
15 absent accident-before paths, while the current `data/**` contains one
additional file that was not in that inventory:

- absent: 11 `data/runtime_index/**` files + 1 runtime Parquet + 3 Japanese
  source CSV files = 15 paths;
- unexpected extra: `data/source/danbooru2026_clean.parquet`;
- net file-count delta: 15 absent minus 1 extra = 14.

The extra Parquet is not a valid substitute. Its SHA-256 is
`20b684cb47c448486f7c32012ed07c6527346f3218c6297f4e4bbb4e3d6a38d5` and its
provenance is the rejected/provisional `ThetaCursed/danbooru-2026-clean-metadata`
snapshot, not the approved runtime snapshot.

The accident-before inventory records these group totals:

| group | accident-before files | accident-before bytes | current files | current bytes |
|---|---:|---:|---:|---:|
| `data/runtime_index/` | 11 | 2,989,206,293 | 0 | 0 |
| `data/runtime_source/` | 1 | 4,088,245,636 | 0 | 0 |
| `data/japanese/` | 5 | 14,510,223 | 2 | 8,060,592 |

The per-file accident-before manifest is not present. Consequently, the
per-file size is reported as `UNKNOWN` below where only a group total or a
handoff metadata size survived. No size is invented from a different snapshot.

## Classification summary

| classification | count | paths |
|---|---:|---|
| `REGENERATABLE_EXACT` | 8 | six raw arrays, `tags.json`, `index_metadata.json` |
| `REGENERATABLE_NEW_SNAPSHOT_ONLY` | 3 | `canonical_overlay.json`, `BUILD_MANIFEST.json`, `build_report.json` |
| `REACQUIRABLE_ORIGINAL` | 4 | one approved runtime Parquet, three pinned Japanese source CSVs |
| `UNIQUE_LOCAL_LOSS` | 0 found | no evidence among the identified paths |
| `UNKNOWN` | 0 for identified paths | per-file manifest gaps remain a verification limitation |

## File-by-file assessment

### 1. `data/runtime_index/post_ids.u32`

- classification: `REGENERATABLE_EXACT`
- expected size: **44,873,448 bytes** (`11,218,362 * 4`)
- expected SHA-256: `f2a1bc0f7a66359efd6131241e9685796215d5f1b28b2411e74717402882e9bc`
- role: ordinal-to-real-post-ID array for Stage 5 true post-level search.
- created from: the approved runtime Parquet, filtering `is_deleted IS NOT TRUE`.
- generation script/command: `tools/build_runtime_index.py --source <approved-parquet> --output data/runtime_index`.
- upstream: `nyanko-devs/danbooru2026@ebb02a630201c7b51487e45fb90b3fcf4cbedc20:metadata/posts-snapshot.parquet`.
- deterministic: yes for this binary when the exact source bytes, current
  dictionary input, script/version, row predicate, batch scan, and output
  algorithm are frozen. The script refuses a source SHA mismatch.
- what can change: a different snapshot, a changed predicate, changed source
  row order, changed script, or changed input schema changes post ordinals and
  the SHA. The alternate ThetaCursed Parquet must not be used.
- impact: missing raw post IDs prevents verified post-level search results and
  candidate evidence; Special dictionary identity is unchanged, but
  recommendation statistics and Stage 5/6 audit evidence cannot be certified.

### 2. `data/runtime_index/post_tag_offsets.u64`

- classification: `REGENERATABLE_EXACT`
- expected size: **89,746,904 bytes** (`(11,218,362 + 1) * 8`)
- expected SHA-256: `cce3557b8ffaa590cf3d8b30ef97387a3d7751ed52380c2ed732cbd96b0d163e`
- role: post ordinal to contiguous forward tag-list offsets.
- created from: the same approved Parquet and the same `is_deleted IS NOT TRUE`
  population.
- generation script/command: `tools/build_runtime_index.py` as above.
- upstream: the same pinned `nyanko-devs/danbooru2026` snapshot.
- deterministic: yes under the exact source and build contract.
- what can change: population membership, tag tokenization, source order, or
  any build algorithm change changes offsets and downstream array alignment.
- impact: forward post-to-tag traversal and aggregation cannot be validated;
  Special search/candidate aggregation and audit evidence remain unavailable.

### 3. `data/runtime_index/post_tag_ids.u32`

- classification: `REGENERATABLE_EXACT`
- expected size: **1,418,284,880 bytes** (`354,571,220 * 4`)
- expected SHA-256: `5723dbad4112462c5199e9d0e5a76fa9cdfa9909b01b19762588a0d836546290`
- role: contiguous source General-tag IDs for each retained post.
- created from: the exact approved Parquet `tag_string_general` values.
- generation script/command: `tools/build_runtime_index.py`.
- upstream: the same pinned `nyanko-devs/danbooru2026` revision and file SHA
  `5b6b2671dc0fa966de71af76dfd342f485f76581447cec9e26c313ba9fb1c2fd`.
- deterministic: yes under exact source, dictionary-independent source tag
  ordering, tokenizer, and script version.
- what can change: any source tag spelling/order, deletion predicate, or code
  change changes the byte stream.
- impact: no verified reverse aggregation or candidate counts; Special
  recommendation statistics and audit replay are blocked.

### 4. `data/runtime_index/tag_post_offsets.u64`

- classification: `REGENERATABLE_EXACT`
- expected size: **825,592 bytes** (`(103,198 + 1) * 8`)
- expected SHA-256: `e35ebb6bec5871a3be11fb517eceaa67fa72fe7d4a90e25ae97be395fa01435c`
- role: runtime General-tag ID to posting-list offsets.
- created from: the stable sorted unique General-tag set and post-tag data from
  the approved Parquet.
- generation script/command: `tools/build_runtime_index.py`.
- upstream: the same pinned approved Parquet.
- deterministic: yes if the exact source, stable sort, and tag-ID assignment
  remain unchanged.
- what can change: tag set, sort/order rules, or source population changes the
  tag IDs and every reverse posting offset.
- impact: true AND search cannot be reconstructed; Special lookup and
  recommendation counts cannot be trusted.

### 5. `data/runtime_index/tag_post_ordinals.u32`

- classification: `REGENERATABLE_EXACT`
- expected size: **1,418,284,880 bytes** (`354,571,220 * 4`)
- expected SHA-256: `f9a65e470dc0cc221a1e18ac0b95735b9197aeb23be178cde7323c9ff4261d84`
- role: reverse posting lists from each runtime tag to post ordinals.
- created from: the same post/tag arrays and stable tag sort in the runtime
  index builder.
- generation script/command: `tools/build_runtime_index.py`.
- upstream: the same pinned approved Parquet.
- deterministic: yes under the exact source and stable sorting contract.
- what can change: source row order, tag tokenization, tag-ID order, or sort
  implementation changes the posting bytes.
- impact: true multi-tag AND, candidate aggregation, Special recommendation
  counts, and post-level audit replay are blocked.

### 6. `data/runtime_index/runtime_global_counts.u32`

- classification: `REGENERATABLE_EXACT`
- expected size: **412,792 bytes** (`103,198 * 4`)
- expected SHA-256: `2b5896da23c0c6c58e39a3fdced01aa4bf4cd7cb62b70d7d8c218cfe6d4662f1`
- role: same-population General-tag global counts.
- created from: `tag_string_general` in the approved Parquet after the fixed
  deletion predicate.
- generation script/command: `tools/build_runtime_index.py`.
- upstream: the same pinned approved Parquet.
- deterministic: yes under exact source and population rules.
- what can change: source snapshot, deleted-row handling, tag tokenization, or
  population policy changes counts and the SHA.
- impact: global frequency, recommendation ranking inputs, and audit count
  comparisons cannot be verified; Special dictionary rows themselves remain
  unchanged.

### 7. `data/runtime_index/tags.json`

- classification: `REGENERATABLE_EXACT`
- expected size: **UNKNOWN**; the surviving inventory records only the
  runtime-index group total and the file SHA.
- expected SHA-256: `b8be4780f5d21bcd938ddace58220d0a003418407e29d1563f937a60b9a867aa`
- role: runtime tag ID to source General-tag string mapping; 103,198 entries.
- created from: the sorted unique `tag_string_general` values in the approved
  Parquet.
- generation script/command: `tools/build_runtime_index.py`.
- upstream: the same pinned approved Parquet; current dictionary is used only
  for unresolved-tag audit counts, not to invent runtime tags.
- deterministic: yes under exact source bytes and Python/JSON serialization
  contract used by the builder.
- what can change: source snapshot, tag spelling/order, JSON serialization, or
  source schema changes the file; a current dictionary must not be used to
  silently rewrite it.
- impact: raw runtime tag identity and lookup are unavailable. Special
  canonical identity is not itself deleted, but search, recommendation, and
  audit mapping cannot be replayed.

### 8. `data/runtime_index/index_metadata.json`

- classification: `REGENERATABLE_EXACT`
- expected size: **1,187 bytes** in the Stage 5 handoff; accident-before size
  is not independently proven by the missing per-file manifest.
- expected SHA-256: `237f93b497ef2fda8c0abeb99dac81cd53b790b0fdc81581821f962884cbc2db`
- role: runtime format, snapshot, population, tag-count, and unresolved-tag
  metadata contract.
- created from: `tools/build_runtime_index.py` metadata fields.
- generation script/command: `tools/build_runtime_index.py`.
- upstream: the same pinned approved Parquet plus the current approved
  dictionary snapshot used by the original build.
- deterministic: yes; unlike `BUILD_MANIFEST.json`, the builder's metadata
  object has no build timestamp or elapsed-time field.
- what can change: source statistics, dictionary contents/hash, format version,
  or JSON serialization changes the bytes.
- impact: the runtime cannot establish snapshot compatibility. Search,
  recommendation, and audit must remain on hold without it.

### 9. `data/runtime_index/BUILD_MANIFEST.json`

- classification: `REGENERATABLE_NEW_SNAPSHOT_ONLY`
- expected size: **2,255 bytes** in the Stage 5 handoff; accident-before size is
  not independently proven.
- expected SHA-256: **UNKNOWN**; no accident-before hash survived.
- role: provenance manifest and per-file hash manifest for the runtime index.
- created from: `tools/build_runtime_index.py`.
- generation script/command: `tools/build_runtime_index.py`.
- upstream: the same approved Parquet, dictionary, Special, and semantic
  inputs are named in the builder.
- deterministic: **no for the complete file**. `index_build_timestamp` is
  generated from `datetime.now(timezone.utc)`, so a new build changes the
  manifest even when every data byte is identical.
- what can change: timestamp, input hashes if any protected input changed,
  file hashes, format version, and JSON serialization.
- impact: the runtime may be rebuilt only after a new audit establishes the
  manifest; the Special dictionary is unaffected directly, but exact recovery
  and audit provenance cannot be claimed.

### 10. `data/runtime_index/build_report.json`

- classification: `REGENERATABLE_NEW_SNAPSHOT_ONLY`
- expected size: **1,352 bytes** in the Stage 5 handoff; accident-before size is
  not independently proven.
- expected SHA-256: **UNKNOWN**; no accident-before hash survived.
- role: build statistics and timing/audit report.
- created from: `tools/build_runtime_index.py` after the index arrays and JSON
  metadata are written.
- generation script/command: `tools/build_runtime_index.py`.
- upstream: same approved Parquet and dictionary inputs as the raw index.
- deterministic: **no for the complete file** because `build_seconds` uses
  wall-clock execution time. The population and tag-entry fields are
  deterministic, but the serialized report SHA is not.
- what can change: elapsed time, environment, I/O, and any metadata fields.
- impact: no direct Special search behavior, but the build/audit evidence is
  incomplete and cannot certify the accident-before artifact.

### 11. `data/runtime_index/canonical_overlay.json`

- classification: `REGENERATABLE_NEW_SNAPSHOT_ONLY`
- expected size: **UNKNOWN**; the pre-freeze inventory records the group total
  but no surviving per-file size.
- expected SHA-256: `bf9a62105740ec579ea0618721b78a0d3ccc2279cf18aabf402c3083ede05195`
- role: current-canonical to raw source-tag identity overlay, including alias
  unions and runtime-only statuses.
- created from: `tools/build_canonical_overlay.py`, using the raw runtime index
  and `TagKnowledgeCore.load(root)`.
- generation script/command: `tools/build_canonical_overlay.py --index data/runtime_index --output data/runtime_index/canonical_overlay.json`.
- upstream: the exact raw runtime index, current dictionary snapshot
  `2026-09-02`, alias/semantic inputs loaded by `TagKnowledgeCore`, and the
  project normalizer.
- deterministic: **payload conditionally yes, complete file no**. The payload
  hash is deterministic for identical raw index and dictionary inputs, but
  `mapping_build_timestamp` changes on every build.
- what can change: dictionary/alias files, raw source tag IDs, mapping rules,
  overlay format, JSON ordering, and timestamp.
- impact: Special canonical union counts, alias-aware search, recommendation
  aggregation, and mapping audit are unavailable. The Special source itself is
  not modified.

### 12. `data/runtime_source/posts-snapshot-ebb02a630201c7b51487e45fb90b3fcf4cbedc20.parquet`

- classification: `REACQUIRABLE_ORIGINAL`
- expected size: **4,088,245,636 bytes**
- expected SHA-256: `5b6b2671dc0fa966de71af76dfd342f485f76581447cec9e26c313ba9fb1c2fd`
- role: fixed upstream post-level source for the Stage 5 runtime index.
- created from: external acquisition; it is not a locally generated derivative.
- generation script/command: no project generation command; acquire the exact
  pinned file only after an explicit future recovery decision.
- upstream: `nyanko-devs/danbooru2026`, revision
  `ebb02a630201c7b51487e45fb90b3fcf4cbedc20`,
  `metadata/posts-snapshot.parquet`.
- deterministic: the source bytes are fixed by the upstream revision and
  expected SHA, but re-acquisition has not been performed in this assessment.
- what can change: upstream availability, download content, or selecting a
  different snapshot. The SHA must be checked before any future build.
- impact: without this source, the raw runtime index cannot be rebuilt or
  independently re-audited. Special dictionary content remains present, but
  post-level search/recommendation statistics and audit replay are blocked.

### 13. `data/japanese/sources/pyu224_danbooru-jp_b5da8f0.csv`

- classification: `REACQUIRABLE_ORIGINAL`
- expected size: **UNKNOWN**; only the Japanese-group aggregate and exact
  source hash survive.
- expected SHA-256: `ef4d6b82dab3f9a086f1e6e5aa62cd3fac522103c6b2587c2c04758ef23ffd1a`
- role: pinned external Japanese candidate source used to produce the local
  Japanese terms sidecar.
- created from: external repository export; not generated by the project.
- generation script/command: consumed by `tools/build_japanese_overlay.py`;
  no acquisition or build was executed.
- upstream: `PYU224/tagdb-updater`, revision
  `b5da8f0141de06cbda3df864ef8afee66131052b`.
- deterministic: original bytes are re-acquirable by revision and SHA; any
  regenerated derived output is conditional on byte-exact acquisition and the
  same builder.
- what can change: upstream availability or content, line endings/encoding,
  and future source revisions. This source is candidate-only in the project
  policy.
- impact: current `japanese_terms.csv` and runtime overlay are present, so
  immediate Special dictionary/search behavior is not removed. Japanese
  overlay provenance and exact rebuild/audit completeness are affected;
  recommendation statistics are not directly sourced from this file.

### 14. `data/japanese/sources/boorutan_danbooru-jp_cec5f7e.csv`

- classification: `REACQUIRABLE_ORIGINAL`
- expected size: **UNKNOWN**; per-file size is not present in the surviving
  accident-before manifest.
- expected SHA-256: `d7523b81e3c62219fc12f2d5a99b4be76e89c7a96d08e70fc30cedea3e058d24`
- role: pinned external Japanese candidate source.
- created from: external repository export; not generated by the project.
- generation script/command: consumed by `tools/build_japanese_overlay.py`;
  no acquisition or build was executed.
- upstream: `boorutan/booru-japanese-tag`, revision
  `cec5f7eefbe5c3addd8fb9338d11435518ae8ccf`.
- deterministic: exact original bytes are re-acquirable if the revision and
  SHA are obtained; derived output is conditional on exact bytes.
- what can change: external repository availability, file bytes, encoding, or
  future revision. The manifest explicitly says its human-authored candidates
  remain candidate-only until project review.
- impact: no direct deletion of current Special/search data because generated
  local outputs survive. Japanese provenance and reproducibility audit remain
  incomplete. The source is human-authored upstream, but it is not a unique
  local-only artifact under the pinned revision.

### 15. `data/japanese/sources/newtextdoc1111_danbooru_tags_fdf2772.csv`

- classification: `REACQUIRABLE_ORIGINAL`
- expected size: **UNKNOWN**; per-file size is not present in the surviving
  accident-before manifest.
- expected SHA-256: `a48e1e63b81e8e4fc3091c660fd763e9d05e19beea3b98d1ee78d00ed10ac9d3`
- role: pinned external Japanese alias/source export; kana-containing aliases
  can become search-only terms under the project policy.
- created from: external dataset export; not generated by the project.
- generation script/command: consumed by `tools/build_japanese_overlay.py`;
  no acquisition or build was executed.
- upstream: `newtextdoc1111/danbooru-tag-csv`, revision
  `fdf2772213f13d46bff60fc5ebd876e1a811a053`.
- deterministic: exact source bytes are re-acquirable by revision and SHA;
  derived output is conditional on exact input and builder version.
- what can change: upstream bytes, CSV schema/encoding, alias interpretation,
  and future revision. External metadata is deliberately not copied into
  project canonical metadata.
- impact: current generated Japanese terms and runtime overlay remain present,
  so Special dictionary/search behavior is not immediately removed. Exact
  source provenance and rebuild/audit completeness are affected; no direct
  recommendation count is derived from this source.

## Runtime-index rebuildability conclusion

The existing source code is sufficient to identify a deterministic raw-index
path. `tools/build_runtime_index.py` checks the approved Parquet SHA before
building, uses the documented `is_deleted IS NOT TRUE` predicate, performs
stable tag ordering, and refuses to overwrite an existing output directory.
The raw arrays and `tags.json` therefore meet the evidence threshold for
`REGENERATABLE_EXACT` **only conditionally** on first re-acquiring and hashing
the exact approved source and freezing the build inputs/version. This report
does not execute that command.

`runtime_index` is not safely replaceable from the present
`data/source/danbooru2026_clean.parquet`. That file is a different snapshot,
has a different schema/population policy, is explicitly not the selected source
in `DATA_SOURCE_DECISION.md`, and has a different SHA.

The canonical overlay has deterministic mapping payload logic, but the full
file is `REGENERATABLE_NEW_SNAPSHOT_ONLY` because its metadata includes a fresh
timestamp. `BUILD_MANIFEST.json` and `build_report.json` have the same problem
and additionally lack surviving accident-before hashes.

## Human-edited unique-local-loss check

No identified missing path is proven to be a unique local-only human edit:

- raw runtime arrays, tags, metadata, overlay, and reports are generated
  artifacts;
- the runtime Parquet is an external pinned source;
- the three Japanese files are external pinned repository/dataset exports,
  including one explicitly described as human-authored upstream, but their
  exact revisions and SHA-256 values are recorded in the surviving manifest.

This is not proof that every local historical edit is recoverable: the original
per-file manifest is missing, and no complete exact-copy backup was found. It is
the reason the verdict is partial rather than safe.

## Search/recovery evidence

- Current `data/**` was inspected without modifying it.
- The approved runtime source path, exact source SHA, builder, predicate, and
  runtime layout were found in the Stage 5 decision and builder.
- Japanese source revisions and hashes were found in
  `data/japanese/japanese_sources.json`; the source files themselves are
  absent.
- Existing backups, `_handoff`, archive, worktrees, and Windows Recycle Bin
  searches found no candidate with the expected runtime-index SHA.
- The Recycle Bin package previously found is a different 90-file snapshot and
  was not used.
- The current alternate Parquet was identified and intentionally not used.

## Explicit non-actions

- no source/runtime/runtime_index/derived regeneration;
- no external download or re-acquisition;
- no file copy into `data/**`;
- no overwrite of existing files;
- no deletion or cleanup;
- no snapshot/version substitution;
- no pytest;
- no `git clean`;
- no `#35` completion, `#49` start, or main merge.

## Final stop point

`PARTIAL_REBUILD_POSSIBLE` is the final assessment. Stop here until a future
task explicitly authorizes a controlled recovery plan with exact source
acquisition, per-file manifest handling, isolated output, hash verification,
and an independent post-recovery gate.
