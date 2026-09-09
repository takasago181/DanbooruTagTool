# 05 Failure diagnosis and assisted control

Owner: PROMPT / Issue #5
Status: diagnosis/routing knowledge summary. Not production specification.

## 目的

hard-targetの失敗を「出た/出ない」だけで扱わず、原因別に分ける。

研究背景でも、subject neglect、attribute binding、object relation、complex composition、layout confusionは別failureとして観測されている。exact WAI/NoobAI/Anima挙動の証明ではないが、Stage10の診断語彙として採用する。

## Core failure taxonomy

### Semantic / target
- `TARGET_MISSING`
- `PARTIAL_TARGET`
- `MULTI_SPECIAL_DROP`
- `MODEL_TRIGGER_MISMATCH`

### Binding / relation
- `ACTOR_TARGET_SWAP`
- `BODY_SITE_BINDING_ERROR`
- `ATTRIBUTE_LEAKAGE`
- `IDENTITY_MIXING`
- `RELATION_FAILURE`
- `COUNT_FAILURE`

### Object / geometry / visibility
- `OBJECT_DEGRADES`
- `GEOMETRY_FAILURE`
- `VISIBILITY_FAILURE`
- `CROP_OCCLUSION_FAILURE`
- `COMPOSITION_CONFLICT`

### Prompt interaction
- `NEGATIVE_COLLISION`
- `QUALITY_STYLE_DRIFT`
- `OVERPROMPTED_CONFLICT`
- `SUPPORT_COLLISION`

### Evaluation / ceiling
- `EVALUATOR_UNSUPPORTED`
- `PROMPT_ONLY_LIMIT`
- `ASSISTED_CONTROL_CANDIDATE`

## Failure -> first diagnosis

### TARGET_MISSING
確認順:
1. exact modelがconceptを知っているか
2. canonical/alternate surface
3. family-specific placement/order
4. competing concepts
5. supportでcoreが埋もれていないか

quality語を最初に増やさない。

### SITE_WRONG / BODY_SITE_BINDING_ERROR
確認:
1. SITE ambiguity
2. competing site tags
3. actor ownership
4. pose geometry
5. crop/visibility

### BINDING_LOST / RELATION_FAILURE
確認:
1. actor count
2. identity separation
3. relation ambiguity
4. multiple competing acts
5. appearance anchor
6. family-specific short NL support

### OBJECT_DEGRADES
確認:
1. object identity
2. object role/active component
3. ownership/source/contact relation
4. frame visibility
5. too many objects/functions

### GEOMETRY_FAILURE
確認:
1. conflicting pose/orientation
2. impossible/overconstrained structure
3. camera-induced distortion
4. support density

semanticが正しいのにgeometryだけ繰り返し壊れる場合、Prompt追加を止める。

### VISIBILITY_FAILURE
確認:
1. crop
2. subject scale
3. viewpoint
4. occlusion
5. target region readability

visibility supportはtransparentではない。追加でrelation/poseが悪化する可能性を記録。

### OVERPROMPTED_CONFLICT
症状:
- target薄化
- pose競合
- quality/style drift
- object/actor混線

対処候補:
- last-added supportを外す
- same-role blockを1つへ
- core -> necessary supportへ戻す

## Prompt-only escalation ladder

PROMPT側候補:

1. `PROMPT_ONLY_BASELINE`
2. `PROMPT_ONLY_TARGETED_SUPPORT`
3. `REGION_CONDITIONING`
4. `POSE/DEPTH_CONTROL`
5. `LOCAL_INPAINT_REPAIR`

難しいから自動的にassistedへ行くのではなく、**診断されたfailure classがcontrolled attempts後も残る時にだけ昇格**。

## Forge Couple

Evidence: `OFFICIAL_RUNTIME_FACT`

向くfailure:
- multi-actor identity mixing
- attribute leakage
- left/right/region-specific ownership
- actor-target binding

注意:
- checkpointがscene自体を理解しない問題は解決しない
- successは`ASSISTED_CONTROL`として記録

## Regional Prompter

向くfailure:
- actor/objectのspatial separation
- cross-region leakage
- role distribution

注意:
- exact Forge Neo compatibility/modeを実機確認

## ControlNet

向くfailure:
- pose instability
- depth/layout
- repeated geometry failure

注意:
- compatible control model/version必須
- geometry successはtext semantics successの証明ではない

## ADetailer

向くfailure:
- semantic/composition成功後のface/hand/local-detail defect

重要:
- pre-ADetailerとpost-ADetailerを分離
- postだけ見てPrompt-only成功としない

## Hires.fix

主にfinish/limb correction lane。

WAI17作者はv17でHires.fix limb correction改善を試みた旨を説明している。

監査:
- base txt2img
- Hires result
を分離。

Hiresで救われたsemantic/geometryをbase Prompt成功に混ぜない。

## Dynamic Prompts

failure rescueというよりsystematic test生成。

用途:
- support variants
- canonical/Alias variants
- family baselines
- combinatorial experiments

必須:
- `SOURCE_TEMPLATE`
- `RESOLVED_PROMPT`
を両方保存。

複数変数が同時に変わるwildcardはcausal A/Bに使わない。

## Assisted evidence record

最低限:
- Prompt-only or assisted
- extension name/version/commit
- mode
- region/mask/control settings
- pre-control Prompt
- resolved actual Prompt
- model/settings
- pre/post image evidence where applicable

## Prompt-only ceilingの判断候補

同じfailure classが、意味を弱めずtargeted supportを段階追加しても再現する場合:

- supportを無限に足さない
- `PROMPT_ONLY_LIMIT`
- `ASSISTED_CONTROL_CANDIDATE`
へrouting

最終production自動昇格は未決定。

## 詳細証拠

- `docs/stages/STAGE_10_PROMPT_COMPOSITIONAL_FAILURE_RESEARCH_LEDGER_20260909.md`
- `docs/stages/STAGE_10_PROMPT_ASSISTED_CONTROL_OFFICIAL_CAPABILITIES_20260909.md`
- `docs/stages/STAGE_10_PROMPT_HIGH_QUALITY_HARD_IMAGE_CONTRACT_20260909.md`
