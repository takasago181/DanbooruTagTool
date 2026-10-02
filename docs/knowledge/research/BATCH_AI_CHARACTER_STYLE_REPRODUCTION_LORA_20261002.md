# BATCH_AI — Character / style reproduction and LoRA disentanglement — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: official docs + research papers + controlled/practical community evidence
Focus: 2D character fidelity, art-style fidelity, editability, LoRA training, subject/style fusion

## 1. Core decomposition

Two-dimensional reproduction should not use one generic “similarity” verdict.

### Character reproduction
Evaluate:
- identity fidelity
- editability/generalization
- clothing mutability
- pose/camera mutability
- style mutability
- background/context independence
- accessory/detail fidelity

### Style reproduction
Evaluate:
- line/shape language
- coloring/palette
- shading
- texture/brush/detail pattern
- face/eye/body stylization
- composition bias
- semantic-content preservation
- identity preservation

### Combined character + style
Evaluate both axes again after composition.

A character that looks perfect only in the training pose/style is not fully reproduced.
A style that matches reference images only by reproducing their subjects/compositions is not isolated style.

## 2. Why reconstruction-only evaluation is weak

Hugging Face DreamBooth documentation explicitly warns that personalization is hyperparameter-sensitive and easy to overfit.

Source:
https://huggingface.co/docs/diffusers/training/dreambooth

Community Anima layer-ablation testing:
https://note.com/studiomasakaki/n/nf39775327336

The latter found that freezing one of Self-Attention / Cross-Attention / MLP could still reproduce training-like character images surprisingly well.

Interpretation:
- in-distribution reconstruction can hide major differences in learned representation;
- evaluation needs prompts/images absent from the training dataset.

Minimum OOD matrix:
- unseen pose
- unseen background
- unseen outfit
- unseen camera distance
- unseen expression
- unseen style for character LoRA
- unseen subject/content for style LoRA

Promoted:
- K-EVAL-011.

## 3. Anima official training constraints

Official model card:
https://huggingface.co/circlestone-labs/Anima

Current author guidance:
- train LoRAs on Anima-Base;
- do not train the LLM adapter;
- low learning rate;
- rank-32 example starts around 2e-5;
- the base already contains a broad visual prior, so use a light touch.

Reason given:
- the LLM adapter processes text embeddings before diffusion;
- it contains significant knowledge and is easy to degrade.

This makes “preserve base knowledge/editability” a first-class Anima LoRA requirement.

## 4. Character LoRA = identity allocation problem

The adapter must decide which features become trigger-implicit and which stay prompt-controlled.

Training risks:
- fixed background becomes identity;
- fixed outfit becomes identity;
- repeated pose becomes identity;
- source rendering style becomes identity;
- 3D/game-render source style remains attached to a character intended for 2D output.

Community discussion:
https://huggingface.co/circlestone-labs/Anima/discussions/187

A user attempting a 3D-source character LoRA asked how to suppress the 3D look.
Responses disagree on layer exclusions but converge on an important issue:
**character information and style information are not perfectly separable in the trainable network**.

Practical mitigation hypotheses:
- caption/source-style state explicitly;
- diversify rendering style where possible;
- preprocess/convert training sources if the unwanted style dominates the dataset;
- test lower or module-specific learning rates rather than assuming one layer can simply be removed.

Do not promote exact exclude-pattern recipes without controlled replication.

## 5. Style LoRA = residual-style learning problem

Recent Reddit discussion:
https://www.reddit.com/r/StableDiffusion/comments/1wq972q/training_a_style_lora_for_anima_a_few_tagging/

Recurring practical idea:
- describe/tag visible non-style content;
- remove false auto-tags;
- avoid leaving repeated characters/backgrounds/objects unlabeled if the goal is style-only learning.

Interpretation:
If content is not explained by conditioning, the adapter has an incentive to absorb it into its learned residual.

This is only a community hypothesis, but it agrees with:
- style/content disentanglement research;
- earlier project context-entanglement evidence.

Promoted:
- K-COMM-STYLE-002.

## 6. Style-content separation research

B-LoRA:
https://arxiv.org/abs/2403.14572

Findings:
- style and content separation matters for stylization;
- adaptation location matters;
- selective SDXL blocks can improve independent style manipulation and reduce overfitting.

Project use:
This is evidence that “which layers are trained” is not merely a speed/memory knob.

Boundary:
- do not copy SDXL block prescriptions to Anima;
- use it as a conceptual foundation for module-specific Anima experiments.

Promoted:
- K-LORA-005.

## 7. Anima layer-ablation evidence

Sources:
- https://note.com/studiomasakaki/n/nf39775327336
- https://huggingface.co/circlestone-labs/Anima/discussions/187

Community observations:
- MLP changes strongly influence style but also character reproduction;
- Self-Attention/Cross-Attention changes affect flexibility/prompt response;
- freezing one module can still reproduce training-like samples.

Important lesson:
**style / identity / editability are distributed properties**, not cleanly assigned to one module.

The correct evaluation is OOD generalization, not “did this epoch reproduce the dataset?”.

Promoted:
- K-COMM-ANIMA-021.

## 8. LoRA can suppress Anima's native artist prior

Sources:
- https://huggingface.co/circlestone-labs/Anima/discussions/60
- https://huggingface.co/circlestone-labs/Anima/discussions/240

Reported failure:
- artist tags strong without LoRA;
- after loading character/style/concept LoRA, the same artist response weakens or disappears;
- trained LoRA can also become less responsive to body/appearance variation tags.

Treat as:
`BASE_KNOWLEDGE_SUPPRESSION / LORA_EDITABILITY_LOSS`

Diagnostic:
1. base + artist tag
2. LoRA + no artist
3. LoRA + artist
4. LoRA weight sweep
5. same prompt with intended mutable attributes changed

Do not misclassify as “artist tag unsupported”.

Promoted:
- K-COMM-ANIMA-020.

## 9. Style-LoRA inference weight is not one-dimensional

Controlled community sweep:
https://note.com/stray_dog0012/n/n6ebc324c1211

Same seed; weight 0.4 / 0.6 / 0.8 / 1.0 / 1.2.

Reported:
- stronger weight improved visual resemblance to the target style;
- at the stronger end, composition became more fixed and unwanted parts appeared.

Project metric:
Plot:
- style fidelity
- composition freedom
- prompt adherence
- identity preservation
versus weight.

Do not maximize style similarity alone.

Promoted:
- K-COMM-STYLE-003.

## 10. Character vs style training-noise distribution

Community experiment:
https://note.com/kuon_noise/n/n82be977f167d

Anima Base style-LoRA timestep tests showed a different useful region from the author's earlier character-LoRA experiment.

Durable conclusion:
- character and style LoRAs should not automatically inherit the same timestep/noise-distribution recipe;
- exact sweet spots remain dataset/trainer specific.

Promoted:
- K-COMM-STYLE-004.

## 11. Subject/character + style LoRA composition

Mix-of-Show:
https://arxiv.org/abs/2305.18292

The paper explicitly treats multiple customized LoRAs as a difficult multi-concept fusion problem with:
- concept conflict
- identity loss
- binding/missing-object issues.

Dynamic Subject/Style LoRA Fusion:
https://arxiv.org/abs/2602.15539

The paper argues static subject/style LoRA fusion is insufficient and proposes dynamic layer/timestep selection.

Project principle:
`character LoRA success + style LoRA success != combined success`.

Promoted:
- K-LORA-004.

## 12. A practical composition test

For one character C and one style S:

### Base
B0 = base, no LoRA
B1 = base + native artist/style prompt

### Character
C0 = character LoRA only
C1 = C0 with unseen pose/background/outfit
C2 = C0 with a different native artist/style prompt

### Style
S0 = style LoRA only, training-domain-like content
S1 = style LoRA with unseen character/content
S2 = style LoRA across multiple compositions

### Combined
CS0 = character + style
CS1 = weight sweep
CS2 = LoRA scheduling
CS3 = masked/regional when multiple characters are involved

Score:
- identity
- style
- prompt adherence
- pose/layout freedom
- outfit mutability
- background independence
- composition diversity
- unwanted learned-content leakage

## 13. Reference-conditioning alternatives

AnimeAdapter:
https://arxiv.org/abs/2605.20237

Proposes:
- single-reference anime appearance conditioning;
- pose-aware separation between appearance and spatial layout;
- no per-character fine-tuning at deployment.

Research implication:
LoRA should not be the only baseline for character reproduction.
Compare future workflows against:
- native checkpoint knowledge
- character LoRA
- reference adapter
- regional/reference + LoRA combinations

Promoted as research CANDIDATE:
- K-TOOL-026.

## 14. Current training-source hierarchy for Anima

Highest:
1. current Anima author card
2. exact trainer/source documentation
3. author-shared style LoRA config/dataset if recoverable
4. controlled same-dataset experiments
5. detailed community training reports
6. recipe-only comments

Community numbers such as “1500 steps”, “3000 steps”, “rank 64” are retained only as local recipes unless reproduced.

## 15. High-value next experiments

### Character LoRA
- same dataset; rank/dim controlled
- style-diverse vs style-homogeneous dataset
- background-diverse vs background-homogeneous
- trigger-only vs reduced vs full captions
- unseen outfit/pose/background/style evaluation

### Style LoRA
- same artist/style images
- low vs high content diversity
- content fully captioned vs weak captioning
- weight sweep
- timestep distribution comparison

### Character + style
- independent adapters
- same exact seeds
- weight matrix
- masked/scheduled variants
- check native artist-tag retention

### Cross-model
Train same dataset separately on:
- Anima Base
- NoobAI/Illustrious-compatible base where trainer path permits

Do not test cross-family LoRA portability as a substitute for same-family retraining.

## Promotion result

New ACCEPTED:
- K-CHAR-001
- K-STYLE-001
- K-EVAL-011
- K-LORA-004
- K-LORA-005

New CANDIDATE:
- K-COMM-STYLE-002
- K-COMM-ANIMA-020
- K-COMM-ANIMA-021
- K-COMM-STYLE-003
- K-COMM-STYLE-004
- K-TOOL-026

No exact universal step/rank/learning-rate recipe accepted.
