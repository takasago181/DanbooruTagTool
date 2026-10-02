# BATCH_AB — Negative prior / censor-context / training toolchain — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: community failure synthesis + current runtime/tool maintenance audit
Scope: Anima / Forge Neo / adult hard-scene diagnostics / LoRA training

## 1. Ordinary Negative Prompt vs positive-prior entanglement

Sources:
- https://huggingface.co/circlestone-labs/Anima/discussions/94
- https://huggingface.co/circlestone-labs/Anima/discussions/104
- https://huggingface.co/circlestone-labs/Anima/discussions/152
- https://huggingface.co/circlestone-labs/Anima/discussions/132

Repeated public report:
- some artist/concept surfaces repeatedly carry watermark/censor/text-like artifacts;
- ordinary Negative terms may reduce them inconsistently or fail entirely;
- users attribute the persistence to dataset correlations where the artifact is part of the positive concept/style representation.

Project interpretation:
Distinguish at least:
1. weak/insufficient ordinary Negative;
2. positive-prior/context entanglement;
3. LoRA-specific contamination;
4. postprocess artifact.

Do not respond to every case by increasing a generic Negative stack.

Promoted:
- K-NEG-004.

## 2. NegPiP as a distinct intervention

Primary tool sources:
- https://github.com/hako-mikan/sd-webui-negpip
- https://github.com/Haoming02/sd-forge-negpip

Documented behavior:
- negative weight inside Positive Prompt creates suppressive effect;
- negative weight inside Negative Prompt can create enforcing effect;
- intended to provide a stronger/different route than ordinary Negative Prompt conditioning.

Evidence rule:
`ordinary Negative` and `NegPiP suppression` are different lanes.

If a difficult concept is only suppressible under NegPiP:
- record ordinary Negative failure separately;
- record NegPiP-assisted success;
- never rewrite that result as if the base checkpoint obeyed an ordinary Negative.

## 3. Maintenance state

Haoming02/sd-forge-negpip:
- documents SD1 / SDXL / Anima support;
- intended for Forge Classic / Neo;
- archived 2026-09-30;
- remains readable but frozen.

Original hako-mikan/sd-webui-negpip:
- remains the upstream project;
- current main documentation does not establish the same Forge-Neo-Anima path as the archived Haoming02 fork;
- issue history shows Anima/Forge Neo compatibility was a distinct support question.

Project rule:
Tool identity includes:
- repository;
- branch;
- commit;
- WebUI runtime;
- model family;
- active/inactive maintenance state.

## 4. TrainTrain current Anima path

Source:
https://github.com/hako-mikan/sd-webui-traintrain

Current documentation:
- update 2026-09-04 added Anima and Krea2 on Forge Neo;
- Anima 2B confirmed; 2.9B/3.8B use the same path;
- TrainTrain trains the model already loaded by Forge Neo;
- text encoder is not trained in the documented Anima path;
- gradient checkpointing should be enabled;
- docs state a 1024px Anima training run does not fit within 16GB without it.

Project consequence:
- trainer/runtime architecture must be stored with LoRA evidence;
- a LoRA trained through TrainTrain is not assumed equivalent to sd-scripts/diffusion-pipe training;
- text-encoder behavior differs by tool path.

Promoted:
- K-TOOL-017.

## 5. Adult/hard-scene suppression ladder

When an unwanted visual prior interferes with an adult/hard target:

A. Identify source:
- model base prior?
- artist/concept prior?
- LoRA prior?
- prompt lexical ambiguity?
- postprocess?

B. Same-seed baseline:
- unwanted prior OFF
- unwanted prior ON

C. Ordinary Negative:
- minimal targeted term only

D. Alternative positive representation:
- replace/remove the correlated artist/concept if possible

E. Assisted suppression:
- NegPiP-style conditioning if runtime supports it

F. Edit/postprocess:
- inpaint/crop/reconstruction if structure is already correct

Keep all lanes separate.

## 6. Negative interaction with hard anatomy/count targets

Existing project principle remains:
- broad anatomy/count negatives can overlap with desired unusual structure;
- exact family effect remains HOLD.

Therefore suppression work should avoid mixing:
- unwanted context/censor removal
with
- broad anatomy cleanup
in one uncontrolled change.

## 7. Toolchain freshness

The adult-generation corpus should recheck:
- Forge Neo branch/commit
- Regional Prompter
- Forge Couple
- NegPiP implementation actually installed
- ComfyUI LoRA masking/scheduling path
- TrainTrain or sd-scripts trainer path

before treating tool-specific behavior as current local truth.

## Promotion result

New ACCEPTED:
- K-TOOL-015
- K-TOOL-016
- K-TOOL-017
- K-TOOL-018

New CANDIDATE:
- K-NEG-004

No ordinary-Negative HOLD was closed.
