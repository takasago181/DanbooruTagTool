# BATCH_Z — Compositional evaluation and assisted-control foundations — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: research-paper + official-runtime synthesis
Scope: relation-heavy / multi-subject / hard adult structural generation

## Why this batch

Hard adult generation stresses the same capabilities that current compositional T2I research measures:
- exact subject count;
- attribute ownership;
- spatial relation;
- non-spatial interaction;
- multi-subject composition;
- visibility/occlusion;
- complex constraint satisfaction.

This batch imports stronger evaluation/control principles without replacing adult-domain semantics.

## 1. T2I-CompBench

Source:
https://arxiv.org/abs/2307.06350

The benchmark separates:
- color binding;
- shape binding;
- texture binding;
- spatial relations;
- non-spatial relations;
- complex compositions.

Project consequence:
A generated image can contain all requested visual elements while still failing the relation or ownership predicate.
This directly supports the project distinction:
`presence != binding/relationship success`.

## 2. CompAlign / CompQuest

Source:
https://arxiv.org/abs/2505.11178

CompAlign:
- 900 difficult multi-subject prompts;
- combines numeracy, 3D-spatial relations and attribute binding;
- explicitly stresses scenes with 3+ subjects.

CompQuest:
- decomposes a complex prompt into atomic sub-questions;
- gives fine-grained binary feedback per compositional element.

Project consequence:
Hard-scene audit should ask atomic questions such as:
- are the required subjects present?
- is the exact count correct?
- does each attribute belong to the correct subject?
- is the intended relative geometry correct?
- is the required relation/contact actually visible?
- is the target site owned by the intended subject?

This is stronger than one holistic “looks right” verdict.

## 3. T2I-FineEval

Source:
https://arxiv.org/abs/2503.11481

The paper argues that common aggregate metrics such as CLIPScore can fail to reveal compositional errors and proposes finer image/text decomposition.

Project consequence:
For relation-heavy scenes:
- do not let one embedding similarity score override a visible ownership/count/relation failure;
- evaluator outputs should be predicate-specific and routed to human review when semantics exceed evaluator capability.

## 4. Complexity scaling

Sources:
- CompAlign
- https://arxiv.org/abs/2512.11542

Across compositional benchmarks, reliability degrades on:
- multiple entities;
- bound attributes;
- numeracy;
- spatial/3D relationships;
- complex multi-object prompts.

Project rule:
`2-subject success` must not be treated as evidence for `3+ subject reliability`.

Create an explicit stress axis:
- S1: one subject
- S2: two subjects / one relation
- S3: three+ subjects or simultaneous relations
- S4: composite relation + count + topology + occlusion

## 5. ComfyUI native LoRA masking

Official source:
https://blog.comfy.org/p/masking-and-scheduling-lora-and-model-weights

ComfyUI supports:
- spatial masks for LoRA/model weights;
- adapter hooks attached to specific conditioning;
- different LoRAs in different regions;
- combination with ControlNet/other conditioning.

Project consequence:
When global multi-LoRA inference causes cross-character contamination, add a separate test lane:
`global LoRA -> masked LoRA`.

This is assisted control and cannot certify plain global-LoRA capability.

## 6. ComfyUI LoRA scheduling

Same official source.

Scheduling allows:
- weight keyframes across the denoising trajectory;
- separate scheduling of model and optionally text/CLIP effect.

ComfyUI's example describes:
- early stages as important to global composition/layout;
- scheduled LoRA use as a way to retain more base composition while still applying adapter features.

Project experiment axes:
- LoRA all steps;
- LoRA later only;
- LoRA early only;
- region-masked + scheduled.

Never turn one schedule into a universal default.

## 7. FreeFuse

Source:
https://github.com/yaoliliu/FreeFuse

Public description:
- training-free multi-subject LoRA fusion;
- adaptive token-level routing;
- spatially confines subject LoRA influence;
- prevents other LoRAs from directly intruding into the subject region;
- public implementation includes SDXL/Flux-family workflows.

Research value:
This independently supports the hypothesis that multi-LoRA identity bleed is partly a routing/spatial-locality problem rather than only a Prompt wording problem.

Boundary:
- current public support does not establish Anima compatibility;
- preserve as a research/tool lead, not an Anima default.

## 8. Hard-domain evaluation template

For each difficult scene, define atomic predicates before generation:

### Entity
- subject_count
- subject_identity

### Binding
- attribute_owner
- role_owner
- target_site_owner

### Relation
- contact_relation
- spatial_relation
- source_destination
- connectivity/topology

### Numeracy/state
- implement_count
- simultaneous_count
- state/timing

### Observability
- target_visible
- relation_visible
- occlusion acceptable

### Integrity
- collateral_anatomy
- context/style leak
- censor/watermark artifact

### Intervention
- plain_prompt
- LoRA_global
- LoRA_masked
- LoRA_scheduled
- regional/control
- inpaint/postprocess

Evaluation should retain each predicate separately.

## 9. Highest-value local experiment designs

### Multi-LoRA contamination
A: no LoRA
B: LoRA A
C: LoRA B
D: A+B global
E: A+B region masked
F: A+B region masked + schedule

Use same seeds and score:
- identity
- attribute spillover
- relation
- composition
- background/style contamination.

### Complexity ladder
Same concept family:
- one subject
- two subjects
- three subjects
- two simultaneous relations

Keep style/background minimal.

### Atomic evaluator comparison
For a fixed image set:
- human predicate labels;
- unary tagger;
- MLLM yes/no questions;
- aggregate embedding score.

Measure which failure types each evaluator misses.

## Promotion result

New ACCEPTED:
- K-HARD-008
- K-EVAL-008
- K-HARD-009
- K-TOOL-012
- K-TOOL-013

New CANDIDATE:
- K-TOOL-014

No adult semantic category was collapsed.
No production behavior changed.
