# FEATURE_PRIORITY.md

## Status

Current v1 priority follows `docs/PRODUCT_GOAL_LOCK.md` and Issue #42.
Historical Stage5/6/9 capabilities are preserved assets, not automatic v1 requirements.

**Stage10 is a separate parallel learning priority**, defined by Issue #65 / `docs/stages/STAGE_10_LEARNING.md`. It does not change the v1 feature list below.

## MUST — v1の存在理由

1. 既存Promptを貼り付け/読み込みできる
2. Prompt内の既知タグを日本語-first + canonical Englishで理解できる
3. 不要タグを手動で外せる
4. 日本語/英語/混在検索ができる
5. exact canonical / Aliasを安全に扱う
6. Special Core Dictionaryを深いジャンル/サブジャンルから閲覧・発見できる
7. production Japanese overlay 30,629件のGeneralタグを浅い実用ジャンルから閲覧・発見できる
8. Special/Generalをユーザーが明示的に追加・削除・並べ替えできる
9. 最終Promptをcanonical Englishとしてpreview/copyできる
10. 日本語表示/検索、canonical identity、UI taxonomyを別レイヤーとして保つ
11. runtime非LLM・ローカル完結
12. Forge等の生成環境と同時常駐して邪魔にならない軽量runtime
13. focused test / regression / 実Windows UI確認を維持

## SHOULD — v1内で実使用から価値が確認できれば

- Alias/詳細表示
- Danbooru current post countの補助表示
- co-occurrence候補を控えめな「関連タグ」として表示
- Semantic Bridgeを検索補助として利用
- Prompt履歴/お気に入り
- Core/General選択状態の保存

SHOULDはv1 completion blockerではない。

## HOLD / AFTER v1 product features

- model verification/status UI
- 専用類似タグ比較UI
- A/B Prompt experiment manager
- niche-tag effect判定
- local generation success/failure DB
- troubleshooting wizard
- model-family-specific Prompt guidance in the product UI
- Forge / ComfyUI direct-send adapter
- advanced Prompt history/preset management

These remain product-feature HOLDs even if the user learns the same concepts manually during Stage10.

## REJECT FROM DEFAULT v1 CORE

- automatic support insertion
- automatic minimum-sufficient Prompt construction
- automatic conflict removal
- automatic Negative生成
- automatic model-family Prompt rewrite
- Prompt文字列だけからのautomatic failure diagnosis
- evaluator confidenceをsuccess probabilityとして表示
- Raw Lift / rare-relationを主UIにする
- aggregate recommendation score/ranking-method dashboard
- always-on Semantic Support / Generation Profile dashboard
- runtime WD14/Kagami/CL tagger stackの必須化
- full 11M-post / ~3GB statistics indexの通常利用必須化
- full 100k+ Danbooru taxonomy化
- direct image generationのv1必須化
- runtime LLM

## Stage10 learning priority — parallel, not product feature scope

Current learning owner:
- Issue #65
- `docs/stages/STAGE_10_LEARNING.md`

Primary model:
- NoobAI XL 1.1 EPS + Forge Neo

Learning order:
1. environment / metadata / reproducibility
2. Prompt fundamentals
3. composition / camera / visibility
4. hard/niche relation/body-site/count structure
5. failure diagnosis / controlled iteration
6. seed / Negative / weights / LoRA
7. Hires / ADetailer / img2img / inpaint
8. regional / Control escalation
9. independent capstone generation

Stage10 completion is a **skill outcome**, not a product implementation checklist.

## Data classification depth

### Special
深く分類する。
ニッチ・複雑概念を「検索語を知らなくても発見できる」ことが目的。

### General 30,629
浅く分類する。
Prompt用途中心の実用ジャンルで「こういうタグがある」と発見できればよい。
完全ontologyは作らない。

## v1 completion shorthand

`Promptを理解 -> 日本語/英語またはジャンルからタグを発見 -> 自分で選ぶ -> canonical-English Promptをコピー`

## Stage10 completion shorthand

`意図 -> Prompt -> 生成 -> 原因分解 -> 修正 -> 必要な補助 -> 仕上げ -> 再現可能な保存`
