# Hard / Niche Fetish Generation Knowledge — Source Registry

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `DEEP_RESEARCH_V1`

## Evidence policy

Rank sources by authority/experimental control, not language.

1. exact model/version author source
2. model-family author source
3. primary research
4. controlled practical comparison
5. practical exact-model report
6. adapter/LoRA creator report
7. general community report

One translated/reposted experiment is not independent corroboration.

---

# A. Exact model / author sources

## HF-WAI-017 — WAI Illustrious v17 author card
URL: https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md
Language: English / multilingual
Class: `FACT_EXACT_MODEL`
Scope: exact WAI Illustrious v17
Used for:
- 15–30 steps / CFG 5–7 / Euler a
- official minimal quality/Negative guidance
- `general / sensitive / nsfw / explicit` safety vocabulary
- warning against too many quality/aesthetic tags and overly long Negative
- Hires limb-repair behavior
- recommended Forge Neo context.
Hard-fetish relevance:
- giant generic Negative stack is not exact-model authority;
- base vs Hires evidence must be separated.

## HF-NOOB-11 — NoobAI XL 1.1 EPS
URL: https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
Language: English
Class: `FACT_EXACT_MODEL`
Scope: exact NoobAI XL 1.1 EPS
Used for:
- Danbooru + e621 native tag caption training
- CFG/steps/sampler/resolution
- caption order `count -> character -> series -> artist -> special -> general -> other`
- SFW-oriented safety example warning.
Hard-fetish relevance:
- Special-before-General exact structural evidence;
- broad explicit/nonhuman exposure plausible, exact rare current token exposure unproven.

## HF-ANIMA — CircleStone Anima author card
URL: https://huggingface.co/circlestone-labs/Anima
Language: English
Class: `FACT_EXACT_MODEL / FAMILY`
Used for:
- tags + natural language + mixed prompting
- Qwen-family text encoder behavior context
- lowercase / spaces / Gelbooru preference
- tag dropout
- Base/Aesthetic/Turbo separation
- multi-character description guidance.
Hard-fetish relevance:
- relation-heavy cases can be tested as tag-only vs concise factual hybrid;
- every implied tag need not be injected.

## HF-ANIMA-MULTI-93 — Anima multi-character discussion
URL: https://huggingface.co/circlestone-labs/Anima/discussions/93
Language: English
Class: `PRACTICAL / COMMUNITY_ON_OFFICIAL_HOST`
Used for:
- some character combinations work individually but fail together
- explicit appearance/position can help some combinations
- strong concept/series token can bleed into another subject.
Limitation:
- no controlled benchmark; use as failure-mode evidence only.

## HF-ANIMA-MULTI-120 — Anima separate-character tagging discussion
URL: https://huggingface.co/circlestone-labs/Anima/discussions/120
Language: English
Class: `COMMUNITY_ON_OFFICIAL_HOST`
Used for:
- attribute/identity assignment can swap between subjects.
Limitation:
- anecdotal; supports binding risk, not exact success rates.

## HF-ANIMA-NSFW-141 — Adult relation-caption practical discussion
URL: https://huggingface.co/circlestone-labs/Anima/discussions/141
Language: English
Class: `PRACTICAL / COMMUNITY_ON_OFFICIAL_HOST`
Used only for:
- stable subject IDs
- explicit relative-position/contact decomposition as a relation-prompting hypothesis.
Important boundary:
- external runtime LLM generation from that discussion is NOT adopted; DanbooruTagTool runtime remains non-LLM.

---

# B. Primary research

## R-RARE-SEEDSELECT
Title: Generating images of rare concepts using pre-trained diffusion models
URL: https://arxiv.org/abs/2304.14530
Language: English
Class: `FACT_GENERAL`
Claims used:
- long-tail imbalance contributes to rare-concept underrepresentation
- seed selection can materially affect rare-concept fidelity.
Project implication:
- one failed or successful seed does not establish rare Special reliability.

## R-RARE-R2F
Title: Rare-to-Frequent: Unlocking Compositional Generation Power of Diffusion Models on Rare Concepts with LLM Guidance
URL: https://arxiv.org/abs/2410.22376
Language: English
Class: `FACT_GENERAL`
Claims used:
- rare compositions are hard
- exposing related frequent concepts can improve rare composition.
Project implication:
- test one broad/frequent constituent as controlled support; do not adopt runtime LLM.

## R-RARE-CI-2026
Title: Rare Concept Generation via Counterfactual Inference in Diffusion Models
URL: https://arxiv.org/abs/2607.14765
Language: English
Class: `FACT_GENERAL / RECENT`
Claims used:
- common-knowledge bias interferes with unusual attributes/compositions.
Project implication:
- rare targets may collapse to common nearby visual states.

## R-CONCEPTMIX
URL: https://arxiv.org/abs/2408.14339
Language: English
Class: `FACT_GENERAL`
Claims used:
- compositional performance degrades as requested concept count grows, especially for open models.
Hard-fetish relevance:
- hard composites must be decomposed before tag-unsupported conclusions.

## R-T2ICOMP
Title: T2I-CompBench
URL: https://arxiv.org/abs/2307.06350
Language: English
Class: `FACT_GENERAL`
Claims used:
- separate attribute binding, spatial relation, non-spatial relation, complex composition evaluation.
Hard-fetish relevance:
- object presence cannot substitute for relation/body-site/topology judgement.

## R-NEGATIVE
Title: Understanding the Impact of Negative Prompts
URL: https://arxiv.org/abs/2406.02965
Language: English
Class: `FACT_GENERAL`
Claims used:
- negative conditioning can remove concepts through cancellation/neutralization.
Hard-fetish relevance:
- anatomy/count Negative is an active intervention and may conflict with intended unusual anatomy.

## R-CONTROLNET
URL: https://arxiv.org/abs/2302.05543
Language: English
Class: `FACT_GENERAL`
Used for:
- pose/depth/edge etc as assisted spatial conditioning.
Boundary:
- assisted-control success != Prompt-only success.

---

# C. Tool / control sources

## TOOL-DWPOSE
URL: https://github.com/IDEA-Research/DWPose
Language: English
Class: `FACT_TOOL`
Used for:
- whole-body/keypoint geometry side evidence and pose-control input.
Limit:
- does not understand niche sexual/BDSM semantics.

## TOOL-FORGE-COUPLE
URL: https://github.com/Haoming02/sd-forge-couple
Language: English
Class: `FACT_TOOL`
Used for:
- regional conditioning / actor separation
- explicit warning that regional prompting cannot make a checkpoint understand a composition it does not understand.
Hard-fetish relevance:
- actor/resource separation assisted lane only.

---

# D. Evaluator sources

## EVAL-WD-EVA02-V3
URL: https://huggingface.co/SmilingWolf/wd-eva02-large-tagger-v3
Class: `FACT_EXACT_MODEL`
Key project fact:
- tags with fewer than 600 images were filtered out.
Hard-fetish implication:
- many rare/Extended/Semantic targets are structurally uncovered or weakly covered; missing output != generated-image failure.

## EVAL-KAGAMI-24K
URL: https://huggingface.co/Redstonexs/kagami-24k
Class: `FACT_EXACT_MODEL`
Use:
- broader-vocabulary candidate after dictionary freeze.
Limit:
- wide vocabulary does not prove reliable rare relation semantics.

## EVAL-CL-TAGGER-V2
URL: https://huggingface.co/cella110n/cl_tagger_v2
Language: Japanese / English
Class: `FACT_EXACT_MODEL`
Use:
- broad tag vocabulary
- per-tag thresholds/calibration
- OOD reference information.
Hard-fetish implication:
- evaluator confidence should be tag-specific/coverage-aware rather than one global threshold.

---

# E. Japanese practical sources

## JA-WAI-V17-INTRO
Title: WAI-illustrious-SDXL V17が登場！人物描写やコントラストが改善！？
URL: https://note.com/novapen_create/n/n7ef484c8f4d4
Language: Japanese
Class: `PRACTICAL_EXACT_MODEL`
Use:
- exact v17 practical generation setup and output comparison context.
Limit:
- not a hard-fetish controlled benchmark.

## JA-WAI-NSFW-MEMO
Title: 〖基本メモ〗WAI-NSFW-illustrious-SDXL 使うっす〖追補版〗
URL: https://note.com/ren_ai_coach/n/n2fb066b01801
Language: Japanese
Class: `PRACTICAL / mostly author-guidance restatement`
Use:
- independent Japanese corroboration of WAI safety/quality/inference guidance.
Limit:
- additional author suggestions beyond exact model card remain practical only.

## JA-WAI-TO-ANIMA
Title: WAI-illustrious から WAI-ANIMA へ ── アニメ系画像生成モデル移行の実践記録
URL: https://note.com/nonb0716/n/nc7644494c360
Language: Japanese
Class: `PRACTICAL`
Use:
- actual migration evidence that Illustrious and Anima prompting/control assumptions differ
- Forge Couple use for multi-character separation
- separate post-processing workflow in memory-constrained practice.
Limit:
- individual workflow; not exact hard-fetish benchmark.

## JA-WAI-LORA-PRACTICE
Title: CivitaiでダウンロードしたLoraの効き目が分からない人へ＃１
URL: https://note.com/ready_ibis7848/n/nbf164fed3dd1
Language: Japanese
Class: `PRACTICAL`
Use:
- reinforces need to compare base model vs LoRA effect rather than assume adapter necessity.

## JA-ILL-LORA-COMBINATION
Title: WAI-NSFW-illustriousで作る自分のお気に入り画風が探せるLoRA組み合わせ５パターン集
URL: https://note.com/nobinlog/n/n23775017fb96
Language: Japanese
Class: `PRACTICAL`
Use:
- reports checkpoint/version changes can alter adapter recipes and multiple LoRA composition should be empirically tested.
Limit:
- style-oriented, not hard-fetish semantic authority.

---

# F. Chinese / Traditional-Chinese practical sources

## ZH-WAI-CHARACTER-SELECT
URL: https://github.com/lanner0403/WAI-NSFW-illustrious-character-select
Language: Traditional Chinese / English
Class: `PRACTICAL_TOOL_ECOSYSTEM`
Use:
- demonstrates real WAI ecosystem uses structured action/prompt presets and LoRA bundles.
Limit:
- presets are not semantic authority; some versions are old and runtime AI option conflicts with current product's non-LLM runtime policy, so that feature is not adopted.

## ZH-WAI-COMFY-SELECT
URL: https://github.com/zch9241/WAI_NSFW_illustrious_character_select_for_ComfyUI
Language: Simplified Chinese
Class: `PRACTICAL_TOOL_ECOSYSTEM`
Use:
- explicit warning that some LoRAs/prompts from the upstream extension do not match current WAI versions.
Project implication:
- adapter/prompt version compatibility is evidence identity.

## ZH-ANIMA-PROMPT-RULES
URL: https://github.com/LLJ-code1/tishicigongcheng/blob/main/WAI_ANIMA_%E6%A8%A1%E5%9E%8B%E8%A7%84%E8%8C%83.md
Language: Chinese
Class: `PRACTICAL / secondary synthesis`
Use:
- multi-person scenes should reduce conflict density and bind actions/positions to subjects.
Limitation:
- secondary ruleset; official Anima source remains authority.

## ZH-ILL-PROMPT-DETAIL
Title: 〖Stable Diffusion/Illustrious〗同样提示词，为什么细节多这么多？
URL: https://www.bilibili.com/video/BV1MJj666ERA/
Language: Chinese
Class: `PRACTICAL`
Use:
- argues detail does not require massive prompt stacks; supports minimum-sufficient direction only.

---

# G. Korean practical sources

## KO-ANIMA-GUIDE
URL: https://onebrotravel.tistory.com/entry/ComfyUI-%EC%B4%88%EA%B0%84%EB%8B%A8-%EC%9E%85%EB%AC%B8%EA%B0%80%EC%9D%B4%EB%93%9C-%E2%80%94-Anima%EB%A1%9C-%EC%B2%AB-%EC%9D%B4%EB%AF%B8%EC%A7%80-%EC%83%9D%EC%84%B1
Language: Korean
Class: `PRACTICAL_CORROBORATION`
Use:
- corroborates official Anima tag order / spaces / Gelbooru preference / tag dropout / tag+NL mixture.
Limit:
- official model card remains authority.

---

# H. Niche concept / LoRA creator reports

These are deliberately low-authority for semantic meaning but high-value for identifying failure modes, training-context leakage and postprocess reliance.

## LORA-MACHINE-IL
Title: sex machine - v1.0 XL (Illustrious)
Mirror: https://www.tensor.art/models/786538361914394082
Original linked page: https://civitai.com/models/829330
Class: `LORA_CREATOR_PRACTICAL`
Observed:
- recommended weight around 1.0
- trigger bundle includes machine, restraint, tubing/cable, blindfold, insertion/toy/context terms.
Interpretation:
- adapter learned a context bundle; whole trigger list is not canonical meaning.

## LORA-TENTACLE-CLOTHES-IL
Title: Tentacle Clothes - IL-v1
Mirror: https://tensor.art/models/874867747715032813
Original linked page: https://civitai.com/models/1659744
Class: `LORA_CREATOR_PRACTICAL`
Observed:
- trained from multiple artists/groups specifically hoping to reduce style impact and increase concept flexibility
- main trigger `tentacle clothes`; broad `living clothes` also reported helpful.
Interpretation:
- narrow concept datasets can entangle style; broad parent may help an adapter but is not universal base-model rule.

## LORA-RESTRAINT-TOPOLOGY-IL
Title: Takatekote bound from behind - concept - IL_v1.1
Mirror: https://tensor.art/models/931646314498757531
Original linked page: https://civitai.com/models/2036060?modelVersionId=2407744
Class: `LORA_CREATOR_PRACTICAL`
Observed:
- creator notes chain link structure may fail due XL limitations
- recommends inpainting with another model for small-structure repair.
Interpretation:
- dedicated concept LoRA does not guarantee connector topology;
- inpaint success is `POSTPROCESS_RESCUE`.

## LORA-INFLATION-IL
Title: Female Inflation XL - Illustrious
Mirror: https://tensor.art/models/870283245936222083
Original linked page: https://civitai.com/models/1610639/female-inflation-xl-illustrious
Class: `LORA_CREATOR_PRACTICAL`
Observed:
- creator decomposes multiple body regions, size levels and sub-concepts
- several ancillary concepts remain inconsistent; some words caused unrelated object generation and were replaced by custom triggers.
Interpretation:
- anatomy-changing concept has multiple independent dimensions;
- ordinary natural-language token can carry an unwanted common semantic prior;
- custom LoRA trigger behavior is adapter-specific.

---

# I. Project canonical dictionary sources

- `data/special2788/prompt_reference/04_性行為・性的刺激.txt`
- `data/special2788/prompt_reference/05_挿入・性具・機械.txt`
- `data/special2788/prompt_reference/06_拘束・BDSM・支配.txt`
- `data/special2788/prompt_reference/08_異形・触手・非人間.txt`

These establish the project inventory/layer/post-count references. They do not alone establish model activation reliability.

---

# J. Source-use rules

1. LoRA trigger bundles are hypothesis generators, never canonical definitions.
2. Community explicit prompts are not copied into production defaults without exact-family controlled evidence.
3. Model-family claims need family/version identity.
4. Hires/inpaint/control/LoRA must be recorded in evidence metadata.
5. Rare current post_count is a triage signal, not exact training exposure.
6. Semantic-layer phrases are search/semantic assets, not proof of learned model tokens.
7. Automatic evaluator confidence is invalid when vocabulary/semantic class/OOD does not support the judgement.
8. Multilingual practical evidence may identify gaps and candidate tests, but exact author evidence wins on conflicts.
