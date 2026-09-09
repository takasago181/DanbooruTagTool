# Hard Fetish Generation Knowledge — Fluids / Excretion / Contamination Relations

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `DEEP_RESEARCH_V1 / evidence-reference`

## 1. Scope

成人向けの fluid / excretion / contamination 系 Special を、**fluid identity + source + destination/body-site + timing + quantity/trajectory** の関係問題として扱う。

Project inventory includes frequent and rare examples such as:
- broad fluid states (`cum`, `saliva`, `pee` etc.)
- destination-specific variants (`... on body/site`, `... in container`, `... under/through clothes`)
- trajectory/timing variants (`projectile`, drip, after/imminent)
- quantity states (`excessive`, pool/bath-like states)
- multi-person/self-target variants
- rare excretion-related entries.

This file covers generation/audit structure for adult consensual content. It does not expand into R18G/gore generation optimization.

## 2. Semantic decomposition

### Fluid/material identity
What substance/material class is intended?

### Source
Where does it originate?
- person/body
- object/container
- environmental residue

### Destination / target
- body/site
- clothing layer
- mouth/opening
- floor/bed/object/container
- viewer-facing direction when intrinsic.

### State
- suspended/in-flight
- dripping
- puddle/pool
- stain/residue
- inside/under/through a layer.

### Quantity
- ordinary
- excessive/multiple
- coverage area.

### Temporal state
- imminent
- active
- after-state.

## 3. Why unary detection is insufficient

A model/tagger can detect the fluid/material while the requested destination relation is wrong.

Examples of structural false PASS:
- material visible somewhere else on the body
- material present but outside rather than inside/under a layer
- puddle produced instead of stain
- trajectory present but wrong source/target
- multi-person relation attached to wrong actor.

Therefore `FLUID_PRESENT` is not enough for target success.

## 4. Main failure modes

### `DESTINATION_MISBIND`
Correct material, wrong target/site.

### `SOURCE_MISBIND`
Correct material/destination appearance but wrong originating actor/object.

### `STATE_COLLAPSE`
Specific state (drip/stain/pool/inside/through) collapses to generic wetness/fluid presence.

### `LAYER_RELATION_FAIL`
Under/inside/through-clothes relation becomes ordinary surface contamination.

### `QUANTITY_COLLAPSE`
Excessive/multiple concept becomes ordinary amount or uncontrolled visual clutter.

### `TRAJECTORY_RANDOMNESS`
Flow direction does not connect source and destination.

### `COLOR_TEXTURE_ALIAS`
The model substitutes generic liquid, sweat, water, shine, paint-like material, etc.

### `VISIBILITY_SCALE_FAIL`
Small stain/drip target is below useful pixel scale or obscured.

### `STYLE_LEAK`
Strong fluid terms shift overall rendering style, gloss, wetness or skin appearance rather than only the intended relation.

## 5. Relation graph

For destination-specific concepts, model as:

`SOURCE --[material/state]--> DESTINATION`

Optional attributes:
- quantity
- active/after timing
- clothing layer relation
- actor ownership.

This graph abstraction is useful because visually dense fluid scenes can otherwise be over-scored by broad taggers.

## 6. Visibility support

Fluid/stain concepts often compete with image composition:
- wide shot preserves person/actor context but reduces small-fluid visibility;
- close-up improves visible target but can hide source/actor relation;
- dark/complex background can reduce material readability;
- Hires may change fine droplets/stains.

Visibility support must be chosen according to the predicate being tested, not globally added.

## 7. Model-family implications

### WAI Illustrious v17
High-resolution author guidance may help small details, but Hires can materially modify final structures. For fluid micro-details, keep base PNG and Hires output separately.

Excessive quality/Negative stacks remain discouraged by exact author evidence.

### NoobAI XL 1.1 EPS
Native Danbooru/e621 tags plausibly cover many common material concepts. Still, rare destination-specific/Semantic wording requires exact trigger testing.

### Anima
Natural-language/hybrid structure can express source -> destination relations, but relation benefits should be compared against tag-only anchors. Avoid pronouns when multiple actors/sources are involved.

## 8. Evaluator design

### Unary evidence
May support broad material presence.

### Required relation predicates
- `MATERIAL_OK`
- `SOURCE_OK`
- `DESTINATION_OK`
- `STATE_OK`
- `QUANTITY_OK` if intrinsic
- `LAYER_RELATION_OK` if intrinsic
- `VISIBILITY_OK`.

For rare destination variants, human/structured visual review may be required even when broad material tag confidence is high.

## 9. Rare-tail issue

Many destination-specific variants are below 600 posts while broad material tags are extremely common. This creates a predictable evaluator/model pattern:

- broad material is easy;
- specific relation is rare;
- model may collapse to broad material;
- WD-like tagger may reward broad presence and miss the relation failure.

Therefore exact relation must dominate the audit verdict.

## 10. Minimum-sufficient support

Do not strengthen a specific destination concept by adding many synonyms.

Preferred sequence:
1. specific Special
2. source/actor identity if ambiguous
3. one destination/site clarification
4. one visibility support if not judgeable
5. one broad material parent only as controlled A/B
6. quantity/state support only if intrinsic.

A broad material parent that increases liquid everywhere but reduces destination fidelity is anti-support.

## 11. Multi-hard composites

High-risk combinations:
- fluid destination + insertion/body-site relation
- fluid state + under-clothes relation
- fluid + multiple actors
- fluid + machine/tube relation
- fluid + tentacle/nonhuman relation.

Decompose each component first. Do not use a broad wetness/material score as the final composite metric.

## 12. HOLD backlog

- exact family-specific destination-binding accuracy
- tag-only vs concise NL source-target clauses in Anima
- best small-detail resolution/framing for micro-targets
- broad parent material support benefit/harm
- automatic trajectory/source-target evaluator
- Hires effect on small droplets/stains by model family.

## Sources

- Project dictionary: `data/special2788/prompt_reference/07_体液・排泄・汚損.txt`
- WAI v17 author card: https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md
- NoobAI 1.1: https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- Anima: https://huggingface.co/circlestone-labs/Anima
- T2I-CompBench: https://arxiv.org/abs/2307.06350
- ConceptMix: https://arxiv.org/abs/2408.14339
