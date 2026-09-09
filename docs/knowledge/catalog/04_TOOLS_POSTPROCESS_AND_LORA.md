# 04 — Tools, Postprocess and LoRA

## Core rule

Prompt-only capability, assisted-control capability, and postprocess-repaired output are different evidence lanes.

## Hires Fix

Hires is not a neutral resolution multiplier. On WAI v17 the author explicitly describes improved limb/hand/foot correction.

Record separately:
- base image/result
- upscaler
- Hires steps
- denoise
- final result.

Useful outcome labels:
- `BASE_SUCCESS_FINAL_SUCCESS`
- `BASE_FAIL_POSTPROCESS_RESCUE`
- `BASE_SUCCESS_POSTPROCESS_DAMAGE`
- `NO_MATERIAL_CHANGE`.

A final image repaired by Hires does not certify base Prompt anatomy/geometry.

## ADetailer

Mechanism: generate -> detect/mask -> inpaint.

ADetailer may use its own Prompt/Negative/inpaint settings. If it edits the body site/face/hand that matters to the target, it is a confound for base-generation claims.

Detection order is not semantic actor authority.

## img2img / inpaint

These can preserve or replace local structure depending on mask/denoise. Keep `PROMPT_ONLY` and `EDIT_ASSISTED` verdicts separate.

## ControlNet / pose controls

ControlNet/OpenPose/depth/edge/segmentation add external spatial conditioning. They are useful when Prompt-only reaches a spatial ceiling, but their success does not prove Prompt-only capability.

## Regional prompting / Forge Couple

Useful for:
- multiple actors
- asymmetric clothing/attributes
- actor/resource separation
- spatially partitioned conditioning.

Treat as `ASSISTED_CONTROL`, not evidence that the plain checkpoint can bind the same scene without regional help.

## Dynamic Prompts

Best current project use is controlled variant enumeration:
- support A/B variants
- fixed candidate sets
- bounded combinations
- repeatable seed/Prompt matrices.

Random exploration can be useful for discovery, but production evidence still needs exact resolved Prompt and seed identity.

## LoRA — loaded state is a variable

Record every loaded LoRA and weight even if trigger text is absent.

`LoRA loaded + no trigger` is not guaranteed to equal base checkpoint.

When interaction matters compare:
- base
- A only
- B only
- A+B
- optionally order/weight variants if implementation makes them relevant.

## LoRA context leakage

Niche/style/concept LoRAs may import:
- pose prior
- style prior
- framing/background
- object bundle
- anatomy/detail tendencies
- learned scene context.

Therefore LoRA creator trigger bundles are excellent hypothesis generators but are not canonical definitions and do not prove base-model incapability.

## Training-base compatibility

Preserve when known:
- LoRA training base/family
- inference checkpoint
- role: character/style/pose/concept
- trigger
- weight.

Do not generalize adapter behavior across model families without evidence.

## Primary originals

- `../GENERATION_KNOWLEDGE_CORPUS.md`
- `../research/TOSHIAKI_WIKI_PRACTICAL_FINDINGS_20260909.md`
- `../research/HARD_FETISH_SOURCES_20260909.md`
- `../research/BATCH_A_FALSE_ASSUMPTION_PREVENTION_20260909.md`