# Model-Family Knowledge

## Current practical priority

For practical-generation research, the current priority is now:

1. **NoobAI XL 1.1 EPS** — tag-first primary workhorse
2. **Anima official family** — hybrid / relation-explicit primary family
3. NoobAI V-Pred 1.0 — separate alternate inference lane
4. WAI Illustrious v17 — comparison/reference and existing local baseline

This does not make generation-effectiveness Claims without image evidence. It changes research/operational emphasis only.

Current practical entry:
`../current/PRACTICAL_GENERATION_NOOB_ANIMA.md`

Deep research:
`../research/BATCH_L_NOOB_ANIMA_PRACTICAL_GENERATION_DEEP_DIVE_20260913.md`

Japanese source audit:
`../research/BATCH_M_JAPANESE_PRACTICAL_SOURCE_AUDIT_NOOB_ANIMA_20260913.md`

---

## NoobAI XL 1.1 EPS — primary tag-first lane

Exact author facts:
- CFG 5–6
- Steps 25–30
- Euler a
- around SDXL 1MP sizes
- native caption organization: `count -> character -> series -> artists -> special -> general -> other`
- trained using current/full Danbooru + e621 native tag captions
- project-defined quality/date surfaces are model Prompt conventions, not Danbooru score metadata

Practical role:
- broad anime/character/tag knowledge
- niche/Special vocabulary exploration
- mature SDXL/Illustrious runtime and LoRA ecosystem
- first-pass tag-centric generation in Forge Neo

Important adult-workflow caution:
The author example Negative contains `nsfw`; this is not suitable as a blind default when the intended image is adult-rated. Author recipes are intent/profile scoped.

Known HOLD:
- exact rare Special activation rate
- actor-target/body-site/topology/count ceiling
- canonical/Alias/historical trigger response
- broad+specific support effect
- exact anatomy/count Negative effects
- exact Illustrious-LoRA cross-use reliability

## NoobAI V-Pred 1.0 — separate inference lane

Exact author facts:
- CFG 4–5
- Steps 28–35
- **Euler**
- author warns other samplers do not work properly
- separate V-Pred prediction/inference regime
- same native caption organization family
- model description includes Danbooru + e621 and natural-language captions

Runtime:
Current Forge Neo supports V-Pred/Zero-SNR metadata handling for advanced SDXL models.
Model merges can lose metadata assumptions; runtime identity must be checked when output becomes noise/incorrect.

Community hypothesis, not promoted fact:
- V-Pred is often reported as better for darker / higher-contrast rendering than EPS.

Never pool EPS and V-Pred results as if they were one model profile.

---

## Anima official family — primary hybrid/relation lane

Official family properties:
- anime / illustration focus; realism is not its strength
- Danbooru-style tags + natural language + mixed Prompt
- lowercase tag surfaces and spaces generally preferred; score tags keep underscore
- Gelbooru form may be preferred when exact surfaces differ
- artist surface uses `@artist`
- official grouping: quality/meta/year/safety -> count -> character -> series -> artist -> general
- explicit multi-character identity/basic appearance context is recommended

### Anima Base v1.0

Current exact official file SHA-256:
`bd43b7cffe1ed1153d9c41e7beb2f18cb1273eafbaa3af3edd6a173dc90a006e`

Official role:
- maximum flexibility/diversity/style adherence
- official LoRA training base

Normal generation guidance:
- 30–50 steps
- CFG 4–5
- roughly 512²–1536² supported range

Author sampler descriptions:
- er_sde: neutral / flat-color / sharp-line reasonable default
- euler_a: softer/thinner; can trend 2.5D
- dpmpp_2m_sde_gpu: more variable/creative
- euler: simple creative alternate

### Anima Aesthetic v1.1

Current exact official file SHA-256:
`3c1868387a3a1ff504bbb87c33678321965ead381fcf87afbd0264daa600c082`

Official family role:
- stronger default consistency / quality

Important Prompt behavior:
- Aesthetic training removed quality tags from captions
- positive quality tags are not required
- `masterpiece, best quality` may remain
- author recommends avoiding `score_*` in Positive and Negative

### Anima Turbo v1.1

Current exact official file SHA-256:
`fba11953276b57edf59d1dc4f1857ac05aa079c56f982b4d7c20298d57d3f7eb`

Official role:
- rapid iteration
- CFG 1
- 8–12 steps
- increased stability / stronger default style
- reduced diversity
- author recommends starting with Turbo for fast iteration

Critical operational boundary:
CFG1 changes the practical role of ordinary Negative conditioning. Do not apply a normal Base/Aesthetic Negative workflow blindly.

Japanese current comparisons reinforce that Turbo is a distinct generation profile, not simply Base rendered faster. Exact structural superiority remains test-required.

### Anima practical relation knowledge

High-value current practical pattern:
- identify actors explicitly
- preserve exact count
- give distinguishing visible attributes when multiple actors matter
- use concise factual relation wording when tags alone are ambiguous
- avoid relying on Prompt-token distance for ownership
- old BREAK-based SDXL separation tricks are not semantic binding

This is a serious intervention lane, but tag-only vs hybrid success rate remains HOLD until controlled local tests.

### Anima assisted-control ecosystem

Current Forge Neo + Forge Couple supports:
- Forge Couple Basic / Advanced / Mask
- Anima support
- Anima LLLite
- Anima Region ControlNet

Escalation:
`plain explicit Prompt -> concise hybrid relation -> Forge Couple Basic -> Advanced/Mask -> ControlNet when geometry is the bottleneck`

Assisted success remains separate from plain-Prompt capability.

### Advanced/watch Anima derivatives

Current Forge Neo documents support for community Anima 2.9B / 3.8B variants.
These remain `ADVANCED_WATCH`, not current default project baselines.
Do not silently transfer official 2B Base/Aesthetic/Turbo guidance to them.

---

## NoobAI vs Anima — practical division

### Prefer NoobAI first when
- target can be expressed primarily with booru-style vocabulary
- mature SDXL/Illustrious LoRA assets matter
- character/tag coverage is the main need
- familiar SDXL runtime is preferred

### Prefer Anima first when
- actor ownership or relation wording is central
- multiple characters are mixing
- hybrid natural-language clarification is useful
- current Anima-specific regional/control tooling is relevant

### Compare both when
- the target is difficult/important enough that family-level inductive bias matters
- a source claim says one family is superior without direct project evidence

Do not declare a universal winner from one seed or one aesthetic sample.

---

## WAI Illustrious v17 — reference / comparison lane

Exact author facts:
- recommended software: Forge Neo
- Sampler: Euler a
- Steps: 15–30
- CFG: 5–7
- integrated VAE
- original size larger than 1024×1024 area; author examples 1024×1344
- minimal quality example: `masterpiece, best quality, amazing quality`
- minimal Negative example: `bad quality, worst quality, worst detail, sketch, censor`
- author warns too many quality/aesthetic tags and overly long Negative can reduce quality / blur
- Hires example: 1.5 upscale, 20 Hires steps, Anime6B upscaler, denoise 0.35–0.5
- v17 Hires may repair limbs/hands/feet, so base and Hires results are separate evidence states.

WAI remains useful for comparison and existing WAI-specific HOLDs, but it is no longer the sole practical-generation focus.

---

## Illustrious XL baseline

Useful family-level facts:
- Booru-oriented captioning
- critical composition tags can conflict
- derivative checkpoints must be revalidated
- NoobAI descends from the family, making Illustrious LoRAs reasonable candidates, not guaranteed matches.

---

## LoRA family boundaries

Safe:
- Anima LoRA is a separate family from SDXL/Illustrious/Noob
- official Anima training base = Base
- Noob/Illustrious proximity makes cross-use a testable candidate

Not safe:
- all Illustrious LoRAs automatically work on Noob
- SDXL/Noob LoRAs can be reused on Anima
- adapter behavior is stable across Base/Aesthetic/Turbo without testing

---

## Cross-family rules safe to transfer

Safe as general warnings:
- presence != relation success
- negative conditioning is active
- composition load matters
- rare concepts are seed-sensitive
- LoRA/postprocess/control are confounders
- evaluator coverage must be checked.

Do not transfer without evidence:
- exact Prompt order
- exact quality/Negative lists
- camera tag placement
- weight values
- canonical/Alias preference
- natural-language superiority
- simultaneous-Special ceiling
- profile-specific LoRA behavior.

## Primary originals

- `../GENERATION_KNOWLEDGE_CORPUS.md`
- `../research/BATCH_L_NOOB_ANIMA_PRACTICAL_GENERATION_DEEP_DIVE_20260913.md`
- `../research/BATCH_M_JAPANESE_PRACTICAL_SOURCE_AUDIT_NOOB_ANIMA_20260913.md`
- `../research/HARD_FETISH_MODEL_FAMILY_MATRIX_20260909.md`
- `../research/HF_MODEL_DISCUSSIONS_AUDIT_20260909.md`
- `../research/WAI17_LOCAL_ENV_TEST_BASELINE_20260909.md`
