# Adult Image Generation Teaching Curriculum

Owner: Issue #44 `KNOWLEDGE:#44`  
Scope: clearly adult, consensual/adult-fantasy image generation  
Primary practical families: Anima / NoobAI XL / Illustrious-WAI  
Purpose: make the knowledge corpus teachable, testable and usable during real generation.

---

## 0. Teaching doctrine

Do not teach by handing over one giant “best prompt”.

Teach:
1. what the current target is;
2. what the model/tool is expected to control;
3. what failed;
4. what single change is being tested;
5. what the result proves;
6. what remains uncertain.

Every exercise distinguishes:

- **Possibility** — one successful sample exists.
- **Reliability** — repeated success under fixed evaluation.
- **Salvageability** — failed generation can be repaired through assisted tools.

A polished rescued image is not evidence of plain-model reliability.

---

## 1. Module A — Runtime literacy

### Learner must understand
- exact checkpoint/profile
- seed
- resolution/aspect ratio
- sampler/scheduler
- steps
- CFG
- positive/negative conditioning
- LoRA loading and weights
- Hires/img2img/inpaint
- metadata/workflow preservation

### Exercise
Generate one simple adult single-subject image with:
- one fixed seed
- one alternate seed
- one sampler change

### Pass condition
Learner can explain which variables changed and can reproduce the baseline from metadata.

---

## 2. Module B — Prompt decomposition

Teach four modules:

### CHARACTER
Identity and stable appearance.

### RELATION / SCENE
Count, role, position, contact/relation, camera, visibility.

### STYLE
Artist/style/rendering/quality.

### ENVIRONMENT
Background, props, lighting.

### Exercise
Start from a reference and write a **structure-only** representation without character/style/background detail.

Then add:
1. identity;
2. style;
3. environment
one at a time.

### Pass condition
Learner can identify which added module first causes a failure.

---

## 3. Module C — Seed literacy

### Exercise
Run the same minimal prompt over a fixed small seed set.

Label each output:
- semantic pass/fail
- composition variation
- local anatomy issue
- visibility issue

### Pass condition
Learner can distinguish:
- repeated semantic failure -> change representation/control
from
- seed-level aesthetic variation -> search seeds.

---

## 4. Module D — Single-character reproduction

### Skills
- native model identity
- character LoRA
- reference adapter
- character editability

### Evaluation
- identity
- unseen pose
- unseen outfit
- unseen background
- alternate style
- camera changes

### Pass condition
Character remains identifiable while at least several non-identity factors remain editable.

---

## 5. Module E — Style reproduction

### Skills
- native artist/style surface
- style LoRA
- reference-style conditioning
- style/content leakage diagnosis

### Evaluation
- style fidelity
- content preservation
- character identity preservation
- composition freedom
- OOD subject generalization

### Pass condition
Style transfers to content unlike the training/reference examples without simply reproducing their subjects/layouts.

---

## 6. Module F — Two-subject binding

Begin without LoRAs when possible.

### Skills
- exact count
- identity separation
- relative position
- role ownership
- body-part ownership
- visibility/occlusion

### Exercise ladder
F1 — two distinct adults, no interaction  
F2 — simple relative pose  
F3 — simple contact/relation  
F4 — stronger overlap/occlusion

### Pass condition
Learner can label whether failure is:
- count
- identity
- role
- geometry
- visibility
- anatomy.

---

## 7. Module G — Adult relation grammar

Treat complex adult scenes as atomic predicates.

### Entity
- subject_count
- subject_identity

### Binding
- role_owner
- attribute_owner
- target_site_owner

### Relation
- contact/relation
- source_destination
- connectivity/topology

### State
- exact count
- simultaneous state
- visibility

### Integrity
- local anatomy
- context/style leak
- censor/watermark prior

### Pass condition
Learner can score a generated image predicate-by-predicate instead of only “looks right / wrong”.

---

## 8. Module H — LoRA interference

### Exercise
Use:
- base
- LoRA A
- LoRA B
- A+B global

Same seeds/settings.

Score:
- identity
- style
- composition
- prompt adherence
- cross-character contamination.

### Pass condition
Learner can identify adapter interference before trying Regional.

---

## 9. Module I — Regional/control escalation

Teach mechanisms separately.

### Regional text / attention
Separates textual conditioning by area.

### Adapter localization
Localizes LoRA/reference influence where supported.

### Pose/depth/line
Constrains geometry.

### Inpaint
Locally reconstructs an accepted global composition.

### Important Anima rule
Current Forge Neo Regional Prompter:
- regional Latent/Attention supported;
- Region LoRA unsupported.

ComfyUI has separate experimental hook/mask/timestep primitives.

### Pass condition
Learner can state which capability the chosen tool actually supplies.

---

## 10. Module J — Separation versus interaction

Regional control creates a tradeoff:

- stronger separation can reduce identity bleed;
- too much isolation can make subjects look disconnected or produce hard boundaries.

### Exercise
Compare:
- no regional
- soft regional
- stronger regional

Score:
- identity separation
- relation/contact
- region boundary artifacts
- whole-image coherence.

### Pass condition
Learner chooses the weakest regional intervention that solves the actual contamination.

---

## 11. Module K — Staged conditioning

Advanced only.

### Exercise
Compare:
- constant minimal prompt
- constant full prompt
- minimal -> full schedule
- LoRA all steps
- LoRA late only

### Purpose
Test whether early structure and late rendering pressure can be separated.

### Pass condition
Learner does not use scheduling to hide a fundamentally wrong count/role/geometry.

---

## 12. Module L — Local repair

Only after global semantics pass.

### Tools
- masked inpaint
- detailer
- pose/depth-assisted local reconstruction

### Exercise
Take:
- one relation-correct image with a local anatomy failure
- one anatomy-clean image with a relation failure

Use local repair only on the first.

### Pass condition
Learner understands that anatomy repair cannot fix semantic binding.

---

## 13. Module M — High-resolution finishing

### Order
1. structural acceptance
2. local repair
3. Hires/img2img/enhancement
4. conservative final upscale
5. final audit

### Evaluate final vs source
- identity drift
- style drift
- anatomy drift
- relation drift
- new hallucinated details.

### Pass condition
Learner can tell whether the finishing stage improved resolution or silently changed the image.

---

## 14. Module N — LoRA training

### Character LoRA
Train for:
- identity fidelity
- editability
- context independence.

### Style LoRA
Train for:
- style fidelity
- content diversity
- OOD transfer.

### Multi-character target
Represent:
- solo identity
- coexistence
- interaction
as separate dataset states.

### Evaluation
Save intermediate checkpoints.
Use a fixed prompt/seed suite.
Do not select from loss alone.

### Pass condition
Learner can choose an intermediate checkpoint based on visual/generalization evidence and explain why later training may be worse.

---

## 15. Module O — Research-grade practice

Every serious experiment records:
- exact checkpoint/hash
- runtime/version
- prompt modules
- seed set
- sampler/scheduler
- CFG/steps
- resolution
- LoRAs/weights
- control masks/preprocessors
- schedules
- Hires/img2img/inpaint state.

Keep:
- successes
- failures
- original PNG/workflow metadata.

### Pass condition
A later session can reproduce the experiment without relying on memory.

---

## 16. Teacher diagnostic response pattern

When the learner says “it doesn’t work”, answer in this order:

1. **What is failing?**  
   Count / identity / role / geometry / visibility / anatomy / style / finishing.

2. **What already works?**  
   Do not change successful axes unnecessarily.

3. **What is the lowest intervention?**  
   Seed -> Prompt cleanup -> weight -> LoRA -> Regional -> pose/depth -> inpaint.

4. **What should remain fixed?**  
   Model, seed set, resolution and unrelated settings.

5. **What result would confirm the hypothesis?**  
   Define before generating.

6. **What does success prove?**  
   Possibility / reliability / salvageability.

---

## 17. Graduation standard

A learner is no longer a beginner when they can:

- reproduce an exact baseline;
- classify a failure correctly;
- avoid giant uncontrolled Prompt changes;
- run same-seed A/B tests;
- keep identity/style/scene modules separate;
- understand LoRA interference;
- know when Regional helps and when it harms interaction;
- use inpaint only for local residual defects;
- preserve metadata;
- explain whether a final success was native, assisted or repaired.

Advanced competence requires:
- multi-character LoRA diagnosis;
- relation/body-site/visibility scoring;
- staged conditioning;
- LoRA checkpoint evaluation;
- reproducible dataset/training experiments.

---

## 18. Canonical reading order

1. `PRACTICAL_GENERATION_NOOB_ANIMA.md`
2. `../catalog/05_HARD_NICHE_ADULT_GENERATION.md`
3. `../research/BATCH_AP_ADULT_PRACTICAL_LEARNING_METHOD_20261002.md`
4. `../research/BATCH_AQ_REGIONAL_LEARNING_AND_REPRODUCIBILITY_20261002.md`
5. `../research/BATCH_AR_STAGED_CONDITIONING_AND_LEARNING_20261002.md`
6. `../research/BATCH_AS_LORA_TRAINING_EVALUATION_METHOD_20261002.md`
7. `../research/BATCH_AT_TEACHING_CURRICULUM_AND_NATIVE_HOOKS_20261002.md`

This file is the teaching map; Claims and focused research files remain the evidence authority.

---

## 19. Dataset bias exercise

Take one character/style dataset and create a coverage table for:
- rendering style
- background
- outfit
- camera
- pose
- partner/role
- props.

Identify the most constant mutable factor.

Create one validation prompt that attempts to change it.

### Pass condition
Learner can predict which factor is most likely to become welded into the LoRA and can propose a dataset/caption correction before touching optimizer settings.

