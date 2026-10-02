# BATCH_R — Advanced community failure diagnostics — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Branch: `knowledge/generation-corpus`  
Mode: advanced public-user experiment harvest  
Scope: multi-character LoRA binding, regional conditioning, Anima LoRA training parameters, upscale/detailer practice

## 1. WAI-Anima: separate LoRA contamination from character binding

Source:
- クロ, 2026-06-13  
  https://note.com/kla_cla/n/n801437941d2e

Verification environment reported:
- ComfyUI
- WAI-ANIMA v1.0
- RTX 3090
- two custom character LoRAs

Experiment sequence:
1. both LoRAs around 0.65 in a two-character action scene;
2. one character collapsed more strongly;
3. weights changed asymmetrically to 0.85 / 0.55;
4. stronger character improved, but its blonde hair leaked into the other character in 3/4 images;
5. prompt audit found:
   - weighted blonde-hair instruction plus another hair descriptor;
   - multiple near-synonyms for the same fighting action;
   - conflicting framing (`half body` + `cowboy shot`);
6. after removing the redundant/weighted hair pressure, hair-color leakage disappeared in the shown rerun;
7. left/right outfit assignment still swapped in 3/4 images;
8. restoring style-token groups restored the intended 2.5D texture without fixing the remaining outfit swap.

Practical diagnostic value:
- do not treat all “character blending” as one failure;
- one axis is global prompt/LoRA contamination;
- another axis is actor↔attribute binding;
- raising one LoRA can improve that identity while worsening cross-character leakage;
- deleting every apparently redundant style token can fix binding pressure while destroying target style;
- diagnose by changing one pressure source at a time.

The author's architectural explanation about a 0.6B text encoder “attention budget” is useful as a hypothesis but is not promoted as a proven causal mechanism.

Promoted:
- K-COMM-ANIMA-010.

## 2. Per-character reconstruction as a rescue workflow

Same source reports a staged workflow:
- first obtain acceptable global composition;
- mask one character;
- inpaint that region with only that character's LoRA/prompt;
- repeat for the other character;
- finish faces separately.

A narrow denoise window was reported for that exact workflow.

Treatment:
- retained as a C3 recipe only;
- numeric denoise values are not promoted;
- success after per-character inpaint is assisted/postprocess capability, not plain-checkpoint binding.

This reinforces K-TOOL-001 and K-TOOL-004.

## 3. Anima Regional Conditioning user practice

Source:
- HKMC_AILab, 2026-05-30  
  https://note.com/hkmclab/n/n1526e44f4df9

User workflow:
- separate character A / character B / common / background conditioning;
- explicit masks for target areas;
- article reproduces the node project's recommended patch parameters;
- author reports a practical tradeoff: higher CFG made region boundaries more visible, while lower CFG weakened prompt following in that setup.

Treatment:
- useful recipe/failure lead;
- no Claim promotion from the CFG observation because sample breadth is insufficient;
- current Regional Prompter official runtime documentation remains higher authority for Forge Neo support.

## 4. Anima multi-character natural-language tests

Sources:
- Nora, 2026-06-25 and 2026-09-08  
  https://note.com/stray_dog0012/n/n6576baad72c1
  https://note.com/stray_dog0012/n/n74ad8ac4582f
- HKMC_AILab, 2026-06-06  
  https://note.com/hkmclab/n/n7611426be16a
- ゆりしー, 2026-05-29  
  https://note.com/ulyssesx00/n/n8f6a2c961e7c

Repeated practical pattern:
- subject-specific prose can improve ownership without a regional extension;
- identity/core appearance tends to survive better than local accessories;
- 3-person consistency is possible in user examples but degrades as scene/action complexity rises;
- natural-language success is not equivalent to guaranteed left/right binding.

Treatment:
- already represented by K-COMM-ANIMA-001..004; no duplicate Claim.

## 5. Anima LoRA timestep parameters — high-priority research lead

Source:
- 久遠ノイズ, 2026-08-11  
  https://note.com/kuon_noise/n/na40804c255b5

Public article explicitly focuses on:
- `timestep_sampling`
- `sigmoid_scale`
- `discrete_flow_shift`
- extreme-setting experiments;
- an earlier unofficial-GUI configuration mistake.

Treatment:
- HIGH-PRIORITY lead.
- Not promoted because this batch could not recover enough complete experimental detail to state the direction/magnitude safely.
- Next controlled work should confirm trainer implementation semantics first, then test the same dataset with one timestep-distribution parameter varied at a time.

## 6. Style-LoRA tagging discussion — latest community snapshot

Sources:
- Reddit, 2026-09-25  
  https://www.reddit.com/r/StableDiffusion/comments/1wq972q/training_a_style_lora_for_anima_a_few_tagging/
- Reddit, 2026-05-15  
  https://www.reddit.com/r/StableDiffusion/comments/1tdobjq/anima_loras_cant_learn_the_characters_style_no/
- Reddit, 2026-04-29  
  https://www.reddit.com/r/StableDiffusion/comments/1sz8y14/anima_lora_training_config_recommendations/

Current disagreement remains:
- some users omit character tags for style LoRA;
- others retain image-true tags;
- dropout users commonly keep the style trigger;
- small-dataset users report that recipes from 200+ image datasets do not transfer cleanly;
- several users report Anima learning identity/outfit more easily than exact source style in their setups.

Treatment:
- no new Claim; K-COMM-LORA-002 already correctly records that caption strategy is unsettled.

## 7. Upscale / USDU / img2img latest practical reports

Sources:
- Reddit, 2026-06-03  
  https://www.reddit.com/r/StableDiffusion/comments/1tvhmrm/what_are_your_experiences_in_upscaling_anima_with/
- Reddit, 2026-05-24  
  https://www.reddit.com/r/StableDiffusion/comments/1tmrh0l/the_not_so_anime_anima/
- Reddit, 2026-05-09  
  https://www.reddit.com/r/StableDiffusion/comments/1t87xbc/anima_settings_in_forge_neo/

Repeated reports:
- Anima can react strongly to second-pass denoise;
- users often lower denoise substantially compared with their SDXL habits;
- sampler choice can alter smudging/smoothness in img2img;
- style-mismatched upscalers can add artifacts;
- some users prefer img2img over classic Hires Fix for Anima.

Treatment:
- strengthens K-COMM-ANIMA-006 only.
- exact denoise/scale thresholds remain recipe-level.

## 8. Detailer behavior

Source:
- Reddit, 2026-05-20  
  https://www.reddit.com/r/StableDiffusion/comments/1tj1fw2/detailing_in_anima_is_really_confusing_any_guides/

Reported:
- large detailer masks sometimes became noisy rather than refined;
- small facial features worked better in that setup;
- sampler/scheduler changes strongly altered detailer outcome.

Treatment:
- single-user unresolved troubleshooting report;
- source-map only;
- useful future test axis: mask size × sampler × denoise under pinned Anima profile.

## 9. Automated LoRA dataset extraction/tagging

Source:
- Reddit, 2026-05-01  
  https://www.reddit.com/r/StableDiffusion/comments/1t0yirq/built_a_3step_allinone_lora_builder_for_anima/

Public tool workflow:
- shot splitting;
- YOLO + CCIP subject filtering;
- near-duplicate removal;
- WD14 tag + natural-language caption generation;
- manual tag/pill editing;
- Anima-specific trainer.

Research value:
- demonstrates the current community trend toward semi-automated dataset curation;
- does not establish that auto-caption output is sufficiently accurate without review;
- reinforces keeping auto-tagging and human QA as separate stages.

No Claim promoted.

## Promotion result

New CANDIDATE:
- K-COMM-ANIMA-010

No HOLD closed.
No product/runtime default changed.
