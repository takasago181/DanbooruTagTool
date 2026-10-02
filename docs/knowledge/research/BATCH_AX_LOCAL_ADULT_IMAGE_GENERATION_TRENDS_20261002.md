# BATCH_AX — 2026年秋 ローカル成人向け画像生成トレンド調査 — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Branch: `knowledge/generation-corpus`  
Scope: local/open-weight adult image generation, with primary emphasis on 2D/anime; realism kept as a separate lane  
Mode: ecosystem/trend research; popularity is not generation authority

## 0. 目的

「今どのcheckpointが人気か」だけでなく、2026年秋にローカル成人向け生成の**作り方そのものがどう変わっているか**を整理する。

見る軸:

- model ecosystem
- LoRA資産
- Prompt dialect
- local LLM/VLM
- multi-character binding
- Regional / reference / edit
- training
- Hires / detailer / inpaint
- UI/runtime
- anime vs photoreal branch

Trendは時点依存なので、current model factと混同しない。

---

## 1. 結論: 一つのモデルへの一本化は起きていない

2026年秋の二次元成人向けローカル生成は、大きく二本立て。

### Lane A — SDXL / Illustrious / Pony / NoobAI

強み:
- 膨大な既存LoRA
- 既存checkpoint派生
- Danbooru/e621 tag資産
- Forge / ComfyUI / WebUI周辺の成熟
- WAIなど「すぐ綺麗に出る」成人向け派生

### Lane B — Anima

強み:
- 新しいanime knowledge cutoff
- tags + natural language + hybrid
- Base / Aesthetic / Turbo
- compact 2B architecture
- ComfyUI native support
- Forge Neo support
- rapid LoRA / workflow growth
- Regional/reference/edit系の新しい実験が活発

つまり現在は、
**旧資産の厚さ = Illustrious/Pony系**
と
**新しいworkflow/control実験 = Anima**
の両方が重要。

Promoted:
- K-TREND-001

---

## 2. Civitai ecosystem snapshot

Current platform snapshot checked 2026-10-02:

Anima ecosystem page:
- 33K+ models
- 283M+ images generated
- 32K+ LoRAs

The same comparison table lists:
- Illustrious: 199K+ LoRAs
- Pony: 101K+ LoRAs
- NoobAI: 8K+ LoRAs
- Anima: 32K+ LoRAs

Sources:
- https://www.civitai.tech/ecosystems/anima
- https://www.civitai.tech/ecosystems/noobai

Interpretation:

- Anima is no longer merely an early preview curiosity.
- It has a large active adapter ecosystem.
- Illustrious/Pony still retain a much deeper accumulated LoRA library.
- NoobAI has less dedicated LoRA count than Illustrious/Pony, but deep native concept/tag knowledge reduces the need for some LoRAs.

Do not compare raw counts as quality scores.
Multi-base LoRAs, duplicates and platform classification affect counts.

Promoted:
- K-TREND-002

---

## 3. WAI / Illustrious remains a practical adult daily-driver lane

Current WAI v17 remains available and actively mirrored.

Sources:
- https://civarchive.com/models/827184/wai-illustrious-sdxl?modelVersionId=2883731
- https://note.com/novapen_create/n/n7ef484c8f4d4
- https://lilting.ch/articles/wai-illustrious-v17-review

Why this lane persists:

- mature Illustrious LoRA compatibility
- familiar SDXL settings
- strong default aesthetics
- adult-capable finetuning
- Hires/detailer/upscale workflows are already mature

Trend conclusion:
Anima growth has not made WAI/Illustrious obsolete.
For users with established LoRA libraries, migration cost remains significant.

---

## 4. Anima is the main growth lane for anime adult generation

Official Anima current model card:

- 2B parameters
- anime knowledge cutoff September 2025
- Base / Aesthetic / Turbo
- LoRAs should train on Base
- Turbo: CFG 1, 8–12 steps
- tags + natural language + hybrid
- safety tags: safe / sensitive / nsfw / explicit
- native ComfyUI support

Source:
https://huggingface.co/circlestone-labs/Anima/blob/main/README.md

Important workflow consequence:

Turbo is not only a speed model.
The author explicitly recommends it as a prompt-iteration starting point because it is fast/stable, then Base/Aesthetic can be used when diversity/style behavior matters.

This strengthens the practical pattern:

`fast exploration -> exact final profile validation`

which already exists in #44.

---

## 5. Prompting trend: tags-onlyから hybrid / structured NL へ

SDXL/Illustrious/NoobAI:
- booru tags remain central
- tag autocomplete / Danbooru knowledge remain high value

Anima:
- tags still strong
- natural language can express relation/composition
- hybrid prompt is widely explored

Community evidence:
- Anima discussion #140 reports ~100-image informal comparison where tags-only were cleaner while NL added control but could increase hand/anatomy issues.
- Discussion #141 shows users using LLM/VLM systems to convert adult reference images into structured relation-focused natural-language prompts.

Sources:
- https://huggingface.co/circlestone-labs/Anima/discussions/140
- https://huggingface.co/circlestone-labs/Anima/discussions/141

Trend:
**tag discovery is not disappearing; it is becoming one layer inside a larger structured prompt pipeline.**

---

## 6. Local LLM/VLM prompt pre-processing is an emerging adult workflow

Japanese ecosystem evidence:

- 2026-05 article specifically covers local LLM selection/settings for NSFW Anima prompt engineering.
- EasyForgeNeo/Anima ecosystem articles package LLM/VLM-assisted prompting around Forge Neo.

Source:
https://note.com/hirorohi03/n/nbbe8b87a02ec

Tool evidence:

Anima Prompter Forge:
- Forge Neo extension
- LM Studio-compatible local model
- concept -> structured Anima prompt
- optional reference image
- explicit safety-rating override

Source:
https://github.com/opparco/anima-prompter-forge

TIPO / DanTagGen path:
- local prompt pre-sampling
- tag expansion
- tags + natural language

Source:
https://github.com/DamienCz/comfyui-tipo

Interpretation:
The trend is not “LLM writes one giant perfect prompt”.
The useful pattern is:

`human intent -> local LLM/VLM structuralization -> tag/relation modules -> generator -> diagnostic loop`

This aligns with DanbooruTagTool's structural knowledge work.

Promoted:
- K-TREND-003

---

## 7. Multi-character adult generation is driving control-tool adoption

Repeated current pain:
- identity bleed
- attribute swap
- one LoRA overpowering another
- role/relation drift
- overlap anatomy failures

Evidence:
- https://huggingface.co/circlestone-labs/Anima/discussions/202
- https://huggingface.co/circlestone-labs/Anima/discussions/93
- https://www.reddit.com/r/comfyui/comments/1ws23ur/multiple_characters_in_one_single_generated_image/

As a result, workflow interest is shifting from only Prompt tuning toward:

- Regional text/attention
- latent RegionalSampler
- mask-localized reconstruction
- reference adapters
- edit LoRAs
- staged LoRA conditioning
- inpaint after global scene lock

This does not prove these tools always improve interaction.
It explains why they are a current development focus.

---

## 8. Regional control is becoming ordinary advanced tooling

Forge Neo Regional Prompter:
- 2026-09-04 added Anima Latent/Attention support
- Region LoRA remains unsupported

Source:
https://github.com/hako-mikan/sd-webui-regional-prompter

ComfyUI Anima Regional Conditioning:
- mask-routed cross attention
- optional self-attention separation
- explicit warning that stronger isolation can damage inter-region awareness

Source:
https://github.com/Sen-sou/Comfyui-Anima-Regional-Conditioning

Impact-Pack RegionalSampler:
- latent-level regional resampling path

Existing #44 research:
`BATCH_AU_REGIONAL_SAMPLER_PROXY_METHOD_20261002.md`

Trend lesson:
Regional is moving from niche trick to normal advanced workflow component,
but **interaction coherence remains the limiting counter-force**.

---

## 9. Reference-driven generation is a major emerging branch

Current public Anima-specific tools now include:

### Anima IP-Adapter

Examples:
- https://github.com/Wenaka2004/comfyui-anima-ipadapter
- https://github.com/LuciferTC9527/ComfyUI-Anima_IP-Adapter

Goals:
- reference-driven character consistency
- style/reference transfer
- sampling-range control

These are still young community tools.
Do not treat them as mature universal standards.

### Anima Edit / ReferenceLatent

Japanese guide:
https://note.com/hirorohi03/n/na72233a8d6a4

ComfyUI compatibility node:
https://github.com/wochenlong/ComfyUI-Anima-Edit-LoRA

Emerging pattern:

`generate acceptable reference -> preserve identity/composition -> edit only required factors`

This reduces reliance on asking one text prompt to solve everything at once.

Promoted:
- K-TREND-004

---

## 10. LoRA trend: “character LoRA一個”から role-aware / multi-character datasetへ

Current Anima discussions are increasingly about:

- multi-character LoRA support
- reducing identity bleed
- training multiple single-character LoRAs to coexist
- training one multi-character LoRA
- including genuine joint examples
- dataset context/style entanglement

Sources:
- https://huggingface.co/circlestone-labs/Anima/discussions/220
- https://huggingface.co/circlestone-labs/Anima/discussions/222
- https://huggingface.co/circlestone-labs/Anima/discussions/187

Important:
specific claims such as “two joint images are enough” remain anecdotal.
The durable trend is that **coexistence/interaction is becoming a training objective**, not only an inference-time problem.

Existing #44 dataset research already supports this structurally.

---

## 11. Finishing is being bundled into one workflow

Current public Anima AIO workflows include:

- T2I
- I2I
- HighRes
- Inpainting
- Face/Eye detailer
- Upscale
- save/metadata

Example:
https://github.com/n0va39/ComfyUI-EasyUseAnima

This reflects a broader workflow shift:

`base generation -> structure check -> local repair -> highres/detail -> final upscale`

rather than attempting one-pass perfection.

This is especially relevant to adult relation-heavy scenes because:
- global relation correctness
- local anatomy quality
are separate problems.

Promoted:
- K-TREND-005

---

## 12. UI/runtime trend

### Forge Neo

Role:
- daily interactive generation
- familiar WebUI
- Anima support
- Regional extensions
- Japanese beginner ecosystem
- LM Studio/LLM integration is appearing

Japanese sources:
- https://note.com/maynoha/n/neb08ce64c72c
- https://note.com/crody/n/n937474cf1c23
- https://note.com/hirorohi03/n/n26a9ca1ef166

### ComfyUI

Role:
- newest model support
- reproducible graph
- Regional/reference/edit experimentation
- custom-node ecosystem
- advanced LoRA/control workflows

Community local-adult setup guide also frames Forge/reForge as simpler and ComfyUI as the faster-moving advanced backend:
https://github.com/awesome-ai-hentai/awesome-ai-hentai

Trend:
There is no single winning UI.
The split is increasingly:

- Forge Neo = daily interactive work
- ComfyUI = research/complex reproducible pipelines

---

## 13. 中国語圏でもAnima workflowの標準化が進行

Recent Bilibili content:

- 2026-08 Anima “all-in-one” guide covers base selection, workflow, LoRA management, artist selection and prompt templates.
- 2026-08 local ComfyUI tutorial explicitly uses Anima + LoRA.
- 2026-06 prompt plugin + automatic reverse-prompt workflow advertises 6GB VRAM compatibility.

Sources:
- https://www.bilibili.com/video/BV11Eb26mEo9/
- https://www.bilibili.com/video/BV1538m6KE9h/
- https://www.bilibili.com/video/BV1t9Eq6iEwy/

This is useful ecosystem signal:
Anima usage has moved beyond isolated expert experiments into packaged beginner workflows.

---

## 14. Photoreal adult generation is a separate trend lane

Do not pool anime conclusions into realism.

Current realism/community discussions mention:
- Chroma
- Z-Image / Z-Image Turbo
- FLUX.2 Klein / FLUX-family derivatives
- older SDXL realism adult finetunes

Sources:
- https://www.reddit.com/r/StableDiffusion/comments/1ttxmvd/best_local_realistic_image_model_that_is/
- https://www.reddit.com/r/comfyui/comments/1sr0rh7/whats_the_best_photorealistic_model_for_local_use/
- https://www.civitai.tech/ecosystems/chroma
- https://www.civitai.tech/ecosystems/flux2

Why separate:
- different text encoders
- different LoRA ecosystem
- different anatomy/style priors
- different runtime cost
- different adult-data coverage
- different prompting dialect

DanbooruTagTool's current high-value lane remains anime/illustration.

Promoted:
- K-TREND-006

---

## 15. “流行っているが、まだ正本にしない”もの

### Exact Anima adult prompt recipes
Too user/model/seed specific.

### Maximum LoRA stacking
More adapters often reduce control.

### Very high native resolution
Community tests exist, but official Anima guidance remains 512²–1536².
Higher-resolution success is setup/sampler dependent.

### Anima IP-Adapter / Edit as solved standards
Promising and growing, but young.

### Local LLM output as semantic authority
LLM/VLM is a structuring assistant, not ground truth.

### One community “best model” ranking
Popularity and taste do not establish capability.

---

## 16. 2026秋の実用 stack map

### 成熟・安定
- WAI / Illustrious derivatives
- Pony asset ecosystem
- NoobAI tag-centric workflow
- LoRA
- Hires
- detailer
- inpaint
- Forge / ComfyUI

### 急伸
- Anima Base/Aesthetic/Turbo
- Anima LoRA ecosystem
- Forge Neo Anima
- ComfyUI Anima workflows
- hybrid tag + NL
- local LLM/VLM Prompt structuring

### 急速に実験中
- Anima Regional Conditioning
- Anima IP-Adapter
- Anima Edit LoRA / ReferenceLatent
- localized/staged LoRA
- multi-character-aware LoRA datasets

### 別系統
- Chroma / Z-Image / FLUX2 for photoreal adult
- do not transfer anime Prompt/LoRA rules blindly

---

## 17. DanbooruTagToolへの意味

The current product should not become an automatic adult Prompt generator merely because these trends exist.

High-value knowledge contribution:

1. canonical tag discovery remains useful;
2. add model-dialect awareness;
3. expose relation/count/body-site structure;
4. preserve Prompt-only vs Regional/reference/edit evidence;
5. make export usable as input to local LLM/VLM or advanced workflows;
6. preserve exact model/runtime identity.

Future tooling may reasonably support:
- structured scene slots
- prompt module export
- control-route suggestions
- failure labels
- workflow metadata

without hardcoding one explicit recipe.

---

## Promotion result

New ACCEPTED:
- K-TREND-002
- K-TREND-004

New CANDIDATE:
- K-TREND-001
- K-TREND-003
- K-TREND-005
- K-TREND-006

Trend claims are date-scoped and require freshness review.
