# BATCH_AJ — Character/style evaluation and LyCORIS adapter methods — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: evaluation-framework + adapter-method research
Scope: anime character identity, style fidelity, LoRA/LyCORIS comparison

## 1. Character identity needs an anime-aware evaluator

Source:
https://huggingface.co/deepghs/ccip

CCIP (Contrastive Anime Character Image Pre-Training):
- measures visual similarity between anime characters;
- explicitly targets anime-character identity;
- base model-card use case is limited to single-character images.

Project use:
- character identity screening;
- same-character vs different-character comparisons;
- reference-set distance.

Do not use CCIP alone for:
- multi-character ownership;
- pose correctness;
- clothing mutability;
- background independence;
- full-scene relation correctness.

Promoted:
- K-EVAL-012.

## 2. Three-axis character evaluation

A useful character-LoRA evaluator stack:

### Identity
- CCIP / anime identity metric
- human reference review

### Geometry
- DWPose/OKS or keypoint similarity where relevant
- framing/camera checks

### Editability
- prompt success on unseen outfit
- unseen pose
- unseen background
- unseen camera
- alternate style

This prevents a pose-locked/background-locked adapter from receiving a false high score merely because the face matches.

Promoted:
- K-EVAL-013.

## 3. Style-specific metrics

CSD:
https://arxiv.org/abs/2404.01292

The paper learns contrastive style descriptors that are intended to emphasize:
- color
- texture
- shape/style interactions
while reducing semantic-content dependence.

DiffSim:
https://arxiv.org/abs/2412.14580

Uses diffusion features for:
- human-aligned visual similarity
- instance similarity
- style similarity.

The paper finds different denoising timesteps/layers specialize differently:
- some settings work better for style;
- others for instance-level similarity.

Project use:
- CSD/DiffSim-style metric for style fidelity;
- CCIP/instance metric for character identity;
- prompt/task metric for content preservation.

Do not merge them into one score.

Promoted:
- K-EVAL-014.

## 4. OOD style generalization

CSD research tests style similarity under content-constrained and out-of-distribution subjects.

Important result:
Style reproduction can look strong on common/in-domain subjects yet weaken on content unlike the artist/reference distribution.

Project style-LoRA test set should include:
- training-domain-like subject
- unseen character
- non-character object
- unusual environment
- different composition/camera.

Promoted:
- K-STYLE-002.

## 5. LyCORIS evaluation framework

Source:
https://arxiv.org/abs/2309.14859

The ICLR 2024 work explicitly separates evaluation dimensions:
- fidelity
- controllability/text alignment
- diversity
- base-model preservation
- image quality

It also separates prompt types, including:
- concept-targeting prompts
- concept-agnostic prompts used to detect leakage
- alteration/generalization prompts.

This maps directly to character/style LoRA evaluation.

Promoted:
- K-LORA-006.

## 6. Rank/dimension and alpha are coupled

LyCORIS defines conventional LoRA scale approximately through:
`gamma = alpha / rank`.

Their experiments report:
- increasing capacity with rank/alpha ratio fixed often resembles increasing LR/epochs;
- alpha changes can materially alter the trend;
- alpha=1 cases could reverse some observed effects.

Project consequence:
Do not optimize:
`rank -> higher until image looks more similar`.

Instead record:
- dim/rank
- alpha
- effective scale
- learning rate
- epochs/steps
- dataset size
- fidelity/editability/base-preservation metrics.

Promoted:
- K-LORA-007.

## 7. LoRA vs LoCon vs LoHa vs LoKr

LyCORIS:
https://github.com/KohakuBlueleaf/LyCORIS
Research:
https://arxiv.org/abs/2309.14859

Mechanism summary:
- LoRA: low-rank linear updates;
- LoCon: LoRA extended to convolution layers;
- LoHa: Hadamard-product factorization can represent higher effective matrix rank per parameter budget;
- LoKr: Kronecker factorization;
- current LyCORIS also supports additional PEFT families.

Research observations:
- no universally best method;
- algorithm effect depends on concept category, training regime, capacity and desired generalization;
- paper reports task-dependent tradeoffs.

Project rule:
Adapter family is an experimental factor, not a quality tier.

Promoted:
- K-LORA-008.

## 8. Current LyCORIS freshness

Current repository changelog:
- 4.0.0 update dated 2026-09-01;
- multiple algorithms;
- fused kernels / updated backends.

Project use:
Before local comparison pin:
- LyCORIS version/commit;
- training wrapper (sd-scripts/other);
- checkpoint family;
- exact algorithm;
- all rank/alpha/factor options.

Promoted:
- K-TOOL-027.

## 9. DoRA note

Original DoRA:
https://arxiv.org/abs/2402.09353

DoRA decomposes weight magnitude and direction and reported improved learning capacity/stability relative to standard LoRA in its evaluated language/multimodal settings.

Boundary:
- this is not direct evidence that DoRA is superior for Anima character/style training;
- LyCORIS current implementation availability makes it a test candidate;
- require same-dataset diffusion comparison.

No separate “DoRA is better” Claim promoted.

## 10. Recommended character-LoRA scorecard

For each checkpoint:
- Identity / CCIP
- Human likeness
- Prompt adherence
- Outfit editability
- Pose editability
- Camera editability
- Style editability
- Background independence
- Seed diversity
- Base-native artist/style response
- Artifact rate

Do not collapse into one total score until individual failure axes are visible.

## 11. Recommended style-LoRA scorecard

- CSD/DiffSim-style similarity
- human style similarity
- content preservation
- identity preservation
- prompt adherence
- OOD subject generalization
- composition diversity
- color/palette leakage
- unwanted subject/object leakage
- base-model preservation

## 12. High-value experiment

Same dataset, same trainer/runtime:
- LoRA
- LoCon
- LoHa
- LoKr

Use approximately matched parameter/file budgets where feasible.

Evaluate character and style as separate tasks.
Do not assume a winner transfers between them.

## Promotion result

New ACCEPTED:
- K-EVAL-012
- K-EVAL-013
- K-EVAL-014
- K-STYLE-002
- K-LORA-006
- K-LORA-007
- K-LORA-008
- K-TOOL-027
