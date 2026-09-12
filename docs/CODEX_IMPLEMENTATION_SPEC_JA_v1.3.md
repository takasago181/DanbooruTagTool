# Codex 実装仕様 — current v1 product contract

> Path compatibility note: filename `CODEX_IMPLEMENTATION_SPEC_JA_v1.3.md` is retained so existing references do not break. The old Stage0–10 implementation plan is historical and remains recoverable from Git history. This file now describes the current v1 product contract.

## 1. 正本

優先順位:

1. `docs/project/CURRENT_STATE.md`
2. live current DEV GitHub Issue
3. `docs/project/PERMANENT_RULES.md`
4. `docs/PRODUCT_GOAL_LOCK.md`
5. this file / `docs/FEATURE_PRIORITY.md`
6. current Issue-specific design docs

Issue-specific scope always wins over this general product contract.

## 2. v1の目的

画像生成初心者で、英語/Danbooruタグ知識が弱くても:

`理解 -> 発見 -> 選択 -> 出力`

できること。

具体的には:

1. 既存Promptを貼る、または空から始める
2. 既知タグを日本語-first + canonical Englishで理解する
3. 不要タグを外す
4. 日本語/英語で検索する
5. Specialをジャンルから深く発見する
6. General 30,629件を実用ジャンルから浅く発見する
7. 欲しいタグを自分で追加/削除/並べ替えする
8. canonical-English Promptをコピーする

## 3. v1 data surfaces

### Special Core Dictionary

- frozen identity population: 2,788
- #56 Japanese-first UI browse taxonomyを使用
- deep niche/complex discovery surface
- canonical/Alias identityは保護
- product-facing eligibilityは#63 sidecarを使用

### General Japanese overlay

- production target population: 30,629 canonical entries
- Japanese display/search assistance
- canonical identityはEnglish
- General browse taxonomyは#64で別sidecarとして作る
- `japanese_overlay.json` 自体へtaxonomy fieldを混ぜない

## 4. Search

- Japanese / English / mixedを同じsearch pathで扱う
- exact canonical / exact English / word-boundary intentを incidental substring/fuzzyより優先
- Aliasをsilent ambiguous resolveしない
- Japanese wordingはsemantic authorityではない
- SpecialをUI上見つけやすくしてよいが、match qualityを捏造しない
- current ranking/noise defectは#34がowner

## 5. Prompt workbench

v1ではuser explicit choiceが中心。

必要:
- existing Prompt parse/display
- manual add
- manual remove
- reorder
- final preview
- copy

最終payload:
- canonical English / model-facing existing formatter rules

日本語ラベルをPrompt payloadへ混ぜない。

## 6. Automatic behavior boundary

Default v1では以下を実装/有効化しない:

- automatic support insertion
- automatic minimum-sufficient Prompt construction
- automatic conflict removal
- automatic Negative generation
- automatic model-family rewrite
- Prompt-only automatic failure diagnosis
- hidden generation rule injection

既存コードに同様のautomatic/default-on behaviorが残っている場合は、current Issueのscope内で明示的にdisable/remove planを作り、ユーザー選択と表示状態を一致させる。

## 7. Optional existing subsystems

以下は既存資産として保持してよいが、v1通常起動の必須dependencyにしない:

- full Stage5 runtime index / true multi-tag AND
- Candidate Aggregation
- co-occurrence recommendation
- reliability ranking
- Semantic Support
- Generation Profile
- Stage9 Composer advanced variants
- evaluator/tagger stack
- Stage10 A/B infrastructure

必要なfeatureが採用された時だけ利用する。

## 8. Runtime / architecture

- local / non-LLM runtime
- Windows desktop first
- Forge等と同時常駐して邪魔にならないRAM/起動性
- full ~3GB statistics indexが無くてもv1 core pathが起動すること
- optional data不在で`understand -> discover -> choose -> copy`を壊さない
- overengineering禁止
- external/existing tool first

## 9. General taxonomy #64

General 30,629はSpecialと同じ深さにしない。

目的:
- 検索語を知らない初心者が「こういうタグがある」と発見できる

方針:
- broad practical Prompt-role genres
- useful subgenres only
- multi-path allowed where useful
- visible giant catch-allを避ける
- separate canonical-tag keyed sidecar
- reproducible pilot -> boundary audit -> full rollout
- full 100k+ Danbooru ontologyを作らない

## 10. Stage10 relationship

Issue #5 / Stage10はv1 completion blockerではない。

将来次のようなfeatureを採用した場合のみ再activate:
- model-specific tag effectiveness
- evidence-backed support recommendation
- automatic Prompt assistance
- image-dependent failure diagnosis
- A/B experiment support

その場合もone experiment = one questionで最小限にする。

## 11. Safety / integrity

- protected local dataを破壊しない
- `git clean -fdx` / `git clean -fdX` 禁止
- Special ID / canonical / Alias / provenanceをpresentation都合で変更しない
- existing audit/freeze evidenceを消さない
- Japanese overlay / taxonomy / generation metadataを別レイヤーとして保つ
- runtime LLM dependencyを導入しない

## 12. v1 completion

v1は次が実機で成立すればよい:

`Promptを日本語で理解`
`-> 日本語/英語検索またはSpecial/Generalジャンル閲覧`
`-> ユーザーがタグを選択`
`-> canonical-English Promptをcopy`

co-occurrence、Stage10、model verification、automatic optimizationはv1 completion conditionではない。
