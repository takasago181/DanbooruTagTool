# BATCH_AA — Multi-subject LoRA dataset design — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: public training-practice synthesis
Scope: Anima character/multi-character LoRA, relation-heavy scenes, feature bleed

## 1. Why this matters for hard scenes

Inference-time regional prompting can reduce cross-character contamination, but a LoRA can also be trained so that:
- identity survives varied contexts;
- multiple learned identities can coexist;
- the adapter does not assume one fixed background/pose/style;
- interaction is not represented only as isolated portraits.

The training dataset therefore determines part of the later relation/binding ceiling.

## 2. Single multi-character LoRA report

Source:
https://huggingface.co/circlestone-labs/Anima/discussions/220

Practitioner reports:
- genuine multi-character examples help reduce feature bleed;
- stitched single-character composites can help as a cheap fallback but can teach rigid side-by-side separation;
- genuine interaction images are preferred when available;
- solo and multi-character subsets are sampled separately;
- style diversity is added to reduce style overfitting.

Numbers such as “10–50 images” or specific repeat multipliers are treated as one user's recipe, not durable guidance.

Durable hypothesis:
`coexistence/interaction must be represented in the training distribution if direct coexistence is a target capability`.

Promoted:
- K-COMM-LORA-010
- K-COMM-LORA-012

## 3. Multiple separately trained character LoRAs

Sources:
- https://huggingface.co/circlestone-labs/Anima/discussions/202
- https://huggingface.co/circlestone-labs/Anima/discussions/222

Public reports distinguish two strategies:

### Strategy A
Train one multi-character LoRA containing multiple identities.

Advantages:
- coexistence can be learned jointly;
- easier single adapter at inference.

Risks:
- identity/style bleed inside the adapter;
- combinatorial outfit/identity dataset complexity.

### Strategy B
Train separate character LoRAs, but include some multi-character coexistence examples in each relevant dataset.

Claim from one practitioner:
- even a small number of joint examples can materially improve later direct co-generation.

Project treatment:
- retain the mechanism hypothesis;
- reject the specific “two examples per variant is sufficient” threshold until controlled replication.

Promoted:
- K-COMM-LORA-013.

## 4. Background/context entanglement

Source:
https://huggingface.co/circlestone-labs/Anima/discussions/162

One user reported persistent white-background behavior after character-LoRA training.
A responder's diagnosis:
- if background is not described/captioned, the model may absorb it as part of the character concept;
- mutable context should be described rather than silently constant.

This agrees with broader project evidence from:
- K-COMM-LORA-001
- K-COMM-LORA-003
- K-COMM-LORA-008

Promoted:
- K-COMM-LORA-011.

## 5. Viewpoint diversity is necessary but not sufficient

Source:
https://huggingface.co/circlestone-labs/Anima/discussions/119

Reported dataset:
- 46 images;
- frontal / 45° / 75° / 90° views;
- close-ups and wider shots;
- seated/full-body/generalization examples.

Training:
- rank 32;
- LR 2e-5;
- 1500 steps;
- LLM adapter frozen.

Failure:
- identity reproduced strongly mainly in frontal ID-like headshots;
- other views/poses failed likeness.

Why this is valuable:
The dataset superficially had viewpoint diversity, yet generalization still failed.
Therefore “N images + several angles” cannot by itself certify dataset quality.

Possible axes to test:
- identity features over-represented in close-ups;
- caption allocation;
- learning rate/step behavior;
- crop distribution;
- trainer implementation;
- exact preview/base profile.

Promoted:
- K-COMM-LORA-014.

## 6. Training caption structure remains unsettled

Sources:
- https://huggingface.co/circlestone-labs/Anima/discussions/105
- https://huggingface.co/circlestone-labs/Anima/discussions/205

Community approaches include:
- pure Danbooru tags in official ordering;
- mixed tags + natural language;
- tag dropout;
- reduced captions.

Project conclusion remains:
No universal caption recipe.
Choose captions according to what should:
- stay bound to trigger;
- remain changeable;
- be isolated from background/style/context.

## 7. Adult/hard relation consequence

For relation-heavy or adult multi-subject training, dataset design should independently vary:
- subject identity
- role
- relative position
- camera/framing
- background
- clothing/presentation
- interaction state
- visibility/occlusion

If every training example couples the same identity with the same role/side/background, later inference cannot be assumed to separate those dimensions.

## 8. Proposed controlled dataset experiment

Use one target pair and identical trainer settings.

D0:
- solo images only.

D1:
- solo + stitched coexistence images.

D2:
- solo + genuine joint non-contact images.

D3:
- solo + genuine joint interaction images.

Keep total effective sampling approximately balanced.

Evaluate:
- single-character fidelity
- two-character coexistence
- feature bleed
- side/role swaps
- interaction correctness
- style/background leakage

This is more informative than comparing random community LoRAs.

## Promotion result

New CANDIDATE:
- K-COMM-LORA-010
- K-COMM-LORA-011
- K-COMM-LORA-012
- K-COMM-LORA-013
- K-COMM-LORA-014

No exact image-count or repeat recommendation accepted.
