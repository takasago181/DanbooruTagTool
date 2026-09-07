# RUNTIME_INDEX_DECISION — Stage 5

実施日: 2026-09-05  
対象: Stage 5 のみ。Stage 6 ranking / Lift / UI は未実装。

## 結論

production候補は **`stage5-packed-csr-v1`** とする。論理構造はStage 2の決定どおり双方向であり、Python object graph / JSON / pickle / SQLiteはruntime主indexに用いない。

`data/runtime_index/` はread-only NumPy mmapで開く。通常openはsnapshot・寸法・末端offsetのみ検査し、巨大配列全走査でmmapをresident化しない。SHA-256および全構造走査は明示的な検証モードでのみ行う。

## Physical layout

| file | content |
|---|---|
| `post_ids.u32` | ordinal → actual Danbooru post ID |
| `post_tag_offsets.u64`, `post_tag_ids.u32` | ordinal → General tag IDs (CSR) |
| `tag_post_offsets.u64`, `tag_post_ordinals.u32` | General tag ID → sorted post ordinals (CSR) |
| `runtime_global_counts.u32` | 同一population由来tag frequency |
| `tags.json` | runtime tag ID → source General tag string |
| `index_metadata.json`, `BUILD_MANIFEST.json` | snapshot contract / audit / hashes |

実post IDは `post_ids.u32` に保持するため、AND結果は件数だけでなく将来のEvidence Viewerへ渡せる。Candidate AggregationはANDで得たordinalだけのreverse CSRを走査する。

## Source / population

- source: `nyanko-devs/danbooru2026`, revision `ebb02a630201c7b51487e45fb90b3fcf4cbedc20`
- fixed file: `data/runtime_source/posts-snapshot-ebb02a630201c7b51487e45fb90b3fcf4cbedc20.parquet`
- SHA-256: `5b6b2671dc0fa966de71af76dfd342f485f76581447cec9e26c313ba9fb1c2fd` (PASS)
- predicate: `is_deleted IS NOT TRUE`
- raw / included: 11,740,666 / 11,218,362 rows
- deleted counts: true 522,304 / false 9,473,738 / NULL 1,744,624
- max actual post ID: 11,786,128
- tag entries: 354,571,220; source unique General tags: 103,198

## Dictionary reconciliation

現行2026-09-02 dictionaryへ解決できたsource General tagは30,591、未解決は72,607だった。未解決tagは黙って捨てず、fake canonicalを作らず、`tags.json` の明示的runtime-only IDとして保存した。例: `!-shaped_pupils`, `"friends"_(meme)`, `+_@`。

これはsource/dictionary snapshot間の重大な整合性監査事項である。Stage 5はindexの正確性を優先し、後続で辞書へ偽装統合しない。Stage 6へ入る前に、current dictionaryとの対応方針をChatGPT監査で決める必要がある。

## Capacity / build

- index total: 2,974,985,615 bytes (2.77 GiB)
- source scan + packed build total: 351.389 s
- finalization: temp build → integrity validation → rename。partial buildは`.building`でfinal扱いしない。

Windows外部samplerによる計測専用full buildのpeak working setは **4,053,041,152 bytes (3.77 GiB)**。計測出力もhash/構造検証PASS後に削除し、検証済みfinal indexだけを保持した。runtime RAM測定は下記のとおり完了している。

## Correctness

`tools/verify_runtime_index.py` はproduction indexをground truthに流用せず、fixed Parquetを直接再走査した。全candidate co_count、matching actual post IDs、base_count、全runtime global countを比較しPASS。

- 1 tag: `1girl`, 7,773,799
- 2 tags: `1girl AND 2000s_(style)`, 15,033
- 3 tags: 上記 + `:p`, 89
- 5 tags: 上記 + `;p AND animal_ear_fluff`, 3
- small: `.950_jdj`, 1
- medium: `sepia`, 9,998
- large: `crossed_legs`, 100,005

## Full-scale benchmark

測定はwarm process、各15回、median / p95。詳細は `benchmarks/stage5/full_scale_benchmark.json`。

| condition | base | AND median / p95 ms | aggregation median ms | total median ms |
|---|---:|---:|---:|---:|
| 1 tag | 7,773,799 | 16.890 / 17.846 | — | — |
| 2 tags | 15,033 | 33.126 / 34.557 | — | — |
| 3 tags | 89 | 33.489 / 35.608 | — | — |
| 5 tags | 3 | 34.275 / 35.207 | — | — |
| base≈1 | 1 | 0.005 / 0.008 | 0.011 | 0.015 |
| base≈100 | 100 | 0.005 / 0.019 | 1.222 | 1.226 |
| base≈10,000 | 9,998 | 0.022 / 0.064 | 96.906 | 96.361 |
| base≈100,000 | 100,005 | 0.167 / 0.444 | 1222.194 | 1197.340 |

open: 22.303 ms / 48,164,864 bytes RSS。aggregation後RSSはbase≈1: 127,922,176、≈100: 128,495,616、≈10,000: 186,970,112、≈100,000: 600,330,240 bytes。file size、virtual mapped size、resident RSSは混同していない。Forgeを自動操作していないため同居の最終検証は未実施。

## Stage 6 interface

`RuntimeIndex.intersect(canonicals)` returns actual post IDs and `base_count`; `aggregate(result, exclude=canonicals)` returns raw candidate `co_count`; `runtime_global_counts` plus `total_posts` provides same-snapshot values. Lift、shrinkage、generic suppression、role classification、UIはこのStageで実装していない。

## Final Stage 5 overlay decision

既存のraw `stage5-packed-csr-v1` は維持し、`canonical_overlay.json` を別レイヤーとして追加した。overlayはcurrent dictionary canonical → raw source tag IDsを保持し、identity（exact_current_general / unique_alias_to_current_general / runtime_only / exact_current_non_general / unique_alias_to_current_non_general / ambiguous / normalization_collision）をsource tagごとに保存する。

aliasを含むcanonicalのglobal count、matching posts、co_countはsource postingのpost集合unionで計算する。source occurrenceの単純加算は使用しない。監査済み58 merge groupと398 duplicate postをこの規則で扱う。runtime-only 72,491語、Semantic-only一致、source Generalだがcurrent non-Generalのtagは元source identityとstatusを維持する。

overlay metadataには `overlay_format_version`、dictionary snapshot/hash、build timestamp、exact/alias/runtime-only counts、merge group count、`statistics_tag_scope=general`、`model_agnostic_statistics=true`、`overlay_payload_sha256`を含む。`overlay_payload_sha256`はself-hash fieldやJSON metadata wrapperを除いたcanonical mapping payload（`canonical_to_source_tag_ids` と `source_tag_identities`）のhashであり、serialized JSON全体のfile SHA-256とは異なる。file SHA-256は配布・ファイル完全性確認用の外部digestとして扱う。raw physical indexを再buildせず、dictionary更新時はoverlayだけ再生成できる。

実Special workloadの現Counter aggregate観測値は、base≈100kで約1.1秒、base≈518kで約5.5秒、base≈1Mで約10秒。cache、progress、cancel、on-demand実行は後続UI Stageの検討事項であり、Stage 5では最適化していない。statisticsはDanbooru snapshot上の観測値で、Checkpointのtag理解度を表さない。ModelProfileはStage 9へ留保する。
