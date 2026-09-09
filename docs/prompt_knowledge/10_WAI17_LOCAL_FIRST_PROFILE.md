# 10 WAI17 local-first profile

Owner: PROMPT / Issue #5
Status: current local-first Stage10 candidate profile. **Not production specification.**
Profile ID: `WAI17_LOCAL_FIRST_20260909`

## 目的

当面のPrompt実画像検証を、ユーザーの実環境で既にplumbing確認済みの **WAI Illustrious v17 + Forge Neo** に絞って始めるための入口。

詳細・証拠正本:
- `docs/stages/STAGE_10_PROMPT_WAI17_LOCAL_TEST_PROFILE_20260909.md`
- Issue #30 automation/plumbing evidence

このファイルは詳細証拠を置き換えず、次のPROMPT班が最初に読む実用要約。

## Verified local environment

GitHub Issue #30証跡で確認済み:

- runtime: Forge Neo
- checkpoint: `sd\\waiIllustriousSDXL_v170.safetensors`
- SHA-256: `f116b0c78ff441467b0cdc8f1936e1ed18ea31e9997c7b132b1b8db533f0bd04`
- Forge native API path verified
- PNG actual metadata path verified
- WD14 interrogator path verified
- automation infrastructure verdict: `PASS_PIPELINE`
- Seed `5072` used by existing fixture

Installed/relevant existing extensions:
- TagComplete Neo
- WD14 Tagger
- ADetailer Neo
- Forge Couple
- Dynamic Prompts Neo

## Important separation — two profiles

### A. Issue #30 plumbing fixture

Purpose:
- API動作
- fixed-seed A/B
- metadata追跡
- WD14呼び出し
- manual operation削減

これは**Prompt品質の最適設定ではない**。

### B. WAI17 local-first PROMPT profile

Purpose:
- actual Special/hard-target Prompt品質
- target realization
- binding/site/geometry/visibility
- finished image quality

両者を混同しない。

## Author-aligned baseline facts

WAI17 author guidanceとして現在保持:

- Forge Neo recommended
- Steps: 15–30
- CFG: 5–7
- Sampler: Euler a
- VAE integrated
- original size > 1024x1024 recommended
- sample size: 1024x1344
- Hires example: upscale 1.5 / hires steps 20 / denoise 0.35–0.5
- quality example: `masterpiece, best quality, amazing quality`
- Negative example: `bad quality, worst quality, worst detail, sketch, censor`
- avoid too many quality/aesthetic tags
- avoid overly long Negative prompts
- no trigger word required
- v17 notes mention attempted Hires.fix limb-correction improvement

Author guidance = strongest starting baseline, not hard-target optimum proof.

## Current practical baseline candidate

For causal Prompt-quality tests:

- exact checkpoint/hash above
- exact current Forge Neo; silent update禁止
- Sampler: Euler a
- Steps: 25
- CFG: 6
- size:
  - 1024x1024 when square framing is suitable and causal speed matters
  - 1024x1344 for practical portrait stress test
- batch: 1 unless batch is test variable
- fixed seed within A/B
- Seed 5072 may be reused for continuity, not production default
- external VAE: OFF / unnecessary
- LoRA: OFF for baseline
- Hires.fix: OFF for first semantic/causal pass
- Forge Couple/ControlNet/ADetailer等: OFF for PROMPT_ONLY baseline

## Candidate Prompt grammar

Profile: `LEAN_TAG_FIRST`

Conceptual order:

1. subject / count / identity
2. Special / ACT core
3. SITE / OBJECT / required ownership/relation
4. only-needed pose / geometry
5. only-needed frame / visibility
6. minimum family-appropriate quality/aesthetic
7. short target-safe Negative

Do not:
- generic SDXL long boilerplateを初手にする
- quality語を救済として増やす
- long Negativeを万能修正として使う
- same-role pose/camera/visibilityを重ねる

## Negative baseline

Start from short author-family baseline and add only diagnosed failure-specific terms.

Adult hard-target laneでは:
- `nsfw`をNegativeのglobal defaultにしない
- target semanticや近接conceptを機械的にNegativeへ入れない
- anatomy-sensitive negativesはcontrolled ON/OFF候補

## WAI17-first experiment order

1. Special minimal recognition
2. canonical vs approved Alias / alternate surface where applicable
3. no support vs exactly one Meaning/Site support
4. no support vs exactly one Geometry/Visibility support
5. minimum Negative vs expanded Negative
6. single Special vs two-Special composition
7. repeated binding/geometry failure -> PROMPT_ONLY vs assisted-control lane
8. promising Prompt only -> Hires confirmation pass

One experiment = one question.

## Hires confirmation

Semantic candidateが有望になってから:

- Hires.fix ON
- upscale 1.5
- hires steps 20
- denoise start 0.35
- necessary comparison range up to 0.5 candidate

記録:
- `BASE_OUTPUT`
- `HIRES_OUTPUT`

Hiresで修復された結果をbase Prompt-only successへ数えない。

## Main failure diagnosis for WAI17

- `TARGET_MISSING` -> trigger/surface/placement/conflictを確認
- `SITE_WRONG` -> site ambiguity/competing site/pose/visibility
- `BINDING_LOST` -> actor identity/relation/support density
- `OBJECT_DEGRADES` -> object identity/role/contact/frame
- `GEOMETRY_FAILURE` -> pose conflict/overconstraint; tagsを無限追加しない
- `VISIBILITY_FAILURE` -> frame/viewpoint/crop/occlusion
- `OVERPROMPTED_CONFLICT` -> last-added support/quality/Negativeを疑う

## Evaluation

最低でも別軸で記録:

- Target / ACT retention
- Site accuracy
- Binding / relation
- Object integrity
- Geometry
- Visibility
- Finished quality
- Conflict/artifacts
- User repair burden
- Reproducibility

綺麗でもtargetが消えたらproduct successではない。
targetが正しくてもfinishが壊れていれば完成successではない。

## WD14 use

WD EVA02 v3はfirst-pass evidenceのみ。

Known structural limitation:
- <600 training images tags filtered from vocabulary

したがってrare/relational Special:
- low-confidence/unsupported -> `REVIEW`
- no auto FAIL
- human semantic reviewを保持

## Assisted-control escalation

Repeated controlled failure後のみ:

- actor/attribute mixing -> Forge Couple / regional candidate
- pose/geometry -> ControlNet candidate
- local face/hand defect after semantic success -> ADetailer
- Hires -> finish/limb repair confirmation lane

Assisted success != PROMPT_ONLY success.

## Non-actions

- production promotionなし
- final winner/scoring thresholdなし
- WAI17 ruleを他familyへ一般化しない
- author defaultsをhard-target optimumと断定しない
- #30 fixtureをPrompt optimumと扱わない
- silent checkpoint/runtime updateなし

## Next restore path

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #5 latest checkpoint
4. `docs/prompt_knowledge/README.md`
5. this file
6. need-specific category files
7. detailed evidence files only when auditing provenance
