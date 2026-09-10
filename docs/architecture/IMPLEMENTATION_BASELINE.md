# IMPLEMENTATION_BASELINE

確認日: 2026-09-05  
対象: `C:\Codex\DanbooruTagTool`  
実施範囲: Stage 0 および Stage 1 の前提確認のみ

## 1. 製品目的と境界

- 主役は Special Core Dictionary の Special entry・組み合わせから成る Core Tag Set。
- All Danbooru、true multi-tag AND、Candidate Aggregation は Core を補助する。
- Core / Auxiliary / LoRA は後続実装でも内部的に分離する。
- Stage 0/1 では production index、Runtime Index方式比較、推薦UI、Prompt UIを実装しない。
- Candidate Aggregation の方式・性能比較は Approved Dataset を固定した後の Stage 2 に留保する。

## 2. Inventory

| 区分 | 場所 | 状態・用途 |
|---|---|---|
| 正本タグ辞書 | `data/source/danbooru-2026-09-02.csv` | headerless 4列、3,436,154 bytes、124,016 canonical |
| production snapshot/corpus | `data/special2788/` | 互換上の `Special2788` path。CSV / XLSX / README、合計2,788語 |
| Semantic Bridge | `data/semantic/semantic_bridge_v1.csv` | 336行、初期値は全件UNMAPPED |
| 監査済み派生物 | `data/derived/` | canonical・alias・Special linkage・監査報告。正本の代替ではない |
| 参考コード | `references/` | trial v0.2 / legacy prototype。通常実装の入力・正式pytest対象にしない |
| 由来資料 | `archive/provenance/` | Special2788の由来監査専用。通常実装の入力にしない |
| 仕様 | `docs/` | Stage、schema、統計、テスト、アーキテクチャ方針 |
| テスト | `tests/` | ルート `pytest.ini` により正式suiteを限定 |
| manifest | `PACKAGE_MANIFEST.json`, `FILE_HASHES.json` | 同梱物と配布時hashの基準 |
| manifest雛形 | `templates/BUILD_MANIFEST.template.json` | production build時のsnapshot整合性契約 |

このディレクトリはGit repositoryではないため、変更前差分はGitで記録できない。配布時基準は `FILE_HASHES.json` を使用する。

## 3. Source integrity

- `FILE_HASHES.json` の79エントリを実ファイルのsizeおよびSHA-256と照合した。
- 欠落: 0
- size不一致: 0
- SHA-256不一致: 0
- 正本の代表hash:
  - tag dictionary: `9b32d5ac0713ab252e7470ba6af9cb34de56878b6b3b13dfbbf6a4a37d82d95b`
  - Special2788 CSV: `07584b365d5a68dbadd3f5e80859e768c2718b18746e32de02ce4b8bd60935e3`
  - Special2788 XLSX: `70a2705644cbe8503c33f4b5fad16e57b3ab2dc8601d65ae881822226471054a`
  - Semantic Bridge: `d34df85810641447f39e4b12f9dcecab6983b2e1a4384439fa3934dba8c35247`

`data/source/` と `data/special2788/` は変更していない。

## 4. Raw schema baseline

`data/source/danbooru-2026-09-02.csv` を headerless CSV として検証した。

- 全行4列: tag / category / post_count / aliases
- 行数: 124,016
- category: `{0, 1, 3, 4, 5}` のみ
- canonical空文字: 0
- canonical重複: 0
- post_count非整数または負数: 0
- aliasesはquoted CSV fieldとして標準CSV readerで処理可能

`post_count` は current_post_count 用であり、将来のstatistics runtime母数には使用しない。

## 5. Special / Derived baseline

- Special layer: Core 759 / Extended 915 / Alias 778 / Semantic 336、合計2,788
- 一意canonical解決: 2,443
- ambiguous alias: 9（silent resolve禁止）
- Semantic Bridge: 336 unique ID、fake canonical / fake countなし
- 監査済み派生物の既知hashも `FILE_HASHES.json` と一致

## 6. pytest baseline

作業開始時は Python 3.14.7 にpytestが未導入だったため、`requirements-dev.txt` の指定 `pytest>=8,<9` に従い pytest 8.4.2 を導入した。

- 導入前正式実行: `py -m pytest` → `No module named pytest`
- 導入後の初期正式実行: 7 passed
- Stage 0で追加した恒久テスト:
  - protected sourceのsize/hash一致
  - package manifestの正本参照と欠落宣言
  - BUILD_MANIFEST templateの必須field
  - raw canonical重複・post_count整数/非負

## 7. BUILD_MANIFEST初期化方針

- `templates/BUILD_MANIFEST.template.json` の必須fieldをpytestで固定する。
- Stage 1で `statistics_dataset_name`、`statistics_dataset_snapshot_id`、公開ファイルSHA-256、raw total rows、max post IDを決定文書へ固定する。
- `statistics_total_posts` は、Approved Sourceのdeleted/null取扱いを適用した採用post集合から算出する。raw行数をそのまま偽装しない。
- `index_format_version` と `index_build_timestamp` はStage 2以降で実体を作るまで空欄とする。
- production `BUILD_MANIFEST.json` はproduction indexが存在しないStage 0/1では作成しない。
- 後続ではstatistics index / runtime counts / aggregation indexのsnapshot ID不一致を起動時に拒否する。

## 8. Stage 0完了条件

- Source preservation: 達成
- 同梱hash検証: 達成
- Raw schema検証: 達成
- pytest基盤: 達成
- BUILD_MANIFEST初期化方針: 固定
- Source Dataset決定: `docs/decisions/DATA_SOURCE_DECISION.md` に分離
