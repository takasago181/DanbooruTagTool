# WAI Illustrious v17 — Local Environment Test Baseline

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-09

Status: `LOCAL_BASELINE_V1 / TEST-FOCUSED / KNOWLEDGE-ONLY`

## 0. Purpose

This file freezes the current WAI Illustrious v17 test baseline for the user's actual local environment so a future KNOWLEDGE chat can resume without relying on conversational memory.

This is a test/evidence baseline, not a production Prompt grammar and not a claim that every value is globally optimal.

## 1. Known local environment

Local/project context at this checkpoint:
- Windows 11 local generation environment
- GPU: RTX 5070 12 GB
- RAM: 32 GB
- launcher/package management: Stability Matrix
- primary UI: Forge Neo
- primary checkpoint for the immediate test phase: WAI Illustrious v17
- current practical baseline already used locally: Euler a / 25 steps / CFG 5 / 1024-class generation
- installed/available supporting extensions include TagComplete Neo, WD14 Tagger, ADetailer Neo, Forge Couple and Dynamic Prompts Neo.

Any future chat must verify these only if the local environment has materially changed; otherwise this file is the current local baseline.

## 2. Exact-model author facts

Source authority: WAI v17 author model card.

`FACT_EXACT_MODEL`
- recommended software: Forge Neo
- Steps: 15–30
- CFG: 5–7
- Sampler: Euler a
- VAE integrated
- author recommends original dimensions with area larger than 1024×1024; examples use 1024×1344
- positive quality baseline: `masterpiece, best quality, amazing quality`
- negative baseline: `bad quality, worst quality, worst detail, sketch, censor`
- author warns that too many quality/aesthetic tags and overly long Negative Prompts can reduce image quality / cause blur
- v17 author documents Hires as capable of repairing limbs/hands/feet with high probability
- example Hires values: upscale 1.5, Hires steps 20, R-ESRGAN 4x+ Anime6B, denoise 0.35–0.5
- no trigger word is required for the checkpoint itself.

Primary source:
https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md

## 3. Immediate local test baseline

For semantic/Special testing, start with:
- checkpoint: exact WAI v17
- Forge Neo
- Euler a
- Steps: 25
- CFG: 5
- resolution: 1024×1344 as the preferred first portrait baseline when the scene permits; use other 1024-class aspect ratios when the target composition requires them
- fixed predetermined seed for paired A/B
- Hires: OFF
- ADetailer: OFF
- LoRA: OFF unless LoRA itself is the variable under test
- Forge Couple / regional control: OFF unless assisted control is the variable under test
- ControlNet: OFF unless geometry assistance is the variable under test.

Reason: base Prompt capability must be separated from postprocess/adapter/control rescue.

## 4. Prompt baseline

Start from the exact-model minimal quality baseline rather than inherited long templates.

Positive quality prefix candidate:
`masterpiece, best quality, amazing quality`

Negative baseline:
`bad quality, worst quality, worst detail, sketch, censor`

Do not automatically append old universal Negative stacks such as broad anatomy/count suppression to every test.

For unusual anatomy, multiple appendages, multi-penetration, hard count or rare body-state Specials, generic anatomy/count Negatives are explicitly `TEST_REQUIRED` because they may suppress the intended target.

## 5. WAI17 test philosophy

### 5.1 Minimum sufficient, not maximum tags

Do not treat WAI17 as a model where more quality/aesthetic/support tags are automatically better.

Protected semantic nucleus:
- selected Special(s)
- intrinsic actor/count/ownership/target/body-site/relation
- intrinsic implement/modifier
- exact character identity if part of the test.

Add only one functional support role at a time:
- visibility/frame
- geometry/pose
- actor/resource separation
- broad/frequent constituent
- weighting
- assisted control.

### 5.2 One experiment = one question

Examples:
- Does one visibility support improve target observability?
- Does one broad constituent improve a rare Special?
- Does anatomy Negative suppress the intended unusual state?
- Does Alias surface activate better than canonical surface under this exact model version?

Do not change multiple roles simultaneously if the goal is causal evidence.

### 5.3 Unary before composite

For multiple-Special cases:
`A_ONLY -> B_ONLY -> AB minimal -> AB + one support role`

AB failure must not be interpreted as `tag unknown` before composition/binding failure is excluded.

## 6. Hard/niche adult evaluation predicates

For relation-heavy and hard Special tests, object presence alone is insufficient.

Evaluate as applicable:
- target concept present
- correct actor/owner
- correct target
- correct body-site
- correct implement/device
- correct action/relation
- exact count where intrinsic
- restraint topology where intrinsic
- source/destination for fluids/materials
- appendage ownership/source for tentacle/nonhuman relations
- visibility/occlusion
- collateral anatomy error
- style/context leakage.

Possible labels:
- `TARGET_SUCCESS`
- `TARGET_PARTIAL`
- `WRONG_BODY_SITE`
- `WRONG_ACTOR_TARGET`
- `WRONG_COUNT`
- `OBJECT_ONLY_RELATION_FAIL`
- `TOPOLOGY_FAIL`
- `VISIBILITY_UNCLEAR`
- `CONCEPT_OMITTED`
- `NEGATIVE_COLLISION_SUSPECTED`
- `STYLE_CONTEXT_LEAK`
- `UNCLEAR`.

## 7. Postprocess and assisted-control boundaries

### Hires
WAI v17 explicitly documents limb repair during Hires. Therefore:
- base image and Hires result are separate evidence states;
- Hires-fixed anatomy is `POSTPROCESS_RESCUE`, not proof of base Prompt success.

### ADetailer
ADetailer performs detect -> mask -> inpaint after the first image exists. Therefore:
- ADetailer result is separate local repair evidence;
- do not score it as base WAI Prompt capability.

### Forge Couple / regional control / ControlNet
Useful when Prompt-only bounded escalation fails, especially for actor separation or geometry.
But:
- assisted success is `ASSISTED_ONLY` unless base Prompt also passes;
- assisted-control results cannot establish that WAI understood the original relation unaided.

## 8. Evaluator boundary

WD14/WD EVA02 may be used as a common/unary side signal only.

Do not let a unary tagger certify:
- body-site binding
- actor-target ownership
- exact count
- restraint topology
- machine functional relation
- source/destination
- rare Semantic concepts.

Many rare Special targets are structurally outside WD EVA02 v3's useful vocabulary because tags with fewer than 600 images were filtered in that tagger's selection. Missing tagger output is not image failure.

Final automated evaluator routing remains a separate future task after dictionary finalization.

## 9. Current WAI17 evidence states

### KEEP / strong
- Forge Neo is the author-recommended UI.
- Euler a / 15–30 steps / CFG 5–7 is exact-author guidance.
- local 25 steps / CFG 5 sits inside the exact-author regime.
- minimal quality/Negative baseline is preferable to inherited giant stacks for controlled tests.
- Hires/ADetailer/LoRA/control must be separated from base Prompt capability.
- relation/body-site/count success must be judged separately from component presence.
- fixed-seed paired A/B is useful for controlled comparison, while multiple predetermined seeds are required for repeatability evidence.

### TEST_REQUIRED / HOLD
- exact WAI17 canonical vs Alias activation differences
- rare Special exposure/activation
- broad + specific benefit
- exact actor-target/body-site relation ceiling
- exact restraint topology ceiling
- machine/device functional relation ceiling
- tentacle ownership/relation ceiling
- simultaneous Special/count breakpoints
- exact effect of `fully visible`, `in frame`, body-part focus and other visibility supports
- unusual anatomy/count-changing Negative ON/OFF effect
- LoRA × Special/support interactions
- Prompt-only -> Forge Couple/ControlNet escalation threshold.

### REJECT as current WAI17 universal rule
- giant inherited quality blocks
- giant inherited universal Negative templates
- one seed = reliable rule
- high tagger confidence = relation truth
- Hires/ADetailer result = base Prompt success
- LoRA-assisted result = base checkpoint capability
- every semantically related parent/support should be auto-added.

## 10. Immediate test order

When WAI17 becomes the first test target:
1. establish exact checkpoint/hash and actual PNG metadata capture
2. use the local base regime above
3. pick representative Special classes, not only simple common tags
4. run `S_ONLY` / minimal-person baseline
5. add one visibility or geometry support only when needed
6. for rare targets, test one broad/frequent constituent as A/B, never automatic
7. for unusual anatomy/count, run Negative OFF/ON comparison where overlap is plausible
8. retain all predetermined seed outputs, including both-fail cases
9. label relation/body-site/count failures explicitly
10. only after bounded Prompt tests, open assisted-control and LoRA lanes separately.

## 11. Evidence hierarchy

For this local WAI17 lane:
1. exact WAI17 author/model-card fact
2. exact local controlled paired test under pinned environment
3. Illustrious-family primary evidence
4. practical WAI exact-version report
5. older WAI/Illustrious report
6. community heuristic.

Do not allow old WAI v12/v14 advice to override v17 author guidance without a controlled v17 test.

## 12. Restart use

A future KNOWLEDGE chat working on WAI17 should read:
1. `GENERATION_KNOWLEDGE_INDEX.md`
2. this file
3. `HARD_FETISH_MODEL_FAMILY_MATRIX_20260909.md`
4. relevant hard/niche domain research
5. `DANBOORU_WIKI_SEMANTIC_AUDIT_20260909.md`
6. `HF_MODEL_DISCUSSIONS_AUDIT_20260909.md`
7. Batch A/B/C for diagnosis, pruning and evidence strength.

No cross-team handoff is implied by this file.