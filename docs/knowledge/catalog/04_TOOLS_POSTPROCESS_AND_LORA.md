# Tools, Postprocess and LoRA

## Core rule

Prompt-only capability, assisted-control capability, and postprocess-repaired output are different evidence lanes.

Current practical focus:
- NoobAI XL 1.1 EPS / V-Pred
- Anima Base / Aesthetic / Turbo
- Forge Neo current maintained branch

Operational entry:
`../current/PRACTICAL_GENERATION_NOOB_ANIMA.md`

## Hires / upscaling

Hires is not a neutral resolution multiplier.

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

### WAI reference
WAI v17 author explicitly describes Hires as capable of repairing limbs/hands/feet.

### NoobAI practical rule
NoobAI is an SDXL/Illustrious descendant, so conventional SDXL Hires/img2img workflows are available, but exact denoise/upscaler choices remain derivative/runtime scoped.

### Anima practical rule
Official normal Anima range reaches roughly 512²–1536². Above the comfortable native range:
1. establish structure at native size
2. use external/model upscale when preservation is the goal
3. use img2img/tiled refinement only when redraw/detail is intended
4. preserve exact profile/version and denoise

Japanese practical recipes for exact denoise/upscaler values remain `RECIPE / TEST_REQUIRED` rather than universal defaults.

## ADetailer Neo

Current Forge Neo official fork:
`Haoming02/ADetailer-Neo`

Mechanism:
`generate -> detect -> mask -> inpaint`.

Current bundled detector categories include:
- face YOLO
- hand YOLO
- person segmentation
- MediaPipe face detectors

Practical selection:
- face detector: face/local facial detail
- hand detector: visible hands/fingers
- person segmentation: broader person-level redraw only when that larger intervention is intended

ADetailer may use its own Prompt/Negative/inpaint settings. If it edits the body site/face/hand that matters to the target, it is a confound for base-generation claims.

Detection order is not semantic actor authority.
Do not use ADetailer to hide wrong count, wrong relation, wrong actor ownership, or a missing target body site.

## img2img / inpaint

These can preserve or replace local structure depending on mask/denoise.
Keep `PROMPT_ONLY` and `EDIT_ASSISTED` verdicts separate.

Practical repair ladder:
- whole image broadly wrong -> regenerate / revise base Prompt first
- local anatomy/detail wrong -> inpaint/ADetailer candidate
- structure correct but resolution insufficient -> upscale/Hires candidate
- relation/ownership wrong -> fix semantic/region control before cosmetic repair

Repeated inpainting that progressively rewrites the target is an editing workflow, not evidence of base-model capability.

## ControlNet / regional controls

ControlNet/OpenPose/depth/edge/segmentation add external spatial conditioning. They are useful when Prompt-only reaches a spatial ceiling, but their success does not prove Prompt-only capability.

Current Forge Neo documents:
- Anima LLLite support
- Anima Region ControlNet support
- Union ControlNet for supported SDXL paths

Exact parameter recipes require exact current runtime/control model identity.

## Regional prompting / Forge Couple

Current Forge Couple supports Forge Neo and Anima.

Modes:
- Basic: tile/line regions; recommended first for most uses
- Advanced: explicit x/y region ranges and weights
- Mask: user-drawn approximate regions

Useful for:
- multiple actors
- asymmetric clothing/attributes
- actor/resource separation
- spatially partitioned conditioning.

Current extension guidance also says:
- still state the total subject count
- regional conditioning depends on checkpoint Prompt understanding
- it cannot create a composition the checkpoint fundamentally does not understand

Anima escalation:
`plain explicit Prompt -> concise hybrid relation -> Basic -> Advanced/Mask -> Region/Control when geometry is the bottleneck`.

Treat all regional success as `ASSISTED_CONTROL`.

## Dynamic Prompts / X-Y-Z

Dynamic Prompts remains useful for bounded variant enumeration when exact resolved Prompt is retained.

Current Forge Neo also provides X/Y/Z plotting and updated preset/infotext handling.

Daily-use distinction:
- random exploration: discovery
- bounded X/Y/Z or Dynamic variants: comparison
- promotion-grade evidence: exact settings, seeds, resolved Prompt, model hash, adapter/control state retained

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

## NoobAI / Illustrious LoRA compatibility

NoobAI descends from Illustrious, so Illustrious-family LoRAs are reasonable **candidates** for NoobAI.

Do not promote this into blanket compatibility.
Japanese practical sources and community reports show both successful cross-use and adapter/checkpoint-specific failures.

For every adapter preserve:
- creator-declared base model
- training model when known
- target checkpoint
- trigger
- weight
- EPS/V-Pred expectations if relevant

## Anima LoRA boundary

Anima is a separate model family from SDXL/Illustrious/NoobAI.

Safe rules:
- do not assume SDXL/Noob LoRA compatibility
- official Anima recommendation is to train LoRAs on Anima Base
- profile-specific behavior on Base/Aesthetic/Turbo may differ and remains testable

Japanese Anima-specific trainer/instant-LoRA workflows are valuable practical tools but should not redefine what counts as a robust general LoRA.

## Training-base compatibility

Preserve when known:
- LoRA training base/family
- inference checkpoint/profile
- role: character/style/pose/concept
- trigger
- weight.

Do not generalize adapter behavior across model families without evidence.

## Current runtime note

Current maintained Forge Neo authority:
`Haoming02/sd-webui-forge-classic` branch `neo`.

The repository currently documents:
- Anima 2B plus community 2.9B/3.8B support
- updated LoRA implementation
- Anima LLLite/Region ControlNet
- presets
- X/Y/Z
- Soft Inpainting / MultiDiffusion updates

Exact local runtime commit is still required for promotion-critical runtime claims.

## Primary originals

- `../GENERATION_KNOWLEDGE_CORPUS.md`
- `../research/TOSHIAKI_WIKI_PRACTICAL_FINDINGS_20260909.md`
- `../research/BATCH_L_NOOB_ANIMA_PRACTICAL_GENERATION_DEEP_DIVE_20260913.md`
- `../research/BATCH_M_JAPANESE_PRACTICAL_SOURCE_AUDIT_NOOB_ANIMA_20260913.md`
- `../research/HARD_FETISH_SOURCES_20260909.md`
- `../research/BATCH_A_FALSE_ASSUMPTION_PREVENTION_20260909.md`
