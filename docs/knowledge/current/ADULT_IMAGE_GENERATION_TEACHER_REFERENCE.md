# Adult Image Generation — Teacher Reference

Owner: Issue #44 `KNOWLEDGE:#44`  
Role: operational reference for teaching/debugging clearly adult, consensual/adult-fantasy image generation.

This file is not the evidence authority. It is the fast teaching view over the Claim Registry and focused research batches.

---

## 1. First question: what is actually failing?

Never begin with “add more tags”.

Classify the failure first.

| Failure | Typical symptom | First diagnostic | First intervention |
|---|---|---|---|
| concept/trigger | target idea absent | isolate the concept | canonical/model trigger test |
| identity | wrong character / face | A-only / B-only | simplify identity, native vs LoRA |
| count | wrong number of subjects/items | explicit count check | simplify scene; count stress test |
| binding | traits/roles swapped | subject ownership audit | stable IDs, regional text/reference |
| geometry | pose/contact shape wrong | pose/depth review | pose/depth/line control |
| visibility | target off-frame/hidden | camera/occlusion audit | camera/framing/depth |
| local anatomy | hand/limb malformed | relation already correct? | inpaint/detailer |
| style | wrong rendering language | style-only baseline | native style / style LoRA/reference |
| LoRA interference | added adapter breaks prior success | remove adapters one by one | weight/schedule/mask |
| Hires drift | good base, bad final | compare first vs second pass | inspect Hires sampler/denoise/etc. |

---

## 2. The minimum diagnostic package

Ask the learner for:

- exact checkpoint/profile
- original PNG with metadata if possible
- positive prompt
- negative prompt
- seed
- resolution/aspect ratio
- sampler/scheduler
- steps/CFG
- every LoRA + weight
- ControlNet/reference/regional state
- Hires/img2img/inpaint state

If metadata is unavailable, reconstruct only what can be verified and mark the rest unknown.

---

## 3. Model starting cards

These are starting baselines, not universal maxima.

### Anima Base / Aesthetic
- normal generation: about 30–50 steps
- CFG 4–5
- `er_sde` as neutral sharp-line reference
- Euler a / DPM++ 2M SDE GPU are alternative rendering behaviors
- weights often need stronger values than conventional SDXL
- tags and natural language can be mixed
- multi-character prompts benefit from identity + basic appearance rather than names only

### Anima Turbo
- CFG 1
- 8–12 steps
- fast exploration
- lower diversity / stronger default behavior

### NoobAI XL 1.1 EPS
- Euler a
- CFG 5–6
- 25–30 steps
- around 1MP
- native tag order matters as a baseline
- training-era tag exposure must be distinguished from current Danbooru canonical identity

### WAI Illustrious v17
- Forge Neo author baseline
- Euler a
- 15–30 steps
- CFG 5–7
- avoid giant quality stacks / long generic Negative stacks
- Hires example is model-scoped, not universal

---

## 4. Teaching prompt architecture

Keep four logical modules:

### CHARACTER
Who is present and identity-defining features.

### RELATION / SCENE
Count, role, position, contact/relation, camera, visibility.

### STYLE
Artist/style/rendering/quality.

### ENVIRONMENT
Background, props, lighting.

During diagnosis change only one module when possible.

---

## 5. When to change seed vs Prompt

### Change seed first when
- requested concepts consistently appear;
- identities are correct;
- relation is basically correct;
- only aesthetic layout/expression/background arrangement varies.

### Change representation/control when
- the same semantic failure repeats across several diagnostic seeds;
- count is repeatedly wrong;
- role/ownership repeatedly swaps;
- relation repeatedly disappears;
- target is consistently off-frame.

---

## 6. Character LoRA teaching

Test in this order:

1. base/native character if available
2. character LoRA only
3. unseen pose
4. unseen outfit
5. unseen background
6. alternate style
7. final scene
8. multi-character use if required

If only step 1–2 work, the LoRA has fidelity but weak editability.

Do not fix poor editability by only increasing LoRA weight.

---

## 7. Style LoRA teaching

Test:

1. style LoRA alone
2. same-seed weight sweep
3. unseen character
4. non-character content
5. unusual composition
6. character LoRA + style LoRA

Score:
- style fidelity
- identity/content preservation
- composition freedom
- prompt adherence
- leakage.

High style similarity with content lock is not full success.

---

## 8. Two-subject / relation diagnosis

Always check independently:

- count
- identity A
- identity B
- role ownership
- body-part ownership
- contact/relation
- camera visibility
- occlusion
- local anatomy

A scene containing both subjects can still fail binding completely.

---

## 9. Directional-language warning

Do not use left/right alone as proof of:
- actor/receiver
- body-part owner
- topology.

Anima community evidence shows frame-relative and subject-relative direction can invert across seeds.

When exact geometry matters:
- stable subject IDs
- pose/reference
- regional conditioning
are stronger tools.

---

## 10. Regional/control decision

### Need semantic separation
Use regional text/attention.

### Need LoRA/reference isolation
Use adapter localization where the runtime actually supports it.

### Need skeletal geometry
Use pose.

### Need front/back/overlap
Use depth.

### Need contour/layout
Use edge/line.

### Need only one local correction
Use inpaint/detailer.

Current Forge Neo Anima Regional Prompter:
- regional text: yes
- Region LoRA: no

Current ComfyUI:
- native experimental LoRA hooks
- mask-bound conditioning
- timestep ranges
- hook scheduling
provide a separate local/scheduled adapter research path.

---

## 11. Regional interaction warning

More isolation is not always better.

Strong isolation can:
- reduce identity bleed;
- create hard region boundaries;
- reduce inter-region awareness;
- damage natural interaction.

Teach the weakest regional strength that solves the actual contamination.

---

## 12. Staged conditioning

Advanced tool.

Use only after the constant Prompt is understood.

Useful test:
- minimal constant
- full constant
- minimal -> full later
- LoRA all steps
- LoRA late only

Potential use:
let early denoising establish scene structure while later conditioning adds style/detail.

Do not use scheduling to hide wrong count/role/geometry.

---

## 13. Negative Prompt diagnosis

Do not default to giant generic negatives.

Ask:
- is the unwanted feature actually from the positive concept/artist prior?
- does the Negative overlap the desired unusual anatomy/count?
- is the failure local and better repaired by inpaint?

Keep separate:
- ordinary Negative
- positive-prior entanglement
- NegPiP-like assisted suppression
- local postprocess.

---

## 14. Hires / finishing diagnosis

Before Hires:
- global semantics correct?
- count correct?
- identities correct?
- relation correct?
- anatomy acceptable enough?

Forge Hires is a configurable second generation pass, not a pure resize.

When Hires breaks a good source inspect:
- Hires checkpoint
- Hires sampler/scheduler
- denoise
- Hires prompt/negative
- CFG/steps
- adapter/control state.

---

## 15. Local repair rule

Use local repair if:
- global scene is accepted;
- defect is spatially limited.

Examples of defect classes:
- hand/finger
- face/identity detail
- small body region
- localized clothing/object detail.

Do not use a detailer to “fix”:
- wrong actor
- wrong target
- wrong count
- wrong global pose.

---

## 16. LoRA training teaching

Do not teach “train N steps”.

Teach:
- dataset effective diversity
- caption policy
- mutable vs intrinsic features
- rank/alpha/LR/duration interaction
- intermediate checkpoint saving
- fixed visual evaluation suite
- OOD/generalization testing.

Choose checkpoint from generation behavior, not loss alone.

---

## 17. Failure journal labels

Recommended top-level labels:

- CONCEPT_MISSING
- COUNT_WRONG
- IDENTITY_WRONG
- ATTRIBUTE_LEAK
- ROLE_SWAP
- BODY_SITE_OWNER_WRONG
- RELATION_MISSING
- GEOMETRY_WRONG
- WRONG_DEPTH_ORDER
- TARGET_OCCLUDED
- CAMERA_WRONG
- LOCAL_ANATOMY
- STYLE_DRIFT
- LORA_INTERFERENCE
- REGIONAL_BOUNDARY
- HIRES_DRIFT
- EDIT_FAILURE

A learner should be able to apply one primary label before changing settings.

---

## 18. One-session teaching template

### Question
One narrowly defined skill.

### Baseline
Exact reproducible configuration.

### Diagnostic seed set
Small fixed set.

### Evaluation predicates
Defined before generation.

### Single intervention
Only one main change.

### Result
Pass/fail per predicate.

### Conclusion
- possibility?
- reliability?
- salvageability?

### Next lesson
One unresolved variable.

---

## 19. Teacher response examples by failure class

### “Characters are mixing”
1. test each identity alone
2. test pair without LoRAs if model knows them
3. add LoRAs one at a time
4. simplify shared style/context
5. regional text
6. localized adapter/reference/inpaint

### “The relation is wrong”
1. strip style/background
2. keep count + IDs + relation + camera
3. multi-seed check
4. add pose/depth if geometry is limiting
5. restore style/identity modules afterward

### “It only works in one seed”
Treat as possibility, not reliability.

### “Hires ruins it”
Keep the accepted base image; diagnose the second pass independently.

### “Training loss looks good but LoRA is bad”
Compare saved intermediate checkpoints with the fixed evaluation suite.

---

## 20. Teacher readiness checklist

Before giving confident guidance, verify:

- exact model family/version known?
- tool/runtime supports the claimed feature?
- plain vs assisted capability distinguished?
- model-specific author baseline known?
- community advice labeled as community?
- one-variable test possible?
- result can be reproduced?
- any known HOLD/conflict relevant?

If not, teach the test rather than pretending the answer is settled.

---

## 21. Proxy / replacement teaching pattern

When the target character is not known natively or two LoRAs contaminate each other:

1. create a base pair whose geometry and interaction already work;
2. prefer a proxy with a similar silhouette/pose/large traits;
3. replace only the proxy region;
4. keep metadata synchronized;
5. audit relation again after replacement.

Teach four coupled controls:
- mask size
- base preservation
- local adapter/prompt pressure
- region overlap

Goal:
**minimum necessary local rewrite**, not maximum regional freedom.

