# Practical Generation Knowledge Readiness Audit — 2026-09-13

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Status: `AUDITED / PRACTICAL_GAPS_IDENTIFIED`

## Audit question

Does the current KNOWLEDGE corpus let the user move through a real local generation loop:

`choose model -> set baseline -> write Prompt -> generate -> diagnose -> refine -> use LoRA/Hires/ADetailer/inpaint/regional/control when needed -> preserve result/settings`

without relying on vague community habits or rediscovering tool operation every time?

## Executive verdict

Current knowledge is **strong for controlled generation/evaluation** and **only partially complete for normal creative production**.

Strongest areas:
- exact model-family separation
- WAI17 baseline and isolation testing
- Prompt semantic decomposition
- conflict/failure diagnosis
- difficult relation/body-site/count/topology reasoning
- evidence/reproducibility discipline
- distinction between base / LoRA / assisted-control / postprocess success

Weakest areas:
- ordinary production workflow from first draft to finished image
- model-choice decision support
- sampler/scheduler practical tradeoffs
- resolution/aspect-ratio selection by subject/composition
- practical LoRA loading/weight/stacking/trigger workflow
- practical Hires recipe and when to use it
- ADetailer detector/prompt/inpaint operating choices
- img2img/inpaint rescue workflow
- Forge Couple / Region ControlNet escalation workflow
- seed/batch/X-Y-Z workflow for creative search rather than evidence only
- runtime/performance guidance tied to current Forge Neo

The knowledge base currently answers **"why did this fail?"** better than **"what should I do next to finish the picture?"**.

## Coverage matrix

### A — ready for practical use

#### Model/version scope
The corpus correctly keeps WAI17 / Illustrious / NoobAI / Anima separate and rejects universal Prompt grammar.

#### WAI17 basic generation baseline
Current author-supported baseline is well captured:
- Forge Neo
- Euler a
- Steps 15–30
- CFG 5–7
- integrated VAE
- original dimensions above 1024x1024 area; 1024x1344 examples
- short positive/Negative quality baseline

The project isolation profile (Euler a / 25 / CFG5 / 1024x1344 when appropriate / helpers OFF) is suitable for controlled diagnosis.

#### Prompt diagnosis
Strong practical diagnostic ordering already exists:
- spelling/trigger
- model/version
- unary activation
- actor-target/body-site relation
- visibility/crop
- composition conflict
- Negative collision
- density/weight conflict
- seed sensitivity
- LoRA/postprocess/control confounds

#### Hard/niche generation reasoning
The corpus is unusually strong here. It explicitly decomposes:
- body site
- actor/target/owner
- exact count
- topology
- machine functional contact
- tentacle source/ownership
- fluid source/destination
rather than passing on mere object presence.

### B — usable but not consolidated enough

#### Hires Fix
The WAI17 author card gives an actionable recipe:
- upscale 1.5
- Hires steps 20
- R-ESRGAN 4x+ Anime6B
- denoise 0.35–0.5
and states Hires may repair limbs/hands/feet.

The corpus understands Hires as a separate evidence lane but the practical recipe is not surfaced prominently in the current tool/postprocess catalog or quick workflow.

Needed:
- when to enable Hires for ordinary production
- when denoise is too low/high
- preserve-vs-redraw expectations
- when Hires should come before/after ADetailer/inpaint

#### Resolution/aspect ratio
WAI17 and NoobAI author ranges exist, but there is no consolidated practical rule such as:
- portrait character
- upper-body portrait
- landscape/group
- square/product/close-up
- when crop/visibility failure means change aspect ratio rather than add Prompt tags

#### Seed workflow
The corpus is excellent for controlled A/B, but weak for ordinary exploration:
- random-seed discovery
- keep/lock promising seed
- vary Prompt on fixed seed
- return to random exploration after local optimum
- batch-count strategy

#### Model Prompt conventions
Quality / score / artist / Negative conventions are now strong, but they are not yet turned into a one-screen "start here for this model" practical recipe.

### C — significant practical gap

#### Model choice
There is no current decision matrix for choosing between WAI17 / NoobAI / Anima based on task.

Needed dimensions:
- Danbooru-tag-first illustration
- natural-language relation-heavy scene
- multi-character identity/binding
- style/artist control
- niche/rare-tag target
- speed/stability vs creative flexibility
- availability of compatible LoRA/control assets

This must remain evidence-scoped; it should not invent a universal winner.

#### Sampler / scheduler choice
WAI17/NoobAI defaults are recorded, and Anima's author currently provides practical sampler differences, but the corpus does not consolidate them.

Current Anima author guidance includes different characteristics for `er_sde`, `euler_a`, `dpmpp_2m_sde_gpu`, `euler`, and mentions `beta57` for painterly/realistic texture in a specific ComfyUI setup.

Needed:
- exact-model default
- what is safe to vary
- what symptom justifies sampler/scheduler change
- do not turn sampler taste into semantic diagnosis

#### LoRA normal-use workflow
Current knowledge focuses on confounds/evidence and compatibility, not daily use.

Missing practical guidance:
- where/load state in Forge Neo
- character/style/concept LoRA role distinction during generation
- trigger placement
- starting weight strategy
- one-LoRA-first isolation
- stacking two LoRAs
- diagnosing overpowering/context leakage
- when lowering weight beats adding Negative
- how Hires/ADetailer/regional interact with LoRA

#### ADetailer Neo
Current corpus mainly says detect -> mask -> inpaint and treats it as a confound.

Current official Forge Neo fork provides face/hand/person YOLO detectors plus MediaPipe models.

Missing:
- face vs hand vs person detector selection
- when ADetailer is appropriate
- when it can damage identity/style/body-site intent
- separate ADetailer Prompt/Negative use
- inpaint strength/mask behavior basics
- ordering with Hires

#### img2img / inpaint
Current knowledge only records that they can preserve or replace structure depending on mask/denoise.

Missing practical ladder:
- use img2img for whole-image controlled revision
- use inpaint for local correction
- mask only broken region vs include context
- low/mid/high denoise interpretation
- when repeated inpaint is worse than regenerate
- preserve Prompt/seed/LoRA metadata

#### Forge Couple / regional conditioning
Current corpus knows the capability but lacks current operation.

Current Forge Couple supports:
- Basic mode (prompt lines -> rows/columns)
- Advanced coordinate regions
- Mask mode
- Global Effect
- Common Prompts
- Anima support

Its README explicitly warns that regional conditioning cannot fix a checkpoint that does not understand the composition at all.

Needed:
- escalation rule from plain Prompt to Couple
- simplest Basic-mode recipe first
- total-subject count in each region
- global/background line usage
- when Advanced/Mask is worth the complexity
- Hires compatibility behavior

#### Current Forge Neo integrated controls
Current maintained Forge Neo has moved beyond the older corpus snapshot and now documents current features including:
- Anima support
- LLLite ControlNet updates
- Union ControlNet
- Anima Region ControlNet
- X/Y/Z Plot updates
- Preset system storing checkpoint/module/parameters
- updated Soft Inpainting
- current LoRA implementation changes

The corpus needs a current practical runtime layer rather than only mechanism-level ControlNet knowledge.

### D — currently thin / operational debt

#### Normal creative iteration recipe
There is no single durable sequence equivalent to:

1. choose exact model/profile
2. start author baseline
3. build minimal subject/scene Prompt
4. generate several exploratory seeds
5. lock promising seed only for diagnosis
6. fix composition/visibility before piling style/support
7. add LoRA one at a time
8. use Hires for final pass when base structure is acceptable
9. use ADetailer/inpaint for local defects
10. use regional/control only when plain conditioning cannot bind the scene
11. preserve final infotext/preset

This is the largest practical usability gap.

#### Runtime/performance guidance
The current corpus does not sufficiently cover current Forge Neo operation/performance changes.

Examples that require exact-build scope:
- attention backends
- mixed precision
- tiled VAE
- torch.compile
- current memory behavior
- current RTX-generation compatibility warnings

Do not encode these globally without local runtime identity.

## Important source correction found by this audit

The freshness ledger previously pointed Forge Neo at:
`gi0baro/forge-neo`

That repository is a stale fork. Its parent is the actively maintained:
`Haoming02/sd-webui-forge-classic` branch `neo`.

The ledger has been corrected to the maintained upstream while preserving the requirement to pin the user's exact local remote/commit before exact runtime claims.

## Current practical-generation readiness by task

- Generate a clean WAI17 baseline image: **READY**
- Diagnose why a Special/relation failed: **READY / STRONG**
- Compare canonical/Alias/support experimentally: **READY**
- Build a complex relational evaluation case: **READY / STRONG**
- Turn a decent base image into a polished finished image: **PARTIAL**
- Choose the best model for a new target: **PARTIAL**
- Choose sampler/scheduler beyond author default: **PARTIAL**
- Use LoRA confidently without trial-and-error: **NOT YET CONSOLIDATED**
- Use ADetailer/inpaint as a controlled correction workflow: **NOT YET CONSOLIDATED**
- Use Forge Couple/Region Control efficiently: **NOT YET CONSOLIDATED**
- Optimize current Forge Neo for exact local hardware: **LOCAL-STATE REQUIRED**

## Recommended next practical enrichment

Do not jump directly into broad P2 image A/B.

First create a `PRACTICAL_GENERATION` layer with these topics:

1. `PG-01` Daily generation loop / first-draft -> finished-image workflow
2. `PG-02` Exact-model quick-start cards (WAI17 / NoobAI / Anima)
3. `PG-03` Resolution + sampler/scheduler + seed workflow
4. `PG-04` LoRA practical operations and stacking
5. `PG-05` Hires + ADetailer practical finishing workflow
6. `PG-06` img2img / inpaint repair ladder
7. `PG-07` Forge Couple / current ControlNet escalation guide
8. `PG-08` Forge Neo presets / X-Y-Z / infotext / repeatable iteration
9. `PG-09` Local-runtime identity + performance notes only after exact local build is known

Then pull P2 image tests only where a practical rule remains unresolved.

## Guardrails

- practical advice must retain exact model/tool/version scope
- creator/community recipes do not become universal rules
- current runtime features are not proof of checkpoint semantic ability
- assisted/postprocessed success remains distinguishable from base success
- no automatic runtime behavior is added to DanbooruTagTool merely because KNOWLEDGE records it
