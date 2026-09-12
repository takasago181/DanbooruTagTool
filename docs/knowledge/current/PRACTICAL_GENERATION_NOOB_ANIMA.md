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
