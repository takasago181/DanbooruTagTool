# Hard / Niche Fetish Generation Knowledge — Research Index

Owner: Issue #44 `KNOWLEDGE:#44`

Branch: `knowledge/generation-corpus`

Date: 2026-09-09

Status: `DEEP_RESEARCH_V1`

## 0. Purpose

この文書は、DanbooruTagTool の Special Core Dictionary に含まれる成人向け・特殊・ハード系概念について、**意味が分かるか**ではなく、画像生成時にどこで失敗し、何を監査し、どの種類の補助を試すべきかを整理するための research index である。

主な対象:
- anal / anal-object / multi-insertion 系
- BDSM / bondage / restraint topology 系
- sex machine / mechanical device / tool-mediated relation 系
- tentacle / living-clothes / nonhuman appendage 系
- urethral / fisting / large insertion / inflation 等の rare / anatomy-changing 系
- 上記を複数組み合わせた hard composite

本研究は `#44` の知識資料であり、production data、#32 verdict、Prompt grammar、Stage10 scoring を自動変更しない。

## 1. Scope boundary

生成最適化の知識は、**成人・合意下のBDSM/sexual activity、または明確な成人ファンタジー**を対象とする。

Special辞書には非合意・現実の動物との性行為・その他の境界概念も存在するが、本researchではそれらを semantic/audit inventory として区別し、詳細な生成最適化ルールの対象にはしない。

この境界は辞書からの削除を意味しない。`canonical identity` / `translation` / `coverage audit` と generation optimization は別権限である。

## 2. Why hard-fetish generation is structurally different

ハード系は単なる「rare tag」ではない。1つの概念が複数の生成能力を同時要求することが多い。

### Structural classes

1. `UNARY_OBJECT_OR_STATE`
   - device / rope / tentacles / toy などが存在すれば一次条件を満たす。
   - ただし最終成功ではなく、relationを要求するSpecialではpresenceだけでは不足。

2. `BODY_SITE_STATE`
   - 特定body siteの可視性・状態が必要。
   - crop / occlusion / wrong-site が主なfalse success / false failure源。

3. `SIMPLE_RELATION`
   - actor A が object/body-site B に作用していることが必要。

4. `BINDING_RELATION`
   - actor、target、body-site、ownership の対応が正しい必要がある。
   - 「AもBも画像内にある」だけでは失敗。

5. `RESTRAINT_TOPOLOGY`
   - rope/cuff/device と limb/body-site の接続関係が成立している必要がある。
   - rope presence と restraint success を分離する。

6. `DEVICE_RELATION`
   - machine/deviceが存在し、正しいactor/body-siteと機能的に接続している必要がある。

7. `MULTI_PENETRATION_OR_COUNT`
   - implement count / body-site count / actor count / simultaneous relation の整合が必要。

8. `NONHUMAN_APPENDAGE_RELATION`
   - tentacle等のsource/ownership/count/target/actionを区別する必要がある。

9. `ANATOMY_CHANGING`
   - ordinary anatomy distributionから外れる形状・拡張・inflation等。
   - generic anatomy-negativeとの衝突リスクが高い。

10. `COMPOSITE_HARD`
    - 上記を2種類以上同時に要求。
    - concept load と relation load の両方が上がる。

## 3. Risk dimensions

各Special/テストケースは、少なくとも次を独立評価する。

- `EXPOSURE_RISK`
  - rare / post_count / training cutoff / renamed tag / Semantic / Alias
- `BINDING_RISK`
  - actor-target-body-site ownership
- `VISIBILITY_RISK`
  - crop / occlusion / body-site not visible
- `GEOMETRY_RISK`
  - pose / limb / device alignment / rope topology
- `COUNT_RISK`
  - multiple implements / actors / appendages
- `NEGATIVE_COLLISION_RISK`
  - intended unusual anatomy/action vs anatomy/count negatives
- `STYLE_CONTEXT_LEAK_RISK`
  - strong learned concept tag or LoRA importing unrelated style/context/censor priors
- `EVALUATOR_BLINDNESS_RISK`
  - unary tagger can see object but not relation; rare tag outside vocabulary
- `LORA_CONFOUND_RISK`
  - adapter itself supplies concept/context/pose
- `POSTPROCESS_RESCUE_RISK`
  - Hires / inpaint / ADetailer / img2img repairs final image

## 4. Durable cross-cutting conclusions

### 4.1 Presence is not relation success

`FACT_GENERAL`

T2I-CompBench separates attribute binding, spatial relationships, non-spatial relationships and complex composition because these are distinct generation problems. Object-attribute binding research likewise shows that a model can render the objects yet attach attributes to the wrong target.

Hard-fetish audit consequence:
- `tentacles` detected != correct tentacle relation
- `rope` detected != correct restraint topology
- `sex machine` detected != correct machine-body relation
- `anal`-adjacent visual cue detected != correct body-site/action/count

### 4.2 Complex concept load lowers reliability

`FACT_GENERAL`

ConceptMix reports a marked performance drop as requested concept count `k` rises, especially for open models. Hard composites should therefore be decomposed before declaring any single Special unsupported.

Diagnostic sequence:
`A_ONLY -> B_ONLY -> AB minimal -> AB + one functional support role at a time`.

### 4.3 Rare concept failure is a separate long-tail problem

`FACT_GENERAL`

Rare-concept research shows that pretrained diffusion models underperform on long-tail/uncommon concepts and rare compositions. Seed selection alone can materially change success on rare concepts; later Rare-to-Frequent work shows rare compositions may improve when supported by more frequent related visual concepts.

Project consequence:
- rare Special failure at one seed is weak evidence of model ignorance;
- broad/support decomposition is a **test candidate**, not semantic authority;
- runtime LLM guidance from R2F is not adopted because the product runtime is non-LLM; the durable lesson is only that rare concepts may benefit from controlled decomposition/support.

### 4.4 Negative Prompt can suppress the target

`FACT_GENERAL`

Negative-prompt mechanism research shows deletion through latent neutralization: negative concepts can cancel positive concepts.

Hard-fetish consequence:
- unusual anatomy/count-changing targets must not be judged under `bad anatomy / malformed anatomy / extra limbs / extra arms` without ON/OFF comparison when semantic overlap is plausible;
- exact family magnitude remains `IMAGE_TEST_REQUIRED`.

### 4.5 Seed is part of evidence identity

`FACT_GENERAL`

Rare-concept research and project Batch C both support treating seed as part of evidence identity. Hard concepts should be evaluated over predetermined paired seeds, while retaining `both fail` as absolute reliability evidence.

### 4.6 Assisted control is a distinct lane

`FACT_TOOL / FACT_GENERAL`

Forge Couple targets different conditionings to specific regions and explicitly warns that it cannot make a checkpoint understand a composition it does not understand. DWPose/ControlNet can impose body pose geometry.

Therefore:
- regional/pose-assisted success is useful product evidence;
- it does not certify Prompt-only capability;
- use assisted control after bounded Prompt support escalation rather than endlessly adding synonyms.

### 4.7 LoRA trigger bundles are not canonical definitions

`PRACTICAL`

Niche LoRA pages frequently package a concept trigger with restraint, framing, device and quality tags. These bundles reveal what the adapter author found useful, but they are contaminated by adapter training distribution and cannot be promoted into Special meaning or universal base-model support.

Use them for:
- hypothesis generation;
- identifying likely geometry/visibility roles;
- detecting adapter-context entanglement.

Do not use them for:
- canonical definition;
- mandatory support insertion;
- proof that base checkpoint cannot generate the concept.

## 5. Model-family implications

### WAI Illustrious v17

`FACT_EXACT_MODEL`

Exact author card:
- Steps 15–30
- CFG 5–7
- Euler a
- recommends original area larger than 1024x1024; examples 1024x1344
- rating vocabulary `general / sensitive / nsfw / explicit`
- official positive quality `masterpiece, best quality, amazing quality`
- official negative `bad quality, worst quality, worst detail, sketch, censor`
- warns too many quality/aesthetic tags and overly long negatives can reduce quality / blur output
- Hires can repair limbs with high probability

Hard-fetish consequences:
- do not import giant generic Negative stacks into unusual anatomy tests;
- base vs Hires success must be separated;
- high-detail hard scenes should start from minimal model-author baseline, then add functional supports.

### NoobAI XL 1.1 EPS

`FACT_EXACT_MODEL`

- full Danbooru + e621 training with native tag captions
- CFG 5–6 / 25–30 / Euler a / ~1MP
- caption order: count -> character -> series -> artist -> special -> general -> other

Hard-fetish consequences:
- Special-before-General has exact-model structural support;
- broad explicit dataset increases plausible exposure but does **not** prove every current rare/Semantic label was learned;
- official `safe` positive / `nsfw` negative is a SFW-oriented default, not a valid adult stress baseline.

### Anima

`FACT_EXACT_MODEL`

- trained on Danbooru tags + natural-language captions + mixtures
- uses safety tags including `nsfw / explicit`
- Gelbooru spelling preferred when Danbooru/Gelbooru forms differ
- random tag dropout means every related tag need not be included
- natural language and hybrid prompts are supported
- author says multiple characters need identifying/basic appearance context to reduce confusion

Hard-fetish consequences:
- relation-heavy hard scenes are candidates for `tag anchor + concise factual relation clause`, not guaranteed universal rules;
- stable explicit actor IDs/names and relation decomposition are stronger candidates than synonym stacking;
- strong concept tags may carry style/context baggage; score semantic success and collateral leakage separately.

### Illustrious baseline

`FACT_EXACT_MODEL / FACT_GENERAL`

Illustrious uses refined multi-level captions covering tags and natural language, and its model guidance warns about conflicting critical composition tags.

Hard-fetish consequence:
- relation-rich scenes should not be treated as a bag of independent unary tags;
- conflicting frame/pose tags are Prompt conflict before Special failure.

## 6. Evaluator implications

### Unary taggers

Use only for questions such as:
- is `tentacles` likely visible?
- is a broad device/object present?
- is a common unary state detected?

Do not use as sole judge for:
- penetration target/site
- restraint topology
- actor-target ownership
- simultaneous count
- machine-device functional relation
- under-clothes relation
- rare Semantic concepts.

### WD EVA02 specific warning

WD EVA02 v3 filtered tags with fewer than 600 images from its tag vocabulary/training selection. Many hard-fetish Special rows are below this scale or Semantic-only.

Examples from the project dictionary:
- `triple anal` 94
- `anal invitation` 398
- `anal grip` 264
- `anal fisting` 345
- `self fisting` 60
- `urethral penetration` 57
- `mecha on girl` 79
- `riding machine` 105
- `sybian` 148
- `robot sex` 136
- `strappado` 144
- `shrimp tie` 82
- `tentacle masturbation` 92
- `tentacle dildo` 50
- `mechanical tentacles` 463

Therefore `WD did not emit target` is not valid failure evidence for these classes.

## 7. Hard-fetish test ladder

For a target Special `S`:

1. `S_ONLY_MINIMAL`
2. `S + minimum person/count identity`
3. `S + one visibility support` if target cannot be judged
4. `S + one geometry/binding support` if relation is wrong
5. `S + model-specific alternate trigger` only with evidence
6. `S + broad/frequent constituent` as controlled A/B, never automatic
7. Negative collision OFF/ON if anatomy/count overlap exists
8. multi-seed repeatability
9. only then add second hard Special
10. assisted-control lane if Prompt-only bounded escalation fails
11. LoRA-assisted lane separately if concept adapter is used

## 8. Evaluation labels

At minimum:
- `TARGET_SUCCESS`
- `TARGET_PARTIAL`
- `WRONG_BODY_SITE`
- `WRONG_ACTOR_TARGET`
- `WRONG_COUNT`
- `OBJECT_ONLY_RELATION_FAIL`
- `TOPOLOGY_FAIL`
- `VISIBILITY_UNCLEAR`
- `CONCEPT_OMITTED`
- `STYLE_CONTEXT_LEAK`
- `NEGATIVE_COLLISION_SUSPECTED`
- `POSTPROCESS_RESCUE`
- `ASSISTED_ONLY`
- `EVALUATOR_UNCOVERED`
- `UNCLEAR`

## 9. Focused files

- `HARD_FETISH_ANAL_INSERTION_20260909.md`
- `HARD_FETISH_BDSM_RESTRAINT_20260909.md`
- `HARD_FETISH_MACHINE_DEVICE_20260909.md`
- `HARD_FETISH_TENTACLE_FANTASY_20260909.md`
- `HARD_FETISH_RARE_EXTREME_20260909.md`
- `HARD_FETISH_SOURCES_20260909.md`

## 10. Current status

This v1 deep-research corpus is evidence/reference only. Exact WAI v17 / NoobAI 1.1 / Anima hard-fetish response probabilities remain image-test questions where no exact controlled evidence exists.
