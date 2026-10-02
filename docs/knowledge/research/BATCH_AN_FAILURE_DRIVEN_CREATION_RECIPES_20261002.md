# BATCH_AN — Failure-driven creation recipes — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: practical troubleshooting synthesis
Scope: anime character/style generation, regional separation, ControlNet, img2img, upscale, editing

## Goal

Turn failures into deterministic next actions.

Do not ask:
“what else can I add?”

Ask:
“which conditioning source caused the failure, and which capability is actually missing?”

## 1. Character looks right alone, wrong after style LoRA

Test in this order:
1. base + character prompt
2. character LoRA only
3. native artist/style prompt only
4. style LoRA only
5. character LoRA + native style
6. character LoRA + style LoRA

If identity fails only at step 6:
- lower/remove style adapter
- check style-LoRA content leakage
- test scheduling/masking if available
- do not retrain the character immediately.

## 2. Face is accurate but pose stops responding

Likely classes:
- character LoRA over-constrained
- training pose/context entanglement
- character prompt contains scene/style information
- adapter weight too dominant
- structural control missing

Test:
1. character LoRA weight sweep
2. unseen simple pose
3. remove style/background blocks
4. base model pose test
5. pose control if semantics are understood but geometry remains wrong

If the base model responds but the LoRA does not:
treat as LoRA editability loss.

## 3. Background will not change

Test:
- trigger + empty/simple background
- trigger + strongly different background
- lower LoRA weight
- concept-agnostic prompt without trigger
- inspect training data for constant background/context

Do not keep adding synonyms if the background is part of the learned identity prior.

## 4. Native artist/style tag stops working after LoRA

Test:
A. base + artist
B. LoRA + no artist
C. LoRA + artist
D. lower LoRA strength
E. artist/style adapter instead of native tag

Classify:
`BASE_STYLE_KNOWLEDGE_SUPPRESSION`
when artist response exists in base but disappears under LoRA.

## 5. Two characters work individually but mix together

First establish:
- A only works
- B only works
- A+B minimal fails

Then:
1. explicit total count
2. subject-specific distinguishing features
3. remove excessive shared artist/series/style pressure
4. concise relation/position description
5. regional prompt
6. mask/reference/inpaint if needed

Regional tools address locality.
They do not guarantee semantic composition.

## 6. Forge Couple practical rule

Official source:
https://github.com/Haoming02/sd-forge-couple/blob/main/README.md

Forge Couple:
- supports Forge Classic/Neo and Anima;
- targets conditioning at regions;
- explicitly warns effectiveness depends on checkpoint prompt/composition understanding;
- recommends including total subject count in each region.

Practical pattern:
- common/global: total count + shared scene
- region A: A-only traits
- region B: B-only traits
- background/common shared traits separately

Do not duplicate every full prompt in every region.

## 7. Regional Prompter on Anima

Official source:
https://github.com/hako-mikan/sd-webui-regional-prompter/blob/main/README.md

As of 2026-09-04:
- Anima Latent: supported
- Attention: supported
- Region LoRA: unsupported

Attention mode:
- each region is encoded separately;
- model attention is spatially restricted early, then released so the image can integrate globally.

Practical implication:
If regions look like separate collages:
- separation is too strong / source composition too independent
rather than “more regionalization is always better”.

## 8. Control map looks wrong

Before changing the generation model:
1. inspect pose/depth/lineart preprocessor output
2. verify the expected people/limbs/depth ordering
3. check resolution/aspect
4. only then tune ControlNet strength

Official ComfyUI source:
https://blog.comfy.org/p/preprocessor-and-frame-interpolation

Preprocessing is a separate creative/debug stage.

## 9. Img2img changes too much or too little

Official ComfyUI example describes image denoise as the preservation/reinterpretation axis.

Use the concept qualitatively:
- lower denoise -> preserve source
- higher denoise -> larger reinterpretation

Choose based on goal:
- local cleanup
- style transfer
- pose/structure rewrite

Do not copy one denoise threshold across models.

## 10. Hires changes face/style

Rollback:
1. inspect base image at native resolution
2. pixel upscale only
3. generative/img2img pass
4. compare identity/style after each stage

If identity changes only after generative finishing:
the finishing stage caused the drift.

Do not retrain the character LoRA first.

## 11. Upscale lane selection

ComfyUI 2026 handbook:
https://blog.comfy.org/p/upscaling-in-comfyui

Practical classes:

### Pixel/super-resolution
Use when:
- structure is already correct
- need resolution/edge/detail preservation

### Generative upscale / tiled diffusion
Use when:
- base lacks fine texture/detail
- willing to risk reinterpretation

### Img2img refinement
Use when:
- controlled redesign is desired
- prompt should actively modify the image

The strongest upscaler is not automatically the best reproducer.

## 12. Reference edit is too rigid

Community Anima reports:
- reference/edit latent can strongly preserve appearance;
- major pose change can become difficult.

Escalation:
- reference method -> mask area expansion
- inpaint
- pose/depth conditioning
- reconstruct only the changed area

Use reference rigidity when consistency is valuable; switch lane when geometry change is the goal.

## 13. Prompt becomes worse as it gets longer

Rollback to:
- identity/count
- required relation/pose
- camera
- essential environment
- style

Then add one detail group at a time.

For Anima:
tags + concise prose are both supported.
Do not use prose merely to restate every tag.

## 14. Failure-driven rollback protocol

Whenever quality suddenly degrades:

1. save current metadata
2. remove the last major change
3. verify the previous state returns
4. add the change alone
5. test 2–4 seeds
6. classify the failure
7. only then choose a fix

Typical major changes:
- LoRA
- LoRA weight
- style block
- long NL block
- region/control
- sampler/CFG
- Hires/img2img
- detailer/inpaint

## 15. Seed strategy

Use two modes:

### Debug seed
Fixed seed for causal comparison.

### Robustness seeds
Small set of seeds after a candidate configuration is found.

A workflow that only works on one cherry-picked seed is not robust.

## 16. Production acceptance

Before final export verify:
- intended identity
- style
- pose/relation
- count
- camera/crop
- background
- local anatomy
- no LoRA/style leakage
- no finishing-induced identity drift

Keep “base generation” and “final repaired image” verdicts separate.

## Promotion result

New ACCEPTED:
- K-PRACTICAL-008..014

New CANDIDATE:
- K-COMM-ANIMA-023
