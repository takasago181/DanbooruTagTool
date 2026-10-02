# BATCH_AK — Character/style dataset curation — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: author guidance + dataset-tool documentation + recent community practice
Focus: anime character LoRA data collection, crop/pose coverage, caption variants, identity filtering, source-domain control

## 1. Anima does not have one canonical training-caption surface

Author discussion:
https://huggingface.co/circlestone-labs/Anima/discussions/9

The author states every base-training image has multiple caption variants:
- full tag list;
- tag list with dropout;
- tags then natural-language caption;
- natural-language caption then tags;
- short caption;
- long caption.

This matters because community discussions often ask whether Anima LoRA must use only Danbooru tags or only natural language.

Project conclusion:
- no single caption format is required by family alignment;
- caption strategy should instead reflect what should remain trigger-implicit versus independently controllable.

Promoted:
- K-MODEL-ANIMA-017.

## 2. Dataset curation is a pipeline, not “put images in a folder”

waifuc:
https://github.com/deepghs/waifuc

Its character-dataset example includes:
- class/media filtering;
- duplicate filtering;
- face-count filtering;
- person splitting;
- second face-count filter after crop;
- CCIP character-identity filtering;
- resize/alignment;
- auto-tagging;
- duplicate filtering again.

Project implication:
Dataset preparation can be staged and audited.

Recommended evidence artifacts:
- original source manifest;
- duplicate-removal count;
- rejected-identity count;
- per-image crop type;
- tag/caption file;
- final train/validation split.

Promoted:
- K-TOOL-027.

## 3. Character identity filtering

CCIP and anime person/face tools can be used to detect accidental wrong-character images before training.

This is especially valuable when data is collected from:
- large Booru searches;
- screenshots;
- mixed fanart galleries;
- synthetic expansion.

Human review remains necessary for:
- alternate forms;
- similar-looking characters;
- unusual costumes;
- extreme crops.

## 4. Crop/framing is learned data

Community evidence:
- https://note.com/imbolc_02/n/na8d6a1213783
- https://huggingface.co/circlestone-labs/Anima/discussions/140

Reported practical issue:
- LoRAs trained on close-up-biased images can pull generation toward closer framing;
- one user retrained after adding 14 genuine full-body images and paying attention to the visible subject size and margins above/below the body;
- full-body prompt adherence improved in that setup.

Project conclusion:
Dataset metadata should include:
- face close-up;
- portrait;
- upper body;
- cowboy/medium;
- full body;
- body occupancy ratio;
- top/bottom margins where useful.

Do not reduce dataset coverage to a single boolean `full_body=true`.

Promoted:
- K-COMM-LORA-015.

## 5. Structured character dataset coverage

Sources:
- https://note.com/seal309midorin/n/nab2b785e4d13
- https://www.reddit.com/r/StableDiffusion/comments/1q4h3mp/character_lora_training_dataset_howto/
- https://huggingface.co/circlestone-labs/Anima/discussions/119

Examples use deliberate coverage of:
- front / 3/4 / profile / back;
- face / upper body / full body;
- expressions;
- different poses;
- backgrounds;
- outfits.

But Anima discussion #119 is a useful counterexample:
a 46-image dataset with explicit angle diversity still generalized poorly outside frontal identity views.

Therefore:
`coverage labels != guaranteed learned generalization`.

Promoted:
- K-COMM-LORA-016.

## 6. Identity-defining vs mutable attributes

For each dataset property classify:

### Intended identity
Examples:
- stable face geometry
- canonical hair structure/color when truly fixed
- permanent markings/accessories
- species/character-specific anatomy

### Intended mutable
Examples:
- outfit
- pose
- expression
- camera
- lighting
- background
- temporary accessory
- alternate hairstyle if desired

Dataset rule:
If a property is supposed to vary at inference, variation and/or accurate conditioning should exist in training.

Do not assume the model will infer mutability from conflicting unlabeled examples.

Promoted:
- K-DATA-001.

## 7. Background/context entanglement

Existing evidence:
- Anima discussion #162
- prior K-COMM-LORA-011

Recurring failure:
white/plain background remains after training.

Relevant causes:
- background constant across dataset;
- background omitted from captions;
- crop/source processing introduced a repeated blank context.

Dataset audit:
- background distribution;
- caption accuracy;
- blank-background ratio;
- correlation between outfit and background.

## 8. Source-domain contamination

The dataset source itself should be stored as metadata.

Domains:
- official anime frame;
- manga/monochrome art;
- official illustration;
- fanart;
- 3D/game render;
- synthetic diffusion output;
- VLM/edit-model generated dataset;
- mixed.

Why:
- 3D character sources can preserve 3D rendering prior;
- synthetic images can propagate generator artifacts;
- generated character sheets can share one edit model's texture/skin/line artifacts;
- anime screenshots can strongly bind animation-line/color priors.

Promoted:
- K-DATA-002.

## 9. Synthetic expansion rule

Synthetic expansion is not inherently bad.

Use it when:
- source identity is scarce;
- needed pose/outfit/viewpoint is missing.

But record:
- generator/editor model;
- original reference;
- edit prompt;
- human acceptance/rejection;
- artifact/source-style score.

Never let generated expansion silently become “ground-truth reference”.

## 10. Captioning strategy

For character LoRA:
- caption intended mutable attributes consistently;
- avoid false auto-tags;
- decide explicitly whether canonical outfit/hair/feature should be trigger-default or separately controllable;
- backgrounds should not be left silently constant if background freedom matters.

For style LoRA:
- caption visible content/subjects to stop them being absorbed as style;
- preserve a style trigger when using dropout where needed;
- do not assume every artist/image tag is useful.

Anima-specific:
multiple caption styles are family-native, so a mixed evaluation is justified.

## 11. Deduplication and near-duplicate pressure

Repeated/near-identical images disproportionately amplify:
- one pose;
- one camera;
- one expression;
- one background.

Therefore dataset reports should record duplicate-removal policy.

waifuc's reference pipeline filters similarity before and after subject extraction, which is a good operational example.

## 12. Character dataset coverage table

Recommended per-image fields:

- source_domain
- identity_verified
- crop_class
- body_occupancy
- view_angle
- pose_family
- expression
- outfit_id
- hairstyle_variant
- background_class
- lighting_class
- reference_quality
- synthetic/edit model if applicable
- duplicate_cluster
- train/validation split

This enables coverage analysis instead of image-count folklore.

## 13. Validation split

Validation should deliberately contain combinations absent from training:
- new pose;
- new background;
- new outfit;
- new camera;
- new expression;
- different style.

If all validation images resemble training images, it only measures memorization.

## 14. Style-LoRA dataset implication

Style data should maximize content diversity while preserving target style.

Track:
- subject identities;
- landscapes / objects / interiors;
- close-up vs full composition;
- palette range;
- line/painting variations within the artist/style;
- monochrome vs color if both exist.

A style adapter that only sees one character type may accidentally learn character/body priors as “style”.

## 15. High-value project experiment

Build one curated character dataset, then create controlled variants:

D0: raw
D1: deduplicated
D2: deduplicated + background/outfit captioning
D3: coverage-balanced
D4: coverage-balanced + source-domain cleanup

Keep trainer/hyperparameters fixed.

Evaluate:
- identity
- prompt editability
- full-body reliability
- background freedom
- outfit freedom
- artist/style responsiveness.

This directly measures the value of curation.

## Promotion result

New ACCEPTED:
- K-MODEL-ANIMA-017
- K-TOOL-027
- K-DATA-001
- K-DATA-002

New CANDIDATE:
- K-COMM-LORA-015
- K-COMM-LORA-016
