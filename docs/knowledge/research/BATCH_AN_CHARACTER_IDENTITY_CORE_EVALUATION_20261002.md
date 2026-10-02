# BATCH_AN — Character identity-core evaluation — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: evaluation design + current anime community evidence
Focus: true identity vs presentation shortcuts

## 1. Character likeness is multi-component

A character can appear “correct” because:
- default clothes are correct;
- hair color is correct;
- one signature accessory is present;
while the face/identity has drifted.

Therefore identity should be decomposed.

Possible identity anchors:
- face shape / proportions
- eye shape / iris design
- eyebrows / mouth/nose stylization
- hairline / bang structure / hair silhouette
- permanent markings
- ears/horns/tail or species features
- stable body morphology
- silhouette / proportions

Presentation variables:
- outfit
- removable accessories
- pose
- expression
- camera
- lighting
- background
- art style

Which item belongs to identity_core is character-specific.

Promoted:
- K-CHAR-004.

## 2. Shortcut learning

A LoRA can exploit correlations in its training set:
- same outfit;
- same background;
- same source style;
- same crop;
- same camera;
- same pose.

If the generated character only looks correct under these same cues, it has weak identity generalization.

Promoted:
- K-EVAL-018.

## 3. Identity knockout tests

Use controlled conditions:

I0 — normal default presentation
I1 — alternate plain outfit
I2 — remove signature removable accessory
I3 — unseen neutral background
I4 — different artist/style rendering
I5 — unseen camera/view
I6 — altered expression
I7 — full body vs face close-up

Score identity anchors separately.

A robust character adapter should preserve the identity anchors designated as immutable while allowing intended mutable axes to change.

## 4. AnimeAdapter motivation

Source:
https://arxiv.org/abs/2605.20237

AnimeAdapter explicitly aims to:
- inject fine-grained anime appearance from a reference;
- disentangle appearance from spatial layout using pose-aware conditioning.

This research motivation supports the project’s distinction:
`appearance identity != pose/layout`.

It does not establish AnimeAdapter as the best current production method.

## 5. CCIP is a signal, not an explanation

Source:
https://huggingface.co/deepghs/ccip

CCIP is useful for:
- same-character screening;
- clustering;
- comparing generated images against references.

But one distance score cannot tell:
- face drift vs hair drift;
- outfit shortcut;
- wrong permanent marking;
- style-only similarity.

Recommended:
- several clean references;
- multiple views;
- per-feature human/VLM checklist in parallel.

Promoted:
- K-EVAL-019.

## 6. Mutable factors need actual variation

Captioning a constant attribute helps conditioning, but it cannot provide the same evidence as actual variation.

If all training images use:
- one outfit,
- one background,
- one source rendering style,
then the LoRA can still correlate these strongly with identity.

Project dataset principle:
If a factor must be editable, include meaningful variation/counterexamples where possible.

Promoted:
- K-DATA-004.

## 7. Anima prompt-only custom-character drift

Source:
https://www.reddit.com/r/StableDiffusion/comments/1v7h6b2/anima_struggling_to_maintain_consistency_with/

User report:
- same prompt;
- hairstyle and facial-feature consistency remains weak;
- commenters suggest first simplifying/stabilizing character descriptors, then using LoRA if insufficient.

Treatment:
- useful workflow signal;
- does not prove every OC needs a LoRA.

Promoted:
- K-COMM-ANIMA-025.

## 8. Viewpoint-generalization counterexample

Source:
https://huggingface.co/circlestone-labs/Anima/discussions/119

Dataset reported:
- 46 images;
- frontal, 45°, 75°, 90° views;
- close-ups, sitting/full-body and other shots.

Failure:
identity remained strongest mainly in frontal ID-like views.

This is important because it falsifies the simplistic rule:
“include several angles and generalization is solved”.

Possible hidden causes:
- effective sampling imbalance;
- face close-up dominance;
- caption allocation;
- training dynamics;
- source-quality differences;
- model/trainer version.

Promoted:
- K-COMM-ANIMA-026.

## 9. Character evaluation scorecard

Do not report one “character score”.

### Core identity
- face geometry
- eye design
- hair structure
- permanent features
- stable morphology

### Presentation
- default outfit
- alternate outfit
- accessories
- hairstyle variants

### Editability
- pose
- expression
- background
- camera
- style

### Robustness
- seed variation
- viewpoint variation
- full-body vs portrait
- LoRA weight variation

## 10. Reference-set design

Reference set should contain:
- clean face views;
- 3/4/profile where available;
- upper/full body;
- canonical permanent features;
- more than one outfit/background when identity-only is the target.

Do not let the automated evaluator use only the same image that generated synthetic training data.

## 11. Product metadata implication

DanbooruTagTool can eventually attach:
- identity_core features
- mutable presentation features
- default outfit dependency
- known shortcut risks
- CCIP/reference-set identity score
- OOD identity score
to a character LoRA.

This would distinguish “high likeness” from “high likeness only in default costume”.

## Promotion result

New ACCEPTED:
- K-CHAR-004
- K-EVAL-018
- K-EVAL-019
- K-DATA-004

New CANDIDATE:
- K-COMM-ANIMA-025
- K-COMM-ANIMA-026
