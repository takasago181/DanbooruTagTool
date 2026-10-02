# BATCH_AS — LoRA training evaluation method — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: practical training methodology
Scope: character/style/concept LoRA evaluation and stopping criteria

## 1. Training loss is not the product metric

Anima community distillation experiment:
https://huggingface.co/circlestone-labs/Anima/discussions/157

Reported:
- training remained numerically stable;
- no NaN/divergence;
- visual result was still poor;
- author explicitly says intermediate visual generation tests would have caught the problem earlier.

The experiment is specialized, but the learning principle is general:
**numerical convergence != practical generation quality**.

Promoted:
- K-PRACTICAL-024
- K-COMM-LORA-018.

## 2. Save intermediate checkpoints

Do not train only:
`start -> final`.

Save at meaningful intervals and run the same evaluation suite.

Look for:
- identity/style fidelity increasing;
- editability decreasing;
- background/context welding;
- native artist/style response weakening;
- artifact rate increasing;
- prompt adherence changing.

The “best” checkpoint can be earlier than the lowest-loss/final checkpoint.

## 3. Fixed evaluation suite

For character LoRA:

E0 — trigger only  
E1 — familiar/basic scene  
E2 — unseen pose  
E3 — unseen outfit  
E4 — unseen background  
E5 — alternate style  
E6 — concept-agnostic prompt without trigger  
E7 — multi-subject if that is a target use case

For style LoRA:

S0 — training-domain-like content  
S1 — unseen character  
S2 — non-character object  
S3 — unusual composition  
S4 — concept-agnostic prompt  
S5 — character LoRA combination

Keep:
- model
- seed set
- sampler/scheduler
- CFG/steps
- resolution
fixed.

Promoted:
- K-EVAL-016.

## 4. Do not copy step counts without exposure context

Community:
- https://huggingface.co/circlestone-labs/Anima/discussions/106
- https://huggingface.co/circlestone-labs/Anima/discussions/129

Users report useful style/character results at very different step/epoch counts.

Why absolute steps are ambiguous:
- dataset image count
- repeats
- batch size
- epoch definition
- resolution/buckets
- optimizer
- LR
- caption/dropout
- timestep/noise sampling
all alter effective training.

Store:
`images × repeats × epochs / batch`
along with trainer semantics rather than repeating an isolated number.

Promoted:
- K-PRACTICAL-025
- K-COMM-LORA-019.

## 5. Training identity

Minimum training record:

### Base
- exact checkpoint/hash
- model profile/version

### Trainer
- repository
- commit/version
- backend
- precision
- attention implementation

### Dataset
- dataset version/hash
- image count
- caption version
- buckets/resolution
- repeats
- augmentation/crop
- dropout/shuffle

### Optimization
- optimizer
- LR
- scheduler
- epochs/steps
- batch
- timestep/noise distribution

### Adapter
- algorithm
- rank/dim
- alpha
- target modules
- LLM/text-encoder training state

### Evaluation
- checkpoint path
- fixed prompt suite
- diagnostic seed set
- inference settings

Promoted:
- K-EVID-007.

## 6. Determinism caution

Discussion:
https://huggingface.co/circlestone-labs/Anima/discussions/144

A user observed substantial differences despite identical dataset/config/seed.
Responders note that exact determinism can require backend/torch settings and that ordinary training may not be bit-identical.

Learning consequence:
- repeat important comparisons;
- do not infer causality from one training run if the observed change is small;
- use larger effect sizes and multiple evaluation seeds.

Promoted:
- K-COMM-LORA-020.

## 7. Separate training and inference variables

When evaluating checkpoint A vs B:
keep inference fixed.

When evaluating LoRA weight:
keep checkpoint fixed.

When evaluating sampler:
keep checkpoint and LoRA weight fixed.

Do not mix:
`new epoch + different sampler + different Prompt`
into one comparison.

## 8. Training curriculum

### Character LoRA
1. baseline dataset
2. save checkpoints
3. choose fidelity/editability balance
4. test unseen conditions
5. only then change caption/module/training recipe

### Style LoRA
1. content-diverse dataset
2. fixed OOD evaluation
3. choose checkpoint before style becomes composition-locked
4. test with character adapters

### Multi-character LoRA
1. single identity fidelity
2. joint/coexistence samples
3. interaction samples
4. pairwise contamination evaluation

## 9. Stop criteria

Stop or roll back when:
- identity/style improvement plateaus;
- editability drops sharply;
- unwanted context becomes persistent;
- base-model leakage increases;
- extra training only increases strength without useful fidelity.

Do not use loss alone.

## Promotion result

New ACCEPTED:
- K-PRACTICAL-024
- K-EVAL-016
- K-PRACTICAL-025
- K-EVID-007

New CANDIDATE:
- K-COMM-LORA-018
- K-COMM-LORA-019
- K-COMM-LORA-020
