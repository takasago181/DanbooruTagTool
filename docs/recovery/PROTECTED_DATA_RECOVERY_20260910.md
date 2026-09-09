# Protected data recovery — 2026-09-10

## Final verdict

`PROTECTED_DATA_RECOVERY_HOLD`

The supplied accident-before aggregate was not reached. No runtime index or
other file was regenerated or substituted from another snapshot.

## Reference and final inventory

| item | accident-before reference | final observed |
|---|---:|---:|
| files | 89 | 75 |
| bytes | 7,127,474,426 | 3,984,217,957 |
| manifest SHA-256 | `b47148d440e433726abf7e1545629c2cce92d177495db7a1dc0d2b120784fd4f` | `ac5773f851a5276e161ef15199430e12359208dbdbd17982cdba785a54db7492`* |

\* The final value is the SHA-256 of the recovery inventory lines in the
following form, sorted by relative path: `relative-path<TAB>bytes<TAB>file-
sha256<LF>`. It is reported separately because the byte-level accident-before
manifest file/serialization was not present in the workspace.

Residual aggregate difference: **14 files / 3,143,256,469 bytes**.

Known independent manifest mismatch: `data/special2788/illustrious_tag_knowledge_base_2788_README.md`
is 1,146 bytes with SHA-256
`691f896b37ad8eaaad76f0d22a111a0b6da852d96b76e190201e2c07c4476461`, while the
current `FILE_HASHES.json` records 1,106 bytes and
`cb44a99237de588ee2b5934a265078c580dab587af48ebf195251e953a8df70c`. It was
not overwritten because the recovery rules prohibit overwriting an existing
file; this mismatch is included in the HOLD result.

## Recovery performed

Only destinations that did not exist were created. No existing file was
overwritten.

### `data/derived/ruleset2/` — 8 files

The source was the archived Ruleset2 handoff. Every copied file matched the
hash in `RULESET2_MANIFEST.json` before and after copy.

| file | bytes | SHA-256 |
|---|---:|---|
| `01_SPECIAL2788_JAPANESE_COMPLETE_CANDIDATE.csv` | 989,918 | `12f6ccdc5d2dba33123cdfa97a636b2fdd49a519ed89d327d330471696762e02` |
| `06_SEMANTIC336_ROUTING_OVERLAY.csv` | 204,221 | `deb17fd928e7af9fed4a3542fd90d83c96c83e4c4cde9a2d9045b85a2f08e624` |
| `10_MODEL_AUX_CROSSMATCH_UNIQUE_TERMS_2811.csv` | 174,503 | `bc9223d1fbcacdbc19bd41a54b7a093fad8382534707fc858e039aa656a65d81` |
| `24_MODEL_AUX_SOURCE_POLICY_MATRIX.csv` | 988 | `789650ca4d83aac9b3942e302de2b2b9c9e14106525ef745013da69f530f27b7` |
| `31_METADATA_RULESET2_MIGRATIONS_v3.0.csv` | 460,233 | `b9bcf31768e4340b58cc4e6a501d8f398df1f3aa3d15b1e6c72ba696bd8e45a5` |
| `37_ALIAS_SEMANTIC_RELATIONSHIP_v3.0.csv` | 198,908 | `9cb6d667ce4894a8df4e2a9579e0bf9adabd93ccc54ecf28ac57e9dc2581b1d5` |
| `38_ALIAS_STATISTICS_POLICY_v3.0.csv` | 152,089 | `e092014c196bf2406054f7c78c03e63a1cd8cdfdba59c059d2baf50222e7727d` |
| `RULESET2_MANIFEST.json` | 1,460 | `71ca6b039a045fab57be4a3d377a64fc3e1c7638fea98bbc47c1da0c40c444cf` |

### `data/generation/audit/` — 7 files

These are the v2/v2.1 generation-profile audit inputs named by the current
generation-profile report. Each copy matched its handoff source hash after
copy.

| file | bytes | SHA-256 |
|---|---:|---|
| `APPROVED_STATIC_1352_REVIEW_v1.csv` | 545,869 | `dcd09c03e5dd9dedcedfa98e248d758ec8e54a77c0163d3271f2fc779895c30b` |
| `EXPLICIT_STRUCTURAL_OVERRIDES_240_v1.csv` | 94,802 | `e6f20275258c5ad1eb8d40ba21b100c709e457996ba078d7c5bf44270bec09dd` |
| `FAMILY_AUDIT_VALIDATION_v1.json` | 1,002 | `67af388ac98d8414e3a89c0d8e9fff220b2ccf25bdd4830faf1ffe995a05a5dd` |
| `FAMILY_RULE_AUDIT_25_v1.csv` | 7,738 | `70e49f7d1a5ef71167b2ea30bea6bc0ee75a79f60e105575d8ccc3adc49d9975` |
| `HIGH_CONFIDENCE_CORRECTIONS_v1.csv` | 35,507 | `22c76da0cb3a2b58c36b405609823e11c332ae5565c1c4bd35501a3c0be2bbf5` |
| `PROMOTION_COUNTS_v1.json` | 297 | `c6056909e0ed89ef54e386d201f9adeeafe1af7169d5a90913268273b27eb206` |
| `PROMOTION_PLAN_v1.csv` | 1,241,747 | `a1eba3166318bb314c4ac3cb83d85d49b5e60b0bece6300a2fa74022d0197315` |

## Residual missing / unresolved data

The per-file accident-before manifest itself was not found. The following
production contract is known from `docs/architecture/RUNTIME_INDEX_DECISION.md`
and the surviving Stage 5 handoff metadata, but no complete matching copy was
found in the workspace, backups, handoffs, worktrees, or Windows Recycle Bin.

| residual path / class | expected size | current size | expected SHA-256 | recovery candidate |
|---|---:|---:|---|---|
| `data/runtime_index/post_ids.u32` | 44,873,448 | 0 (missing) | `f2a1bc0f7a66359efd6131241e9685796215d5f1b28b2411e74717402882e9bc` | none |
| `data/runtime_index/post_tag_offsets.u64` | 89,746,904 | 0 (missing) | `cce3557b8ffaa590cf3d8b30ef97387a3d7751ed52380c2ed732cbd96b0d163e` | none |
| `data/runtime_index/post_tag_ids.u32` | 1,418,284,880 | 0 (missing) | `5723dbad4112462c5199e9d0e5a76fa9cdfa9909b01b19762588a0d836546290` | none |
| `data/runtime_index/tag_post_offsets.u64` | 825,592 | 0 (missing) | `e35ebb6bec5871a3be11fb517eceaa67fa72fe7d4a90e25ae97be395fa01435c` | none |
| `data/runtime_index/tag_post_ordinals.u32` | 1,418,284,880 | 0 (missing) | `f9a65e470dc0cc221a1e18ac0b95735b9197aeb23be178cde7323c9ff4261d84` | none |
| `data/runtime_index/runtime_global_counts.u32` | 412,792 | 0 (missing) | `2b5896da23c0c6c58e39a3fdced01aa4bf4cd7cb62b70d7d8c218cfe6d4662f1` | none |
| `data/runtime_index/tags.json` | unavailable in surviving manifest | 0 (missing) | `b8be4780f5d21bcd938ddace58220d0a003418407e29d1563f937a60b9a867aa` | none |
| `data/runtime_index/index_metadata.json` | 1,187 in Stage 5 handoff; accident-before size not independently proven | 0 (missing) | `237f93b497ef2fda8c0abeb99dac81cd53b790b0fdc81581821f962884cbc2db` | metadata only, not file copy |
| `data/runtime_index/BUILD_MANIFEST.json` | 2,255 in Stage 5 handoff; accident-before size not independently proven | 0 (missing) | no accident-before hash available | metadata only, not file copy |
| `data/runtime_index/build_report.json` | 1,352 in Stage 5 handoff; accident-before size not independently proven | 0 (missing) | no accident-before hash available | metadata only, not file copy |
| remaining runtime-index / related entries implied by the 89-file manifest | 170,823,179 aggregate remainder; exact per-file split unavailable | 0 or missing | unknown | none |

The exact per-file list for the final four entries cannot be safely invented
from the aggregate manifest digest. No `SIZE_MISMATCH` or `HASH_MISMATCH` was
declared for a file without a surviving expected path/size/hash record.

## Search and safety checks

- Current `data/**` was recursively enumerated and SHA-256 hashed before and
  after recovery.
- Searched existing workspace backups, `_handoff`, `docs/handoff_archive`,
  worktrees, and Windows Recycle Bin metadata/content for exact runtime-index
  copies.
- The deleted old package found in the Recycle Bin was **not** used: it is a
  different 90-file / 3,970,201,250-byte snapshot.
- No data was regenerated, no alternate snapshot was substituted, no unknown
  file was deleted, and no existing data file was overwritten.
- `git clean`, main merge, #35 completion, and #49 start were not performed.

## Stop point

Stopped at `PROTECTED_DATA_RECOVERY_HOLD`. A `PROTECTED_DATA_RECOVERY_PASS`
requires the original per-file manifest or exact copies of all residual files,
followed by a fresh full inventory matching all three supplied reference
values.
