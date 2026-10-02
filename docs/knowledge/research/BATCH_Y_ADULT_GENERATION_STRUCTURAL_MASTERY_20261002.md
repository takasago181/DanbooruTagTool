# BATCH_Y — Adult generation structural mastery — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Branch: `knowledge/generation-corpus`  
Scope: clearly adult / consensual / adult-fantasy generation knowledge  
Mode: technical learning architecture, source refresh, failure diagnosis

## Goal

Build enough knowledge to teach a user how to reason about difficult adult image-generation scenes without reducing the topic to a list of explicit Prompt recipes.

The target capability is:

`scene intent -> adult validity -> relation graph -> model serialization -> generation -> structural evaluation -> minimum correction -> assisted control when needed -> finishing`

The project must be able to explain **why an adult scene fails**, which predicate failed, and which intervention lane is appropriate.

## 1. Adult validity gate

Before optimization:
- all human subjects must be clearly adults;
- adult-only/consensual or adult-fantasy scope must be unambiguous;
- ambiguous-age or non-consensual interpretation is a scene-validity failure, not a Prompt-tuning problem.

This keeps generation optimization separate from dictionary inventory. A tag may exist in a corpus while still being outside the optimized adult-generation lane.

## 2. Adult scene semantic graph

Do not represent an adult scene as one genre phrase.

Use a graph of independently testable predicates:

### Subjects
- count
- stable identity
- adult status
- distinguishing visual features only when needed for binding

### Relation
- actor / receiver / partner role
- ownership
- relative position
- body-to-body or body-to-object relation

### Target/body-site
- which visible body region is relevant
- left/right or owner if structurally necessary
- whether the region is visible enough to judge

### Geometry/topology
- pose
- contact direction
- connectivity
- overlap / occlusion
- object-device alignment when present

### State/timing/material
- state before/during/after where visually meaningful
- exact count where intrinsic
- source/destination for materials/fluids where intrinsic

### Camera/visibility
- framing
- angle
- crop
- occlusion
- whether all required predicates can be visually verified

### Presentation
- expression
- clothing/exposure state
- setting/style/lighting

Presentation is downstream of structural correctness when the relation itself is the target.

## 3. Why adult scenes fail more often

Adult scenes frequently combine:
- more than one subject;
- unusual pose geometry;
- body-site ownership;
- occlusion;
- exact contact;
- unusual anatomy/count;
- simultaneous relations.

This increases **binding workload**, not merely token count.

Therefore diagnose:
`count -> identity -> visibility -> relation -> body-site -> geometry -> state/count -> collateral anatomy -> context leakage`.

Do not repair a relation failure by adding unrelated quality/style terms.

## 4. Model-family entry points

### NoobAI XL 1.1 EPS

Official source:
https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md

Author baseline:
- Euler a
- CFG 5–6
- 25–30 steps
- ~1MP
- caption order: count -> character -> series -> artist -> special -> general -> other
- Danbooru + e621 native tag training

Adult-learning consequence:
- author default `safe` Positive + `nsfw` Negative is explicitly SFW-oriented;
- when the intended test is adult-rated, do not copy the SFW content filter unchanged and then diagnose the target as unsupported;
- start from exact model baseline but make the content-rating control intent-consistent;
- Noob exact actor/body-site/count ceiling remains HOLD.

Current remote checkpoint SHA256:
`6681e8e4b134c81f16533acedb0d406d7e5e366e1624b4105178c64d00b05d51`
(from the current Hugging Face file page; this does not prove a local installed file identity).

### WAI Illustrious v17

Author card:
https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md

Documented:
- Forge Neo recommended
- Euler a / 15–30 / CFG 5–7
- four rating surfaces: general / sensitive / nsfw / explicit
- `nsfw` negative is recommended when the user wants filtering
- short quality/Negative baseline
- Hires can repair limbs/hands/feet

Adult-learning consequence:
- rating token choice is an intent variable;
- base pass and Hires pass must be scored separately;
- do not treat final repaired anatomy as proof the base relation/anatomy was correct.

### Anima

Official card:
https://huggingface.co/circlestone-labs/Anima

Documented:
- tags + natural language + mixed prompts
- multiple subjects benefit from explicit identity/basic appearance context
- stronger-than-SDXL weighting may be needed
- safety tags are model-specific surfaces

Adult-learning consequence:
- use subject-stable relation descriptions as an experimental lane;
- do not rely on vague pronouns or tag distance for ownership;
- keep relation text concise enough that background/style prose does not dominate structural content.

## 5. Censorship / watermark / style-context leakage

Community sources:
- https://huggingface.co/circlestone-labs/Anima/discussions/104
- https://huggingface.co/circlestone-labs/Anima/discussions/132
- https://huggingface.co/circlestone-labs/Anima/discussions/162

Repeated report:
- some artist/concept selections reproduce censorship/watermark-like artifacts;
- targeted Negative terms may not remove them reliably;
- users attribute this to training-distribution correlation where the artifact is visually tied to the artist/concept.

Diagnostic class:
`CENSOR_CONTEXT_LEAK`

Test:
1. same seed without the artist/concept surface;
2. same seed with it;
3. targeted Negative ON/OFF;
4. alternate artist/style or neutral style;
5. if training a LoRA, inspect whether training images consistently contain the artifact.

Do not assume “stronger Negative” is the first or only fix.

## 6. Adult multi-subject relation captioning

Community source:
https://huggingface.co/circlestone-labs/Anima/discussions/141

A public user describes an adult-scene caption workflow that deliberately:
- assigns stable subject IDs;
- keeps count and camera concise;
- emphasizes relative positions and interactions;
- excludes unrelated background/clothing/style details from the relation description.

The durable idea is **relation-focused scene representation**, not the explicit wording from the user's private system prompt.

Use as CANDIDATE evidence:
- stable IDs may reduce pronoun/ownership ambiguity;
- relation text should not be polluted with every visual attribute;
- helper captions still require human review.

## 7. LLM/VLM as planning aid

Community:
- Anima discussions #140 / #141.

Observed:
- users employ vision-language models to derive relation/pose descriptions;
- long prose can improve detail but can hurt hands/anatomy/framing;
- model capability varies strongly;
- hallucinated tags/relations remain a risk.

Knowledge boundary:
- VLM output = editable scene-description candidate;
- not canonical Danbooru semantics;
- not automatic target truth;
- not evidence that the diffusion checkpoint understands the relation.

Recommended learning use:
1. derive a plain structural description;
2. manually verify count/roles/visibility;
3. translate only the useful relation/geometry into the target model's prompt surface;
4. compare against a tag-only baseline.

## 8. Adult failure taxonomy

Add dedicated adult-generation labels:

- `ADULT_SCOPE_INVALID`
- `SUBJECT_COUNT_FAIL`
- `IDENTITY_SWAP`
- `ROLE_SWAP`
- `BODY_SITE_SWAP`
- `CONTACT_RELATION_FAIL`
- `GEOMETRY_FAIL`
- `TOPOLOGY_FAIL`
- `VISIBILITY_OCCLUSION_FAIL`
- `STATE_TIMING_FAIL`
- `COUNT_FAIL`
- `MATERIAL_SOURCE_DESTINATION_FAIL`
- `ANATOMY_COLLATERAL_FAIL`
- `CENSOR_CONTEXT_LEAK`
- `STYLE_CONTEXT_LEAK`
- `NEGATIVE_COLLISION_SUSPECTED`
- `LORA_CONTEXT_LEAK`
- `ASSISTED_ONLY`
- `POSTPROCESS_RESCUE`

This makes “the image is wrong” diagnosable.

## 9. Adult learning ladder

### Level A — structural SFW-equivalent skill
Master:
- two adult subjects
- exact count
- left/right/front/back relation
- body overlap without identity swap
- camera/framing/occlusion
- hands/limbs under contact

### Level B — adult presentation
Master:
- clothing/exposure state
- expression
- body-site visibility
- content-rating/safety surfaces by model
- censorship/context leakage diagnosis

### Level C — adult relation
Master:
- actor/receiver ownership
- body-site binding
- exact contact relation
- simultaneous constraints
- relation + camera visibility

### Level D — difficult topology / count
Master:
- multiple actors/implements
- topology/connectivity
- exact count
- unusual anatomy/count with Negative OFF/ON control

### Level E — assisted control
When bounded plain Prompt work fails:
- regional conditioning
- pose/depth/control
- inpaint
- per-subject reconstruction
- LoRA concept assist

Keep each lane labeled.

## 10. Evaluation protocol

For every adult test, record:

### Identity
- exact model/checkpoint hash
- runtime commit
- sampler/scheduler
- CFG/steps/resolution/seed
- Positive/Negative
- LoRAs + weights
- regional/control state
- Hires/detailer/inpaint state

### Predicates
- adult scope valid?
- exact subject count?
- identities correct?
- roles correct?
- relation correct?
- body-site ownership correct?
- geometry/topology correct?
- required elements visible?
- exact count/state/material relation correct?
- anatomy collateral defects?
- censorship/context leakage?
- assisted/postprocess required?

One aggregate “success” hides too much information.

## 11. Practical model-selection heuristic

Start NoobAI EPS when:
- concept is likely represented by mature Booru vocabulary;
- tag-first control is preferred;
- you want a clean base test.

Compare Anima when:
- ownership/relation phrasing is central;
- concise natural-language clarification may help;
- regional/control ecosystem is likely useful.

Use WAI17 as:
- Illustrious-style comparison/reference;
- especially when its derivative ecosystem or known character/style coverage matters.

This is a workflow heuristic, not a ranking.

## 12. Current unresolved adult research

Highest-value controlled experiments:

1. Noob EPS adult relation:
   - exact count
   - actor/receiver
   - body-site ownership
   - visibility
   - 4 fixed seeds

2. Noob adult Negative collision:
   - SFW author Negative vs intent-scoped Negative
   - unusual anatomy/count target
   - same seeds

3. Anima adult relation:
   - tags-only
   - concise relation sentence
   - stable subject IDs
   - same seeds

4. Censorship/context leakage:
   - neutral style vs artist/concept surface
   - Negative OFF/ON
   - same seed

5. Multi-character LoRA:
   - no LoRA / A / B / A+B
   - stable relation prompt
   - score contamination and ownership separately

6. Assisted-control escalation:
   - plain Prompt
   - relation-focused hybrid
   - regional
   - inpaint reconstruction

## 13. Boundary

This batch intentionally does **not** store reusable explicit sexual Prompt recipes or copied explicit community system prompts.

It does store the full technical structure needed to:
- plan adult scenes;
- choose model/runtime assumptions;
- diagnose relation/anatomy failures;
- understand rating/Negative conflicts;
- identify censorship/data priors;
- decide when LoRA/regional/inpaint is actually the right intervention.

That is the durable learning layer.
