# Codex 初期実装仕様書 v1.3 FINAL

## 1. 最終目的

これは万能Danbooru検索ツールではない。

ユーザーはまず特殊2,788語から1語または複数語を選び、Core Tag Setとして生成の核を作る。
その核だけでは固定しにくい要素を、実postデータのtrue multi-tag ANDとCandidate Aggregationで補助する。
特殊辞書に足りないものだけ全Danbooruへ広げる。
最後に画像生成用英語Promptへ落とす。

ユーザー体験:
特殊辞書から日英で探す
→ 選ぶ
→ 実共起が更新
→ 関連タグを追加
→ 必要なら全Danbooru
→ LoRA
→ Copy

## 2. Special-first

### Core Tag Setを第一級にする

単語1個だけでなく、Special Core Dictionaryの複数Specialの組み合わせを「核」として保持する。

内部区分:
- Core Tag Set
- Auxiliary Tags
- LoRA

v1 minimumは `docs/CORE_TAG_SET_SCHEMA.md` に従う。
高機能preset managerへ拡張しない。


メインUI:
- 特殊辞書
- 関連おすすめ
- 全Danbooru

特殊辞書は別添えではなく主画面。

ただし検索関連度をSpecialだから捏造しない。

Exact matchは常に最優先。
その後にSpecialをUI上優遇する。

## 3. 固定production snapshot（互換識別子: Special2788）

total 2,788
Core 759
Extended 915
Alias 778
Semantic 336

normalized linkage:
canonical 1,674
alias_unique 767
alias_ambiguous_curated 2
alias_ambiguous_multiple 9
semantic_unmapped 336

unique canonical resolved:
2,443 / 2,788

audit:
post_count mismatch 0
Layer mismatch 0
English pairing 2,788/2,788
source category pairing 2,788/2,788
Japanese description pairing 2,788/2,788

translation review candidates:
676

## 4. Source / Derived / Provenance

正本:
- data/source/danbooru-2026-09-02.csv
- data/special2788/illustrious_tag_knowledge_base_2788.csv
- data/special2788/illustrious_tag_knowledge_base_2788.xlsx
- data/special2788/illustrious_tag_knowledge_base_2788_README.md

監査済み派生:
- data/derived/*

由来:
- archive/provenance/*
通常実装では使用しない。

## 5. Stage 0 — Source Preservation / Manifest / pytest基盤

成果物:
- docs/architecture/IMPLEMENTATION_BASELINE.md
- source hash確認
- raw schema test
- pytest baseline
- BUILD_MANIFEST初期化方針

ここからpytestを使う。

## 6. Stage 1 — Source Dataset Decision

目的:
post-level dataの正本だけを決める。

Gate 1:
- snapshot
- coverage
- total posts
- max post id
- schema
- tag fields
- category fields
- null
- duplicate
- deleted post handling
- license
- source credibility
- update continuity
- download practicality

Gate 2:
Gate 1上位1〜2候補だけ。
同一100万〜数百万post程度のsubsetで:
- 必要tag情報が再現可能か
- malformed/null処理
- AND用前処理可能性
を検証。

禁止:
- 全候補full build
- Runtime Index方式比較
- production index

成果物:
docs/decisions/DATA_SOURCE_DECISION.md

Approved Sourceを一度決めたら、
新snapshotごとにDataset Decisionを開き直さない。

再評価条件:
- source停止
- schema大変更
- 品質劣化
- 明確に優れた新候補
- ユーザーによる再評価指示

## 7. Stage 2 — AND + Candidate Aggregation Architecture Decision

同一のApproved Dataset、同一subsetで比較。

重要:
ANDそのものより、AND後の候補tag頻度集計がボトルネックになり得る。

比較候補例:
- Roaring Bitmap
- sorted integer arrays
- mmap binary
- SQLite
- tag->posts + post->tags 双方向index

測定:
- build time
- build peak RAM
- runtime RAM
- index size
- 1-tag
- 2-tag AND
- 3-tag AND
- 5-tag AND
- Candidate Aggregation:
  base=1
  base≈100
  base≈10,000
  base≈100,000
- Forge同時使用を想定した常駐RAM影響
- 実装複雑度

成果物:
docs/architecture/INDEX_ARCHITECTURE_DECISION.md

## 8. Stage 3 — Tag Knowledge Core

実装:
- Canonical
- Alias
- Special Core Dictionary
- Translation layer
- Static Semantic Bridge schema
- normalization
- PromptTag

normalization:
NFKC
lowercase
trim
underscore/space normalized lookup key
canonical exact優先
alias exact
Japanese exact
Semantic exact
prefix/partial

Prompt文字列をspaceでtokenizeしない。

Prompt-level input:
comma/newlineでtag候補単位に分割。

## 9. Semantic 336

Semantic bridgeはruntime AI推論で作らない。

静的表:
semantic_id
semantic_term
ja_label
en_concept
candidate_canonical
relation_type
notes
review_status

1 candidate = 1 row。

relation:
exact-ish
alias-like
broader
narrower
related

Stage 3:
schema / loader / validator / search integrationを完成。

Stage 8:
mapping内容とUXを充実。

336件全レビューをStage 1/2のblockerにしない。

## 10. Stage 4 — Unified Japanese / English Search

1検索欄。

対応:
Japanese
English
mixed
underscore
Prompt-space

検索priority:
1. Exact
2. Special候補
3. All Danbooru候補
4. Semantic「意味から探す」

match qualityをSpecial boostより優先。

## 11. Stage 5 — Full Index + True AND + Candidate Aggregation

Approved Datasetをfull build。

必要:
- true A AND B AND C...
- base_count
- candidate/global count
- co_count
- candidate aggregation
- runtime global counts

runtime global countsはApproved Dataset自身から算出。

2026-09 tag CSVのpost_countを統計母数へ使用禁止。

## 12. Stage 6 — Statistics / Reliability / Ranking

表示値はraw:
- base_count
- co_count
- co_count/base_count
- current_post_count
- relative multiplier

ranking内部だけ少数標本補正。

比較候補:
- minimum support
- Wilson lower bound
- Beta/Bayesian shrinkage

1/1=100%を表示上は100%としても、
ランキング首位へ暴走させない。

generic suppressionもここでDecision。

単純ブラックリストだけに依存しない。
global frequency / relative multiplier / small manual noise listを評価。

成果物:
docs/decisions/RECOMMENDATION_RANKING_DECISION.md

## 12.5 Auxiliary Role Classification

補助候補は可能ならrole別に整理する。

例:
- composition
- pose
- expression
- clothing
- background
- situation
- detail
- other

ただし全124,016タグを先に分類しない。
Recommendation上位に出るGeneralタグから段階的に分類し、未分類はother。
低共起を「相性が悪い」と断定しない。
詳細は `docs/AUXILIARY_TAG_ROLE_POLICY.md`。

## 13. Stage 7 — Special-first UI

主画面:
[特殊辞書]
[関連おすすめ]
[全Danbooru]

画面中央または常時視認位置に:
[現在の核 / Core Tag Set]
を表示する。

操作:
入力
→ Enter
→ 関連を見る
→ +
→ Copy

不要:
language mode
statistics mode
複数ranking mode
大量modal

## 14. Stage 8 — Semantic UX Refinement

静的bridge mapping拡充。
relation typeを見せるかはUX評価。
Semanticをactual Danbooru tagのように偽装しない。

## 15. Stage 9 — Prompt Builder / Minimal LoRA

内部canonical:
school_uniform

output:
school uniform

LoRA別layer:
name
weight
trigger

output:
tag, tag, <lora:name:weight>

LoRA directory crawlerは後。

## 16. Stage 10 — Final Regression / Benchmark / Packaging

pytest全回帰。
性能benchmark。
manifest検証。
packaging。

Stage 10までテストを待たない。

## 17. Snapshot architecture

別物として保持:

current tag dictionary:
2026-09-02 post_count
用途=現在使用数/検索

statistics dataset:
Approved post snapshot
用途=base/co/global/lift/ranking

statistics index群:
同じstatistics_dataset_snapshot_id必須。

tag dictionary snapshotは異なってよい。

## 18. Version Manifest

BUILD_MANIFESTに最低限:
app_version
statistics_dataset_name
statistics_dataset_snapshot_id
statistics_dataset_hash
statistics_total_posts
statistics_max_post_id
tag_dictionary_snapshot
tag_dictionary_hash
special2788_version
special2788_hash
semantic_bridge_version
semantic_bridge_hash
index_format_version
index_build_timestamp
total_canonical_tags

起動時:
statistics index / runtime counts / aggregation indexのsnapshot idが違えば拒否。

## 19. 初版でやらない

- incremental update
- advanced fuzzy
- Artist recommendation
- Meta recommendation
- image metadata extraction
- full TagComplete replacement
- plugin manager
- event bus
- cloud sync
- multi DB abstraction
- complex LoRA crawler
- AI automatic prompt rewriting

## 20. Completion

v1:
Special-first日英検索
→ Core Tag Set形成
→ canonical
→ true multi-tag AND
→ candidate aggregation
→ reliable recommendation
→ 必要ならAll Danbooru
→ Prompt
→ LoRA
→ Copy

これがend-to-endで動くこと。
