# Issue #76 v0.8 — 2,788件統合マッピング焼き込み + knowledge-first 整合性監査

Status: **FULL MAPPING BAKE PASS / TAXONOMY UNRESOLVED 0 / READY FOR WPF BROWSE PROTOTYPE / NOT PRODUCTION FREEZE**

Date: 2026-09-15 JST

## 1. 方針

今回の判定根拠は次の順で扱う。

1. KNOWLEDGE #44 の現行 Claim / HOLD / practical guide
2. NoobAI / Anima / Illustrious の公式・一次情報
3. 現行の日本語実践知識・失敗知識
4. Special 2,788件の意味・発見性
5. Issue #30 WAI17 64枚 / 16実験は補助的な構造証拠のみ

少数のローカル生成結果をモデル一般の根拠にはしない。

## 2. v0.8 で行ったこと

v0.6 の意味上の分類を 2,788件の完全マッピングとして焼き込み、全件の整合性を再検査した。

v0.6 -> v0.8 の**意味上のroute変更は0件**。
データ清掃だけ実施:

- 解決済み `BUTTOCK_ANUS` 監査メモ 62件を active review note から除去
- `v2_reason` の重複トークン 11件を正規化
- canonical Special / Alias / product-fit / General / production WPF は変更なし

完全CSVは `tools/issue76_build_v2_integrated.py` で committed evidence から再生成できる。ローカル参照出力SHA-256:

`de5ef4cb712c31425b77fcc8bf2d8f56917356d79b3720845c81d46d8142d5d0`

## 3. 完全性

- rows: **2788**
- unique Special ID: **2788**
- exact IDs: **1..2788**
- taxonomy unresolved: **0**
- browse対象で route 0件: **0**
- unknown kind/body/theme/status ID: **0**
- stale buttock/anal active review note: **0**
- duplicate reason token: **0**

Product-fit由来の非browse/保留は taxonomy unresolved と混同しない:

- AUTO_CANDIDATE: **2745**
- HUMAN_RESOLVED: **15**
- REFERENCE_ONLY_NO_DIRECT_BROWSE: **21**
- DEFER_PRODUCT_FIT_REVIEW: **6**
- OUT_OF_SCOPE_NO_BROWSE: **1**

## 4. 種類

| 種類 | 件数 |
|---|---:|
| 行為・接触 | 907 |
| 衣服・露出 | 503 |
| 道具・物 | 299 |
| 身体・状態 | 298 |
| 体液・排泄 | 275 |
| ポーズ・構図・場面 | 156 |
| 人物・関係 | 123 |
| 異形・変形 | 119 |
| 表現・メタ | 66 |

browse対象の `kindなし` は14件。
ただし14/14が body/theme の少なくとも一つを持ち、発見routeは存在する。
`kind` を無理に必須化しない。

## 5. 部位 / テーマ

部位:
- 男性器 307
- 乳房・乳首 266
- 女性器 183
- 口・口内 175
- 尻・肛門 113
- 尿道 20

テーマ:
- 拘束・BDSM 366
- 損傷・R18G 66
- 生殖・妊娠・授乳 25

## 6. KNOWLEDGE #44 との整合

採用根拠:

- K-GOV-002: canonical / Alias / UI browse / generation support は別authority
- K-MODEL-NOOB-001/002: NoobAI 1.1 EPSは native Danbooru/e621 tags、captionは special -> general を分離
- K-MODEL-NOOB-004: exact actor/body-site/count ceiling は HOLD。browse taxonomy が生成成功を保証してはいけない
- K-PROMPT-003: frame / viewpoint / orientation / visibility / relation は別role
- K-BIND-001: object/tag presence != relation/body-site/ownership/count correctness
- K-HARD-001..006: body-site / binding / topology / device relation / source-destination は hard target の第一級 predicate

したがって:

**発見UI**
- 種類
- 部位
- テーマ

**Prompt/診断構造**
- actor / target / ownership
- relation
- count
- visibility
- camera / frame
- source/destination
- topology

を分離する。後者を固定taxonomyの細分類へ戻さない。

## 7. 外部知識との整合

### NoobAI XL 1.1
Official:
https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md

- full Danbooru + e621 native tags
- caption order: count -> character -> series -> artist -> special -> general -> other

=> Special discovery axisと、生成時support/structureを別レイヤーにする設計と整合。

### Anima
Official:
https://huggingface.co/circlestone-labs/Anima/blob/main/README.md

- Danbooru-style tags / natural language / mixed prompting
- multi-characterでは identity と basic appearance の明示を推奨

=> actor/ownershipはbrowse shelfではなくPrompt structure側に置く方が自然。

### Illustrious
Paper:
https://arxiv.org/abs/2409.19946

- refined multi-level captions / tags + context が重要

=> 単一の細分taxonomyだけで関係構造まで表現しようとしない。

### Faceted-search UX
NN/g:
https://www.nngroup.com/articles/filter-categories-values/

Baymard:
https://baymard.com/blog/ecommerce-over-categorization

- filter category はユーザーが実際に必要とする属性を優先
- shared attributes を過剰にsub-category化すると発見性を損ない得る
- combinable filters は狭いsubcategoriesの乱立を避ける手段になる

=> 38細分類を戻さず、独立facetを交差させる方向を支持。

## 8. 907件の「行為・接触」

907件は大きいが、件数だけで細分類を復活させない。

- body/themeあり: **534**
- body/themeなし: **373**

代表的な交差:
- 尻・肛門 × 道具・物 = **14**
- 尻・肛門 × 行為・接触 = **43**
- 尿道 × 道具・物 = **5**
- 拘束・BDSM × 道具・物 = **139**
- 拘束・BDSM × 口・口内 × 道具・物 = **43**
- 生殖・妊娠・授乳 = **25**
- 損傷・R18G × 行為・接触 = **19**
- 損傷・R18G × 身体・状態 = **30**
- 口・口内 AND 男性器 = **22**
- 口・口内 AND 女性器 = **4**
- 乳房・乳首 AND 男性器 = **10**

このため、まずWPFで:
- 種類/部位/テーマの複数facet
- 同一軸の複数選択
- 適用中filter chip
- shelf内text search
- usage/post_count sort

を試す。

## 9. 判定

**PASS**
- 2,788件完全マッピングへの焼き込み
- 3軸構造
- `尻・肛門`統合facet
- kind optional
- 旧38 permanent subgenreを戻さない
- taxonomy unresolved = 0

**NOT YET**
- production freeze
- production WPF置換

次Gateは **WPF browse/filter prototype**。
評価は少数のWAI17画像ではなく、KNOWLEDGE #44 + 一次情報から作る実用タスクを主にする。
