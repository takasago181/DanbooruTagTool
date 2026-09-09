# 07 Evaluation and Stage10 testing

Owner: PROMPT / Issue #5
Status: evaluation/test knowledge summary. Not production scoring specification.

## 目的

Stage10で「綺麗な方」だけを選ばず、target成立と完成画像品質を分離して記録する。

## 事前Gate

### GATE-0 Intent identity
- user intent preserved
- Special specificity not silently broadened/softened
- actor/target meaning preserved

Fail: `REJECT_INTENT_DRIFT`

### GATE-1 Traceability
必要:
- Special ID/canonical
- support roles
- actual resolved Positive
- actual Negative
- exact model/hash/settings
- interventions

Fail: `BLOCKED_TRACEABILITY`

### GATE-2 Evaluator capability
relation/ownership/body-site/multi-Special/rare vocabularyをevaluatorが表現できない場合:
- auto FAILにしない
- `REVIEW_EVALUATOR_UNSUPPORTED`

## Human audit vector

primary truthを一つのscalarへ潰さない。

- `T` Target fidelity
- `B` Binding/relation
- `V` Visibility/observability
- `G` Geometry/physical coherence
- `Q` Finished-image quality
- `C` Conflict/artifact burden（高いほど悪い）
- `M` Model-family evidence status
- `U` User repair burden（低いほど良い）
- `R` Reproducibility/traceability

multiple Specialでは `T_A / T_B / T_C` を別記録。

## 0–3のhuman labels候補

### T
0 absent/wrong
1 partial/ambiguous
2 clear but weak/incomplete
3 intended specificity clearly realized

### B
0 wrong
1 mixed/ambiguous
2 mostly correct/minor leakage
3 clear correct ownership/relation

### V
0 not judgeable
1 barely judgeable
2 adequate
3 clear without sacrificing composition

### G
0 major broken
1 substantial inconsistency
2 mostly coherent
3 coherent for intended scene

### Q
0 unusable
1 weak
2 usable/good
3 high-quality finished result

### C
0 none
1 minor
2 significant
3 severe

### U
0 ready-to-use
1 one small edit/choice
2 several edits/choices
3 user must rebuild/search

### R
0 cannot reproduce
1 partial
2 actual Prompt + major settings
3 source/template + actual Prompt + Negative + exact model/settings/interventions

## Verdict vocabulary

- `PASS_HIGH_QUALITY_HARD_TARGET_CANDIDATE`
- `PASS_TARGET_WEAK_QUALITY`
- `PASS_QUALITY_WEAK_TARGET`
- `REVISE_BINDING`
- `REVISE_VISIBILITY`
- `REVISE_GEOMETRY`
- `REVISE_DENSITY_CONFLICT`
- `REVIEW_MODEL_UNKNOWN`
- `REVIEW_EVALUATOR_UNSUPPORTED`
- `PROMPT_ONLY_LIMIT`
- `ASSISTED_CONTROL_CANDIDATE`
- `REJECT_INTENT_DRIFT`
- `BLOCKED_TRACEABILITY`

## A/B record

Shared:
- experiment/question ID
- exact checkpoint/hash
- seed
- resolution
- sampler/scheduler
- Steps/CFG
- LoRA/Hires/Control state

A/B each:
- actual Positive
- actual Negative
- support blocks
- vector labels
- failure classes

必須:
- exactly what changed
- one-sentence human question

単純A_WIN/B_WINだけをprimary recordにしない。

## Seed sensitivity

production rule候補はone-seedで決めない。

状態候補:
- `CONSISTENT_DIRECTION`
- `MIXED_DIRECTION`
- `SEED_SENSITIVE`
- `INSUFFICIENT_SEEDS`

方向反転を平均で隠さない。

## 現在のStage10優先質問

Gate後のPROMPT優先順:

1. semantic support auto-selectionの実効性
2. family block order / Special position
3. multi-Special retention + binding
4. visibility support side effects
5. density: under -> sufficient -> over
6. canonical vs Alias/model-facing surface
7. tag-only vs short relation sentence
8. family/target Negative
9. quality/meta minimum set
10. user effort / replacement burden
11. Prompt-only ceiling / assisted control

WAI17-first laneではさらに:
1. Special minimal recognition
2. canonical vs alternate surface
3. +one meaning/site support
4. +one geometry/visibility support
5. minimal vs expanded Negative
6. single vs two Special
7. Prompt-only vs assisted
8. Hires confirmation

## Issue #30との分離

TEMP #30は**automation/plumbing fixture**。

既知:
- Forge Neo API -> fixed-seed A/B -> PNG actual metadata -> WD14 raw confidenceまでmanual ops 0
- infrastructure verdict `PASS_PIPELINE`
- WAI17 exact local checkpointを使用
- generic standing/sitting/long_hair/smile setはpipeline/evaluator fixture
- generic fixtureはproduct representativenessの証明ではない

PROMPT Stage10は:
- #30 infrastructureを再利用
- product-representative Special testを別profileで実行
- fixture exact settingsを「WAI17最適Prompt設定」と誤認しない

## WD14 boundary

WD EVA02-Large Tagger v3:
- ratings / characters / general tags classifier
- Danbooru由来
- trainingで600 images未満のtagsをfilter

したがって:
- rare/long-tail Specialが未対応でもPrompt FAILではない
- relation/binding semantic judgeではない
- confidenceはfirst-pass evidence
- low-confidence/unsupported -> REVIEW
- human golden labelsはWD confidenceを見せずblindで付けるのが望ましい

## Easy fixtureとproduct proof

Easy/common tags:
- pipeline動作
- metadata
- evaluator plumbing
- REVIEW routing
を確認するcontrol。

Product-purpose proofには:
- rare/niche
- broad vs specific
- relation
- body-site binding
- multi-Special
- difficult visibility/geometry
- model-family差
が必要。

## Human review question

悪い:
- どっちが綺麗？

良い:
- target Aはあるか
- target Bはあるか
- actor/targetは正しいか
- required regionは見えるか
- geometryは成立しているか
- targetを考慮した上でfinished qualityはどちらが高いか

## Current boundary

- production scoring formula未決定
- global weighted sum未決定
- AUTO winner threshold未決定
- final evaluator routingはdictionary freeze/coverage待ち
- Stage10 production A/BはGate前に開始しない

詳細:
- `docs/stages/STAGE_10_PROMPT_HIGH_QUALITY_AUDIT_SCORECARD_20260909.md`
- `docs/stages/STAGE_10_PROMPT_REVALIDATION_BACKLOG_20260909.md`
- Issue #30 / `docs/testing/ISSUE30_SPECIAL_REPRESENTATIVE_ROUTING_DESIGN_20260908.md`
