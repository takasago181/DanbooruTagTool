# Protected data final recovery — 2026-09-10

## Final verdict

`RECOVERY_HOLD`

The four approved/pinned sources were recovered exactly and the eight
deterministic runtime-index files reproduced their accident-before SHA-256.
The three timestamp/timing-bearing metadata files were rebuilt as an audited
new snapshot. However, the complete accident-before per-file manifest is still
absent, and the final inventory does not satisfy the supplied overall byte
count after the known extra is excluded. Existing files were not overwritten to
force the totals to match.

No `pytest` or runtime/search regression suite was run because the requested
Phase 6 gate permits it only for `EXACT_ACCIDENT_STATE_RESTORED` or
`FUNCTIONALLY_RESTORED_WITH_AUDITED_NEW_METADATA`; that gate was not met.

## Phase results

### Phase 1 — exact source reacquisition

`EXACT_SOURCE_RECOVERED 4/4`

All four files were downloaded from the pinned revision/commit, staged first,
SHA-256 verified, and then copied only to previously missing destinations.

| path | size | SHA-256 | upstream | result |
|---|---:|---|---|---|
| `data/runtime_source/posts-snapshot-ebb02a630201c7b51487e45fb90b3fcf4cbedc20.parquet` | 4,088,245,636 | `5b6b2671dc0fa966de71af76dfd342f485f76581447cec9e26c313ba9fb1c2fd` | `nyanko-devs/danbooru2026@ebb02a630201c7b51487e45fb90b3fcf4cbedc20`, `metadata/posts-snapshot.parquet` | exact |
| `data/japanese/sources/pyu224_danbooru-jp_b5da8f0.csv` | 4,874,202 | `ef4d6b82dab3f9a086f1e6e5aa62cd3fac522103c6b2587c2c04758ef23ffd1a` | `PYU224/tagdb-updater@b5da8f0141de06cbda3df864ef8afee66131052b`, `dist/danbooru-jp.csv` | exact |
| `data/japanese/sources/boorutan_danbooru-jp_cec5f7e.csv` | 9,599 | `d7523b81e3c62219fc12f2d5a99b4be76e89c7a96d08e70fc30cedea3e058d24` | `boorutan/booru-japanese-tag@cec5f7eefbe5c3addd8fb9338d11435518ae8ccf`, `danbooru-jp.csv` | exact |
| `data/japanese/sources/newtextdoc1111_danbooru_tags_fdf2772.csv` | 1,565,830 | `a48e1e63b81e8e4fc3091c660fd763e9d05e19beea3b98d1ee78d00ed10ac9d3` | `newtextdoc1111/danbooru-tag-csv@fdf2772213f13d46bff60fc5ebd876e1a811a053`, `danbooru_tags.csv` | exact |

No latest version or alternate snapshot was used.

### Phase 2 — deterministic runtime index

`EXACT_REBUILD_MATCH 8/8`

The index was built only with `tools/build_runtime_index.py`, the recovered
approved Parquet, the existing fixed dictionary/Special/semantic inputs, and
the documented `is_deleted IS NOT TRUE` contract. All eight expected hashes
matched.

| path | size | SHA-256 | result |
|---|---:|---|---|
| `data/runtime_index/post_ids.u32` | 44,873,448 | `f2a1bc0f7a66359efd6131241e9685796215d5f1b28b2411e74717402882e9bc` | exact |
| `data/runtime_index/post_tag_offsets.u64` | 89,746,904 | `cce3557b8ffaa590cf3d8b30ef97387a3d7751ed52380c2ed732cbd96b0d163e` | exact |
| `data/runtime_index/post_tag_ids.u32` | 1,418,284,880 | `5723dbad4112462c5199e9d0e5a76fa9cdfa9909b01b19762588a0d836546290` | exact |
| `data/runtime_index/tag_post_offsets.u64` | 825,592 | `e35ebb6bec5871a3be11fb517eceaa67fa72fe7d4a90e25ae97be395fa01435c` | exact |
| `data/runtime_index/tag_post_ordinals.u32` | 1,418,284,880 | `f9a65e470dc0cc221a1e18ac0b95735b9197aeb23be178cde7323c9ff4261d84` | exact |
| `data/runtime_index/runtime_global_counts.u32` | 412,792 | `2b5896da23c0c6c58e39a3fdced01aa4bf4cd7cb62b70d7d8c218cfe6d4662f1` | exact |
| `data/runtime_index/tags.json` | 2,552,325 | `b8be4780f5d21bcd938ddace58220d0a003418407e29d1563f937a60b9a867aa` | exact |
| `data/runtime_index/index_metadata.json` | 1,187 | `237f93b497ef2fda8c0abeb99dac81cd53b790b0fdc81581821f962884cbc2db` | exact |

Build population was 11,218,362 posts, 103,198 unique General tags, and
354,571,220 tag entries. The recovered source SHA was verified by the builder.

### Phase 3 — audited new metadata

`NEW_SNAPSHOT_VALID 3/3`

| path | size | SHA-256 | validation |
|---|---:|---|---|
| `data/runtime_index/canonical_overlay.json` | 14,220,678 | `815e23dc4666b80f4d33374e30f4f7a8f4850cc3cffdfdeff671da46818c050d` | format, snapshot, dictionary hash, payload validation passed |
| `data/runtime_index/BUILD_MANIFEST.json` | 2,255 | `848be737f2c5269b98687194d164fb26fc81e9a868b32a4f4ce1157e157cad89` | format, snapshot, source hash, eight index hashes passed |
| `data/runtime_index/build_report.json` | 1,352 | `2f96162f813df38e1d9ffa499638629fa8318a88b5a32147cd9fd9306db10877` | source hash, population, and tag-entry values passed |

These are intentionally new-snapshot files. Their accident-before SHA cannot
be required because the overlay contains a new mapping timestamp and the
manifest/report contain a new timestamp or elapsed build time.

## Phase 4 — unexpected extra

`UNEXPECTED_EXTRA_NOT_USED`

| path | size | SHA-256 | provenance | use |
|---|---:|---|---|---|
| `data/source/danbooru2026_clean.parquet` | 3,940,643,859 | `20b684cb47c448486f7c32012ed07c6527346f3218c6297f4e4bbb4e3d6a38d5` | `ThetaCursed/danbooru-2026-clean-metadata`, revision `864d3ed2a88a8adcde895124a508ce5c9ef574ab` | not used |

It is a different, rejected/provisional snapshot and was not used for source
recovery, runtime-index build, overlay build, or validation.

## Phase 5 — final inventory

The complete `data/**` inventory was recomputed with relative path, byte size,
SHA-256, tracked/ignored status.

| group | files | bytes |
|---|---:|---:|
| `data/derived/` | 16 | 25,336,393 |
| `data/generation/` | 10 | 2,493,262 |
| `data/japanese/` | 5 | 14,510,223 |
| `data/runtime/` | 1 | 2,236,277 |
| `data/runtime_index/` | 11 | 2,989,206,293 |
| `data/runtime_source/` | 1 | 4,088,245,636 |
| `data/semantic/` | 19 | 255,241 |
| `data/source/` | 2 | 3,944,080,013 |
| `data/special2788/` | 25 | 1,756,179 |
| **total** | **90** | **11,068,119,517** |

Inventory status counts: 25 tracked, 45 ignored, 20 neither according to the
Git path checks used by the scan.

Current inventory serialization:

`manifest_sha256=89bd5eb2b09ef9fc22ce7a3a8b10f487ba8800ef645c3eb88dc48b3a55cc4d88`

Accident-before reference:

- files: 89
- bytes: 7,127,474,426
- manifest SHA-256: `b47148d440e433726abf7e1545629c2cce92d177495db7a1dc0d2b120784fd4f`

After excluding the one known unexpected extra, the current inventory is 89
files and 7,127,475,658 bytes: **1,232 bytes above the supplied reference**.
The known README discrepancy accounts for 40 bytes (`1,146` current versus
`1,106` in `FILE_HASHES.json`); the remaining **1,192 bytes** are not
locatable to a per-file accident-before record because the original
per-file manifest is absent. No existing file was altered to eliminate this
difference.

## Difference and gate summary

| check | result |
|---|---|
| identified missing paths | 0 |
| exact source recovery | 4/4 |
| exact runtime rebuild | 8/8 |
| audited new metadata | 3/3 |
| exact-source/rebuild hash mismatches | 0 |
| expected hash differences accepted as new snapshot | canonical overlay: 1 |
| known existing FILE_HASHES mismatch | README: 1 |
| unexpected extra | 1 |
| unresolved manifest-level byte difference | 1,192 bytes after known README 40-byte discrepancy |
| unique local loss confirmed | 0 |
| overall accident-before manifest match | no |

Because the overall inventory cannot be proven to differ only by the three
new-snapshot files and the known extra, the final result is `RECOVERY_HOLD`.

## Phase 6 — runtime/search regression tests

Not run. The explicit Phase 6 precondition was not met because the final
inventory Gate remained unresolved. The build itself completed with the fixed
source hash and the overlay builder's internal validation passed, but this is
not a substitute for the requested runtime/search/test gate.

No protected data was deleted, regenerated a second time, or modified to make
tests pass.

## Actions and non-actions

- Restored only the four exact external sources and generated the missing
  runtime-index/metadata files described above.
- Did not use the alternate ThetaCursed snapshot.
- Did not overwrite any existing protected file.
- Did not delete unknown files; only the temporary staging directory created by
  this recovery run was removed after SHA-verified copies were installed.
- Did not run `git clean -fdx` or `git clean -fdX`.
- Did not start or complete #35, start #49, start Stage 10 A/B, or merge main.

## Repository handoff

- branch: `dict-validation/quarantine`
- prior pushed assessment commit: `d076a12`
- final report commit: to be recorded after this document is staged
- protected data itself is not added to GitHub.
