# STAGE 10 — PRACTICAL IMAGE-GENERATION LEARNING

最終更新: 2026-09-13

## Status

**CURRENT STAGE10 DEFINITION / ACTIVE PARALLEL LEARNING LANE / NOT A V1 PRODUCT GATE**

Stage10 is redefined by explicit user decision on 2026-09-13 JST.

The former meaning of Stage10 — broad production A/B validation for the Special Core Dictionary — is no longer the current Stage10 definition.
Historical Stage10 A/B/evaluator/Prompt assets remain preserved as learning and testing evidence.

Operational owner:
- Issue #65 `[STAGE10][LEARNING][ACTIVE] Practical image-generation mastery with NoobAI`

Knowledge owner:
- Issue #44 `KNOWLEDGE:#44`

Product routing remains independent:
- `#64 -> #34 -> #42 -> v1 UI integration / Windows acceptance`

---

## 1. Goal

Stage10 is a **hands-on image-generation learning stage**.

Target outcome:

> A beginner can take a Japanese visual intent, build and understand the Prompt, generate with NoobAI, diagnose failures, change the smallest useful variable, use LoRA / Hires / ADetailer / img2img / inpaint / regional-control when appropriate, and finish difficult/niche adult 2D illustrations without depending on blind recipe copying.

The difficult domain may include consensual adult fictional/anime hard/niche sexual content.
The learning objective is **generation skill and independent problem solving**, not product-side automatic adult-content generation.

Stage10 is complete when the learner can repeatedly move through:

`意図 -> Prompt設計 -> 生成 -> 観察 -> 原因分解 -> 修正 -> 必要なら補助ツール -> 仕上げ -> 再現可能な保存`

without relying on unexplained recipe copying.

---

## 2. Primary model lane

### NoobAI XL 1.1 EPS

Current Stage10 primary learning model:
- NoobAI XL 1.1 EPS
- Forge Neo
- tag-first practical workflow

Initial author-baseline start:
- Sampler: `Euler a`
- Steps: `25–30`
- CFG: `5–6`
- image area: around SDXL 1MP
- caption organization: `count -> character -> series -> artist -> special -> general -> other`

These values are a **starting baseline**, not a promise of universal optimum.

### Secondary lanes

- **Anima** — relation-heavy / multi-character / tag + natural-language comparison/fallback lane
- **WAI Illustrious v17** — historical/comparison lane unless explicitly selected
- **NoobAI V-Pred** — separate advanced comparison profile; never pool with EPS

Do not flatten model-family Prompt grammar.

---

## 3. Learning principles

1. Start from exact model/profile and known author baseline.
2. Learn what each control does before optimizing it.
3. Explore with random seeds; lock a seed only when diagnosing a variable.
4. Do not call every mismatch a Prompt failure.
5. Separate:
   - concept presence
   - relation/binding
   - body-site
   - count
   - camera/visibility
   - style/finish
6. Change one meaningful variable at a time when diagnosing.
7. Add LoRA/support/weights because a specific failure needs them, not because a recipe says more is better.
8. Use Hires/ADetailer/inpaint/control as interventions with known purpose.
9. Preserve infotext/metadata/preset for successful or instructive cases.
10. One successful image is local evidence, not universal model truth.

---

# 4. Curriculum

## Stage10.0 — Environment and reproducibility basics

### Learn
- exact checkpoint/profile identification
- Forge Neo preset and infotext
- Sampler（Sampler＝ノイズから画像へ近づける計算方法）
- Steps（生成計算の反復回数）
- CFG（Promptへの従わせ方の強さ）
- resolution / aspect ratio
- Seed（最初のノイズの出発点）
- random-seed exploration vs fixed-seed diagnosis
- Positive / Negative Prompt fields
- metadata preservation

### Practice
- make one baseline NoobAI EPS preset
- generate several random seeds from one simple Prompt
- choose one seed and repeat it
- change only one parameter or one Prompt block
- compare before/after

### Exit
The learner can:
- reproduce their own generation closely enough for controlled iteration
- explain the purpose of Sampler / Steps / CFG / resolution / Seed
- distinguish exploration from controlled comparison

---

## Stage10.1 — Prompt fundamentals

### Learn
- Noob caption organization
- canonical tag vs Alias vs historical/model trigger
- runtime syntax / weight wrapper vs semantic tag
- General / Special roles
- quality/meta/rating tokens
- Positive vs Negative conditioning
- emphasis/weighting without cargo-cult stacking
- why longer is not automatically worse, but conflict/density can matter

### Practice
Build Prompt from Japanese intent using blocks:
1. count
2. character / identity
3. series
4. artist if intended
5. target Special / core action or state
6. General support
7. composition / camera / background / finish as needed

### Exit
The learner can:
- build a clean Prompt from Japanese intent
- explain every important block
- identify unknown or uncertain surfaces instead of guessing

---

## Stage10.2 — Composition / camera / visibility

### Learn
Keep separate:
- Frame — close-up / upper body / cowboy shot / full body etc.
- Viewpoint — front / side / behind / above / below etc.
- Orientation — torso/body direction, lean/twist when needed
- Visibility — whether the target body part/action is actually observable
- Background/scene — composition context, not semantic target identity

### Practice
- same subject, three framings
- same seed, change one viewpoint
- deliberately create and then correct a crop/occlusion failure
- compare Prompt change vs aspect-ratio/resolution change

### Exit
The learner can intentionally revise framing instead of blindly adding semantic tags.

---

## Stage10.3 — Hard / niche structural generation

For difficult/niche adult fictional content, do not judge only by genre-name presence.

### Decompose into predicates
- `presence` — requested object/state exists
- `actor` — who acts
- `target` — who/what receives the action
- `ownership` — whose body/object/appendage
- `body-site` — exact required location
- `relation` — contact / insertion / restraint / orientation etc.
- `count` — people / objects / body parts / simultaneous actions
- `visibility` — can the required relation be observed
- `source/destination` — for fluid/material relations
- `topology` — for restraint/device connection where intrinsic

### Practice ladder
1. unary/simple target
2. body-site-sensitive target
3. actor-target relation
4. exact-count target
5. composite target

### Exit
The learner can explain a failed image as a specific structural failure instead of only saying `違う`.

---

## Stage10.4 — Failure diagnosis and controlled iteration

Default diagnosis order:

1. exact model/profile
2. exact tag/trigger surface
3. visibility/crop
4. target presence
5. actor-target/body-site/count/relation
6. composition conflict
7. Negative collision
8. Prompt density/weight conflict
9. seed sensitivity
10. LoRA/context leakage
11. assisted-control/edit escalation

### Failure classes
- concept/recognition failure
- binding/relation failure
- body-site failure
- count failure
- camera/visibility failure
- composition conflict
- Negative collision
- LoRA/style/context leakage
- postprocess/repair regression

### Exit
The learner can choose the next change because of an observed failure class, not because of guesswork.

---

## Stage10.5 — Seed / Negative / weights / LoRA

### Seed
Use:
`random exploration -> promising seed -> fixed-seed diagnosis -> return to exploration`

Do not treat one fixed seed as reliability proof.

### Negative
Learn:
- exact-model author baseline first
- Negative is active conditioning, not harmless cleanup
- unusual anatomy/count targets may conflict with generic anatomy/count negatives
- remove a conflicting Negative before piling more positive tags

### Weight
Learn:
- emphasize only when there is a reason
- strong weight can alter surrounding composition/style
- weight is not a substitute for correct relation structure

### LoRA
Separate:
- character LoRA
- style LoRA
- pose/concept LoRA

Practical rule:
- one adapter first
- record name / base family / trigger / weight
- diagnose context leakage before adding another LoRA
- lower/remove LoRA before adding huge Negative stacks

### Exit
The learner can add/remove/retune LoRA without confusing adapter effects with base-model capability.

---

## Stage10.6 — Finishing and local repair

### Hires / upscale
Use after base structure is acceptable.
Understand:
- preserve vs redraw
- denoise as amount of second-stage change
- final repaired anatomy does not prove base generation was correct

### ADetailer
Use targeted detectors for:
- face
- hand
- person/body region when appropriate

Do not use repair to hide wrong actor/target/count/body-site when that relation is the learning target.

### img2img / inpaint
Learn:
- whole-image revision vs local repair
- mask scope
- denoise as preservation/redraw control
- repeated repair can damage identity or relation

### Exit
The learner can turn a structurally acceptable base into a finished image while explaining what was repaired after generation.

---

## Stage10.7 — Regional / control escalation

Escalation ladder:
1. plain Prompt
2. clearer actor/target/appearance wording
3. Forge Couple Basic
4. Forge Couple Advanced / Mask
5. ControlNet / pose / regional control where appropriate
6. local inpaint for remaining defects

### Key rule
Regional/control conditioning may solve spatial separation, but assisted success does not prove the base Prompt alone can bind the same scene.

### Anima fallback
Use Anima as a comparison lane when:
- multi-character ownership is central
- tag-only relation remains ambiguous
- concise factual natural-language relation may help
- current Anima regional/control tooling is useful

### Exit
The learner recognizes a practical Prompt-only ceiling and selects a targeted control tool instead of endlessly adding tags.

---

## Stage10.8 — Efficient daily workflow

### Learn
- reusable Forge Neo presets
- bounded X/Y/Z comparisons
- small seed batches
- Prompt variant matrices
- infotext/metadata retention
- naming successful recipes by purpose, not superstition
- keep local practical evidence separate from universal claims

### Exit
The learner can iterate quickly and still know what changed and why.

---

## Stage10.9 — Capstone / free generation

From a Japanese target description, independently:

1. choose NoobAI or justified fallback
2. create Prompt
3. choose appropriate size/settings
4. generate exploratory candidates
5. identify failure class
6. revise the smallest useful variable
7. add LoRA/support/control only when justified
8. repair/finish
9. preserve final metadata
10. explain the final workflow and remaining limitations

### Required capstone classes
At least:
- one ordinary/simple target
- one body-site/relation-sensitive target
- one composite or multi-actor difficult target

No fixed image-count quota exists.
The point is **independent control and diagnosis**, not grinding a checklist.

---

# 5. Stage10 completion criterion

Stage10 is complete when the learner can repeatedly demonstrate:

- settings literacy instead of unexplained copying
- Prompt construction from intent
- bilingual/tag understanding sufficient to inspect their own Prompt
- deliberate composition/framing control
- relation/body-site/count-aware evaluation
- failure classification
- controlled iteration
- model/profile selection
- Seed/Negative/weight understanding
- LoRA operation and leakage diagnosis
- Hires/ADetailer/img2img/inpaint use
- regional/control escalation
- reproducible result preservation
- independent completion of difficult/niche adult fictional 2D generations

Stage10 completion does **not** require:
- validating all 2,788 Special entries
- building an automatic success-rate model
- converting every HOLD into ACCEPTED
- using evaluator/tagger as relation ground truth
- exposing Stage10 functions in the v1 product UI

---

# 6. Relationship to DanbooruTagTool

DanbooruTagTool supports Stage10 by helping with:
- Prompt understanding
- Japanese/English tag discovery
- Special/General discovery
- canonical English output
- tag identity/meaning inspection

Stage10 teaches the missing practical layer:
- how models react
- how to compose scenes
- how to diagnose failure
- how to revise
- when to use LoRA/control/postprocess

Therefore:

**DanbooruTagTool = knowledge/discovery aid**

**Stage10 = real generation skill acquisition**

The product does not need to become an automatic Prompt optimizer or direct generator for Stage10 to succeed.

---

# 7. Relationship to KNOWLEDGE #44

KNOWLEDGE #44 is the evidence/knowledge supplier for Stage10.

Use #44 for:
- NoobAI / Anima / WAI model guidance
- Prompt/support/Negative knowledge
- hard/niche structural knowledge
- LoRA/Hires/ADetailer/img2img/Control/regional knowledge
- Japanese practical-source research
- unresolved HOLD questions

Stage10 can feed back durable observations.

Promotion rule:
- one successful image = local case
- repeated controlled result = stronger practical evidence
- only appropriately scoped evidence may update Claim Registry

---

# 8. Legacy Stage10 assets

The following remain useful but are **not** the current Stage10 definition:
- `STAGE_10_PREP.md`
- old Stage10 production A/B plans
- historical Issue #5
- Issue #30 evaluator/calibration evidence
- fixed-seed A/B infrastructure
- Multi Prompt Slots / Infinite Image Browsing
- evaluator/tagger pipeline
- Generation Profile
- WAI17 baseline tests
- `STAGE_10_KNOWLEDGE_HANDOFF.md`

Use them as:
- teaching material
- controlled-comparison tooling
- provenance/evidence
- failure-diagnosis aids

Do not use them as current Stage10 completion gates.

---

# 9. Immediate next action

Start at `Stage10.0 -> Stage10.1` with NoobAI XL 1.1 EPS.

First learning checkpoint:
1. install/select exact NoobAI XL 1.1 EPS
2. create a Forge Neo baseline preset
3. generate one simple tagged image with metadata preserved
4. generate several random seeds
5. lock one seed
6. change one Prompt/settings variable
7. explain the visible difference

Only after this loop is understood, move to body-site/relation-sensitive targets.

---

# 10. Checkpoint format

For meaningful learning checkpoints record:

- module (`10.x`)
- exact model/profile/runtime
- target intent
- actual Positive Prompt
- actual Negative Prompt
- relevant settings
- Seed(s)
- tools/LoRA/control state
- result
- failure class if any
- what changed
- lesson learned
- local-only case vs candidate durable knowledge

This record may be brief. The goal is recoverable learning, not paperwork.
