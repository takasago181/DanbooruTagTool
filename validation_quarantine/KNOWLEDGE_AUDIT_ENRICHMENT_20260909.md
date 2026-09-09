# Generation Knowledge Audit Enrichment — 2026-09-09

Issue: #32 `[DICT-VALIDATION] Special2788 generation metadata full validation (quarantine)`

Status: KNOWLEDGE evidence pack / quarantine-only

## Purpose and authority boundary

This file expands the generation knowledge available to the #32 audit. It is evidence and audit guidance, not a production specification and not an automatic R2 rule change.

It MUST NOT by itself:
- change an existing #32 PASS/FIX/REVIEW/IMAGE_TEST_REQUIRED verdict;
- modify production `data/**`;
- convert a model-family observation into model-independent truth;
- treat a practical blog/community observation as exact checkpoint authority;
- treat a useful support tag as part of the intrinsic Special identity;
- treat a post-processing/control intervention as proof that the original Prompt/Special worked unaided.

When this pack exposes a new material interpretation rule, #32 should either apply the existing R2 evidence gate or create a separately reviewed future rule version rather than silently rewriting historical results.

## Evidence discipline

Use the following evidence order when generation behavior matters:

1. **EXACT_MODEL_FACT** — exact checkpoint/version author model card, official repository, exact documented inference settings.
2. **AUTHOR_STATEMENT** — author/team statement for the same model family/version, including official-hosted discussions when authors participate.
3. **PEER_REVIEWED / PRIMARY_RESEARCH** — mechanism or broad T2I behavior, useful for risk plausibility but not exact checkpoint tuning.
4. **CONTROLLED_PRACTICAL** — same model/settings/seed where possible, one variable changed, exact Prompt/settings shown.
5. **PRACTICAL_CORROBORATION** — useful real-world workflow with settings, but not adequately controlled.
6. **COMMUNITY_OBSERVATION** — hypothesis generator only.
7. **HYPOTHESIS** — must remain REVIEW / IMAGE_TEST_REQUIRED when material.

Language is not an evidence rank. Japanese, Chinese, Korean and English material is scored by experimental quality using the same rules.

## High-level audit conclusions

### K-AUD-01 — Model family must be part of the claim identity
A statement such as `full body is useful`, `quality tags improve results`, or `negative prompt is required` is incomplete unless the model family/version and inference regime are known. WAI Illustrious v17, Illustrious early, NoobAI EPS 1.1, NoobAI V-Pred 1.0 and Anima have materially different official prompting contracts.

Audit consequence:
- model-sensitive GenerationProfile claims without model scope are at least REVIEW;
- do not copy EPS behavior to V-Pred or vice versa;
- do not copy Anima syntax/trigger behavior to Illustrious-derived models;
- do not infer exact WAI behavior only from generic Illustrious evidence.

### K-AUD-02 — Canonical identity, model trigger and UI/search identity are separate
The database canonical is the stable semantic identity. A model can respond better to a different surface form because of its training corpus.

Exact Anima author guidance says to prefer the Gelbooru spelling when Danbooru and Gelbooru differ. Official-hosted discussion #136 documents artist-name cases where an older/Gelbooru spelling activates the model while the newer Danbooru spelling does not.

Audit consequence:
- never rewrite canonical identity to match a model trigger;
- if GenerationProfile needs a model-specific trigger spelling, store/interpret it as model-family prompt knowledge, not canonical replacement;
- Alias/canonical equivalence in the dictionary does not prove equal image-generation response.

### K-AUD-03 — Support can improve observability without being intrinsic meaning
Frame, viewpoint, body-site visibility and geometry can be necessary to *judge* a Special even when they are not part of the Special's definition.

Audit consequence:
- distinguish `Meaning support` from `Geometry/Visibility support`;
- a frame tag must not be promoted to CORE_SUPPORT merely because the target is otherwise off-screen;
- requirement overrides are structural needs, not automatic tag insertion commands.

### K-AUD-04 — Multi-concept failure is not evidence that one tag is unknown
Primary research describes catastrophic neglect (requested concepts disappearing), attribute binding failure and concept bleeding in multi-subject/multi-concept diffusion generation.

Audit consequence:
Before declaring a composite/multiple-Special tag unsupported, prefer the sequence:
1. A_ONLY;
2. B_ONLY;
3. AB minimal;
4. AB + minimal frame/visibility;
5. AB + targeted geometry;
6. AB + actor/resource separation when needed.

If A and B work separately but AB fails, classify the problem as composition/binding until evidence proves otherwise.

### K-AUD-05 — Negative prompts are semantic interventions
Research on negative prompts finds concept deletion through neutralization against corresponding positive concepts. Therefore a negative is not a neutral cleanup list.

Audit consequence:
- unusual-anatomy / count-changing / extra-body-part Specials combined with `bad anatomy`, `extra limbs`, `extra arms`, `malformed anatomy` or related negatives are HIGH-risk;
- absence of an intended concept under an overlapping negative does not prove the Special itself is weak;
- broad anatomy/count negatives should remain IMAGE_TEST_REQUIRED where the intended Special semantically overlaps them;
- quality/text-artifact negatives are a different class from body-integrity/count/concept negatives.

### K-AUD-06 — Hires, ADetailer, ControlNet and LoRA are interventions/confounders
A final image can be rescued or damaged after the base Prompt has already generated its structure.

Audit consequence:
- post-processing/control settings are part of the evidence identity;
- a Special that appears only after an intervention is not evidence of unaided Prompt effectiveness;
- compare base-pass and final-pass evidence where the intervention overlaps the target;
- prompt-only and assisted-control lanes must remain separate.

## Exact model-family evidence

### 1. WAI Illustrious v17

Exact source:
- https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md

Author-documented settings/behavior:
- Steps: 15–30
- CFG: 5–7
- Sampler: Euler a
- author asks for original dimensions larger than the 1024×1024 area; examples use 1024×1344
- example positive quality baseline: `masterpiece, best quality, amazing quality`
- example negative baseline: `bad quality, worst quality, worst detail, sketch, censor`
- author explicitly warns that too many quality/aesthetic tags and overly long negative prompts can reduce image quality and make images blurrier
- v17 notes an attempt to improve Hires Fix limb correction
- documented Hires example: upscale 1.5, 20 Hires steps, R-ESRGAN 4x+ Anime6B, denoise 0.35–0.5

Audit implications:
- `quality/meta` must be treated as a model-conditioned variable, not a transparent quality switch;
- a giant universal quality stack is not supported by exact v17 evidence;
- Hires Fix cannot be treated as neutral because the author explicitly describes it as capable of correcting limbs;
- WAI v17 evidence produced with Hires ON cannot certify base-pass anatomy or visibility behavior;
- `bad anatomy` is not part of the author's small documented v17 negative baseline; do not make it mandatory based on generic SDXL habits.

Japanese corroboration:
- https://note.com/drawthingsguide/n/n49f84ee6804f
  - practical comparison argues that quality tags can change face, hair, clothing, painting style, composition and camera proximity, not merely detail level.
  - use as practical corroboration, not exact v17 causal proof for every Prompt.

Korean corroboration:
- https://crowsaint.tistory.com/entry/TensorAI%ED%95%A0%EB%A6%AC%ED%80%B8-%EB%A7%8C%EB%93%A4%EA%B8%B03%EC%B0%A8
  - reports WAI v17 with exact example settings (768×1152, seed, 20 steps, CFG 7, Euler a) while struggling with asymmetric hair-color assignment.
  - useful evidence that left/right/local attribute binding remains a practical failure mode; not a controlled global benchmark.

### 2. Illustrious XL early release

Exact source:
- https://huggingface.co/OnomaAIResearch/Illustrious-xl-early-release-v0

Official contract:
- Euler a
- Steps: 20–28
- CFG: 5–7.5
- supported quality vocabulary includes `worst quality`, `bad quality`, `average quality`, `good quality`, `best quality`, `masterpiece`
- recommended frame families include `upper body`, `cowboy shot`, `portrait`, `full body`
- author explicitly warns not to overuse critical composition tags such as `close-up`, `upside-down`, `cowboy shot` because conflicting composition instructions can confuse generation
- base model intentionally has no default style

Audit implications:
- contradictory Frame tags are a Prompt conflict, not evidence that a Special is semantically wrong;
- one appropriate frame family is preferred for baseline evidence;
- composition support should be tracked separately from Special meaning.

Japanese controlled-practical evidence:
- https://note.com/itsuki_ailab/n/n298758cec98e
  - fixed model/settings/seed; `full body` alone kept the body in frame, while adding `close-up` + `cowboy shot` with `full body` narrowed the frame and cropped the legs/feet.
  - one seed / one image each, so this proves a concrete failure example, not a universal success rate.
- https://note.com/yukyu_haruka/n/n540734f2ce74
  - same-seed practical examples show that changing frame requirements to expose a body site can also change the pose because geometry must become physically compatible.

Audit implication from these Japanese sources:
- visibility and geometry are coupled; a `full body` support choice can alter the pose and should not be called a pure visibility-only no-op.

### 3. NoobAI XL 1.1 EPS

Exact source:
- https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md

Official facts:
- trained from Illustrious lineage using full Danbooru + e621 and native tag captions
- CFG: 5–6
- Steps: 25–30
- Sampler: Euler a
- recommended total area around 1024², with listed portrait/square/landscape resolution families
- positive prefix: `masterpiece, best quality, newest, absurdres, highres, safe`
- official negative includes `bad hands`, `mutated hands` but does not list `bad anatomy`, `extra limbs`, or `extra arms`
- native caption order explicitly places `<special tags>` before `<general tags>`:
  `<count>, <character>, <series>, <artists>, <special tags>, <general tags>, <other tags>`

Audit implications:
- Special-before-General is the strongest exact structural evidence among the currently targeted families;
- broad anatomy negatives are not justified as mandatory by the exact EPS1.1 model card;
- do not infer an exact camera-tag grammar beyond the documented native caption order;
- EPS1.1 camera/visibility optimality remains empirical/HOLD.

### 4. NoobAI XL V-Pred 1.0

Exact source:
- https://huggingface.co/Laxhar/noobai-XL-Vpred-1.0/blob/main/README.md

Official facts:
- CFG: 4–5
- Steps: 28–35
- Sampler: Euler; author explicitly warns other samplers do not work properly
- resolution family around 1024²
- same native caption order with Special before General
- official negative again includes `bad hands`, `mutated hands`

Audit implications:
- V-Pred is not an inference preset for EPS; it is a distinct model/inference regime;
- EPS settings must not be copied into V-Pred evidence or vice versa;
- if sampler/CFG regime is not recorded, controlled generation evidence is incomplete.

### 5. Anima

Exact/author source:
- https://huggingface.co/circlestone-labs/Anima
- official-hosted discussions are useful secondary evidence; distinguish author/team statements from user observations.

Author-documented prompting facts:
- trained on Danbooru-style tags, natural-language captions and combinations
- tag style uses lowercase and spaces instead of underscores; `score_*` is the exception
- when Danbooru/Gelbooru spellings differ, author says to prefer Gelbooru spelling
- recommended positive prefix includes `masterpiece, best quality, score_7, safe`
- recommended negative includes low/worst quality, low score tags, artist name and artifact terms depending on current profile/revision
- prompt weighting works but may need stronger values than typical SDXL; author example `(chibi:2)`
- tag order: quality/meta/year/safety → count → character → series → artist → general
- artist tags require `@`
- random tag dropout was used; the author says every relevant tag need not be supplied
- natural language can be mixed with tags; for multiple characters, author recommends naming a character and describing basic appearance rather than listing names alone
- Aesthetic profile was trained with quality tags stripped; quality tags are therefore not required for that profile and score-tag use is discouraged by current author guidance when it produces overcooked/sloppy output.

High-value official-hosted discussion evidence:

#### Direction / orientation (#99)
- https://huggingface.co/circlestone-labs/Anima/discussions/99
- users report left/right ambiguity and seed sensitivity, including left/right hand actions;
- discussion highlights a key semantic trap: a strong Booru concept such as `looking back` can conflict with a natural-language instruction that tries to assign a different geometry;
- `viewer` is suggested as a better grounded concept than `camera` in this context;
- heavy prompts were reported to reduce directional fidelity.

Audit implication:
- left/right/orientation claims are HIGH-risk and should not be certified statically from Prompt wording alone;
- when a natural-language clause fights a well-established Booru visual concept, classify as Prompt conflict before declaring the tag wrong.

#### Multiple characters (#120)
- https://huggingface.co/circlestone-labs/Anima/discussions/120
- reports attribute bleed and poor binding with 3–4 independently specified characters;
- community recommendation is regional prompting for severe cases.

Audit implication:
- 3–4 actor exact binding is beyond a safe default Prompt-only assumption;
- a support profile that claims deterministic actor separation from ordinary tags alone should remain REVIEW/IMAGE_TEST_REQUIRED unless directly tested.

#### Tags vs natural language (#140)
- https://huggingface.co/circlestone-labs/Anima/discussions/140
- one user reports about 100 generations where tag-only prompts were structurally cleaner, while long natural language added microdetail but more anatomy/hand failures;
- environment-heavy natural language was observed to overpower frame tags and zoom out;
- hybrid tag base + short natural-language relation/layout text is a useful candidate pattern but remains community/practical evidence.

Audit implication:
- no fixed token/paragraph cutoff should be promoted;
- record concept density and relation complexity instead of only character count/token length;
- long environment text is a possible frame-confounder.

#### Model-trigger spelling vs canonical (#136)
- https://huggingface.co/circlestone-labs/Anima/discussions/136
- cases are reported where renamed artist tags respond to the older/Gelbooru form rather than the newer Danbooru form.

Audit implication:
- model trigger spelling must never overwrite canonical identity.

Korean corroboration:
- https://onebrotravel.tistory.com/entry/ComfyUI-%EC%B4%88%EA%B0%84%EB%8B%A8-%EC%9E%85%EB%AC%B8%EA%B0%80%EC%9D%B4%EB%93%9C-%E2%80%94-Anima%EB%A1%9C-%EC%B2%AB-%EC%9D%B4%EB%AF%B8%EC%A7%80-%EC%83%9D%EC%84%B1
  - Korean practical guide mirrors official order, space-vs-underscore rule, Gelbooru preference, tag dropout and mixed tag/NL usage.
  - use as multilingual corroboration only.

Chinese corroboration:
- https://github.com/shuaixn/anima-prompt-writing/blob/main/references/prompt-rules.md
  - Chinese practical rules separate hard Danbooru anchors from natural-language composition/environment/continuous action; warns not to pretend unverified candidate tags are confirmed.
  - useful audit-design corroboration; not an author source.

## Cross-cutting mechanism knowledge for #32

### C1. Concept count / compositional load
Primary source:
- ConceptMix — https://arxiv.org/abs/2408.14339

Finding:
- T2I compositional performance drops as the number of requested visual concepts increases, especially for open models.

Do NOT simplify this to `long prompts are bad`.

Audit fields worth recording when evidence is generated:
- Special count
- distinct actor count
- object count
- number of attribute bindings
- relation count
- body-site count
- frame/visibility requirements
- geometry requirements
- support block count
- natural-language relation sentence yes/no
- token count only as an additional descriptive metric

### C2. Catastrophic neglect and attribute binding
Primary source:
- Attend-and-Excite — https://arxiv.org/abs/2301.13826

Finding:
- diffusion models can omit requested subjects and bind attributes to the wrong subject.

Audit implication:
- missing B in `A + B` is not sufficient evidence that B is an invalid/weak tag;
- actor-target support claims should be tested against identity/attribute bleed, not only target presence.

### C3. Concept bleeding
Primary source:
- Isolated Diffusion — https://arxiv.org/abs/2403.16954

Finding:
- multi-concept synthesis can merge/overlap different concepts and their attached attributes.

Audit implication:
- `Resource parking/disambiguation` is a legitimate support category for composite prompts;
- it should not be promoted to semantic identity merely because it reduces bleeding.

### C4. Negative-prompt suppression
Primary source:
- Understanding the Impact of Negative Prompts — https://arxiv.org/abs/2406.02965

Finding:
- negative prompts take effect through delayed concept suppression/neutralization against positive content.

Audit implication:
Use a semantic-overlap classification for negatives:
1. QUALITY/ARTIFACT — low quality, text, signature, jpeg artifacts
2. BODY-INTEGRITY — bad anatomy, malformed anatomy, bad hands
3. COUNT/LIMB — extra limbs, extra arms, missing limbs
4. CONCEPT-SPECIFIC — direct opposite/absence of the requested concept

Classes 2–4 are not neutral if the Special intentionally changes anatomy/count/limb topology.

### C5. CFG is adherence-vs-quality control, not quality-only
Primary source:
- Classifier-free Guidance with Adaptive Scaling — https://arxiv.org/abs/2502.10574

General finding:
- stronger CFG can improve correspondence to conditioning while reducing perceptual quality; weaker CFG can improve quality/diversity while weakening adherence.

Audit implication:
- exact checkpoint author range overrides generic advice;
- Prompt adherence comparisons at different CFG are not clean tests of Special semantics;
- fixed CFG should be part of each controlled A/B identity.

### C6. LoRA interference
Primary sources:
- Training-Free Multi-Concept LoRA Composition with Prompt-Aware Weighting — https://arxiv.org/abs/2606.03792
- TARA: Token-Aware LoRA for Composable Personalization in Diffusion Models — https://arxiv.org/abs/2508.08812 and AAAI 2026 publication

Findings:
- naive multi-LoRA composition can cause concept interference, degraded quality, identity loss and feature leakage;
- TARA identifies token-wise interference and spatial misalignment as concrete multi-LoRA failure modes.

Audit implication:
- record LoRA list, order, weight and trigger strings;
- do not attribute an A/B failure to the Special if LoRA state differs;
- for Special effectiveness, a no-LoRA baseline is strongly preferred unless LoRA dependency is explicitly the question;
- multiple LoRAs are a separate compositional risk multiplier.

### C7. Hires Fix is a second-stage intervention
Exact WAI v17 author evidence explicitly says Hires can correct limbs.

Audit implication:
Record at least:
- enabled/disabled
- upscale factor
- Hires steps
- upscaler
- denoising strength
- second-pass prompt/negative if different

If the audit target is anatomy/visibility/geometry, base pass and final pass should be distinguishable. A final corrected limb does not prove the base Prompt generated correct limb structure.

### C8. ADetailer is targeted inpainting, not cosmetic metadata
Implementation documentation:
- https://github.com/leejet/stable-diffusion.cpp/blob/master/docs/adetailer.md

ADetailer can run after normal generation with a separate prompt, negative prompt, steps, CFG, denoising strength and inpaint size.

Audit implication:
- record detector/model, mask/target, prompt inheritance/override and denoise;
- if ADetailer mask overlaps the body site or object relevant to the Special, the final image is assisted evidence;
- prompt-only baseline should normally disable it or explicitly label the intervention.

### C9. ControlNet/OpenPose defines an assisted spatial-control lane
Primary source:
- ControlNet — https://arxiv.org/abs/2302.05543
- ICCV paper: https://openaccess.thecvf.com/content/ICCV2023/html/Zhang_Adding_Conditional_Control_to_Text-to-Image_Diffusion_Models_ICCV_2023_paper.html

Finding:
- ControlNet adds explicit spatial conditioning such as human pose, depth, edges and segmentation.

Audit implication:
- if Prompt-only repeatedly fails geometry while the Special is otherwise recognized, consider `prompt-only control ceiling` rather than endlessly adding support tags;
- ControlNet success cannot certify that the Special Prompt works unaided;
- assisted-control evidence should be a separate experiment lane.

## Candidate audit risk matrix

| Pattern found in row/evidence | Default audit concern | Suggested disposition if evidence is weak |
|---|---|---|
| model-family-sensitive wording with no family scope | false global truth | REVIEW |
| `CORE_SUPPORT + ADDITIVE` justified only by semantic plausibility | automatic insertion may be untested | IMAGE_TEST_REQUIRED |
| frame tag claimed as intrinsic Special meaning | visibility conflated with semantics | REVIEW/FIX if definition disproves it |
| broad anatomy/count negative overlaps unusual Special | negative may suppress intended concept | IMAGE_TEST_REQUIRED |
| multiple-Special support claimed from single-Special evidence | compositional neglect/binding untested | IMAGE_TEST_REQUIRED |
| actor-target/body-site binding asserted from tag name only | ownership/assignment may be implicit or ambiguous | REVIEW |
| Alias treated as proven equal model response | identity mapping confused with generation response | REVIEW/IMAGE_TEST_REQUIRED |
| Anima trigger spelling used to replace canonical | model trigger confused with database identity | FIX |
| WAI quality stack copied from generic SDXL folklore | exact v17 author warning conflicts | REVIEW/FIX depending field |
| Noob EPS and V-Pred settings merged | distinct inference/model regimes | FIX |
| final image uses Hires/ADetailer but evidence claims base Prompt success | post-process confound | REVIEW / rerun |
| multiple LoRAs differ between A/B | adapter interference confound | REVIEW / rerun |
| ControlNet/regional control active but claim is Prompt-only support | assisted control conflated with Prompt behavior | REVIEW / rerun |
| long Prompt failure attributed only to token count | concept density/binding not isolated | REVIEW |
| full-body visibility improves target but changes pose | visibility/geometry coupling | REVIEW unless experiment isolates it |

## Suggested controlled-test templates for unresolved #32 claims

These templates are evidence designs, not production Prompt grammar.

### T1 — intrinsic meaning vs support
- A: Special only + family baseline
- B: Special + one candidate support
- same seed/settings/negative/model
- judge Special retention and observability separately

### T2 — multiple-Special interaction
- A_ONLY
- B_ONLY
- AB minimal
- AB + one targeted support class
- use same two or more seeds
- distinguish `tag unknown` from `composition/binding failure`

### T3 — anatomy-negative interference
- N0 family baseline without broad anatomy/count negative
- N1 + body-integrity negative
- N2 + count/limb negative relevant to target
- score intended-Special retention separately from unwanted-error suppression

### T4 — post-processing confound
- base output saved before Hires/ADetailer
- same image through intervention
- judge whether the Special existed before intervention

### T5 — LoRA interference
- no LoRA
- LoRA A only
- LoRA B only if relevant
- A+B
- reversed load/order when implementation semantics make order relevant
- fixed seed/settings

### T6 — canonical/model-trigger response
- canonical surface form
- formal Alias if one exists
- model-family documented trigger form when distinct
- same seed/settings
- never silently normalize strings before comparison

## HOLD / IMAGE_TEST_REQUIRED list to preserve

The following should remain unresolved without direct evidence:
- exact NoobAI EPS1.1 camera/visibility placement optimum;
- a universal simultaneous-Special count breakpoint;
- universal prompt-token/character length threshold;
- broad anatomy-negative safety for unusual-anatomy Specials;
- canonical vs Alias vs Semantic equality of generation response;
- deterministic actor-target separation from ordinary Prompt tags in difficult multi-actor scenes;
- a universal quality/meta stack across WAI / Illustrious / NoobAI / Anima;
- model-independent optimal CFG/sampler/resolution;
- LoRA-free conclusions drawn only from LoRA-active evidence;
- prompt-only conclusions drawn only from Hires/ADetailer/ControlNet/regional-control outputs.

## Multilingual source inventory

### Exact / author sources
- WAI Illustrious v17 model card (EN): https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md
- Illustrious XL early model card (EN): https://huggingface.co/OnomaAIResearch/Illustrious-xl-early-release-v0
- NoobAI XL 1.1 EPS model card (EN): https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- NoobAI V-Pred 1.0 model card (EN): https://huggingface.co/Laxhar/noobai-XL-Vpred-1.0/blob/main/README.md
- Anima model card (EN): https://huggingface.co/circlestone-labs/Anima
- Anima direction discussion #99 (EN/multilingual community): https://huggingface.co/circlestone-labs/Anima/discussions/99
- Anima multi-character discussion #120: https://huggingface.co/circlestone-labs/Anima/discussions/120
- Anima artist rename/model-trigger discussion #136: https://huggingface.co/circlestone-labs/Anima/discussions/136
- Anima tag/NL discussion #140: https://huggingface.co/circlestone-labs/Anima/discussions/140

### Primary research
- ConceptMix: https://arxiv.org/abs/2408.14339
- Attend-and-Excite: https://arxiv.org/abs/2301.13826
- Isolated Diffusion: https://arxiv.org/abs/2403.16954
- Negative Prompt mechanisms: https://arxiv.org/abs/2406.02965
- CFG adaptive scaling / adherence-quality tradeoff: https://arxiv.org/abs/2502.10574
- ControlNet: https://arxiv.org/abs/2302.05543
- Multi-LoRA prompt-aware composition: https://arxiv.org/abs/2606.03792
- TARA multi-LoRA interference: https://arxiv.org/abs/2508.08812

### Japanese practical / controlled-practical
- Illustrious conflicting frame tags, same seed: https://note.com/itsuki_ailab/n/n298758cec98e
- Illustrious body-site/geometry example: https://note.com/yukyu_haruka/n/n540734f2ce74
- model/quality-tag comparison including WAI v17: https://note.com/drawthingsguide/n/n49f84ee6804f

### Korean practical corroboration
- Anima introductory prompt guide: https://onebrotravel.tistory.com/entry/ComfyUI-%EC%B4%88%EA%B0%84%EB%8B%A8-%EC%9E%85%EB%AC%B8%EA%B0%80%EC%9D%B4%EB%93%9C-%E2%80%94-Anima%EB%A1%9C-%EC%B2%AB-%EC%9D%B4%EB%AF%B8%EC%A7%80-%EC%83%9D%EC%84%B1
- WAI v17 exact-settings practical example: https://crowsaint.tistory.com/entry/TensorAI%ED%95%A0%EB%A6%AC%ED%80%B8-%EB%A7%8C%EB%93%A4%EA%B8%B03%EC%B0%A8

### Chinese practical corroboration
- Anima prompt rules / hard-anchor vs NL composition separation: https://github.com/shuaixn/anima-prompt-writing/blob/main/references/prompt-rules.md

## How #32 should use this pack

During deep review, auditors should ask in this order:

1. **What is the Special's intrinsic meaning?**
   - Resolve from identity/meaning authority first.
2. **What structural requirements are intrinsic?**
   - actor count/ownership, body site, implement, pose relation, spatial assignment.
3. **What supports are merely for generation/observability?**
   - frame, camera, visibility, geometry assistance, disambiguation.
4. **Is the claimed behavior model-family specific?**
   - if yes, require family scope and exact evidence.
5. **Could the test be confounded?**
   - Negative overlap, CFG change, Hires, ADetailer, LoRA, ControlNet, regional prompting, differing resolution/sampler.
6. **Is failure actually compositional?**
   - test A_ONLY/B_ONLY before calling a tag unsupported.
7. **Is evidence static or image-dependent?**
   - if image-dependent and material, use IMAGE_TEST_REQUIRED rather than guessed PASS.

This file intentionally favors safe uncertainty over false PASS. A higher REVIEW/IMAGE_TEST_REQUIRED rate is acceptable; incorrectly freezing a model-specific or intervention-dependent observation into production generation metadata is not.
