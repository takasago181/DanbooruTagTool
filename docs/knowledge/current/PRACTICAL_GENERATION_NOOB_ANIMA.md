# PRACTICAL GENERATION — NoobAI / Anima

Owner: Issue #44 `KNOWLEDGE:#44`
Status: `CURRENT_OPERATIONAL_GUIDE / CLAIM_REGISTRY_WINS`

> This is the short operational layer. It does not override `CLAIM_REGISTRY.csv`, exact model author guidance, or HOLD status.

## 0. Current focus

Primary practical generation families:
1. **NoobAI XL 1.1 EPS** — tag-first workhorse
2. **Anima** — hybrid/explicit-relation workhorse

Secondary lanes:
- NoobAI XL V-Pred 1.0 — separate V-Pred rendering/inference lane
- Anima Turbo v1.1 — rapid exploration
- Anima Base v1.0 — flexibility / controlled work / LoRA training
- Anima Aesthetic v1.1 — consistency / default visual quality

WAI17 remains a useful comparison/reference lane, but NoobAI + Anima now receive priority for practical-generation knowledge expansion.

---

# 1. Which one do I start with?

## Start NoobAI EPS when
- the target is well represented by booru-style vocabulary
- character/artist/tag knowledge matters
- you want the mature SDXL/Illustrious LoRA/tool ecosystem
- you want familiar Forge Neo SDXL operation

## Start Anima when
- multiple actors or attribute ownership are central
- tag-only relation wording is ambiguous
- a concise natural-language relation can clarify the scene
- current Anima regional/control tooling may be useful
- you need the Base/Aesthetic/Turbo workflow

## Use both when
A target is important enough to compare generation families.
Do not force one family to solve every case.

---

# 2. NoobAI EPS 1.1 quick start

Author baseline:
- Sampler: `Euler a`
- Steps: `25–30`
- CFG: `5–6`
- Size: around SDXL 1MP

Good portrait starts:
- `832×1216`
- `896×1152`
- `768×1344`

Prompt organization:
`count -> character -> series -> artist -> target Special -> General support -> other`

Daily-use rule:
- begin with the target and minimum visible support
- do not paste the official `nsfw` Negative when the intended output itself is adult-rated
- keep unusual-anatomy/count negatives OFF until there is a reason to add them
- first diagnose without LoRA unless the LoRA is essential to the subject

Failure order:
1. exact model/checkpoint
2. exact tag/trigger surface
3. visibility/crop
4. target presence
5. actor/target/body-site/count
6. composition conflict
7. Negative collision
8. seed sensitivity
9. LoRA/context leakage
10. regional/inpaint assist

---

# 3. NoobAI V-Pred 1.0 quick start

Author baseline:
- Sampler: **Euler**
- Steps: `28–35`
- CFG: `4–5`
- Size: around SDXL 1MP

Important:
- this is not EPS with a different checkpoint filename
- runtime must actually use V-Pred settings
- current Forge Neo supports V-Pred metadata, but merged checkpoints can lose metadata assumptions

Use when:
- intentionally testing V-Pred
- comparing its color/contrast rendering hypothesis

Do not:
- copy EPS sampler/settings
- pool results with EPS as one model
- conclude V-Pred is globally superior from one dark image

---

# 4. Anima Turbo v1.1 quick start

Exact current file SHA-256:
`fba11953276b57edf59d1dc4f1857ac05aa079c56f982b4d7c20298d57d3f7eb`

Official role:
- rapid generation / Prompt iteration
- stronger default style and stability
- reduced diversity

Start:
- CFG `1`
- Steps `8–12`

Important:
- normal Negative conditioning is not a dependable control lane at CFG1
- same seed/prompt does not mean Base-like composition
- treat Turbo as its own generation profile

Best practical use:
- explore Prompt variants/seeds quickly
- find promising composition directions
- if structural fidelity matters, compare the promising Prompt on Base/Aesthetic rather than assuming Turbo outcome is final truth

---

# 5. Anima Base v1.0 quick start

Exact file SHA-256:
`bd43b7cffe1ed1153d9c41e7beb2f18cb1273eafbaa3af3edd6a173dc90a006e`

Official role:
- maximum flexibility/diversity
- strongest base for style flexibility
- official LoRA training base

Start:
- Steps `30–50`
- CFG `4–5`
- `er_sde` = neutral/sharp author default-like choice
- `euler_a` = softer/thinner lines
- `dpmpp_2m_sde_gpu` = more variable/creative
- `euler` = simple creative alternate

Use when:
- Turbo's default style is too strong
- relation/hybrid Prompt needs careful work
- developing/training an Anima LoRA
- doing controlled profile comparison

---

# 6. Anima Aesthetic v1.1 quick start

Exact file SHA-256:
`3c1868387a3a1ff504bbb87c33678321965ead381fcf87afbd0264daa600c082`

Official role:
- consistency
- stronger high-quality default visual style

Important Prompt rule:
- quality tags were stripped during its training fine-tune
- quality tags are not required
- `masterpiece, best quality` may remain
- avoid `score_*` in both Positive and Negative by default per author

Use when:
- visual consistency/default finish matters
- its style bias matches the picture

Switch back to Base when:
- you need more style diversity/flexibility
- Aesthetic's default look fights the target

---

# 7. Anima Prompt construction for difficult scenes

Official/high-confidence conventions:
- lowercase tag surfaces
- spaces instead of underscores except score tags
- `@artist`
- tag + natural language may be mixed
- identify multiple characters/basic appearance explicitly

Practical structure:
1. quality/meta/rating only as needed
2. subject count
3. identities
4. distinguishing appearance
5. target action/relation
6. camera/visibility
7. scene/background
8. short natural-language clarification if relation ownership remains ambiguous

For multi-character relation:
- prefer explicit actor labels over vague `another`/pronoun references
- do not depend on tag distance for ownership
- old BREAK-based character separation is not Anima semantic control

---

# 8. Multiple characters — escalation

1. plain Anima Prompt with explicit identities/attributes
2. add concise factual relation wording
3. Forge Couple Basic
4. Forge Couple Advanced/Mask
5. Anima Region/LLLite ControlNet when geometry/region itself is the bottleneck

Forge Couple rule:
- still state total subject count
- regional prompting cannot invent composition understanding the checkpoint lacks

---

# 9. LoRA rule

## NoobAI
- Noob/Illustrious-family LoRAs are candidates, not guaranteed matches
- check each LoRA's training base/model card
- start one adapter at a time

## Anima
- separate LoRA family from SDXL/Illustrious/Noob
- official training base = Anima Base
- do not assume SDXL LoRA portability

For both:
- if style/background/pose suddenly appears, suspect adapter context leakage
- lower/remove LoRA before adding huge Negative stacks
- loaded LoRA state is part of evidence identity

---

# 10. Finishing ladder

Do not start finishing tools before semantic structure is acceptable.

Recommended order:
1. base composition / relation
2. choose good seed/composition
3. LoRA/style adjustment
4. upscale/Hires or img2img refinement
5. ADetailer/inpaint for local defects
6. regional/control only if still required, or earlier if region separation is the actual core problem

ADetailer Neo:
- face detector -> face detail
- hand detector -> hand detail
- person segmentation -> broader person redraw

Do not use a repair tool to hide wrong count/relation/body-site.

---

# 11. High-resolution Anima

Official normal range reaches roughly 512²–1536².

Practical approach above comfortable native range:
- generate structure at supported size
- upscale mostly-preserve first
- use img2img/tiled refinement only when additional redraw/detail is needed
- keep denoise low enough when preservation is the goal

Exact denoise/upscaler values remain recipe-level until tested under the target profile/runtime.

---

# 12. Current unresolved questions worth image testing

NoobAI:
- EPS vs V-Pred on dark/contrast hard scenes
- rare Special activation
- actor-target/body-site/count ceiling
- Illustrious-LoRA cross-use reliability
- model-specific Negative collisions

Anima:
- tag-only vs concise hybrid relation success rate
- Base vs Aesthetic v1.1 vs Turbo v1.1 on hard relations
- exact profile-specific LoRA behavior
- high-resolution finishing best path
- Forge Couple escalation benefit

These remain HOLD/CANDIDATE until controlled local evidence exists.

---

# 13. Restore reading

For practical Noob/Anima work:
1. this file
2. `../research/BATCH_L_NOOB_ANIMA_PRACTICAL_GENERATION_DEEP_DIVE_20260913.md`
3. `../research/BATCH_M_JAPANESE_PRACTICAL_SOURCE_AUDIT_NOOB_ANIMA_20260913.md`
4. `CLAIM_REGISTRY.csv`
5. `VERSION_FRESHNESS_LEDGER.csv`
6. exact upstream source only as needed

---

## 14. 2026-10-02 source refresh — newly pinned operational notes

These are current upstream facts promoted into the Claim Registry. They do not close the image-test HOLDs for binding/count/Negative/LoRA interaction.

### Anima
- Prompt weighting is supported, but the author explicitly says it needs stronger weights than typical SDXL; the model-card example uses `(chibi:2)`. Treat old SDXL weight habits as a starting hypothesis, not a transferable rule.
- Training used random tag dropout. Do not assume that restating every visible property is necessary; extra tags can still create unnecessary semantic workload.
- Pure natural-language Prompting should be descriptive; the author recommends roughly two sentences or more. Tags and natural language may be mixed.
- For multiple characters, write each identity plus basic appearance. A bare list of names is specifically called out as confusing.
- Base is intentionally neutral/plain without artist or quality guidance. Aesthetic and Turbo have stronger built-in visual priors. Turbo uses CFG 1 / 8–12 steps and sacrifices diversity for stability/default style.
- For Anima LoRA training, use Base; do not train the LLM adapter. Rank-32 LoRA author guidance suggests `2e-5` as a starting learning rate, not a universal optimum.

### NoobAI V-Pred
- Current author guidance remains CFG 4–5 / 28–35 steps / Euler.
- The card describes native-tag plus natural-language captioning, but this does not make V-Pred Prompt behavior interchangeable with Anima or EPS.

### Forge Couple / Forge Neo
- Forge Couple supports Anima and still recommends keeping total subject count in every region.
- It cannot compensate for a checkpoint that does not understand the requested composition.
- Dynamic-Prompts-like preprocessing can break separators/common Prompt handling; record extension state in reproducibility evidence.
- Forge Couple can be disabled during Hires Fix via compatibility mode, so base pass and Hires pass may not share the same regional conditioning.
- Forge Neo currently documents Anima Region ControlNet plus LLLite ControlNet support for SDXL/Anima. Treat this as assisted control, not Prompt-only evidence.

---

## 15. Community evidence layer — 2026-10-02

Community evidence is now tracked separately from author guidance.

High-value working hypotheses:
- For Anima multi-character prompts, write each subject as a closed sentence with identity + appearance + action when flat tag lists start leaking attributes.
- Do not treat `left side:` or a colon as a semantic binding operator by itself.
- Use tags for canonical/common attributes and add short prose only where geometry, ownership, relation, or screen position is not cleanly expressible by tags.
- Multi-character accessory leakage can remain even when hair/eye/skin identity looks correct.
- Treat multi-character LoRA competition as a separate failure axis from checkpoint-native character binding.
- For Anima finishing, avoid assuming SDXL Hires recipes transfer unchanged; compare low-denoise img2img/tiled refinement against the base pass.
- LoRA training data should vary crop/view/pose/background/clothing enough to prevent accidental welding of context into identity.

These are CANDIDATE/community practices, not family-wide defaults. See:
`../research/BATCH_O_COMMUNITY_PRACTICE_HARVEST_20261002.md`.

---

## 16. Community-controlled tag / Negative findings — 2026-10-02

Use these as diagnostic hypotheses, not universal defaults.

### Tags vs natural language
- Prefer a known compact tag when it cleanly represents the concept.
- Add prose when the desired relation/geometry/position has no adequate tag.
- Descriptive English can accidentally materialize ambiguous nouns as visible objects.
- If a specific garment/concept name repeatedly fails, test the defining visual structure without the name before escalating weights.
- A semantically narrow tag may invoke a much broader learned visual prior; Danbooru meaning and generation effect remain separate.

### Context confounds
- A “fixed” style/pose/composition block can already encode the concept being tested.
- When a tag appears weak, first remove overlapping instructions before concluding that the tag is unknown.
- Derivative checkpoints can differ in how local a one-tag change remains.

### Negative
- A Negative term is not guaranteed to be ignored merely because its target is absent.
- Targeted Negative edits should be tested with same-seed ON/OFF pairs.
- Do not use the WAI-Anima community result as proof for official Anima/Noob/WAI; keep family/version scope.

### Regional Prompter
Current 2026-09-04 runtime documentation:
- Forge Neo + Anima Latent: supported
- Forge Neo + Anima Attention: supported
- Anima Region LoRA: unsupported
- Anima regional Attention is not SD/SDXL 75-token chunk splitting.

Research detail:
`../research/BATCH_P_COMMUNITY_TAG_NEGATIVE_RUNTIME_20261002.md`.

---

## 17. Illustrious / NoobAI community layer — 2026-10-02

Working practices from public-user evidence:

- When a character LoRA copies the training set's background/style too aggressively, treat the dataset as entangled before trying to repair everything with Prompt/Negative changes.
- Vary viewpoint, crop, pose, clothing, background and style when those attributes are supposed to remain changeable.
- Caption mutable/context/style factors separately when the trigger should represent identity rather than the entire training-image recipe.
- Cross-derivative LoRA loading is only a compatibility experiment; successful loading does not establish faithful concept transfer.
- Fixed-seed step/CFG sweeps are useful for a single exact checkpoint/runtime, but user-preferred values are recipe evidence rather than model-family truth.
- Same seed across different checkpoints is useful for visual comparison, not a controlled same-latent reliability proof.

Details:
`../research/BATCH_Q_ILL_NOOB_LORA_COMMUNITY_MAP_20261002.md`.

---

## 18. Multi-LoRA failure decomposition — 2026-10-02

When two characters/LoRAs blend, split the diagnosis:

1. **global contamination**
   - one LoRA weight dominates;
   - a weighted/redundant hair or color instruction spills across the image;
   - repeated synonymous action/style pressure consumes prompt capacity.

2. **binding failure**
   - both identities are present but clothes/accessories are assigned to the wrong actor;
   - fixing global color leakage does not necessarily fix ownership.

Practical test order:
- equal LoRA strengths;
- remove duplicate/weighted character attributes;
- remove contradictory framing;
- preserve genuinely necessary style tokens;
- compare same seeds;
- only then escalate to regional/inpaint reconstruction.

Do not call a postprocessed per-character inpaint success “plain two-character binding success”.

Research detail:
`../research/BATCH_R_ADVANCED_COMMUNITY_FAILURE_DIAGNOSTICS_20261002.md`.

---

## 19. Tag generation-effect diagnostics — 2026-10-02

When evaluating a tag/prompt surface, record more than “worked / didn't work”:

1. **canonical meaning** — what the tag means in Danbooru;
2. **activation strength** — how much the image changes;
3. **semantic fidelity** — whether that change matches the intended meaning;
4. **spillover** — pose/clothing/background/identity changes outside the target;
5. **context sensitivity** — what happens when scene/style/visibility instructions compete;
6. **model/profile** — exact checkpoint/derivative/runtime.

Practical lessons from community-controlled tests:
- a large visual change can still be the wrong semantic effect;
- extreme framing often benefits from canonical framing tags;
- visibility-conflicting descriptions can defeat a correct framing tag;
- Anima/WAI-Anima should not inherit Illustrious underscores/BREAK/weight habits blindly;
- for multi-character binding, subject-specific sentences are a strong candidate when positional tag grouping becomes fragile;
- quality/meta tags can alter face/rendering priors, not only perceived detail.

Research:
`../research/BATCH_S_TAG_STYLE_COMPOSITION_COMMUNITY_20261002.md`.

---

## 20. LoRA caption and stacking diagnostics — 2026-10-02

For LoRA work, ask two separate questions:

**Training/caption allocation**
- What should the trigger alone reproduce?
- What must remain switchable?
- Which attributes vary in the dataset?
- Which attributes are explicitly captioned?
- Is the dataset itself generated by the same model and therefore carrying its biases?

**Inference interference**
- What changes with LoRA OFF?
- What changes with exactly one LoRA?
- What new unrequested content appears as adapters are stacked?
- Does weight change only style, or also identity/clothing/composition/background?

Do not assume:
- more training captions are always better;
- fewer captions are always better;
- more LoRAs mean more quality;
- LoRA weight is only “effect strength”;
- synthetic training data is neutral with respect to the base model's concept correlations.

Research:
`../research/BATCH_W_LORA_CAPTION_STACKING_COMMUNITY_20261002.md`.

---

## 21. Parameter and high-resolution testing — 2026-10-02

When tuning Anima:
- use author settings as the first baseline;
- change one variable at a time;
- treat steps as a diminishing-return curve, not a quality score;
- record resolution whenever judging CFG/shift/sampler;
- do not assume a high-resolution rescue LoRA helps at standard resolution;
- test helper LoRA strength at the resolution where the failure actually occurs.

For character-LoRA repair:
- diagnose what survived the first training pass;
- replace weak/confounded training examples rather than only adding more images;
- generate candidate data deliberately for the missing attribute/coverage axis;
- manually reject incidental props/artifacts before retraining;
- remember recursive synthetic training can amplify both target traits and generator biases.

Research:
`../research/BATCH_X_PARAMETER_HIGHRES_DATASET_COMMUNITY_20261002.md`.

---

## 22. Noob exact identity and dataset freshness — 2026-10-02

Official remote identities:
- EPS 1.1 SHA256: `6681e8e4b134c81f16533acedb0d406d7e5e366e1624b4105178c64d00b05d51`
- V-Pred 1.0 SHA256: `ea349eeae87ca8d25ba902c93810f7ca83e5c82f920edf12f273af004ae02819`

NoobAI author documentation places Danbooru exposure at its training-era snapshot (v1.0 approximately before 2024-10-23) plus e621-2024-webp-4Mpixel.

Therefore:
- current tag existence/post_count does not prove exposure;
- renamed/new tags need trigger-freshness testing;
- semantic identity stays current Danbooru authority even when an older model surface generates better.

NoobXL-specific normal/depth/canny ControlNets are documented as released assisted-control options.

Research:
`../research/BATCH_AC_NOOBAI_EXACT_IDENTITY_DATASET_CONTROL_20261002.md`.

---

## 23. Structural-control escalation — 2026-10-02

Choose assistance by failure type:

- pose wrong -> Pose Control
- front/back or overlap wrong -> Depth
- contour/layout wrong -> Lineart/Edge
- character/LoRA leakage -> Region/Mask
- only one local area remains wrong -> Inpaint

Do not use pose control as a substitute for actor/target/ownership reasoning.

Evidence identity must retain:
- preprocessor
- preprocessor output
- control type
- control strength/schedule
- edit mask
- whether success existed before assistance

Research:
`../research/BATCH_AD_POSE_DEPTH_REGION_INPAINT_ESCALATION_20261002.md`.

---

## 24. Count and camera diagnosis — 2026-10-02

If a target looks wrong, ask separately:

- target present?
- exact count correct?
- owner/actor correct?
- relation correct?
- relevant region visible?
- camera angle lets you judge it?

Do not try to fix exact count by endlessly rephrasing the same number.
Do not try to fix camera failure by adding more semantic target tags.

Count and viewpoint are separate capabilities.

Research:
`../research/BATCH_AE_COUNT_CAMERA_VISIBILITY_LIMITS_20261002.md`.

---

## 25. Anatomy vs relation — 2026-10-02

Separate:
- relation correct?
- local anatomy correct?
- depth/occlusion correct?

If relation is right and only a hand/local region is broken:
use local repair.

If anatomy is clean but ownership/relation is wrong:
do not waste time on detailers/inpaint first.

If the target exists but is hidden:
classify visibility/occlusion failure.

Research:
`../research/BATCH_AF_ANATOMY_OCCLUSION_LOCAL_REPAIR_20261002.md`.

---

## 26. Secondary-source conflict handling — 2026-10-02

If a blog/community recipe conflicts with the exact current model card:
- keep the recipe as a separate experiment;
- do not average settings;
- do not silently replace the author baseline;
- record the exact checkpoint/runtime used by the community source.

Current example:
a recent NoobAI review recommends V-Pred settings that conflict with current V-Pred 1.0 author guidance.

Use author baseline first, secondary recipe second.

Research:
`../research/BATCH_AH_ILL_NOOB_MULTI_SUBJECT_AND_SOURCE_CONFLICT_20261002.md`.

---

## 27. Character and style reproduction — 2026-10-02

### Character LoRA
Do not ask only “does it look like the character?”

Score:
- identity fidelity
- unseen pose
- unseen background
- outfit mutability
- camera mutability
- expression mutability
- ability to accept a different style

### Style LoRA
Score:
- line/style fidelity
- coloring/shading/texture fidelity
- subject/content preservation
- composition freedom
- identity preservation
- prompt responsiveness

### Character + Style LoRA
Test each adapter alone before combining.
Combined success is not implied by independent success.

For Anima:
- train against Base as the official default;
- freeze the LLM adapter;
- preserve native artist-tag response as an explicit evaluation metric;
- do not judge layer-training variants only on training-domain reconstruction.

Research:
`../research/BATCH_AI_CHARACTER_STYLE_REPRODUCTION_LORA_20261002.md`.

---

## 28. LoRA capacity and character/style evaluation — 2026-10-02

Do not optimize LoRA by rank alone.

Record:
- rank
- alpha
- LR
- target modules
- dropout
- captions
- steps/timestep distribution
- trainer path

Character evaluation:
- identity: human + anime-domain CCIP where applicable
- editability: unseen pose/background/outfit/camera/style

Style evaluation:
- style similarity
- content preservation
- identity preservation
- composition freedom

CLIP alone is not sufficient as a style metric.

Before training a character LoRA, consider a reference-adapter baseline where compatible.

Research:
`../research/BATCH_AJ_LORA_CAPACITY_REFERENCE_AND_EVALUATION_20261002.md`.

---

## 29. Character/style dataset curation — 2026-10-02

Character LoRA data should be audited for:
- wrong-character images
- duplicates
- crop/framing distribution
- front/side/back coverage
- pose/expression coverage
- outfit/background correlation
- source domain
- synthetic/editor artifacts

Anima does not require one single caption surface; its base training used multiple caption variants per image.

Do not use image count as the main quality metric.
Use coverage of intended mutable axes.

Research:
`../research/BATCH_AK_CHARACTER_STYLE_DATASET_CURATION_20261002.md`.

---

## 30. Native style before Style LoRA — 2026-10-02

Before training a Style LoRA:

1. test the native artist/style surface;
2. use a neutral fixed prompt;
3. test multiple seeds;
4. test different subjects/content;
5. test with the intended character LoRA.

Train/apply Style LoRA only when native style is absent, unstable, insufficiently faithful, or you need a reusable custom style.

Do not judge raw artist strength while simultaneously changing quality/year/series modifiers.

Research:
`../research/BATCH_AL_NATIVE_STYLE_VS_STYLE_LORA_20261002.md`.

---

## 31. Character identity vs outfit variants — 2026-10-02

Decide the adapter target before training:

- identity-only
- identity + default outfit
- identity + multiple switchable outfits

Do not score all three with one criterion.

If clothes should change later, treat them as independently conditioned/mutable during dataset design.
If default clothes should be trigger-implicit, bind them deliberately and test whether alternate clothes remain possible.

Separate outfit LoRAs can change identity; test them as multi-adapter interference.

Research:
`../research/BATCH_AM_CHARACTER_IDENTITY_OUTFIT_FACTORING_20261002.md`.

---

## 32. Character identity-core tests — 2026-10-02

A character is not “correct” only because the hair color and default outfit match.

Define:
- identity_core
- default presentation
- mutable variants

Then deliberately change:
- outfit
- background
- style
- camera
- viewpoint

and verify identity survives.

Use CCIP as an anime identity screening signal where applicable, but pair it with feature-level review.

Research:
`../research/BATCH_AN_CHARACTER_IDENTITY_CORE_EVALUATION_20261002.md`.

---

## 33. Base family changes LoRA behavior — 2026-10-02

Do not assume the same dataset produces the same kind of LoRA on:
- Illustrious/WAI
- NoobAI
- Anima

Compare independently trained adapters.

Watch for:
- identity vs style balance
- source-style entanglement
- palette/tint leakage
- editability
- default outfit binding

Do not copy the same hyperparameters across architectures merely to make the comparison “fair”; use each family's valid baseline and keep the dataset/evaluation target fixed.

Research:
`../research/BATCH_AO_ILL_NOOB_CHARACTER_STYLE_TRAINING_20261002.md`.

---

## 28. Character/style evaluation stack — 2026-10-02

### Character LoRA
Use separate metrics for:
- anime identity (CCIP/reference review)
- pose/composition
- prompt editability
- background/style independence

### Style LoRA
Use separate metrics for:
- style similarity (CSD/DiffSim-like)
- content/identity preservation
- OOD subject generalization
- composition freedom

### Adapter training
Do not tune only by rank or file size.
Rank/dim, alpha, LR and duration interact.

LoRA/LoCon/LoHa/LoKr are experimental choices, not quality tiers.

Research:
`../research/BATCH_AJ_CHARACTER_STYLE_EVALUATION_AND_LYCORIS_20261002.md`.

