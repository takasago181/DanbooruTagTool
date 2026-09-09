# 01 Product purpose and guardrails

Owner: PROMPT / Issue #5
Status: PROMPT knowledge summary. Not production specification.

## 現在目的

PROMPT班ではDanbooruTagToolを次の制作支援として扱う。

> 日本語の制作意図から、Specialを核に必要な補助・構造を選び、対象model familyで高品質かつ生成難度の高いニッチ/複合画像を狙い通り成立させやすい完成Promptへ変換し、ユーザーの手直しを可能な限り減らすローカル非LLM制作支援。

目的の中心は辞書整備そのものではなく、最終的に狙った画像へ到達しやすくすること。

## 優先順位

1. Intent fidelity — 意味・強度・関係・対象を勝手に薄めない
2. Target realization — Promptに語があるだけでなく画像で成立する
3. Binding correctness — actor/target/body-site/ownershipを正しく結ぶ
4. Visual quality — anatomy/coherence/composition/style/artifactを含む完成度
5. Model-family fitness — WAI/Illustrious/NoobAI/Anima等を一つのgrammarへ潰さない
6. Minimum sufficient structure — 最短ではなく、必要十分で競合の少ない構造
7. Low user effort — Special探索/support再設計/Prompt再構築をユーザーへ戻しすぎない
8. Reproducibility/traceability — actual Prompt、Negative、model/settings/interventionを追える

## 「minimal prompt」の意味

`minimal = 短い` ではない。

正しい意味は:
- 成立に必要な構造は入れる
- 効果のない/重複/競合する要素だけ削る
- hard imageはeasy imageよりsupport blockが増えてよい

## 2つのPromptモード

### Experimental Isolation

目的: 一つの疑問だけ検証する。

- one experiment = one question
- A/B差分以外を固定
- quality/background/lighting等は観測に不要なら削る
- 因果分離、再現性、観測性を優先

この簡素さをproduction-qualityの理想形へそのまま昇格しない。

### Production-quality Stress Test

目的: 実利用に近い完成Promptを評価する。

- Specialを主題として保持
- 必要ならgeometry/visibility/relation/camera/quality/aesthetic/Negativeを足す
- family固有grammarを維持
- 主題を埋没させる無関係な装飾は増やさない

## Prompt班の役割

PROMPT班が担う:
- Prompt構造設計
- model-family別候補
- supportの役割分離
- hard-target failure診断
- Stage10のA/B質問設計
- 評価軸設計
- 必要最小のreplacement workflow
- Prompt-only ceilingの判定候補

PROMPT班が勝手にしない:
- production `data/**`変更
- #32 dictionary verdict変更
- Stage9 Composer仕様上書き
- DEV仕様決定
- KNOWLEDGE #44のongoing corpusを代行/改変
- 未検証知識のproduction FACT化
- Stage10本番開始宣言

## User effort原則

- ユーザーに2788件から毎回探させない
- ambiguityがなければPROMPT側が第一推奨を作る
- alternativesは必要時だけ
- replacement slotは必要最小
- slotを減らすために意味・強度・specificityを弱めない

将来UI候補として:
- Recommended
- Faithful/Raw
- Alternatives

は有望だが、PROMPT班単独ではproduction仕様にしない。

## Traceability原則

保持したい流れ:

`user intent -> Japanese search/display -> Special identity -> canonical/Alias/Semantic provenance -> render strategy -> resolved actual Prompt -> generation metadata -> result`

canonical identityとmodel-facing surfaceは同じとは限らない。違うsurfaceを試す場合でもprovenanceは保持する。

## 現在の高品質成功条件

少なくとも:
- intentを弱めていない
- targetが画像上で成立
- bindingが必要なら正しい
- targetが観測可能
- geometryが致命的に壊れていない
- 完成画像としてusable/high quality
- familyに合う
- conflictが過大でない
- userが大幅に再構築しなくてよい
- actual Prompt/settingsを追える

詳細:
- `docs/stages/STAGE_10_PROMPT_CURRENT_PURPOSE_AUDIT_20260909.md`
- `docs/stages/STAGE_10_PROMPT_HIGH_QUALITY_HARD_IMAGE_CONTRACT_20260909.md`
- `docs/stages/STAGE_10_PROMPT_REPLACEMENT_REFERENCE.md`
