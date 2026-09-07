# SEMANTIC_BRIDGE_SCHEMA.md

Semantic 336は実Danbooru canonicalではない。

runtime AIで毎回推測せず、静的bridge tableを正本にする。

File:
`data/semantic/semantic_bridge_v1.csv`

1 candidate = 1 row。

columns:
- semantic_id
- special_id
- semantic_term
- ja_label
- en_concept
- candidate_canonical
- relation_type
- notes
- review_status

relation_type allowed:
- exact-ish
- alias-like
- broader
- narrower
- related
- UNMAPPED

review_status:
- UNREVIEWED
- REVIEWED
- REJECTED

初期v1.2では336 semantic termを全て行として登録し、
candidate未設定はrelation_type=UNMAPPED。

Stage 3:
loader / validator / search対応。

Stage 8:
candidate mappingの充実。

Semanticにfake countを与えない。
