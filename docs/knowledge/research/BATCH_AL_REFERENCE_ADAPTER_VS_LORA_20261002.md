# BATCH_AL — Reference adapters versus LoRA for character/style reproduction — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: method-selection research
Scope: native knowledge, reference adapters, LoRA, sequence consistency

## 1. Why LoRA is not always the first tool

Reproduction goals differ:

### one-off reference match
Need:
- minimal setup
- no training
- flexible text control.

### reusable custom character
Need:
- persistent identity
- repeated use
- low reference dependency.

### reusable style
Need:
- style transfer across new subjects/content.

### sequence/story
Need:
- identity/style consistency across multiple related images.

### multi-character scene
Need:
- identity separation
- relation/layout control.

These are different problems.

## 2. IP-Adapter

Source:
https://arxiv.org/abs/2308.06721

Key properties:
- image prompt conditioning;
- lightweight adapter;
- frozen base model;
- decoupled text/image cross-attention;
- compatible with text prompts and controllable-generation tools.

Project role:
**reference-conditioning baseline**.

Advantages:
- no per-character training;
- good for rapid experiments;
- reference can supply appearance hard to verbalize.

Risks:
- reference content/composition can leak;
- generic image similarity is not anime identity guarantee;
- multi-subject ownership remains separate.

Promoted:
- K-TOOL-028.

## 3. InstantStyle

Source:
https://arxiv.org/abs/2404.02733

Problem:
reference features contain both style and content.

Method:
- content/style feature decoupling;
- inject reference into selected style-specific blocks;
- reduce style leakage and weight-tuning burden.

Project implication:
Reference-style conditioning suffers from the same fundamental problem as style LoRA:
`style fidelity vs content preservation`.

Promoted:
- K-STYLE-003.

## 4. StyleAligned

Source:
https://arxiv.org/abs/2312.02133

Uses shared attention for tuning-free style alignment across generated images.

Project role:
- sequence/set style consistency;
- useful baseline where persistent fine-tuned style is unnecessary.

Boundary:
consistent style across images != portable learned style adapter.

Promoted:
- K-STYLE-004.

## 5. StoryDiffusion

Source:
https://arxiv.org/abs/2405.01434

Targets:
- consistent subjects and details across long image/video sequences.

Uses:
- Consistent Self-Attention;
- zero-shot augmentation of existing T2I models.

Project lesson:
Character identity has another axis:
`cross-image consistency`.

A character LoRA can score high on independent single images yet drift across a comic/story sequence.

Promoted:
- K-CHAR-004.

## 6. AnimeAdapter

Existing source:
https://arxiv.org/abs/2605.20237

Particularly relevant because it targets:
- anime characters;
- single-reference appearance;
- pose-aware disentanglement;
- no per-subject fine-tuning.

Status:
research candidate until code/model release and practical compatibility are verified.

## 7. Method-selection matrix

### Base/native tags
Use first when:
- model already knows the character/style;
- exact canonical/model trigger works;
- no custom identity needed.

### Reference adapter
Use when:
- 1–few references;
- rapid one-off generation;
- training cost is undesirable;
- appearance reference is more useful than a trigger.

### Character LoRA
Use when:
- recurring reusable character;
- identity must work without reference image each run;
- dataset can cover editability axes.

### Style LoRA
Use when:
- recurring reusable rendering style;
- target should transfer across unrelated content;
- enough content diversity exists to isolate style.

### Shared-attention/reference style
Use when:
- style consistency across a batch/series matters;
- persistent adapter training is not necessary.

### Regional/reference/control hybrid
Use when:
- multiple characters;
- identity ownership;
- specific layout/geometry.

Promoted as project routing:
- K-CHAR-005.

## 8. Benchmark all methods under the same task

For one known target character:
- native tag only
- reference adapter
- character LoRA
- character LoRA + reference
- regional/reference condition if multi-subject.

Evaluate:
- identity
- editability
- latency/setup cost
- repeated-use cost
- style freedom
- composition freedom.

For one target style:
- artist/style prompt
- reference style adapter
- StyleAligned/InstantStyle-like method
- style LoRA.

Evaluate:
- style fidelity
- content preservation
- OOD subject generalization
- sequence consistency
- setup/training cost.

## 9. Sequence evaluation

For comic/story-like use:
generate the same character over:
- 5 independent scenes
- changed camera
- changed outfit
- changed lighting
- interaction with another character.

Measure:
- per-image identity
- inter-image identity variance
- style variance
- accidental outfit/feature drift.

This requires more than a single-image CCIP result.

## Promotion result

New ACCEPTED:
- K-TOOL-028
- K-STYLE-003
- K-STYLE-004
- K-CHAR-004
- K-CHAR-005
