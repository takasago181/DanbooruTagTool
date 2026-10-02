# BATCH_Q — Illustrious / NoobAI / LoRA community map — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Branch: `knowledge/generation-corpus`  
Mode: broad public-user harvest with conservative promotion  
Scope: Illustrious / WAI / NoobAI EPS+V-Pred / LoRA training / regional prompting / parameter sweeps

## Purpose

The Anima ecosystem currently has more high-quality public controlled tests than NoobAI/Illustrious. This batch therefore separates:
1. evidence strong enough for a scoped CANDIDATE Claim;
2. useful practical recipes;
3. unresolved failure reports;
4. low-confidence anecdotes.

The goal is not to force symmetry in Claim counts.

## A. Same-dataset WAI vs Anima LoRA retraining

Source:
- おじさんAIラボ / Zenn, 2026-07-22  
  https://zenn.dev/ojisan_ai_lab/articles/lora-wai-anima-howto-20260722

Reported environment:
- kohya sd-scripts main, commit 6565877
- Python 3.11.15
- PyTorch 2.11 + CUDA 12.8
- RTX 5090
- 64-image dataset ×10 repeats
- Danbooru-tag captions
- trigger: `labchan_char`
- WAI path: `sdxl_train_network.py`
- Anima path: `anima_train_network.py`

Dataset construction lesson:
- the author's earlier dataset had been generated in a narrow style, and that visual style became entangled with the character trigger;
- in the rebuilt dataset, style was varied and captioned separately from the character trigger;
- viewpoints, expressions, clothing and scene variation were intentionally widened;
- the same source dataset was then used to build both WAI and Anima variants.

Reported run identity:
- WAI: 2560 steps / 8 epochs
- Anima: 3200 steps / 10 epochs
- reported local throughput roughly ~1 s/step for WAI and ~1.7 s/step for Anima;
- reported VRAM roughly 12.8 GB vs 11 GB, but these values are environment-specific and not promoted.

Interpretation:
- supports a practical entanglement warning already seen across independent user reports;
- particularly useful because the author documents an earlier failure and a revised dataset;
- does not establish one universal caption-density rule.

Promoted:
- K-COMM-LORA-003.

## B. Illustrious XL V2.0 steps / CFG fixed-seed sweep

Source:
- NVIDIAじゃないGPUで画像生成している個人検証, 2026-04-07  
  public web article indexed during this batch.

Environment reported:
- Radeon RX 9060 XT
- Illustrious XL V2.0
- fixed seed
- step sweep: 28 / 30 / 35 / 40 / 45
- then CFG sweep: 3 / 4 / 5 / 6 / 7 at 30 steps

Author's subjective conclusion:
- 30–35 steps was preferred over tested lower/higher values;
- CFG 5–6 was preferred in that setup;
- excessive settings were not judged monotonically better.

Interpretation:
- useful local parameter evidence;
- checkpoint/hardware/runtime dependent;
- must not override WAI v17, NoobAI, or Anima author baselines;
- user aesthetic preference is part of the verdict.

Promoted:
- K-COMM-ILL-002.

## C. WAI v16 garment geometry / color ambiguity

Source:
- public user experiment, 2026-01-20, WAI Illustrious v16.

Reported:
- `cross-laced skirt` alone produced variable slit/lacing placement across generations;
- skin-adjacent garment colors sometimes made the intended skirt/body boundary ambiguous;
- extra structural wording was used to constrain location.

Treatment:
- retained as a narrow tag-behavior lead;
- not promoted because sample design and model identity are too narrow for a durable Claim.

## D. Forge Couple on WAI v17

Source:
- Japanese community workflow article using:
  - Forge Neo
  - WAI Illustrious v17
  - Forge Couple v7.0.7

Useful practical notes:
- region prompts were used to isolate clothing/character attributes;
- BREAK/chunk organization was used as a human-facing construction method;
- the article explicitly acknowledges that checkpoint composition understanding still matters.

Treatment:
- recipe/source-map only.
- official Forge Couple runtime documentation already has higher authority in K-TOOL-008 / K-TOOL-009.
- no duplicate Claim added.

## E. NoobAI V-Pred style/detail observations

Sources:
- several public same-prompt model-comparison posts;
- NoobAI V-Pred user LoRA discussions;
- Reddit training/failure threads.

Repeated observations:
- V-Pred is often praised for small clothing/accessory detail retention;
- style LoRAs can introduce tint/background/style coupling;
- count and relation behavior vary sharply by prompt surface and checkpoint;
- users frequently copy EPS settings into V-Pred and then diagnose rendering problems incorrectly.

Treatment:
- current official Noob V-Pred guidance already covers the only durable operational part;
- detail-retention praise is too subjective for promotion;
- tint/style coupling is already covered by the broader LoRA-entanglement Claims.

No new Noob Claim added.

## F. Cross-model same-seed comparisons

Sources include public tests comparing:
- WAI Illustrious
- NoobAI V-Pred
- Anima
- related derivatives

Typical design:
- same seed
- same or nearly same Prompt
- same nominal sampler/steps/CFG
- one/few images per checkpoint

Useful only for:
- discovering model-family style/trigger hypotheses;
- spotting gross interpretation differences.

Not valid for:
- declaring one model better;
- assuming the same seed implies equivalent latent/composition conditions across different checkpoints;
- exact reliability estimates.

Treatment:
- preserve in source map only.
- K-EVID-004 and model-family scoping already cover the durable methodological principle.

## G. Illustrious character-LoRA failure reports

Public Reddit reports harvested:
- ~25-image curated character datasets after larger failed sets;
- ~30–50 image single-character training;
- 200-image style-LoRA training;
- single-artist style datasets;
- Noob V-Pred style LoRA tint problems.

Recurring failure families:
- face/style drift across prompts;
- background/style baked into the trigger;
- clothing treated as immutable identity;
- high LoRA weight causing distortion;
- insufficient viewpoint/crop diversity;
- style and identity impossible to separate when the training set itself never varies them.

Treatment:
- strengthens K-COMM-LORA-001 and K-COMM-LORA-003;
- no additional duplicate Claim.

## H. Chinese-language community harvest

Sources:
- Bilibili Illustrious multi-style LoRA report  
  https://www.bilibili.com/opus/1181478497372078082
- Anima + Illustrious + LoRA workflow showcase  
  https://www.bilibili.com/video/BV1mk5f6UEaq/
- Illustrious detail/finishing workflow  
  https://www.bilibili.com/video/BV1HJXKBJEge/
- NoobAI prompt/explainer clips and derivative workflows indexed in this batch.

Recurring ecosystem practice:
- Illustrious LoRAs are often tried across derivatives and NoobAI;
- creators themselves commonly warn that strength/CFG needs adjustment and compatibility is not guaranteed;
- some Anima workflows retrain assets rather than assuming SDXL/Illustrious adapter portability;
- staged img2img/regional workflows are common when cross-family assets are involved.

Treatment:
- ecosystem evidence only.
- existing K-LORA-001 / K-LORA-002 already encode the durable compatibility boundary.

## I. Negative-Prompt community anecdotes

One recurring community pattern:
- long generic Negative stacks are copied between Illustrious/Noob/Pony recipes;
- same-seed anecdotal comparisons sometimes favor short or no Negative;
- many posts change UI/runtime/model at the same time and therefore cannot isolate cause.

Treatment:
- no new Claim.
- K-NEG-001 / K-NEG-003 plus K-COMM-NEG-001 are stronger and better scoped.

## J. What this batch says about evidence quality

The public NoobAI/Illustrious ecosystem has a high ratio of:
- recipes;
- showcases;
- merged-checkpoint comparisons;
- bundled workflow changes.

It has a lower ratio than current Anima community material of:
- explicit fixed-seed A/B;
- published image counts;
- one-variable changes;
- failure reruns after confounds are found.

Therefore absence of promotion is **not** absence of useful information. It means the information remains in research/source-map status until better evidence arrives.

## Promotion result

New CANDIDATE:
- K-COMM-LORA-003
- K-COMM-ILL-002

No HOLD closed.
No production behavior changed.
