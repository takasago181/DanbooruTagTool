# BATCH_X — Parameter / high-resolution / iterative-dataset community evidence — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: large controlled public-user experiment harvest
Focus: Anima inference parameters, Highres helper LoRA, iterative LoRA dataset repair

## 1. Anima Aesthetic v1.1 parameter sweep — 162 images

Source:
- mono. works, 2026-09-02  
  https://note.com/tasty_cougar8018/n/n7315197114a6

Baseline:
- Anima Aesthetic v1.1
- Anima Base v1.0 text encoder
- qwen_image_vae
- er_sde / simple
- CFG4
- 30 steps
- ModelSamplingAuraFlow shift 3.0
- no upscale

Design:
- two fixed source scenes/prompts/seeds;
- one parameter changed at a time;
- CFG: 1–12 over 15 levels;
- steps: 4–60 over 13 levels;
- shift sweep;
- sampler comparison;
- 162 total images.

Reported CFG behavior:
- low values produced paler/yellower and softer output;
- below ~2 was judged visibly weak in those scenes;
- higher values sharpened outlines;
- above ~10, background structure changed more strongly in the landscape scene;
- no single “higher is always better” pattern.

Reported steps:
- 4: underdeveloped/sketch-like;
- 6–12: rapid detail formation;
- ~16: broadly near-complete in shown examples;
- higher values mainly changed smaller background/detail aspects;
- measured time rose almost proportionally:
  - 4: 6.0 s
  - 8: 10.2 s
  - 16: 20.0 s
  - 30: 36.3 s
  - 44: 52.3 s
  - 60: 70.3 s
  in the author's environment.

Reported shift:
- 0.5 looked more distinct;
- most other tested values changed color/cloud detail more than global layout in those two scenes.

Treatment:
- profile/scene/hardware-local;
- useful response curve, not a replacement for author-recommended ranges;
- reinforces diminishing-returns reasoning for steps.

Promoted:
- K-COMM-ANIMA-016.

## 2. Iterative character-LoRA dataset repair — 49 -> 61 images

Source:
- 机の上のAI, 2026-09-11  
  https://note.com/ai_on_desk/n/nfed78c91d76a

Generation environment:
- WAI-Anima v1.0
- ComfyUI 0.34.0
- RTX 5060 8GB
- euler_ancestral / normal / 30 steps / CFG4.5.

Training:
- cloud Anima LoRA service;
- first dataset: 49 images;
- 1600 total steps;
- trigger token absorbs hair/eye identity;
- data consisted of original variations, expressions, side views, close-ups and edited scene variants.

First result:
- trigger alone recovered hair/eye/face identity;
- unseen scenes retained face;
- body type still followed base-model/seed tendency.

Second pass:
- first LoRA generated ~40 candidate images with target body descriptors;
- author manually curated them;
- replaced weaker mask-composite samples;
- rebuilt dataset to 61 images;
- second LoRA retained face and fixed target body type even without body tags in the shown tests.

Failure/contamination lesson:
- one incidental object from candidate data later appeared unexpectedly;
- manual candidate inspection remained necessary.

Interpretation:
- iterative dataset design can target a residual failure dimension after the first LoRA;
- “more images” is not the durable conclusion; **error-driven replacement and better coverage** is;
- self-generated data can recursively reinforce both desired and incidental correlations.

Promoted:
- K-COMM-LORA-008.

## 3. Anima Highres/Aesthetic Boost v1.0 — 279 images

Source:
- mono. works, 2026-09-26  
  https://note.com/tasty_cougar8018/n/nf4cff0c56535

LoRA:
- Anima Highres/Aesthetic Boost v1.0
- no trigger word.

Design:
- 9 strengths: 0 / 0.2 / 0.4 / 0.6 / 0.8 / 1.0 / 1.5 / 2.0 / 3.0;
- 3 seeds;
- 5 scene types;
- 3 resolution tiers;
- 279 total images.

Reported resolution behavior:
- at ~1.8MP / ~3.1MP, base generation could remain normal without the LoRA in the tested scenes;
- at ~4.9MP (1920×2560), strength 0 produced haze/desaturation and smaller/rougher characters in repeated tests;
- moderate LoRA application restored color/shadow and usable depiction in those high-resolution tests.

Reported strength behavior at normal-ish resolution:
- effect often modest and seed-dependent around 1.0;
- around 2.0 shadows became stronger;
- at 3.0, all three tested seeds showed blur/green shift and one body-shape failure, with large measured loss of local contrast/fine detail.

Interpretation:
- helper adapter benefit depends heavily on actual resolution and prompt/scene;
- an adapter intended for high-resolution rescue need not improve a normal-resolution baseline;
- excessive strength can reverse the intended benefit.

Promoted:
- K-COMM-LORA-009.

## 4. Parameter evidence hierarchy

For inference settings, preserve:
- exact profile/checkpoint;
- resolution;
- seed count;
- scene count;
- prompt class;
- sampler+scheduler;
- steps;
- CFG;
- shift/timestep configuration;
- hardware/runtime;
- subjective vs measured endpoints.

Do not turn one sweep's “preferred value” into a cross-profile default.

## Promotion result

New CANDIDATE:
- K-COMM-ANIMA-016
- K-COMM-LORA-008
- K-COMM-LORA-009

No author baseline or HOLD was overwritten.
