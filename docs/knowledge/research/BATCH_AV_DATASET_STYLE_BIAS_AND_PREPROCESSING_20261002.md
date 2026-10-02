# BATCH_AV — Dataset style bias and preprocessing — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Scope: Anima character/style LoRA dataset preparation and teacher diagnostics

## 1. A training problem may actually be a dataset problem

Source:
https://huggingface.co/circlestone-labs/Anima/discussions/187

Case:
- target character source material is strongly 3D/game-render styled;
- trained LoRA reproduces identity together with unwanted 3D rendering style.

Community suggestions include:
- module/layer exclusions;
- lower learning rates for style-sensitive modules;
- explicitly tagging the 3D style;
- converting source images toward 2D anime style before training.

The most durable lesson:
**if every image carries the same nuisance style, the trainer has little evidence that style is separable from identity.**

Promoted:
- K-COMM-LORA-021.

## 2. Dataset correction before parameter gymnastics

Project rule:

If the unwanted factor is nearly constant:
1. ask whether it can be diversified;
2. if not, label/caption it as mutable context;
3. if the target output domain differs strongly, consider preprocessing/domain conversion;
4. only then experiment with module exclusions/LR changes.

This aligns with identity-context disentanglement research.

Promoted:
- K-PRACTICAL-031.

## 3. Auto-taggers need manual nuisance audit

In the 3D-style case, the user reports the auto-tagger did not mark the recurring `3d` factor.

This illustrates a broader dataset risk.

Before training manually inspect:
- source style/medium;
- fixed background;
- UI/text/watermark;
- outfit;
- camera;
- pose family;
- props;
- color cast;
- rendering artifacts.

An auto-caption can be syntactically correct and still omit the factor most important for disentanglement.

Promoted:
- K-PRACTICAL-032.

## 4. Nuisance-factor constancy audit

For each mutable factor estimate:
- frequency;
- number of distinct states;
- correlation with target identity.

High-risk example:
- 95% same background
- 100% same rendering medium
- 100% same outfit
- 90% close-up framing

Then create a validation prompt trying to change that factor.

Promoted:
- K-EVAL-018.

## 5. Teacher diagnostic

When learner says:
“My LoRA always looks 3D / has the same room / same outfit / same camera.”

Do not immediately prescribe:
- more steps;
- higher rank;
- stronger weight;
- different sampler.

First inspect the dataset.

Ask:
- Was that factor present in nearly every image?
- Was it captioned?
- Did the auto-tagger omit it?
- Is there enough counterexample diversity?

## 6. Style removal versus identity preservation

Aggressive dataset transformation can also damage:
- facial identity;
- small accessories;
- silhouette;
- texture cues.

Therefore compare:
A. original dataset
B. caption-corrected dataset
C. partially transformed dataset

with the same evaluation suite.

Do not assume preprocessing is automatically superior.

## 7. Adult-generation relevance

For adult character/concept LoRAs, nuisance factors can include:
- one repeated pose family;
- one camera distance;
- one background;
- one interaction role;
- one partner identity;
- one rendering style.

If these remain constant, the LoRA may later:
- force the same role;
- resist alternate pose;
- leak partner traits;
- resist style change.

This is a dataset-design problem before it is a Prompt problem.

## Promotion result

New ACCEPTED:
- K-PRACTICAL-031
- K-PRACTICAL-032
- K-EVAL-018

New CANDIDATE:
- K-COMM-LORA-021
