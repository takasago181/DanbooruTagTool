# BATCH_AK — Personalization disentanglement and dataset design — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: personalization research synthesis
Scope: 2D character LoRA, style LoRA, dataset design, overfitting, multi-concept training

## 1. Identity vs context entanglement

DisenBooth:
https://arxiv.org/abs/2305.03374

Problem statement:
subject-driven tuning often entangles:
- identity-relevant information
with
- identity-irrelevant pose/background/context.

Failure modes:
- learned context dominates later prompts;
- target identity itself becomes unstable when context changes.

Project translation for anime character LoRA:
If the dataset always contains:
- one outfit
- one background
- one camera
- one pose family
- one source style

then those dimensions cannot be assumed to remain independently editable.

Promoted:
- K-CHAR-002.

## 2. Two kinds of overfitting

Infusion:
https://arxiv.org/abs/2404.14007

Separates:
### concept-agnostic overfitting
Fine-tuning damages non-customized/base-model knowledge.

### concept-specific overfitting
The learned subject becomes confined to limited modalities:
- background
- layout
- style
- other training conditions.

This maps directly to current project failures:
- native artist tags stop working;
- background becomes sticky;
- clothing becomes immutable;
- character only looks right in one camera/pose.

Promoted:
- K-LORA-009.

## 3. Dataset design as editable-factor design

For every dataset attribute classify:

### Identity-intrinsic
Wanted even when prompt is minimal:
- core face
- hair identity
- stable body/marking features
- canonical defining accessory if truly intrinsic

### Switchable
Must vary in data and/or be explicitly captioned:
- outfit
- expression
- pose
- camera
- background
- lighting
- style

### Optional context
Should not silently remain constant:
- props
- weather
- framing
- recurring location
- source-specific visual artifact

This is a design model, not an automatic tagging recipe.

## 4. Training-set diversity is necessary but evaluate effective diversity

Do not count only “number of images”.

Track:
- identity-visible crops
- head/full-body balance
- front/profile/back coverage
- pose diversity
- outfit diversity
- background diversity
- rendering-style diversity
- camera distance
- expression
- occlusion
- duplicate/near-duplicate rate

A 100-image dataset can have lower effective diversity than 30 deliberately varied images.

## 5. Concept-agnostic leakage tests

LyCORIS evaluation work:
https://arxiv.org/abs/2309.14859

Use prompts that deliberately omit the trigger to test:
- did the learned face/style appear anyway?
- did unrelated base outputs drift toward the training palette/background?
- did base-model artist/style behavior change?

Infusion independently motivates checking preservation of non-customized knowledge.

Promoted:
- K-EVAL-015.

## 6. Generalization/alteration tests

Target-trigger prompts should deliberately alter:
- background
- outfit
- pose
- camera
- style
- scene category.

A character adapter that only succeeds on training-like prompts has high fidelity but low controllability/generalization.

## 7. Multi-concept customization

Custom Diffusion:
https://arxiv.org/abs/2212.04488

Shows:
- efficient concept customization;
- joint multi-concept training;
- constrained combination of separately tuned concepts.

Break-A-Scene:
https://arxiv.org/abs/2305.16311

Uses:
- concept masks;
- masked diffusion loss;
- attention-map regularization;
- union sampling
to separate/combine multiple concepts from one image.

Project lesson:
multi-character learning needs explicit anti-entanglement strategy.

Promoted:
- K-LORA-010.

## 8. Masked dataset learning as a research option

When training images contain:
- character A
- character B
- recurring object
- shared background

a caption alone may not fully specify which pixels belong to which learned concept.

Break-A-Scene suggests masks/attention supervision are principled alternatives for concept separation.

Project candidate:
- compare ordinary captions vs per-subject masks in a multi-character dataset.

Promoted as CANDIDATE:
- K-CHAR-003.

## 9. Character dataset audit table

For each image record:
- subject ID
- crop type
- pose
- camera
- outfit
- background
- expression
- style/source type
- occlusion
- other recurring concepts
- captioned mutable factors
- quality flag
- near-duplicate group

Then compute coverage rather than only image count.

## 10. Style dataset audit table

For each image record:
- subject/content category
- composition
- line-art character
- palette
- shading
- texture/material
- rendering medium
- recurring motif
- artist-specific content bias
- auto-tag false positives
- captions explaining non-style content

Goal:
maximize style consistency while varying content.

## 11. Dataset splits should include OOD validation

Keep a validation prompt/image plan that is not represented directly in training:
- unseen outfit
- unseen location
- unusual pose
- unusual object
- different art style for character adapter
- different subject category for style adapter.

Do not choose epochs using only training-domain outputs.

## 12. Multi-character source images

When source material frequently contains multiple characters:
- subject isolation/cropping can help;
- masks are a research-backed separation option;
- pair images can be retained intentionally when coexistence is a target;
- do not accidentally mix “identity training” and “coexistence training” without labels.

## Promotion result

New ACCEPTED:
- K-CHAR-002
- K-LORA-009
- K-EVAL-015
- K-LORA-010

New CANDIDATE:
- K-CHAR-003
