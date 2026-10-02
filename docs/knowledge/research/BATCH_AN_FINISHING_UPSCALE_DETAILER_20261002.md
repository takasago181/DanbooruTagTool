# BATCH_AN — Finishing / upscale / detailer practical workflow — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: official workflow guidance + current Anima community practice
Scope: Hires, img2img, pixel/generative upscale, detailer, final delivery

## 1. Upscale vs enhancement

Official ComfyUI guide:
https://blog.comfy.org/p/upscaling-in-comfyui

Distinction:
- **Upscale**: increase resolution while reconstructing/preserving detail.
- **Enhancement**: improve perceived quality, which can include denoise, sharpen, restoration, color or re-imagined detail.

The guide explicitly separates:
- conservative/preservation-oriented upscale;
- creative/generative upscale.

For stylized illustration:
- distinctive/unique style generally benefits from conservative processing when style preservation is the priority;
- creative approaches can add detail but may drift away from the original style.

Production rule:
Do not ask one finishing stage to maximize both exact preservation and creative reinterpretation.

Promoted:
- K-PRACTICAL-008.

## 2. Repair before upscale

Same official guide warns against relying on upscaling to fix:
- extra/malformed fingers;
- anatomy errors;
- morphing;
- typical AI artifacts.

Recommended production order:
`Generation -> Refinement/Fix -> Upscale -> Delivery`.

This matches the project structural gate:
fix semantic/anatomy errors before final-resolution processing.

Promoted:
- K-PRACTICAL-009.

## 3. Forge Hires is a second generation pass

Current Forge UI source:
https://github.com/lllyasviel/stable-diffusion-webui-forge/blob/main/modules/ui.py

Hires UI exposes separate choices for:
- checkpoint
- VAE / Text Encoder
- sampling method
- scheduler
- prompt
- negative prompt
- Hires CFG-related settings

Therefore:
`base result -> Hires result`
is not equivalent to:
`base result -> deterministic pixel resize`.

Evidence identity must retain both passes.

Promoted:
- K-TOOL-029.

## 4. Second-pass diagnostic template

When Hires changes the image unexpectedly, inspect:

### Source pass
- model/profile
- seed
- resolution
- sampler/scheduler
- CFG/steps
- LoRA/control

### Hires pass
- resize/upscaler
- output dimensions
- denoise
- Hires checkpoint
- Hires VAE/TE
- Hires sampler/scheduler
- Hires prompt/negative
- Hires CFG/steps
- adapter/control state

Do not diagnose only the upscaler.

## 5. Anima img2img/upscale sensitivity

Community reports:
- https://www.reddit.com/r/StableDiffusion/comments/1tmrh0l/the_not_so_anime_anima/
- https://www.reddit.com/r/StableDiffusion/comments/1t87xbc/anima_settings_in_forge_neo/
- https://www.reddit.com/r/StableDiffusion/comments/1wqb41q/anima_upscaling/

Reported practical patterns:
- er_sde can be attractive for initial generation yet produce smudging in some img2img/upscale setups;
- users switch sampler for second pass in some workflows;
- low-denoise img2img / tiled methods are common attempts to retain structure;
- direct high-resolution, Hires, tiled diffusion, SeedVR-style restoration and pixel upscalers are all used, with no single current community standard.

Treatment:
- preserve the **sensitivity pattern**;
- do not promote exact denoise or scale factors.

Promoted:
- K-COMM-ANIMA-023.

## 6. Conservative vs creative anime finishing

If the current image already has:
- correct face
- correct line language
- desired artist/style
- correct clothing design

prefer a preservation-oriented first test.

If the source image:
- lacks texture/detail;
- is intentionally a rough draft;
- has large clean regions intended for reinterpretation

a more creative enhancer can be tested.

Always compare:
- identity drift
- line/style drift
- color/palette drift
- anatomy drift
- text/logo hallucination
- new unwanted objects.

## 7. Detailer is a local second sampler

Current Anima community thread:
https://www.reddit.com/r/StableDiffusion/comments/1tj1fw2/detailing_in_anima_is_really_confusing_any_guides/

User reports:
- large sampled body areas could become noisy;
- eyes/mouth and smaller regions worked better in that setup;
- scheduler/sampler changed the outcome substantially.

Do not generalize the exact recipe.

Operational evidence identity:
- detector
- crop/mask size
- padding
- resolution
- denoise
- sampler/scheduler
- steps/CFG
- prompt overrides.

Promoted:
- K-COMM-ANIMA-024.

## 8. Detailer routing

Use detailer when:
- global scene is already correct;
- target is local;
- detector/mask can isolate the defect.

Avoid as first repair when:
- whole-body pose is wrong;
- identity binding is wrong;
- global composition is wrong;
- large-area regeneration is required.

Escalate large regions to:
- inpaint with deliberate mask/context;
- pose/depth guidance;
- img2img/regional reconstruction.

## 9. Production finishing ladders

### Preservation-first illustration
1. local repair
2. conservative pixel/restoration upscale
3. output sharpen/color if needed
4. final identity/style audit

### Detail-enhancement illustration
1. structural gate
2. moderate generative/img2img enhancement
3. compare against source for identity/style drift
4. local fixes
5. conservative final resize if needed

### Anima diagnostic
1. direct source image
2. pixel upscale only
3. img2img second pass
4. tiled/regional enhancement
5. detailer local crops

Change one lane at a time.

## 10. Final audit

Before delivery compare source vs final:
- face/identity
- line style
- palette
- clothing/accessory design
- hands/anatomy
- composition
- relation
- background objects/text
- unintended detail hallucination

A sharper image is not automatically a better reproduction.

## Promotion result

New ACCEPTED:
- K-PRACTICAL-008
- K-PRACTICAL-009
- K-TOOL-029

New CANDIDATE:
- K-COMM-ANIMA-023
- K-COMM-ANIMA-024
