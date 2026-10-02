# BATCH_AM — Practical creation workflow — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: practical production synthesis
Scope: anime character/style generation from first prompt to final repair

## Goal

Convert the existing knowledge corpus into a production sequence that can be followed while making images.

The practical loop is:

`intent -> fast exploration -> structural lock -> identity/style tuning -> high-resolution finishing -> local repair -> final audit`

The purpose is not to prescribe one magic workflow. It is to make failures observable and reversible.

## 1. Stage 0 — choose the lane before prompting

Ask what is actually being made:

- known character already represented by the checkpoint
- custom/weakly known character
- target art style
- character + style combination
- multi-character scene
- reference-image edit
- repeated/sequence images

Tool choice follows from the task:
- native tags/prompts
- character/style LoRA
- reference adapter
- regional/control
- img2img/inpaint

Do not start by stacking every available control.

## 2. Stage 1 — fast exploration

### Anima

Official source:
https://huggingface.co/circlestone-labs/Anima

Author guidance:
- Turbo: CFG 1, 8–12 steps
- Base/Aesthetic normal regime: 30–50 steps, CFG 4–5
- Turbo is specifically recommended for fast prompt iteration
- Turbo gains stability and speed but reduces diversity

Practical use:
1. iterate scene/prompt rapidly with Turbo when appropriate;
2. identify a workable composition/semantic structure;
3. revalidate on the intended final profile.

Do not assume a Turbo success transfers perfectly to Base/Aesthetic.

### NoobAI XL 1.1 EPS

Author baseline:
- Euler a
- CFG 5–6
- 25–30 steps
- ~1MP
- native tag-oriented caption order

Practical use:
begin close to the author baseline before changing sampler/CFG/steps.

### WAI v17

Author baseline:
- Forge Neo
- Euler a
- 15–30 steps
- CFG 5–7
- original resolution >1024² area
- author example 1024×1344

Use author baseline as first diagnostic condition.

## 3. Stage 2 — prompt skeleton

Build only enough prompt to establish:

1. subject count
2. character/identity
3. composition/camera
4. pose/relation
5. essential clothing/props
6. background if needed
7. style/rendering

For Anima:
- use tags for known atomic concepts;
- use concise natural language where relation/ownership/geometry needs clarification;
- tag dropout means every visible tag need not be enumerated.

Avoid adding quality, style, camera, anatomy, background and LoRA changes simultaneously.

## 4. Modular prompt construction

Keep three conceptual modules even when the runtime later concatenates them:

### STYLE
- artist/style surface
- style LoRA
- rendering medium
- quality/meta where appropriate

### CHARACTER
- identity
- core appearance
- character LoRA/reference

### SCENE
- count
- pose/action/relation
- camera
- environment
- props

Reason:
if pose breaks after adding a style adapter, or identity breaks after a scene rewrite, the changed module is visible.

This is organizational separation, not proof that prompt ordering alone solves attention binding.

## 5. Character-LoRA practical workflow

Community source:
https://note.com/moribro/n/na743c1e66884

Useful scoped observations:
- identical captions across all images caused pose controllability problems in that user's project;
- changing per-image captions helped preserve pose response;
- keeping character appearance separate from style/scene instructions improved practical reuse.

Do not promote that user's exact:
- dimension
- LR
- LoRA weight
as universal Anima settings.

Practical character-LoRA test:
1. character LoRA only
2. unseen pose
3. unseen outfit
4. unseen background
5. different style
6. final scene

If step 2–5 fail, do not compensate by simply raising LoRA strength.

## 6. Style-LoRA practical workflow

Start from:
- base / native style prompt
- style LoRA alone
- same-seed strength sweep
- unrelated subject
- character LoRA + style LoRA

Measure:
- style similarity
- identity preservation
- composition freedom
- prompt adherence
- unwanted content/style leakage

Community same-seed experiments show higher style-LoRA weight can increase resemblance while locking composition or introducing unwanted features.

## 7. LoRA stacking

Controlled community source:
https://note.com/fresh_macaw9581/n/n7a3a7f6ed1e7

In a fixed-seed Anima test:
- no LoRA
- one LoRA
- three LoRAs
were compared with common generation settings.

Reported direction:
- additional adapters could add detail/lighting;
- larger stacks also added unrequested content and reduced consistency.

Default practical sequence:
`base -> adapter A -> adapter B -> A+B -> additional adapter`.

Do not debug a 3–5 LoRA stack before establishing each adapter independently.

## 8. Parameter tuning

Default diagnostic rule:
- fixed seed
- fixed prompt
- fixed model
- fixed resolution
- one changed parameter

Tune in roughly this order:
1. model/profile
2. scene/prompt
3. sampler/scheduler
4. CFG
5. steps
6. LoRA weight
7. control strength

Reason:
late parameter tuning cannot rescue a fundamentally wrong scene definition.

## 9. Structural acceptance gate

Before Hires/upscale/detailer, verify:
- subject count
- identity
- relation/pose
- camera
- visibility
- major clothing/props
- gross anatomy

If these fail, return upstream.

Do not upscale a structurally wrong image and then judge the model by the final retouched image.

## 10. High-resolution finishing

### WAI v17 author example

Source:
https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md

Author example uses:
- Hires upscale 1.5
- Hires steps 20
- R-ESRGAN 4x+ Anime6B
- denoise 0.35–0.5

These are WAI-v17-scoped reference settings, not general SDXL/Anima defaults.

### Anima

Community reports show Anima can be sensitive to second-pass denoise/sampler/upscaler choices.
Treat:
- direct high-resolution
- pixel upscale
- tiled diffusion
- img2img
- Highres helper LoRA
as separate finishing lanes.

## 11. Editing / rescue

Public Anima workflows:
- https://www.reddit.com/r/StableDiffusion/comments/1totumo/anima_can_edit_images_and_this_is_possible_in_two/
- https://www.reddit.com/r/StableDiffusion/comments/1v729sl/remake_you_character_in_the_new_style_anima/

Two recurring patterns:

### Reference/Edit-latent path
Good for:
- preserving appearance
- clothing/background edits
Can become rigid for major pose change.

### Mask/Inpaint/Control path
Good for:
- local reconstruction
- opening new image area
- larger pose/background changes
Requires:
- masks
- source geometry
- more workflow setup

Record these as assisted-edit capability.

## 12. Local repair

Once global semantics are acceptable:
- face/hand/body region inpaint
- detailer
- mask + pose/depth
- per-subject reconstruction

Do not use local repair to hide:
- wrong actor
- wrong relation
- wrong count
- wrong composition.

## 13. Evidence metadata

Every retained good/bad example should preserve:

### Core
- exact model/checkpoint/hash
- runtime
- seed
- resolution
- sampler/scheduler
- steps
- CFG

### Prompt
- positive
- negative
- modular style/character/scene representation if used

### Resources
- each LoRA + weight
- reference image/method
- regional/mask/control
- ControlNet/preprocessor

### Finishing
- Hires
- img2img denoise
- upscaler
- detailer
- inpaint mask/edit

This makes later comparisons possible.

## 14. Practical iteration loop

When image is wrong:

### Concept missing
- verify trigger/tag
- simplify prompt

### Character weak
- test native character prompt vs LoRA/reference
- do not immediately raise multiple weights

### Pose/relation wrong
- reduce unrelated prompt load
- test concise relation wording
- then pose/depth/regional

### Style wrong
- test native artist/style without character LoRA
- style LoRA alone
- combined interference

### Composition wrong
- fix composition before Hires

### Local defect only
- inpaint/detailer

## 15. Production recipe philosophy

Keep two saved workflows:

### Diagnostic / Research
- deterministic seed
- minimal automation
- explicit metadata
- one-variable comparisons

### Production / Final
- chosen model/profile
- intended LoRAs/controls
- Hires/upscale
- detailer/inpaint

Never use the production workflow to answer a scientific question about base capability.

## Promotion result

New ACCEPTED:
- K-PRACTICAL-001..007

New CANDIDATE:
- K-COMM-LORA-015
- K-COMM-ANIMA-022

No numeric community recipe was promoted as a universal default.
