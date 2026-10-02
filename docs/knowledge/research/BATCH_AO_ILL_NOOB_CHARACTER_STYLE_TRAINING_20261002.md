# BATCH_AO — Illustrious / NoobAI character and style LoRA behavior — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: current community troubleshooting + same-dataset comparison
Focus: how base-family choice changes identity/style/context learning

## 1. Base model changes what the adapter learns

Character/style LoRA behavior is not portable as an abstract recipe.

The same source data can produce different balances of:
- identity fidelity;
- source-style fidelity;
- default outfit recall;
- prompt editability;
- background/color leakage.

Therefore cross-model comparison should retrain from the same curated dataset rather than load one adapter everywhere and judge compatibility.

Promoted:
- K-EVAL-020.

## 2. Illustrious can absorb character and source style together

Community:
https://www.reddit.com/r/StableDiffusion/comments/1rsqv6y/lora_training_illustrious/

A practitioner states that when the training character comes from one distinctive visual style, the resulting Illustrious LoRA tends to capture both character and style; removing style while keeping character is the harder task.

Japanese failure report:
https://zenn.dev/ojisan_ai_lab/articles/post-20260411-ltes8r

The author describes a synthetic character dataset where the image generator's thick-line style became embedded in the character LoRA.

Project interpretation:
For identity-only Illustrious training, style diversity/source cleanup matters.
For identity+source-style training, the same entanglement may be intentional.

Promoted:
- K-COMM-ILL-004.

## 3. Better curation does not automatically solve face/style drift

Source:
https://www.reddit.com/r/StableDiffusion/comments/1r318hl/helpquestion_sdxl_lora_training_on_illustriousxl/

The user:
- replaced an initial 50-image dataset;
- curated 25 higher-quality images;
- deliberately included face / upper body / full body;
- pruned immutable character tags and kept mutable context tags.

Yet:
- character consistency improved;
- face/style still drifted significantly.

Project lesson:
Do not reduce troubleshooting to:
- “use fewer/better images”;
- “remove immutable tags”.

Also inspect:
- source-domain consistency;
- trainer/hyperparameters;
- module allocation;
- validation distribution;
- base checkpoint prior.

Promoted:
- K-COMM-ILL-005.

## 4. NoobAI V-Pred style-LoRA palette leakage

Source:
https://www.reddit.com/r/StableDiffusion/comments/1vbsj8k/what_am_i_doing_wrong_in_my_lora_training/

Reported setup:
- NoobAI XL V-Pred 1.0-family base;
- 21 style images;
- persistent brown tint/filter in inference;
- target style otherwise recognizable.

Only a small part of the dataset visibly contained brown background/skin-adjacent tones.

The cause is unresolved.

Project evaluation consequence:
Style fidelity must include:
- global hue shift;
- saturation shift;
- contrast;
- unwanted palette prior
as separate failure axes.

Promoted:
- K-COMM-NOOB-003.

## 5. Anima versus Illustrious style capture

Source:
https://www.reddit.com/r/StableDiffusion/comments/1tdobjq/anima_loras_cant_learn_the_characters_style_no/

One practitioner reports:
- Anima character/outfit learning was very strong;
- source style remained more generic;
- the same source material trained on Illustrious reproduced style better in their workflow.

Same-dataset WAI/Anima retraining documentation:
https://zenn.dev/ojisan_ai_lab/articles/lora-wai-anima-howto-20260722

Project interpretation:
This is evidence for a cross-base difference worth formal testing.
It is NOT evidence that one base is universally better.

Promoted:
- K-COMM-ANIMA-027.

## 6. Cross-base benchmark design

Use one cleaned source dataset.

Train independently:
- WAI/Illustrious-compatible LoRA;
- Anima Base LoRA;
- NoobAI-compatible LoRA if trainer/prediction path is validated.

Keep as much as architecture permits:
- source images;
- captions;
- validation prompts;
- target concept definition.

Do not force identical hyperparameters across architectures if author guidance differs.

Score:
- identity;
- style;
- editability;
- palette drift;
- context leakage;
- default outfit;
- OOD pose/camera/background.

## 7. Style LoRA failure taxonomy additions

Add:
- `PALETTE_LEAK`
- `GLOBAL_TINT`
- `SOURCE_STYLE_OVERBOUND`
- `STYLE_UNDERLEARNED_IDENTITY_GOOD`
- `STYLE_GOOD_IDENTITY_DRIFT`
- `BASE_PRIOR_DOMINATES_STYLE`

## 8. Character LoRA base-selection question

Base choice should consider intended target:

### Need native anime character/style knowledge
Anima / Noob / Illustrious families may already contain useful identities/artists.

### Need identity-only adapter
Prefer the base/training recipe that preserves:
- face identity;
- prompt editability;
- style mutability.

### Need character + exact source art style
A base that readily absorbs both can be useful rather than a defect.

Base selection is therefore objective-specific.

## Promotion result

New ACCEPTED:
- K-EVAL-020

New CANDIDATE:
- K-COMM-ILL-004
- K-COMM-ILL-005
- K-COMM-NOOB-003
- K-COMM-ANIMA-027
