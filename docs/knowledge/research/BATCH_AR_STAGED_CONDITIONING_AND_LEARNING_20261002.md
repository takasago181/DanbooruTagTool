# BATCH_AR — Staged conditioning and practical learning — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Branch: `knowledge/generation-corpus`  
Mode: current runtime + community technique synthesis  
Scope: ComfyUI scheduling, Anima prompt/LoRA staging, relation-heavy practical study

## 1. Conditioning can change over the diffusion trajectory

Tool:
https://github.com/asagi4/comfyui-prompt-control

Current Prompt Control supports:
- prompt scheduling;
- LoRA scheduling;
- regional/mask/composition controls;
- advanced text encoding;
- graph expansion into standard ComfyUI conditioning/timestep nodes.

Scheduling syntax can switch:
- text;
- LoRAs;
- other compatible conditioning
at chosen fractions of sampling.

Project classification:
`constant Prompt` and `scheduled Prompt` are different evidence lanes.

Promoted:
- K-TOOL-032.

## 2. Learn scheduling from a constant baseline

Bad experiment:
- change prompt content;
- add LoRA;
- change sampler;
- add schedule;
- change CFG.

Good experiment:
A. constant prompt
B. exact same prompt, one term removed after X
C. exact same prompt, one term introduced after X

Keep:
- seed;
- model;
- sampler/scheduler;
- CFG;
- steps;
- resolution
fixed.

This teaches what early vs late conditioning actually changed.

Promoted:
- K-PRACTICAL-022.

## 3. Anima community staged-quality example

Source:
https://huggingface.co/circlestone-labs/Anima/discussions/146

A user describes:
- first establishing an asset with a simpler/natural-language conditioning;
- quality modifiers could reduce the intended structure;
- using prompt scheduling to introduce quality modifiers after roughly the early stage improved the desired tradeoff in that use case.

Durable lesson:
some modifiers can be useful at one phase of denoising and harmful at another.

Do not promote:
- the exact 30% switch point;
- the exact quality stack;
- the asset-specific recipe.

Promoted:
- K-COMM-ANIMA-026.

## 4. Relation-heavy use

For a clearly adult relation-heavy scene:

### Baseline
Use a minimal relation/identity/camera prompt.

### If semantics are correct but finish is weak
Test late introduction of:
- style;
- quality;
- secondary detail.

### If semantics are wrong
Do not schedule around the error.
Fix:
- count;
- actor/target;
- body-site;
- geometry;
- visibility
first.

Promoted:
- K-PRACTICAL-023.

## 5. LoRA scheduling

Prompt Control can schedule LoRA presence/effect across sampling.

This is useful for experiments where:
- a character/style LoRA dominates early composition;
- the desired base composition is correct before adapter pressure;
- later adapter application may preserve more structure.

This aligns with the separate ComfyUI LoRA-hook scheduling evidence already in K-TOOL-013.

Learning matrix:
- adapter all steps
- early only
- late only
- masked + all steps
- masked + scheduled

Score:
- identity;
- style;
- composition;
- relation;
- spillover.

## 6. Why schedule data must be stored

A saved text prompt such as:
`character, scene, style`
does not reproduce:
- when style was introduced;
- when a LoRA stopped;
- whether a regional condition ended early.

Therefore save:
- schedule source string;
- expanded before/after states if possible;
- each switch fraction;
- scheduled LoRA path/weight;
- regional/mask state;
- exact Prompt Control version/commit.

Promoted:
- K-EVID-006.

## 7. Practical study exercise

Choose one accepted scene.

Run:
S0 — constant minimal prompt
S1 — constant full prompt
S2 — minimal -> full at early-middle schedule
S3 — full -> minimal after structure stage
S4 — LoRA all steps
S5 — LoRA late only

Use same diagnostic seeds.

Interpret:
- S0 good semantics / weak finish = rendering problem
- S1 broken semantics = full prompt overload
- S2 recovers both = candidate staged solution
- S4 breaks composition / S5 preserves it = adapter timing interference candidate

Do not call one seed definitive.

## 8. Failure modes

Scheduling can:
- hide an underlying prompt conflict;
- create abrupt style/semantic transitions;
- interact with sampler behavior;
- complicate reproducibility;
- make debugging harder than constant conditioning.

Use it after basic Prompt competence, not as a beginner default.

## Promotion result

New ACCEPTED:
- K-TOOL-032
- K-PRACTICAL-022
- K-PRACTICAL-023
- K-EVID-006

New CANDIDATE:
- K-COMM-ANIMA-026
