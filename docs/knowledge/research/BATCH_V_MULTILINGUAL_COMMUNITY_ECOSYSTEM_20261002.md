# BATCH_V — Chinese / Korean community ecosystem map — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Branch: `knowledge/generation-corpus`  
Mode: multilingual public-user ecosystem harvest  
Languages: Chinese / Korean  
Focus: Anima training, ControlNet, low-VRAM workflows, LoRA/model metadata management, cross-derivative practice

## Purpose

Expand #44 beyond Japanese/English community evidence without converting tutorial popularity into model-performance facts.

This batch maps what practitioners are actually using in 2026:
- training stacks;
- auto-tagging/dataset workflows;
- ControlNet/inpaint/pose/depth workflows;
- low-VRAM/Turbo workflows;
- LoRA/model metadata management;
- cross-derivative reuse warnings.

No new generation-effect Claim is promoted from this batch because the retrieved material is mostly tutorial/workflow evidence rather than controlled A/B.

## Chinese-language ecosystem

### 1. Anima Standalone Trainer

Source:
- Bilibili, 2026-04-16  
  https://www.bilibili.com/video/BV1EyQHBWEnF/

Linked project:
- `gazingstars123/Anima-Standalone-Trainer`

Observed community role:
- lowers setup friction for Anima LoRA training;
- positioned for lower-VRAM/local or cloud usage;
- packages a model-specific training UI rather than asking users to assemble generic SDXL scripts manually.

Knowledge value:
- confirms that Anima training practice rapidly moved toward dedicated trainers;
- tool availability is useful for future local test planning;
- the video's time-to-train headline is hardware/dataset specific and is not promoted.

### 2. Anima auto-tag + cloud LoRA pipeline

Source:
- Bilibili, 2026-05-17  
  https://www.bilibili.com/video/BV1YNLE62E4o/

Observed workflow:
- cloud environment;
- automatic tagging;
- character LoRA training;
- dedicated Anima trainer.

Knowledge value:
- corroborates English/Korean trends toward semi-automated dataset preparation;
- auto-tagging is treated as workflow acceleration, not semantic authority;
- exact “20-minute” training headline is not a project fact.

### 3. Anima LLLite / ControlNet practice

Source:
- Bilibili, 2026-05-23  
  https://www.bilibili.com/video/BV1pGGv6NEFx/

Linked model:
- `kohya-ss/Anima-LLLite`

Covered practical controls:
- inpainting;
- pose;
- depth;
- downloadable workflows.

Knowledge value:
- shows Anima-specific control tools are in mainstream community practice rather than only experimental GitHub projects;
- effectiveness remains assisted-control evidence and does not certify Prompt-only capability.

### 4. Current open-source Anima LoRA trainer practice

Source:
- Bilibili, 2026-08-25  
  https://www.bilibili.com/video/BV14ehG64EAq/

Linked project:
- `wochenlong/lora-scripts-next`

Knowledge value:
- shows active migration from one-off early trainers toward newer maintained training wrappers;
- exact current trainer implementation should be pinned before controlled training evidence.

### 5. Anima integrated workflow / prompt / LoRA practice

Sources:
- Bilibili, 2026-05-25  
  https://www.bilibili.com/video/BV18BGx6xEH5/
- Bilibili camera-control user plugin, 2026-07-15  
  https://www.bilibili.com/video/BV11SNq6wEvP/

Community trend:
- users package prompt templates, artist/style selection, LoRA management, redraw/control and camera controls into front ends around ComfyUI;
- some custom camera controls work by emitting selected prompt surfaces rather than adding a spatial-control model.

Knowledge implication:
- “camera UI” can merely serialize text; it must not be conflated with geometric conditioning;
- when evaluating a helper/plugin, record whether it emits Prompt text or adds external conditioning.

### 6. Illustrious LoRA cross-derivative reuse

Source:
- Bilibili post, edited 2026-04-11  
  https://www.bilibili.com/opus/1181478497372078082

Author reports:
- trained variants on Illustrious XL 0.1 / 2.0;
- tried the LoRA on multiple Illustrious derivatives and Noob / V-Pred;
- explicitly warns other Illustrious models are not guaranteed and CFG/LoRA strength may need adjustment.

Treatment:
- useful ecosystem evidence that “loads successfully” is not identical to “portable at the same strength”;
- exact cross-family reliability remains unresolved and is already bounded by K-LORA-001/002.

## Korean-language ecosystem

### 7. Anima-specific LoRA selection / model compatibility

Source:
- Korean practical guide, 2026-06-16  
  https://onebrotravel.tistory.com/entry/ComfyUI-%EC%B4%88%EA%B0%84%EB%8B%A8-%EC%9E%85%EB%AC%B8%EA%B0%80%EC%9D%B4%EB%93%9C-%E2%80%94-Anima%EC%97%90-LoRA-%EC%A0%81%EC%9A%A9%ED%95%98%EA%B8%B0

Practice:
- filters Civitai by base model = Anima before applying style LoRAs;
- teaches LoRA as model-family-specific resource rather than generic plug-in asset.

Knowledge value:
- multilingual corroboration of the project's existing compatibility discipline;
- not a new Claim.

### 8. Fine-tuned Anima checkpoint and LoRA metadata management

Source:
- Korean practical guide, 2026-06-16  
  https://onebrotravel.tistory.com/entry/Civitai%EC%9D%98-Anima-%EC%B2%B4%ED%81%AC%ED%8F%AC%EC%9D%B8%ED%8A%B8%EB%A1%9C-%EC%9D%B4%EB%AF%B8%EC%A7%80-%EC%83%9D%EC%84%B1%ED%95%98%EA%B8%B0

Practice:
- Civitai fine-tuned Anima checkpoints;
- LoRA Manager used to retrieve/manage model metadata.

Ecosystem implication:
- base-model metadata and trigger information are becoming part of practical resource management;
- this directly supports DanbooruTagTool's idea of keeping LoRA identity/base/trigger metadata available at use time.

### 9. Thumbnail-first Danbooru Prompt Gallery

Source:
- Korean developer post, 2026-06-17  
  https://kwoon.tistory.com/122

Tool concept:
- ComfyUI custom node;
- Danbooru prompt words grouped into files;
- thumbnail browser;
- click to append Prompt terms.

Product-relevant observation:
- another independent local tool converges on visual tag discovery rather than forcing users to remember tag strings;
- this is UX ecosystem evidence, not proof of optimal browse taxonomy.

### 10. Simplified Anima front-end / model metadata retrieval

Source:
- Korean community tool, 2026-06-24  
  https://gall.dcinside.com/mgallery/board/view/?id=wrtnai&no=1044018

Features described:
- simplified prompt-first local UI around ComfyUI;
- saved “style” presets;
- scans local LoRAs and retrieves thumbnail / trigger word / base-model information from Civitai.

Product-relevant observation:
- local users value resource discoverability and remembered metadata as much as raw generation settings;
- DanbooruTagTool's shared-LoRA quick-use direction is aligned with an independent community need.

### 11. Korean Anima-specific LoRA training pipeline project

Source:
- Korean community post, 2026-04-22  
  https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1129120

Linked project:
- `sorryhyun/anima_lora`

Public material discusses:
- Anima architecture/training;
- optimization;
- timestep concepts;
- LoRA-specific training pipeline.

Treatment:
- useful technical research lead;
- do not accept generated infographics or author explanations as upstream mechanism authority without source-code/paper confirmation.

### 12. Low-end / integrated-GPU Anima recipe

Source:
- Korean community post, 2026-05-15  
  https://gall.dcinside.com/mgallery/board/view/?id=thesingularity&no=1184244

Reported recipe:
- low base resolution;
- official Turbo;
- external 2× upscale;
- low-denoise img2img few-step refinement.

Treatment:
- valuable low-resource recipe lead;
- numeric speed/denoise values are hardware/workflow specific;
- reinforces staged low-resolution -> upscale -> light refinement as an ecosystem pattern, not a universal quality optimum.

### 13. Artist mixing custom-node practice

Source:
- Korean community developer patch, 2026-06-15  
  https://gall.dcinside.com/mgallery/board/view/?id=wrtnai&no=1037870

Author reports:
- Anima artist-tag mixing can be weak with multiple artists/LoRAs;
- custom cross-attention mixing node intentionally mixes styles more aggressively;
- warns stronger mixing can create other problems and has compatibility constraints.

Treatment:
- high-value tool/failure lead;
- no model-effect Claim until a reproducible benchmark exists;
- useful future test: tag-only multi-artist vs helper-node vs style LoRA under same seeds.

## Cross-language synthesis

Chinese/Korean community practice converges on several ecosystem needs:

1. **model-specific trainer selection**
   - Anima users increasingly use Anima-aware trainers instead of generic SDXL assumptions.

2. **dataset automation + human correction**
   - auto-tagging and extraction are common;
   - this does not eliminate the need for semantic QA.

3. **base-model metadata at resource-selection time**
   - LoRA users need to know base family, trigger and intended use before loading an adapter.

4. **assisted control is mainstream**
   - pose/depth/inpaint/regional are ordinary workflow stages, but must remain separate evidence lanes from Prompt-only generation.

5. **simplified visual front ends are independently recurring**
   - thumbnail tag browsers, preset galleries and LoRA metadata browsers repeatedly appear in community tools.

6. **cross-family LoRA reuse is opportunistic**
   - creators test it, but warn that strength/CFG and fidelity vary; retraining remains common.

## Promotion result

No new Claim promoted.
This batch is ecosystem/source-map evidence.

No production behavior changed.
