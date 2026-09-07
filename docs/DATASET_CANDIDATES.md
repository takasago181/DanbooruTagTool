# DATASET_CANDIDATES.md
確認日: 2026-09-04

Stage 1の初期候補。
この3つ以外を禁止しない。
より良い候補は「候補D」として報告し、無断採用しない。

## Candidate A — nyanko-devs/danbooru2026

Official page:
https://huggingface.co/datasets/nyanko-devs/danbooru2026

確認済み:
- 11M+ images
- IDs up to 11,740,611 とDataset Cardに記載
- `metadata/posts.parquet` がfile treeに存在
- Dataset Card上License: MIT
- 画像本体は不要。metadataだけを対象にする。

Gate 1で必ずposts.parquet実schemaを検査する。

## Candidate B — ThetaCursed/danbooru-2026-clean-metadata

Official:
https://huggingface.co/datasets/ThetaCursed/danbooru-2026-clean-metadata

Files:
- `danbooru2026_clean.parquet` 約3.94 GB
- `tags_dictionary.parquet` 約7.49 MB

公開file pageでclean parquet SHA256:
20b684cb47c448486f7c32012ed07c6527346f3218c6297f4e4bbb4e3d6a38d5

Gate 1でcleaning内容・欠落列・post coverageを確認。

## Candidate C — Shio-Koube/Danbooru-2026-parquet-metadata

Official:
https://huggingface.co/datasets/Shio-Koube/Danbooru-2026-parquet-metadata

複数parquet shard。
公開shard例:
- output_part_00.parquet 約497 MB
- output_part_02.parquet 約592 MB

派生mirrorでは10,621,765 rows / 6.25 GBと表示されるため、
正本側の実row countをGate 1で確認する。

## Reference only — u-haru/danbooru-tags-20260518

https://huggingface.co/datasets/u-haru/danbooru-tags-20260518

README:
Collected post ids 1 ~ 11,403,815

既製2026-05共起行列と照合する参考source。
本番primary sourceに自動採用しない。

## Gate 1 不採用条件例

- post単位のtag情報がない
- 必要なGeneral tagを再構築できない
- coverage不明か著しく少ない
- schema/欠損がAND集計に不適
- license/配布条件が用途に不適
- 取得が現実的でない
- data corruption / duplicateが重大

## Gate 2

Gate 1上位1〜2候補のみ。
同一の100万〜数百万post程度のsubsetを使う。

Stage 1ではfull production indexを作らない。
