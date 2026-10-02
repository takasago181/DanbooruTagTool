# BATCH_AJ — LoRA capacity / reference conditioning / evaluation stack — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: official training docs + personalization/style research + current community evidence
Focus: character/style LoRA hyperparameters, reference baselines, automated evaluation

## 1. Rank is capacity, not quality

Official sd-scripts:
- https://github.com/kohya-ss/sd-scripts/blob/main/docs/train_network.md
- https://github.com/kohya-ss/sd-scripts/blob/main/docs/train_network_README-ja.md

Documented:
- `network_dim` = LoRA rank/dimension;
- larger rank increases expressive capacity;
- also increases file size/compute;
- values from low single digits to much larger ranks are possible depending on module/task;
- DyLoRA docs explicitly note that higher rank is not automatically better and lets one train/extract multiple ranks for comparison.

Project consequence:
Do not define:
`rank 64 > rank 32 > rank 16`.

Define:
`required capacity vs overfit/editability vs cost`.

For character/style training, rank must be evaluated jointly with:
- dataset size/diversity;
- learning rate;
- alpha;
- target modules;
- steps/noise distribution.

Promoted:
- K-LORA-006.

## 2. Alpha / dropout / block allocation are experiment identity

sd-scripts documents:
- `network_alpha` as a LoRA scaling parameter related to learning-rate/weight scaling;
- optional `network_dropout`;
- Conv2d LoRA ranks;
- block-wise rank/alpha for supported architectures.

Project rule:
Every LoRA experiment must record:
- rank/dim
- alpha
- target modules
- dropout
- learning rate
- text-encoder/LLM training state
- trainer implementation

A rank comparison with different alpha is not a clean rank comparison.

Promoted:
- K-LORA-007.

## 3. Current Anima community hyperparameter uncertainty

Source:
https://www.reddit.com/r/StableDiffusion/comments/1wpjl3p/advice_on_anima_character_lora_training_parameters/

Reported case:
- ~46 images
- rank 32 / alpha 16
- LR 1e-4
- character facial-detail drift

Community response suggests lower LR and explicitly says there is no universal LR; dataset/captioning may be responsible as well.

Treatment:
- no numeric LR recommendation accepted;
- useful evidence that “bad face => increase rank” is a weak diagnosis.

Promoted:
- K-COMM-ANIMA-022.

## 4. Anime-domain identity metric: CCIP

Source:
https://huggingface.co/deepghs/ccip

CCIP:
- Contrastive Anime Character Image Pre-Training;
- measures visual similarity of anime characters;
- current card is designed around single-character images;
- publishes same-character discrimination/clustering benchmarks.

Project use:
For generated character images:
- crop/detect the intended subject;
- compare against multiple clean references;
- aggregate reference distances;
- use as an automated identity signal.

Do not let CCIP override:
- clothing correctness;
- pose;
- expression;
- body features;
- style match;
- multi-character ownership.

Promoted:
- K-EVAL-012.

## 5. Why CLIP alone is not a style metric

CSD:
https://arxiv.org/abs/2404.01292

The research builds dedicated style descriptors because semantic image retrieval features conflate content/style.

Implementation caveat:
https://github.com/learn2phoenix/CSD
currently warns of a discrepancy involving uploaded model weights/reported paper numbers.

Project treatment:
- accept the conceptual result;
- do not silently rely on the current published CSD weight as a calibrated production metric until the repository issue is resolved/pinned.

DiffSim:
https://arxiv.org/abs/2412.14580

Reports:
- pixel/perceptual metrics miss mid-level semantics;
- CLIP/DINO compress appearance details;
- diffusion attention features can better track appearance/style similarity.

Promoted:
- K-EVAL-013.

## 6. Human-aligned personalization evaluation

DreamBench++:
https://arxiv.org/abs/2406.16855

Goal:
automate personalized-image evaluation while aligning better with human judgement via multimodal models.

Project consequence:
Character/Style Lab should eventually combine:
- domain identity metric
- style metric
- text/predicate checks
- human or MLLM pairwise judgement.

No single scalar should determine the final verdict.

Promoted:
- K-EVAL-014.

## 7. Stylization breaks normal face-identity metrics

StyleID:
https://arxiv.org/abs/2604.21689

Reports:
- photo-oriented identity encoders become brittle when style changes texture/color/geometry;
- human perception of “same person under stylization” requires calibration.

For anime:
- do not assume InsightFace/ArcFace-style photo embeddings are reliable identity ground truth;
- prefer anime-domain metric/reference review;
- use human judgement when strong stylization changes face geometry.

Promoted:
- K-EVAL-015.

## 8. Reference-image conditioning as a non-LoRA baseline

IP-Adapter:
https://github.com/tencent-ailab/IP-Adapter

Properties:
- lightweight image-prompt adapter;
- text + image conditioning;
- can work with custom models sharing the supported base architecture;
- supports control workflows.

AnimeAdapter:
https://arxiv.org/abs/2605.20237

Anime-specific design:
- single character reference;
- fine-grained appearance injection;
- pose-aware disentanglement;
- no per-character fine-tuning at deployment.

Project use:
When deciding whether to train a character LoRA, compare:
1. native checkpoint knowledge;
2. reference conditioning;
3. character LoRA;
4. reference + LoRA if compatible.

LoRA advantages:
- reusable trigger;
- no reference image required each generation;
- can encode identity details strongly.

Reference-adapter advantages:
- no per-character training;
- easier identity updates;
- potentially more flexible if pose/content separation is strong.

Promoted:
- K-CHAR-002.

## 9. Style reference methods expose the same leakage problem

InstantStyle:
https://arxiv.org/abs/2404.02733
https://github.com/instantX-research/InstantStyle

Core idea:
- subtract content features from image features;
- inject style features only into style-specific blocks;
- reduce content leakage.

InstantStyle-Plus:
https://arxiv.org/abs/2407.00788

Explicitly decomposes:
- style
- spatial structure
- semantic content.

Project consequence:
Whether style comes from:
- artist tag
- style LoRA
- reference adapter
the evaluation problem is the same:
`style fidelity vs content/identity/layout preservation`.

Promoted:
- K-STYLE-002.

## 10. Proposed Character/Style Lab evaluator stack

### Character identity
Primary:
- human reference review
- CCIP distance for anime single-subject images

Secondary:
- CLIP/DINO appearance similarity
- MLLM identity-feature questions

### Style
Primary research candidates:
- human pairwise style comparison
- CSD-style descriptor
- DiffSim-style appearance/style similarity

Secondary:
- artist/style classifier
- palette/line/texture statistics

### Editability
Predicate matrix:
- pose changed?
- background changed?
- outfit changed?
- camera changed?
- expression changed?
- identity preserved?
- style remained/changed as requested?

### Combined character + style
Need four outputs, not one score:
- identity fidelity
- style fidelity
- prompt/content adherence
- editability/composition freedom

## 11. Hyperparameter experiment design

For one fixed character dataset:

### Rank sweep
Keep fixed:
- alpha ratio or exact alpha policy
- LR
- steps
- captions
- target modules

Compare e.g. several capacities rather than assuming high rank.

### Alpha sweep
Hold rank fixed.

### LR sweep
Hold rank/alpha fixed.

### Dropout
Only after a stable baseline exists.

### Module/block experiments
Use only if ordinary training reveals:
- style contamination;
- editability loss;
- native artist-tag suppression.

Avoid changing rank/LR/captions/modules simultaneously.

## 12. Dataset evaluation split

Training-set-like validation is insufficient.

Create:
- ID split: similar to training distribution;
- OOD-pose;
- OOD-background;
- OOD-outfit;
- OOD-camera;
- OOD-style;
- combination stress.

For style:
- seen-like content;
- unseen characters;
- scenery;
- non-character objects;
- different composition.

This becomes the standard evaluation grid.

## Promotion result

New ACCEPTED:
- K-LORA-006
- K-LORA-007
- K-EVAL-012
- K-EVAL-013
- K-EVAL-014
- K-EVAL-015
- K-STYLE-002
- K-CHAR-002

New CANDIDATE:
- K-COMM-ANIMA-022
