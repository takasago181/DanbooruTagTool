# Batch L — NoobAI / Anima Practical Generation Deep Dive

Owner: Issue #44 `KNOWLEDGE:#44`
Date: 2026-09-13
Status: `PRACTICAL_SOURCE_SYNTHESIS_COMPLETE / IMAGE_EFFECTIVENESS_HOLDS_RETAINED`

## Purpose

This batch makes **NoobAI XL** and **Anima** the two primary practical-generation knowledge lanes for current research.

The target is not a generic model overview. It is a daily local-generation reference for:
- first useful settings
- Prompt construction
- niche / relation-heavy / adult-oriented anime generation
- multiple actors and binding
- LoRA use and compatibility
- Forge Neo runtime behavior
- Hires / ADetailer / img2img / regional-control escalation
- failure diagnosis

This file is KNOWLEDGE evidence/synthesis. It does not change production behavior or claim that one model is universally superior.

---

# 1. Executive practical decision

## NoobAI XL 1.1 EPS — tag-first workhorse

Use as the first practical lane when the target is primarily expressible in Danbooru/e621-style vocabulary and the workflow benefits from the mature SDXL/Illustrious ecosystem.

Strong reasons:
- exact official training context includes current Danbooru + e621 native tags
- exact official caption structure places `special tags` before `general tags`
- familiar SDXL workflow in Forge Neo / ComfyUI
- very large existing Illustrious/NoobAI LoRA ecosystem
- suitable for fast tag-centric iteration

Do **not** infer from training coverage alone that complex actor-target/body-site/count relations are solved. Those remain controlled-test questions.

## Anima — relation/hybrid-prompt workhorse

Use as the main second lane when the target needs explicit actor assignment, relation wording, mixed tag + natural-language description, or current Anima-specific regional/control tooling.

Strong reasons:
- official model supports Danbooru-style tags, natural language, and mixed Prompt
- explicit official multi-character guidance asks for character identity/basic appearance context
- Japanese practical sources consistently find explicit actor descriptions more useful than old tag-distance tricks for multi-person separation
- current Forge Neo directly supports Anima and current Anima control/regional tooling

Do **not** treat natural language as a guarantee of binding correctness. Relation/body-site/count correctness remains a first-class predicate.

## Recommended practical split

- **NoobAI EPS 1.1**: default tag-first production / broad anime knowledge / existing SDXL-style asset ecosystem
- **Anima Turbo v1.1**: fast Prompt exploration
- **Anima Base v1.0**: flexibility/diversity, LoRA training base, high-control experimentation
- **Anima Aesthetic v1.1**: consistency/default visual quality when its style bias fits the target
- **NoobAI V-Pred 1.0**: separate alternate lane; use only with correct V-Pred inference settings and exact author sampler guidance

This split is operational, not a universal quality ranking.

---

# 2. NoobAI XL 1.1 EPS — exact practical baseline

Primary author source:
https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md

Exact author guidance:
- CFG: `5–6`
- Steps: `25–30`
- Sampler: `Euler a`
- resolution: approximately SDXL 1MP; documented examples include `768×1344`, `832×1216`, `896×1152`, `1024×1024`, `1152×896`, `1216×832`, `1344×768`
- positive prefix example: `masterpiece, best quality, newest, absurdres, highres, safe`
- native caption organization: `count -> character -> series -> artists -> special tags -> general tags -> other tags`
- training/caption context includes full Danbooru + e621 native tags

## Practical interpretation

### Use the official order as an exact-model organizing aid

For difficult targets, start with a readable skeleton:
1. subject count
2. character / series when needed
3. artist/style only when intentionally used
4. target Special / relation concept
5. minimum General support needed for visibility/pose/context
6. optional other/meta details

Do not turn this into a universal grammar for WAI or Anima.

### Adult-generation caution: the official Negative is not an adult default

The published example Negative contains `nsfw`. That makes sense as a filtering/safety-oriented sample, but for an adult-generation workflow it would directly oppose the intended rating domain.

Project rule:
- treat the author Negative as **an example recipe scoped to intent**, not a universal baseline
- start from the minimum Negative needed for the actual task
- do not copy broad anatomy/count negatives into anatomy-changing or count-sensitive targets without an OFF/ON check

### Why Noob is promising for niche vocabulary

Evidence that can safely be accepted:
- Danbooru and e621 were explicitly included
- native tag captioning is explicit
- current Japanese Illustrious/Noob community treats Noob as a broad-knowledge descendant of Illustrious

Evidence that is **not** yet accepted without local image testing:
- “Noob always knows rare adult tags better than Anima”
- exact success ceiling for body-site / actor-target / topology / multiple simultaneous hard concepts
- exact canonical vs historical Alias trigger superiority

---

# 3. NoobAI V-Pred 1.0 — separate model lane

Primary author source:
https://huggingface.co/Laxhar/noobai-XL-Vpred-1.0/blob/main/README.md

Exact author guidance:
- prediction regime: V-Pred, not EPS
- CFG: `4–5`
- Steps: `28–35`
- Sampler: **Euler**
- author warning: other samplers do not work properly
- same approximate 1MP resolution family
- caption organization remains count -> character -> series -> artist -> special -> general -> other
- training description includes full Danbooru + e621 and natural-language captioning

## Runtime rule

Do not treat EPS and V-Pred as two interchangeable checkpoints.

Current Forge Neo documents support for advanced SDXL model metadata including:
- `v_pred`
- Zero Terminal SNR / `ztsnr`

Current maintained Forge Neo:
https://github.com/Haoming02/sd-webui-forge-classic/tree/neo

Japanese practical sources note an important failure mode:
- V-Pred metadata can be lost or altered by model merging
- when automatic detection fails, the runtime may need explicit V-Pred / Zero-SNR configuration

That is a runtime identity problem, not a Prompt-semantic failure.

## Community hypothesis: contrast / dark scenes

Japanese community material often describes V-Pred as stronger for contrast and genuinely dark night scenes than EPS.

Status: `PRACTICAL_CANDIDATE / NOT PROMOTED AS UNIVERSAL FACT`

Reason:
- plausible and repeatedly reported
- not enough exact paired project evidence yet

If this matters, compare EPS vs V-Pred with the same semantic target under each model's own recommended inference settings; do not force identical sampler/settings across prediction regimes.

---

# 4. NoobAI LoRA ecosystem — strong but compatibility is not binary

Useful source classes:
- official NoobAI model lineage
- current Japanese Illustrious/Noob practical guides
- Civitai base-model metadata / individual LoRA cards
- community reports only as compatibility hypotheses

## Safe rule

Because NoobAI is an Illustrious descendant, Illustrious-family LoRAs are **reasonable candidates** for NoobAI, but compatibility must not be stated as guaranteed.

Preserve for every LoRA:
- training base / baseModel label
- EPS/V-Pred expectation if relevant
- character/style/concept role
- trigger text
- recommended weight
- example checkpoint used by creator

## Why “same family = always compatible” is too strong

Cross-checking Japanese articles and community reports shows both:
- many successful Illustrious <-> Noob use cases
- failures or severe character/style drift on specific adapters/checkpoints

Therefore:
`same lineage -> candidate compatibility`, not `same lineage -> guaranteed compatibility`.

For practical use:
1. test target checkpoint without LoRA
2. load one LoRA only
3. start from creator's documented weight when available
4. if no reliable weight exists, use a conservative mid-range trial rather than stacking several adapters
5. if pose/background/style suddenly appears, suspect LoRA context leakage before adding more Prompt
6. only then stack additional LoRAs

---

# 5. Anima official family — current version state

Primary author source:
https://huggingface.co/circlestone-labs/Anima

Current official files checked 2026-09-13:
- `anima-base-v1.0.safetensors`
  - SHA-256: `bd43b7cffe1ed1153d9c41e7beb2f18cb1273eafbaa3af3edd6a173dc90a006e`
- `anima-aesthetic-v1.1.safetensors`
  - SHA-256: `3c1868387a3a1ff504bbb87c33678321965ead381fcf87afbd0264daa600c082`
- `anima-turbo-v1.1.safetensors`
  - SHA-256: `fba11953276b57edf59d1dc4f1857ac05aa079c56f982b4d7c20298d57d3f7eb`

Important freshness note:
The public model-card prose describes the Base/Aesthetic/Turbo family concept, but the repository file tree has moved ahead to Aesthetic/Turbo v1.1. Exact generation evidence should therefore retain the **actual file version/hash**, not merely `Anima Aesthetic` or `Anima Turbo`.

## Base v1.0

Official role:
- maximum flexibility
- maximum diversity
- strongest style adherence/flexibility
- official recommended base for LoRA training

Practical role:
- final/high-control experimentation
- reference lane when Turbo's default style/stability becomes too constraining
- LoRA development/training

## Aesthetic v1.1

Official family role:
- better consistency
- stronger default quality/style

Prompt-specific official rule:
- trained with quality tags stripped from captions
- positive quality tags are not required
- `masterpiece, best quality` can remain
- author recommends avoiding `score_*` in both positive and negative for Aesthetic because they can push output too hard

Practical role:
- stable high-quality default when its aesthetic bias matches the target
- not a universal replacement for Base; style/control needs may favor Base

## Turbo v1.1

Official role:
- distilled fast model
- CFG `1`
- `8–12` steps
- increased stability
- stronger default style
- reduced diversity
- author recommends starting with Turbo for fast iteration

Critical practical consequence:
At CFG 1, standard Negative conditioning is effectively not available in the ordinary way. Do not build a Turbo workflow around a large Negative recipe.

Japanese v1.1 comparisons show:
- enormous speed advantage remains
- the same seed/prompt does **not** imply the same composition as Base
- Base can be cleaner on structural details in some cases, but both can fail depending on seed

Status:
- speed/stability/default-style role: official fact
- exact anatomy/structure superiority of Base vs Turbo: `COMMUNITY / TEST_REQUIRED`

---

# 6. Anima Base/Aesthetic normal-generation baseline

Official general settings for non-Turbo Anima:
- resolution: works from roughly `512²` to `1536²`
- Steps: `30–50`
- CFG: `4–5`

Official sampler notes:
- `er_sde`: neutral style, flat colors, sharp lines; author uses it as a reasonable default
- `euler_a`: softer/thinner lines; may lean 2.5D; tolerates somewhat higher CFG
- `dpmpp_2m_sde_gpu`: similar family but more creative/variable; may get too wild
- `euler`: basic/creative, useful for Turbo/Aesthetic because those are more stable

Practical rule:
Start with author behavior descriptions; do not ask one sampler to be the universal winner.

For controlled work, record sampler and scheduler because sampler choice changes line/color/style, not just speed.

---

# 7. Anima Prompt grammar — do not import SDXL habits unchanged

Official prompt support:
- Danbooru-style tags
- natural-language captions
- mixed tag + natural language

Official surface conventions:
- lowercase tags
- spaces instead of underscores, except score tags
- prefer Gelbooru form when documented Danbooru/Gelbooru tag forms differ
- artist tags require `@artist`
- full grouping: quality/meta/year/safety -> count -> character -> series -> artist -> general

## Practical Japanese consensus worth retaining

Japanese Anima guides repeatedly reinforce:
- explicit actor descriptions are more useful than relying on tag distance
- direct relation wording can reduce feature leakage between multiple people
- avoid ambiguous pronouns when ownership matters
- name/identify actors and basic appearance explicitly in multi-person scenes
- hybrid Prompt is especially useful for relation-heavy composition

Example pattern at the structural level:
`[count / identities] + [each actor's visible distinguishing features] + [explicit factual relation/action] + [camera/scene tags]`

The project should **not** store an explicit adult sentence as a universal template. The durable knowledge is the actor/target/body-site/ownership structure.

## BREAK warning

Japanese Anima community guidance warns against carrying old SDXL `BREAK`-based character separation habits directly into Anima.

Project interpretation:
- `BREAK` remains runtime/parser syntax, not learned semantic ownership
- if a custom runtime or helper uses BREAK internally, that is runtime behavior and must be scoped to that implementation
- do not use BREAK as proof that Anima understands actor binding

---

# 8. Anima multi-character / binding practical ladder

For scenes where characters or attributes mix:

### Level 0 — plain Prompt
- exact count
- identify each actor
- give each actor at least one or two distinctive visible attributes when identity separation matters
- state relation/action explicitly when tags alone are ambiguous

### Level 1 — concise hybrid relation wording
Use tag anchors plus a short factual relation description.

Status:
`HIGH-VALUE PRACTICAL PATTERN / exact benefit remains controlled-test dependent`

### Level 2 — Forge Couple Basic
Current official extension supports Anima.
Use when left/right or region separation is the main failure.

Official extension guidance:
- Basic mode usually handles most use cases
- prompts are mapped to image regions/lines
- total subject count should still be included
- extension cannot fix composition the checkpoint does not understand

### Level 3 — Advanced / Mask
Use when equal tiles are insufficient.
- Advanced: explicit x/y region ranges + weights
- Mask: hand-drawn approximate regions

### Level 4 — ControlNet / Region ControlNet
Current Forge Neo documents:
- Anima LLLite support
- Anima Region ControlNet support

Use when geometry/region is the actual bottleneck.

Important evidence rule:
Regional/control success is assisted success, not proof of plain-Prompt binding.

---

# 9. Forge Neo is now a first-class Anima runtime

Current maintained upstream:
https://github.com/Haoming02/sd-webui-forge-classic/tree/neo

Current documented capabilities include:
- Anima 2B
- community Anima 2.9B / 3.8B support
- Anima Edit
- updated LLLite / Region ControlNet
- Preset system that can retain model/modules/parameters
- X/Y/Z Plot
- Soft Inpainting / MultiDiffusion updates
- LoRA implementation updates
- current infotext rewrite

Therefore older web pages that say “Anima is basically ComfyUI-only” are stale for this project.

ComfyUI remains useful as a reference/official workflow environment, but Forge Neo is a valid current daily GUI lane.

---

# 10. ADetailer Neo / local repair

Current official Forge Neo fork:
https://github.com/Haoming02/ADetailer-Neo

Mechanism:
`generation -> detector -> mask -> inpaint`

Current bundled detector families include:
- face YOLO
- hand YOLO
- person segmentation
- MediaPipe face

Practical use:
- use ADetailer **after** base composition and target relation are acceptable
- face detector for face/detail repair
- hand detector for hand repair when hands are visible and important
- person segmentation only when a broader person-level redraw is actually desired

Do not use ADetailer to hide a failed semantic target:
- if the base image has the wrong actor, wrong target relation, wrong count, or missing body site, first fix the base composition/Prompt
- a repaired final image does not prove base generation capability

---

# 11. Hires / upscaling — Noob vs Anima

## NoobAI

NoobAI is conventional SDXL-family output, so standard SDXL Hires/img2img workflows are available. However exact best denoise/upscaler values are checkpoint/derivative dependent.

Practical rule:
- establish composition first
- upscale after target geometry is acceptable
- if Hires changes anatomy/relation materially, record it as a rescue/rewrite, not a neutral scale operation

## Anima

Official Anima says normal operation supports up to roughly 1536². Japanese community reports warn that simply pushing much beyond that can introduce noise/instability.

Practical escalation:
1. native generation within supported range
2. external/image upscaler for mostly-preserve enlargement
3. img2img / tiled refinement at low/moderate denoise when extra detail is needed
4. regional/tiled methods for very large output

Community values such as exact denoise `0.12` or a particular upscaler are **recipes**, not global truths.

---

# 12. LoRA — Noob vs Anima must be separate asset pools

## Noob / Illustrious family

- NoobAI descends from Illustrious
- cross-use of Illustrious-family LoRAs is often a reasonable candidate
- exact adapter/checkpoint compatibility varies
- use individual LoRA base metadata and samples as authority

## Anima

Anima is not SDXL/Illustrious.

Safe rule:
- SDXL/Illustrious/Noob LoRAs must **not** be assumed compatible with Anima
- train/use Anima LoRAs on the Anima family
- official recommendation: train LoRAs on Anima Base

Japanese training sources show fast-evolving Anima-specific tooling, including Forge-Neo-oriented learning guides and Anima LoRA factory/trainer projects.

Practical caution:
- one-image/instant LoRA methods are useful experiments, not the same thing as a robust general character/style LoRA
- low-weight LoRA can stabilize style, but context leakage (pose/background/animals/accessories) must be checked
- multi-character LoRA can still mix identities; region separation may be required

---

# 13. Practical failure diagnosis — NoobAI

When a hard target fails:

1. confirm EPS vs V-Pred and exact checkpoint
2. confirm exact author sampler/settings for that regime
3. confirm canonical / known trigger spelling
4. test target concept alone or minimum unary form
5. check visibility/crop before adding more tags
6. check actor/target/body-site/count separately
7. remove conflicting Negative terms
8. reduce same-role composition tags
9. test multiple predetermined seeds
10. test one support intervention at a time
11. only then add LoRA / regional / inpaint

Noob's broad vocabulary must not cause `tag exists -> relation should work` reasoning.

---

# 14. Practical failure diagnosis — Anima

When a hard target fails:

1. identify Base/Aesthetic/Turbo **and exact file version**
2. confirm Base/Aesthetic vs Turbo settings are not mixed
3. confirm spaces/lowercase / `@artist` / exact model surface conventions
4. check whether the Prompt is too short or underspecified for the relation
5. identify actors explicitly; avoid ambiguous pronouns
6. add a concise factual relation clause rather than simply adding more unrelated tags
7. simplify conflicting style/quality pressure
8. if Aesthetic, remove unnecessary `score_*`
9. if Turbo, remember CFG1 changes normal Negative behavior
10. if identity bleed persists, use Forge Couple Basic before more complicated control
11. move to Advanced/Mask/Control only when regional geometry is the actual problem

---

# 15. Practical default lanes for this project

These are **starting lanes**, not accepted superiority claims.

## Lane N1 — NoobAI EPS 1.1 / tag-first
- Euler a
- 25–30 steps
- CFG 5–6
- ~1MP aspect-ratio preset
- official caption ordering
- minimal task-appropriate Negative
- LoRA OFF for first diagnosis

Use for:
- tag-centric discovery
- broad anime/character knowledge
- niche Special vocabulary
- mature SDXL/Illustrious ecosystem access

## Lane N2 — NoobAI V-Pred 1.0 / alternate rendering
- Euler only
- 28–35 steps
- CFG 4–5
- correct V-Pred runtime detection

Use for:
- V-Pred-specific comparison
- dark/high-contrast hypothesis testing

Do not use as an “EPS but better” drop-in.

## Lane A1 — Anima Turbo v1.1 / exploration
- CFG 1
- 8–12 steps
- current exact file/hash
- do not rely on ordinary Negative conditioning

Use for:
- rapid seed/Prompt exploration
- fast rough composition search

## Lane A2 — Anima Base v1.0 / flexible controlled generation
- 30–50 steps
- CFG 4–5
- start er_sde or another author-described sampler according to visual goal

Use for:
- maximum flexibility/diversity
- relation/hybrid prompting
- LoRA training/controlled testing

## Lane A3 — Anima Aesthetic v1.1 / consistent finish
- Base/Aesthetic normal step/CFG family
- avoid `score_*` by default per author

Use for:
- quality/consistency-oriented generation when its default style is acceptable

---

# 16. What Japanese sources add beyond model cards

The strongest Japanese practical contribution is not a new “magic setting.” It is a set of workflow observations:

- Noob V-Pred/EPS runtime mismatch is a real operational failure mode
- model merging can erase metadata assumptions
- Noob/Illustrious LoRA compatibility is probabilistic rather than binary
- Anima actor separation benefits from explicit identities/attributes/relation text
- old SDXL prompt-distance/BREAK habits should not be treated as Anima semantic control
- Turbo is excellent for speed but is not merely “the same Base image faster”
- Aesthetic quality/score behavior differs materially from Base habits
- Anima high-resolution finishing often benefits from separate upscaling/img2img/tile workflows rather than just increasing native size
- LoRA context leakage remains a common practical cause of unexplained style/background/pose drift
- Forge Couple and Anima Region ControlNet provide current escalation paths

These are exactly the types of practical details missing from model cards.

---

# 17. Remaining controlled-test backlog

Source research is now strong enough that the next value comes from exact local image evidence.

High-priority tests when the user wants them:

1. **Noob EPS vs V-Pred**
   - same semantic targets, each at own recommended settings
   - dark/contrast + hard relation cases

2. **Noob rare/hard Special ceiling**
   - unary activation -> body-site -> actor-target -> count/composite

3. **Anima Base vs Aesthetic v1.1 vs Turbo v1.1**
   - same semantic target, profile-correct settings
   - judge relation/body-site/count, not just prettier image

4. **Anima tag-only vs concise hybrid relation**
   - predetermined paired seeds

5. **Noob/Illustrious LoRA cross-use**
   - small representative matrix, not blanket compatibility

6. **Anima LoRA x Base/Aesthetic/Turbo**
   - record adapter base + weight + profile

7. **Forge Couple escalation**
   - plain -> Basic -> Advanced/Mask

8. **Hires/ADetailer/inpaint rescue**
   - separate base semantic success from repair success

---

# 18. Source hierarchy used

Highest authority:
1. exact model/tool author current documentation
2. current model files / hashes / official runtime source
3. primary technical research
4. exact-version practical comparisons
5. current Japanese Wiki / detailed Japanese articles
6. Reddit/community anecdote
7. generic model-comparison SEO pages

Community sources are used for failure discovery, workflow ideas, and hypotheses. They do not silently override official model behavior or Danbooru semantics.

---

# Sources — primary / official

1. Laxhar Lab, NoobAI XL 1.1 model card  
   https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
2. Laxhar Lab, NoobAI XL V-Pred 1.0 model card  
   https://huggingface.co/Laxhar/noobai-XL-Vpred-1.0/blob/main/README.md
3. CircleStone Labs, Anima model card  
   https://huggingface.co/circlestone-labs/Anima/blob/main/README.md
4. CircleStone Labs, Anima file tree  
   https://huggingface.co/circlestone-labs/Anima/tree/main/split_files/diffusion_models
5. Anima Base v1.0 exact file  
   https://huggingface.co/circlestone-labs/Anima/blob/main/split_files/diffusion_models/anima-base-v1.0.safetensors
6. Anima Aesthetic v1.1 exact file  
   https://huggingface.co/circlestone-labs/Anima/blob/main/split_files/diffusion_models/anima-aesthetic-v1.1.safetensors
7. Anima Turbo v1.1 exact file  
   https://huggingface.co/circlestone-labs/Anima/blob/main/split_files/diffusion_models/anima-turbo-v1.1.safetensors
8. Forge Neo maintained branch  
   https://github.com/Haoming02/sd-webui-forge-classic/tree/neo
9. Forge Couple  
   https://github.com/Haoming02/sd-forge-couple
10. ADetailer Neo  
    https://github.com/Haoming02/ADetailer-Neo

# Sources — Japanese practical

11. としあきdiffusion Wiki — Illustrious-XL / NoobAI  
    https://wikiwiki.jp/sd_toshiaki/Illustrious-XL
12. としあきdiffusion Wiki — Anima  
    https://wikiwiki.jp/sd_toshiaki/Anima
13. としあきdiffusion Wiki — LoRA  
    https://wikiwiki.jp/sd_toshiaki/LoRA
14. としあきdiffusion Wiki — 初めてのLoRA作り（Anima編）  
    https://wikiwiki.jp/sd_toshiaki/%E5%88%9D%E3%82%81%E3%81%A6%E3%81%AELoRA%E4%BD%9C%E3%82%8A%EF%BC%88anima%E7%B7%A8%EF%BC%89
15. Crody, Anima画像生成ガイド  
    https://note.com/crody/n/n937474cf1c23
16. 秋葉原IT戦略研究所, Anima Turbo v1.1 / Base comparison  
    https://note.com/akb428/n/nc794be92ebc2
17. かみもと, Anima Raw / Turbo / Aesthetic comparison  
    https://note.com/sepiablue/n/nc0b2feee1ae8
18. EasyForgeNeo Japanese README  
    https://github.com/hirorohi03/EasyForgeNeo/blob/main/README_JP.md

# Sources — secondary ecosystem/context

19. AirMore, local anime model comparison (Civitai API ecosystem counts; runtime compatibility claims require freshness correction)  
    https://airmore.ai/ja/ai-review/local-anime-ai-image-models-comparison
20. selesteia AI, 2026 anime model comparison (community practical; blanket LoRA-compatibility wording is not adopted)  
    https://prompt.selesteia.com/articles/anime-ai-model-hikaku-2026

## Rejected / bounded source patterns

Do not promote:
- generic articles that merge EPS and V-Pred settings
- “same family means every LoRA works” claims
- Preview-era Anima settings as current Base/Aesthetic/Turbo defaults
- current Forge-Neo incompatibility claims from articles that predate maintained Neo support
- long universal Negative recipes
- one-seed model rankings
