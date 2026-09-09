# Stage10 PROMPT compositional failure research ledger

最終更新: 2026-09-09  
Owner: PROMPT / Issue #5  
Status: research-background ledger. **Not model-specific production specification.**

## Purpose

hard-targetが壊れる理由を「そのタグをモデルが知らない」だけで説明しないため、text-to-image研究で繰り返し観測される failure classes をStage10監査語彙へ接続する。

## R1 — Attend-and-Excite

Source: https://arxiv.org/abs/2301.13826
Evidence: `RESEARCH_BACKGROUND`

Reported problems:
- catastrophic neglect: prompt内のsubjectが画像で欠落
- incorrect attribute binding: attributeが別subjectへ結びつく

Project mapping:
- `TARGET_MISSING`
- `MULTI_SPECIAL_DROP`
- `ATTRIBUTE_LEAKAGE`
- `ACTOR_TARGET_SWAP`

Important:
This was studied on public Stable Diffusion-family models. It supports the failure taxonomy, not exact WAI/NoobAI/Anima behavior.

## R2 — T2I-CompBench

Source: https://arxiv.org/abs/2307.06350
Evidence: `RESEARCH_BACKGROUND`

Benchmark categories:
- attribute binding
- object relationships
- complex compositions
- spatial relationships
- non-spatial relationships

Project mapping:
- hard-target should not be represented by easy single-tag tests only
- relation / body-site / multi-object / multiple-Special cases need separate evaluation
- one global evaluator threshold is unlikely to represent all complexity classes

## R3 — Object-Attribute Binding in Text-to-Image Generation

Source: https://arxiv.org/abs/2404.13766
Evidence: `RESEARCH_BACKGROUND`

Reported:
- diffusion models can struggle to bind named attributes to the correct objects
- syntactic structure and focused cross-attention can improve binding

Project mapping:
- short relation sentence / syntactic relation support is a legitimate Stage10 hypothesis
- success of a broad concept does not prove correct ownership/site binding

## R4 — MultiDiffusion

Source: https://arxiv.org/abs/2302.08113
Evidence: `RESEARCH_BACKGROUND`

Reported:
- spatial guiding signals such as segmentation masks and bounding boxes can improve control without retraining the base model

Project mapping:
- repeated spatial/binding failure is a valid reason to consider regional/mask-based control rather than endless Prompt expansion
- region control should be evaluated as a separate intervention lane

## R5 — Concept Conductor

Source: https://arxiv.org/abs/2408.03632
Evidence: `RESEARCH_BACKGROUND`

Reported multi-concept problems:
- attribute leakage
- layout confusion
- reduced concept fidelity / semantic consistency

Project mapping:
- multiple-Special and multi-actor cases need explicit leakage/layout failure classes
- isolation of concepts/regions is theoretically aligned with the kind of problem Forge Couple/Regional tries to address operationally

## Research-backed audit principles

1. `token present` is not sufficient evidence.
2. Missing target and wrong binding are different failures.
3. Multi-object/relation scenes are a distinct difficulty class.
4. Attribute leakage is not an edge case; it is a recognized compositional failure mode.
5. Spatial control can be a rational escalation when Prompt-only semantics are correct but layout is not.
6. Evaluators should distinguish existence, relation, binding and visual quality.
7. Improvements in one dimension can hide failures in another; do not reduce all results to one score too early.

## Stage10 candidate metrics

- `TARGET_EXISTENCE`
- `ACT_RETENTION`
- `SITE_ACCURACY`
- `ACTOR_TARGET_BINDING`
- `ATTRIBUTE_OWNERSHIP`
- `OBJECT_INTEGRITY`
- `SPATIAL_RELATION`
- `NONSPATIAL_RELATION`
- `COUNT_ACCURACY`
- `GEOMETRY`
- `VISIBILITY`
- `IMAGE_QUALITY`
- `ARTIFACT_RATE`

## What research does NOT prove

- exact best Prompt order for WAI/NoobAI/Anima
- exact support tag for a Special
- canonical vs alias response
- exact negative profile
- exact threshold for auto-winner routing

Those require model-specific evidence.

## Boundary

Research papers supply failure taxonomy and intervention rationale only. They do not override model-author instructions, Danbooru semantics, or Stage10 image evidence.