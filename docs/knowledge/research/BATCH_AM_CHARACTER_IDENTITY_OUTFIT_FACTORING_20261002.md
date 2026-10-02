# BATCH_AM — Character identity / outfit / variant factoring — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: current Anima feedback + community LoRA training practice
Focus: identity-only vs default-outfit vs switchable multi-outfit character reproduction

## 1. “Character” is not one training target

A character adapter can target at least three different products:

### C1 — Identity-only
Trigger should primarily reproduce:
- face/identity;
- stable body/species traits;
- permanent character-specific features.

Desired:
- clothing, pose, background, camera and style remain highly editable.

### C2 — Identity + default outfit
Trigger should reproduce:
- identity;
- canonical/default outfit with minimal extra prompting.

Desired:
- alternate outfit still possible, but default recall is strong.

### C3 — Identity + switchable variants
Trigger + variant token should select:
- default outfit;
- alternate outfit(s);
- hairstyle variants;
- accessory sets;
- transformation/forms where relevant.

These are different objectives.
A dataset/training recipe optimized for C2 can look “bad” under C1 criteria because the clothing is intentionally bound.

Promoted:
- K-CHAR-003.

## 2. Anima native character vs default outfit

Current user feedback:
https://huggingface.co/circlestone-labs/Anima/discussions/206

The user reports:
- character tag alone or a short clothing prompt can fail to reproduce the official/default outfit consistently;
- fully describing the outfit improves recall;
- this creates long and cumbersome prompts.

This is feedback, not a family-wide benchmark.

Durable diagnostic:
test separately:
- identity-known?
- default outfit-known?
- compact outfit cue sufficient?
- detailed outfit decomposition required?

Promoted:
- K-COMM-ANIMA-024.

## 3. Caption allocation for mutable clothes

Community:
https://www.reddit.com/r/StableDiffusion/comments/1gkqi9f

Recurring practical rule:
- if clothing should remain changeable, caption/describe it during training;
- if recurring clothing is intentionally left uncaptioned, it is more likely to be absorbed into the trigger/concept.

This aligns with the project’s existing caption-allocation model:
`captioned factor = independently conditionable candidate`
vs
`consistent uncaptioned residual = trigger-absorption risk`.

Important:
This is not guaranteed behavior for every architecture/trainer.
Dataset correlations still dominate.

Promoted:
- K-COMM-LORA-017.

## 4. Multi-outfit tokens inside one LoRA

Recent community discussion:
https://www.reddit.com/r/StableDiffusion/comments/1vgrr7b

Proposed design:
- one character trigger in all relevant images;
- an outfit-specific trigger only on images of that outfit;
- vary pose/background/expression;
- avoid one outfit dominating effective sampling.

Older discussion:
https://www.reddit.com/r/StableDiffusion/comments/156s203

Also emphasizes balancing outfit examples so one variant does not dominate.

Project treatment:
- the multi-concept design is plausible and common;
- exact “15–25 images” and exact balance ratios are NOT accepted;
- controlled same-dataset testing is needed.

Promoted:
- K-COMM-LORA-018.

## 5. Outfit LoRA as a separate adapter

Community:
https://www.reddit.com/r/StableDiffusion/comments/1qkrofm/train_clothes_and_cosplay_outfit_loras/

Users warn:
- independent clothing/cosplay LoRA can change character face/identity;
- plain prompting can work when exact outfit consistency is not required;
- a reference-editing workflow can transfer a specific outfit without making a permanent adapter;
- a multi-concept LoRA can train identity + outfit relationships together.

Project conclusion:
Outfit LoRA is not a free modular layer.
Test:
- character LoRA alone;
- outfit LoRA alone on neutral identity;
- character + outfit;
- reference-edit alternative.

Promoted:
- K-LORA-008.

## 6. Character feature taxonomy

Dataset/LoRA schema should distinguish:

### identity_core
- face/eye geometry
- stable hair structure/color where canonical
- permanent markings
- species/ears/horns/tail if identity-defining
- stable body morphology where truly canonical

### default_presentation
- default outfit
- default hairstyle if it changes canonically
- signature accessories that are removable

### variant
- alternate outfits
- alternate hairstyles
- seasonal/collaboration costume
- equipment/accessory variants
- transformations/forms

### independent scene factors
- expression
- pose
- camera
- background
- lighting
- art style

Promoted:
- K-DATA-003.

## 7. Evaluation matrix

Character LoRA must not get one score.

### Identity
- face
- hair/core silhouette
- permanent markings/features

### Default outfit
- recall with trigger only
- recall with compact outfit cue
- recall with full outfit prompt

### Variant controllability
- default -> alternate outfit
- alternate -> default
- remove signature accessory
- change hairstyle if intended mutable

### Generalization
- unseen pose
- unseen camera
- unseen background
- unseen style

Promoted:
- K-EVAL-017.

## 8. Failure labels

Add:
- `IDENTITY_GOOD_DEFAULT_OUTFIT_WEAK`
- `DEFAULT_OUTFIT_OVERBOUND`
- `OUTFIT_TOKEN_WEAK`
- `OUTFIT_VARIANT_BLEED`
- `HAIRSTYLE_OVERBOUND`
- `ACCESSORY_OVERBOUND`
- `OUTFIT_LORA_IDENTITY_DRIFT`
- `CHARACTER_LORA_BLOCKS_OUTFIT_CHANGE`

These are more actionable than “LoRA bad”.

## 9. Training experiment

Same character source pool:

D1 — identity-only target
- caption all clothing/outfit features.

D2 — identity+default outfit
- deliberately bind selected default outfit.

D3 — multi-outfit
- identity trigger + outfit-specific tokens.

Keep:
- rank/alpha/LR/trainer;
- effective total sampling;
- validation seeds
as controlled as possible.

Evaluation:
- identity fidelity
- default outfit recall
- variant token accuracy
- alternate clothing freedom
- native artist/style responsiveness
- cross-outfit bleed.

## 10. Product implications

Future DanbooruTagTool LoRA metadata should store:
- adapter target: character/style/outfit/concept
- character identity trigger
- default outfit implicit? yes/no/partial
- outfit variant triggers
- hairstyle/accessory variants
- known overbound features
- known mutable features
- compatible base
- recommended tested weight range as evidence, not universal rule.

This allows the tool to tell the user:
“this character LoRA already bakes the default costume”
versus
“you must prompt the outfit separately”.

## Promotion result

New ACCEPTED:
- K-CHAR-003
- K-DATA-003
- K-EVAL-017

New CANDIDATE:
- K-COMM-LORA-017
- K-COMM-LORA-018
- K-COMM-ANIMA-024
- K-LORA-008
