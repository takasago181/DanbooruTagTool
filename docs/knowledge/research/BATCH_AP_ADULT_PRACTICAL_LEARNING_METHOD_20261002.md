# BATCH_AP — Adult practical learning method and evidence loop — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Scope: clearly adult / consensual-adult-fantasy image generation
Mode: practical learning methodology + community practice synthesis

## Goal

Turn adult-image generation from trial-and-error prompt collecting into a repeatable learning discipline.

The core loop is:

`reference -> structural decomposition -> minimal generation -> fixed-seed evaluation -> one-variable correction -> assisted escalation -> local repair -> retained evidence`

This batch deliberately stores the learning method and structural observations, not reusable explicit sexual prompt recipes.

## 1. What to learn first

Do not begin with the hardest multi-person scene.

Recommended skill ladder:

### L0 — tool literacy
Understand:
- model/profile
- seed
- sampler/scheduler
- CFG/steps
- resolution
- LoRA loader/weight
- img2img/denoise
- mask/inpaint
- metadata saving

### L1 — one adult subject
Learn:
- character identity
- framing
- pose
- exposure/presentation state
- local anatomy
- style/LoRA isolation

### L2 — two adults, no complex interaction
Learn:
- count
- left/right/front/back
- distinct identities
- separate clothing/features
- camera visibility

### L3 — simple interaction/contact
Learn:
- stable role assignment
- body-part ownership
- contact visibility
- occlusion
- hands/limbs under overlap

### L4 — relation-heavy adult scene
Learn:
- actor/receiver role stability
- target-site ownership
- state/count/material predicates when relevant
- relation vs local-anatomy scoring

### L5 — multi-subject / multi-LoRA
Learn:
- global contamination
- pairwise interference
- regional separation
- pose/layout control
- per-subject reconstruction

### L6 — production finishing
Learn:
- Hires/img2img
- local detailer
- inpaint
- conservative upscale
- final identity/relation audit

Do not advance because one seed looked good.
Advance when the same skill is understandable and reasonably reproducible across a small seed set.

## 2. Learn from references by removing irrelevant detail

Anima discussion:
https://huggingface.co/circlestone-labs/Anima/discussions/141

A public adult-generation workflow uses a VLM/LLM to produce a structural description focused on:
- people count
- stable subject IDs
- camera/framing
- relative positions
- contact/interaction
- visible facial/body state

while deliberately excluding:
- clothing
- detailed appearance
- background
- lighting
- art style.

Project interpretation:
This is a good **study method** because it creates a relation-only representation.

Learning exercise:
1. choose a clearly adult reference;
2. write/obtain a structure-only description;
3. manually verify the description;
4. generate from the structural representation;
5. add character/style modules later.

Do not trust VLM captions blindly.
They can hallucinate ownership/contact or miss occluded details.

Promoted:
- K-ADULT-009.

## 3. Use stable subject identifiers while studying binding

The same community practice assigns persistent IDs/names to subjects throughout the scene description.

Why this helps learning:
- easier to see when role ownership swaps;
- easier to compare generations;
- removes vague pronoun ambiguity from the experiment.

This is a representation technique, not evidence that the diffusion model implements symbolic variables.

## 4. Separate scene semantics from character appearance

Learning prompt organization:

### Relation module
- count
- role
- position
- contact
- visibility
- camera

### Character module
- identity
- core visual features
- character LoRA/reference

### Style module
- artist/style
- style LoRA
- rendering/palette

### Environment module
- background/props/lighting

Study relation first with minimal noise.
Then add character/style/environment one module at a time.

If the relation works before a character LoRA and fails after it:
classify LoRA/binding interference.

## 5. Learn plain generation before regional control

Community sources:
- https://www.reddit.com/r/comfyui/comments/1dpwju8/
- https://www.reddit.com/r/comfyui/comments/1i7b6fz/
- https://www.reddit.com/r/comfyui/comments/1dzh275

Recurring issue:
multiple character LoRAs can affect the whole image and mix identities.

Regional/mask solutions can isolate:
- conditioning
- LoRA influence
- per-subject reconstruction.

Learning order:
1. base model / no LoRA
2. one character LoRA
3. two character LoRAs globally
4. regional masks/conditioning
5. pose/depth if geometry needs help
6. local inpaint

If a learner starts at step 4, they may obtain a good image without understanding the base failure.

Promoted:
- K-ADULT-010.

## 6. Divide geometry and identity

Community workflow:
https://www.reddit.com/r/comfyui/comments/1arhe7s

A practical route used by multi-character creators:
1. create base layout/pose;
2. place/reconstruct desired characters;
3. apply regional identity conditioning;
4. Hires/refine.

This is useful pedagogically because:
- pose/layout can be evaluated before identity;
- identity can be evaluated without changing global geometry;
- LoRA leakage becomes visible.

Promoted:
- K-ADULT-011.

## 7. Reproduce before modifying

When studying a community workflow:

Bad:
- change checkpoint
- change sampler
- change LoRA
- rewrite prompt
- change resolution
and then decide whether the original method works.

Better:
1. identify exact original versions/settings;
2. reproduce the closest possible baseline;
3. verify one representative output pattern;
4. make one change;
5. keep before/after outputs.

If exact versions are unavailable:
mark the reproduction as approximate.

Promoted:
- K-PRACTICAL-016.

## 8. Keep the failures

Do not keep only:
- beautiful final outputs.

Also retain:
- identity swaps
- count failures
- relation errors
- hidden targets
- malformed anatomy
- LoRA leakage
- bad regional boundaries
- Hires drift.

For each failed image record:
- intended predicates
- which predicates passed
- which failed
- settings
- one suspected cause
- next test.

This creates a local failure corpus.

Promoted:
- K-PRACTICAL-017.

## 9. Use a failure journal

Minimal record:

`Experiment ID`
`Target skill`
`Model/runtime`
`Seed(s)`
`Prompt modules`
`LoRAs/weights`
`Controls`
`Pass predicates`
`Fail predicates`
`Single change made`
`Result`
`Next hypothesis`

The goal is not bureaucracy.
It prevents cycling through the same failed ideas.

## 10. XY/grid learning

Community comparison practice:
- https://www.reddit.com/r/StableDiffusion/comments/1dhdyt7
- https://www.reddit.com/r/StableDiffusion/comments/1e9eqj6

Useful axes:
- LoRA weight
- CFG
- steps
- denoise
- sampler
- one Prompt representation change

Keep:
- model
- seed
- resolution
- unrelated settings
fixed.

Avoid giant grids where five parameters vary simultaneously.

Promoted:
- K-PRACTICAL-018.

## 11. Multi-seed before conclusion

A single good adult scene can be an accidental seed success.

For a learning exercise:
- retain a small fixed diagnostic seed set;
- evaluate the same predicates across all;
- distinguish reliability from possibility.

Later production may choose the best aesthetic seed.
Research conclusions should not.

## 12. Captioning for LoRA study

Anima discussions:
- https://huggingface.co/circlestone-labs/Anima/discussions/105
- https://huggingface.co/circlestone-labs/Anima/discussions/205

Practitioners use:
- Danbooru tags
- mixed tags + natural language
- tag dropout
- author-like ordering.

There is no community consensus on one best caption format.

Learning method:
compare caption policies using the **same image dataset**.

Score:
- trigger identity
- relation/pose editability
- clothing/background mutability
- artist/style response
- leakage.

Promoted:
- K-COMM-LORA-016.

## 13. Multi-character LoRA learning curriculum

Anima discussion:
https://huggingface.co/circlestone-labs/Anima/discussions/202

Practitioners report value from:
- solo subsets;
- joint/coexistence subsets;
- actual interaction examples where available;
- balancing effective sampling between solo and joint states.

Study in order:
1. each character alone
2. A+B non-interacting
3. A+B simple interaction
4. more complex interaction
5. additional subjects

Do not infer stage 4 from stage 1.

Promoted:
- K-COMM-LORA-017.

## 14. Image-edit learning is separate

Img2img/inpaint allows a learner to ask:
- can the model preserve geometry?
- can it change character identity?
- can it change style?
- can it repair one local relation?

Denoise is a central variable:
low values preserve more source structure;
higher values allow stronger reinterpretation but increase drift.

Treat edit skill separately from txt2img skill.

## 15. Common learning traps

### Trap: copy a giant prompt
Why bad:
you cannot tell which term mattered.

### Trap: only save good images
Why bad:
you lose evidence of model limits.

### Trap: always add tags
Why bad:
failure may be geometry/binding, not vocabulary.

### Trap: immediately use Regional
Why bad:
you may never learn the checkpoint's plain capabilities.

### Trap: judge a LoRA on one hero image
Why bad:
identity fidelity can hide poor editability.

### Trap: compare different seeds/settings simultaneously
Why bad:
causal interpretation becomes impossible.

### Trap: use a detailer to fix relation mistakes
Why bad:
local anatomy repair and semantic binding are different.

## 16. Personal study sessions

A productive session should have one question.

Examples:
- Can this checkpoint maintain two adult identities?
- Does the relation survive adding character LoRA A?
- Does a style LoRA change body/identity?
- Does regional masking reduce contamination?
- Does a second pass preserve the accepted scene?
- Does caption policy change editability?

End each session with:
- one retained finding;
- one rejected hypothesis;
- one next experiment.

## 17. Promotion standard

A practical observation can move toward durable knowledge when:
- exact setup is known;
- the change is isolated;
- more than one seed/example supports it;
- failure/success criteria were defined before looking at the result;
- it does not contradict stronger exact-model evidence without explanation.

## Promotion result

New ACCEPTED:
- K-ADULT-008
- K-PRACTICAL-016
- K-PRACTICAL-017
- K-PRACTICAL-018

New CANDIDATE:
- K-ADULT-009
- K-ADULT-010
- K-ADULT-011
- K-COMM-LORA-016
- K-COMM-LORA-017
