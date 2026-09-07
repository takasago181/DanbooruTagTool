# DATA_SOURCE_DECISION

決定日: 2026-09-05  
対象Stage: Stage 1  
結論: **Candidate A — `nyanko-devs/danbooru2026` を Approved Source とする。**

## 1. 評価原則

- post単位でGeneral tagを再構築できること。
- true multi-tag ANDの入力にできること。
- post ID重複、欠損、削除状態を検査できること。
- Gate 1は公開metadata/schema、Gate 2は上位2候補の同一ID範囲で比較する。
- 画像本体は対象外。production indexおよびRuntime Index方式比較は行わない。

## 2. Candidate Gate 1

公式配布ページ:

- [Candidate A — nyanko-devs/danbooru2026](https://huggingface.co/datasets/nyanko-devs/danbooru2026)
- [Candidate B — ThetaCursed/danbooru-2026-clean-metadata](https://huggingface.co/datasets/ThetaCursed/danbooru-2026-clean-metadata)
- [Candidate C — Shio-Koube/Danbooru-2026-parquet-metadata](https://huggingface.co/datasets/Shio-Koube/Danbooru-2026-parquet-metadata)

| Dataset | 固定revision / metadata | raw rows / distinct ID | max ID | 必要tag・category | null / duplicate | deleted handling | license / continuity | 取得性 | Gate 1 |
|---|---|---:|---:|---|---|---|---|---|---|
| A | `ebb02a630201c7b51487e45fb90b3fcf4cbedc20`; `metadata/posts-snapshot.parquet`; 4,088,245,636 bytes; SHA-256 `5b6b2671dc0fa966de71af76dfd342f485f76581447cec9e26c313ba9fb1c2fd` | 11,740,666 / 11,740,666 | 11,786,128 | `tag_string`と5 category別tag文字列、category別countあり | ID/tag文字列のParquet null 0、ID重複0。`is_deleted` null 1,744,624 | `is_deleted`を保持。false 9,473,738 / true 522,304 / null 1,744,624 | Dataset CardはMIT。1 revisionで更新方針は未提示 | 単一4.09 GB parquet。画像不要 | **通過・1位** |
| B | `864d3ed2a88a8adcde895124a508ce5c9ef574ab`; `danbooru2026_clean.parquet`; 3,940,643,859 bytes; SHA-256 `20b684cb47c448486f7c32012ed07c6527346f3218c6297f4e4bbb4e3d6a38d5` | 9,228,854 / 8,715,129 | 10,068,668 | 全tagと5 category別tag文字列あり、17列へclean済み | ID重複行513,725。category列にnullあり | `is_deleted`列なし。cleaning根拠を実データから再現不能 | license表記なし。短期間3 commits、継続方針なし | 単一3.94 GB parquet | **不採用** |
| C | `203df76a018bd5d463c37666c394b88b5acaa202`; 10 parquet shards; 合計約6.25 GB | 10,621,765 / 9,996,042 | 10,068,670 | 全tag、5 category別tag文字列・count、削除flagあり | ID重複行625,723。shard ID範囲が各20万重複。category列にnullあり | `is_deleted`あり、Parquet null 0 | license表記なし。2 commits、継続方針なし | shard取得可能だが重複除去が必須 | **通過・2位** |

補足:

- AのDataset Card記載上限 `#11,740,611` と実Parquetのmax ID `11,786,128` は一致しないため、実ファイルのfooter値を採用した。
- BのViewer表示 `10.1M rows` とrevision固定raw parquetの行数は一致しないため、決定にはraw parquet値を採用した。
- A/B/CはいずれもDanbooru公式exportではなく、Hugging Face上のcommunity datasetである。AはDataset Card上でsourceをDanbooru Communityとし、metadataを比較的そのまま保持する。B/Cは加工・mirror由来の制約が大きい。
- update continuityは3候補とも確立済みとは判断しない。Approved Sourceはrevisionとfile hashで固定し、無条件に`main`を追従しない。

## 3. Gate 2

同一subset条件:

- selection rule: `1 <= id <= 1,000,000`
- contiguous ID range
- 比較候補: Gate 1上位のAとC
- 検査: ID重複、空tag、General tag null、削除flag、`tag_count_general`再現、5 category count合計
- 読み方: ID欠番があるため「100万ID範囲」であり、実post行数は100万未満になり得る

| Dataset | rows | distinct ID | duplicate rows | empty all tags | General null | deleted=true | General count mismatch | category sum mismatch | AND前処理可能性 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A | 970,265 | 970,265 | 0 | 0 | 0 | 91,218 | 0 | 0 | **そのまま可能**。post ID→General tagsを一意に構築できる |
| C | 1,124,465 | 970,265 | 154,200 | 0 | 0 | 105,197 | 4 | 2 | 可能だが、shard重複除去と不整合処理が先に必要 |

Candidate Cのshard範囲は例としてpart 00がID 1..999,999、part 01が800,000..1,999,999であり、20万IDの意図的または生成工程上の重複区間がある。これはfull build前に必ず除去規則を必要とし、Aに対する利点にならない。

## 4. Approved Source

- Name: `nyanko-devs/danbooru2026`
- Revision: `ebb02a630201c7b51487e45fb90b3fcf4cbedc20`
- File: `metadata/posts-snapshot.parquet`
- Snapshot ID: `nyanko-devs/danbooru2026@ebb02a630201c7b51487e45fb90b3fcf4cbedc20:metadata/posts-snapshot.parquet`
- SHA-256: `5b6b2671dc0fa966de71af76dfd342f485f76581447cec9e26c313ba9fb1c2fd`
- Raw rows / unique post IDs: 11,740,666 / 11,740,666
- Raw max post ID: 11,786,128
- Stated license: MIT（Dataset Card）

採用理由:

1. 3候補中でcoverageとmax IDが最大。
2. 全post IDが一意で、B/Cのような事前dedupを必要としない。
3. `tag_string_general`およびcategory別tag/countを保持し、General tagの再構築と検算ができる。
4. `is_deleted`を失っておらず、削除扱いを本プロジェクト側で監査可能。
5. 同一100万ID範囲でtag count不整合が0だった。

## 5. `is_deleted = NULL` 追加監査と採用方針

2026-09-05にApproved Sourceの固定revisionを追加監査した。

### 三値件数

| state | rows | raw全体比 |
|---|---:|---:|
| `true` | 522,304 | 4.448674% |
| `false` | 9,473,738 | 80.691658% |
| `NULL` | 1,744,624 | 14.859668% |
| total | 11,740,666 | 100% |

### NULL行のtag completeness

- `tag_string` null/empty: 0 / 1,744,624（0%）
- `tag_string_general` null: 0
- `tag_string_general` empty: 64（0.003668%）
- `tag_count_general`とtoken数の不一致: 0
- empty Generalの代表例は`tag_count_general=0`で、全tagはMeta中心に6件存在する動画postだった。欠損ではなくGeneral tagがない行として整合する。

### NULL行のpost ID分布

| ID range | rows | 備考 |
|---|---:|---|
| 4,800,000–4,828,461 | 28,453 | 独立した旧IDのbackfill状block |
| 10,068,671–10,999,999 | 930,887 | Candidate Cのmax ID直後から始まる |
| 11,000,000–11,786,128 | 785,284 | Approved Sourceの最新側block |

NULLは全期間へランダムに散らばらず、取得・変換batch境界と一致する連続的なID帯へ集中する。

### `true`行との主要field欠損比較

| field | NULL rows | true rows | 判断 |
|---|---:|---:|---|
| `tag_string` missing | 0 (0%) | 0 (0%) | 差なし |
| `tag_string_general` empty | 64 (0.003668%) | 159 (0.030442%) | NULL側の方が少ない |
| `md5` missing | 36,308 (2.081136%) | 21,238 (4.066214%) | NULL側の方が少ない |
| `file_url` missing | 36,308 (2.081136%) | 21,238 (4.066214%) | NULL側の方が少ない |
| ID / created / updated / rating / dimensions / tag counts / file type / file size / media asset missing | 0 | 0 | 差なし |
| `uploader_id` / `is_pending` / `is_flagged` / `is_banned` missing | 1,744,624 (100%) | 0 | NULL blockで関連source fieldが一括欠落 |

主要な統計入力であるpost IDとtag情報はNULL行でも完全であり、削除済みpostに特有の欠損増加は見られない。一方、`is_deleted`と同時にuploader・複数booleanが100%欠落するため、NULLはpost状態そのものよりsourceのbatch/schema差を示すと判断する。

ID帯の両端から選んだ代表6件（4,800,000 / 4,828,461 / 10,068,671 / 10,999,999 / 11,000,000 / 11,786,128）は、固定Parquet内でtag、tag count、日時、rating、寸法、file typeを保持していた。Danbooru公式APIの2026-09-05現在値でも6件すべて`is_deleted=false`だった。現在APIは補助確認にのみ使用し、snapshot内のtag countを現在値で置換しない。

### Production statistics population

採用predicate:

```sql
is_deleted IS NOT TRUE
```

- `true` 522,304件のみ除外する。
- `false + NULL` 11,218,362件を、他の採用条件を適用する前のpopulation候補とする。
- NULLをfalseへ書き換えない。staging/runtime auditではraw三値を保持し、`is_deleted_null_count=1,744,624`をmanifestまたはbuild reportへ記録する。
- NULLを全除外すると、tag情報が完全な14.86%を失い、特に最新ID帯を体系的に除外する既知のbiasが生じるため採用しない。
- 代表例確認は全件の削除状態を外部APIで再取得したものではない。将来のsource更新時も三値件数とID帯を再検証する。

Stage 1ではproduction ingestionを行わない。後続buildではさらに次を守る。

- revision URLとSHA-256を固定し、`main`を直接本番入力にしない。
- tagはspace区切りのsource fieldから読み取るが、アプリのPrompt入力をspace tokenizeする設計には流用しない。
- statistics runtimeのglobal countは、このApproved Datasetの採用post集合から計算する。
- 2026-09 tag dictionaryのpost_countはcurrent_post_count専用とする。

## 6. Rejected / retained candidates

- B: ID重複、coverage縮小、削除flag欠落、license未記載のため不採用。
- C: schemaは十分だがshard重複が全体625,723行、Gate 2でも154,200行あり、Aより前処理リスクが高いため不採用。
- 新Candidate D: 今回は追加していない。

## 7. Decision stability

新しいsnapshotが出ただけでは再決定しない。再評価条件は次のみ。

- source停止
- schemaの大変更
- 品質劣化
- 明確に優れた新候補
- ユーザーによる再評価指示

Stage 2へ進む場合は、このApproved Datasetと同一subsetを固定してANDおよびCandidate Aggregation方式を比較する。本作業ではStage 2を実施していない。
