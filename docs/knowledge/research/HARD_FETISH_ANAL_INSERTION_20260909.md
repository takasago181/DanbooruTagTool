# Hard Fetish Generation Knowledge — Anal / Insertion

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `DEEP_RESEARCH_V1 / evidence-reference`

## 1. Scope

対象は、成人・合意下の anal / insertion 系 Special と、その生成・監査で必要になる body-site / object / count / timing / state の分離知識。

Project dictionary examples:
- `anal` ID147 Core / 74188
- `anal fingering` ID148 Core / 4377
- `anal object insertion` ID149 Core / 19986
- `double anal` ID150 Extended / 705
- `imminent anal` ID151 Core / 2408
- `multiple anal` ID152 Extended / 861
- `pegging` ID153 Extended / 714
- `triple anal` ID154 Extended / 94
- `anal only` ID155 Core / 1139
- `anal invitation` ID156 Extended / 398
- `anal grip` ID157 Extended / 264
- `anal insertion` Alias -> `anal_object_insertion`
- `anal sex` Alias -> `anal`
- `anal stretching / anal training / gaping anus / anal play` are Semantic-layer search/support concepts, not automatically exact model triggers.

Related insertion examples:
- `double penetration` Core / 14509
- `multiple penetration` Extended / 70
- `triple penetration` Core / 1870
- `anal fisting` Extended / 345
- `fisting` Extended / 600
- `large insertion` Core / 3183
- `self fisting` Extended / 60
- `urethral insertion` Core / 1758
- `urethral penetration` Extended / 57

## 2. Semantic decomposition

An anal/insertion concept should not be treated as one binary tag. Decompose into predicates:

### 2.1 Site
- target opening/body site
- target ownership (whose body site)
- site visibility sufficient for judgement

### 2.2 Action/state
- contact only
- imminent insertion
- actual insertion
- post-action state
- manipulation/stimulation
- stretching/state change

### 2.3 Implement
- body part
- object/toy
- strap-on/device
- nonhuman appendage
- machine actuator

### 2.4 Count
- number of implements/actors
- simultaneous vs sequential
- one site vs multiple sites

### 2.5 Actor-target relation
- who acts
- who receives
- whether the implement belongs to the correct actor/device

A visually explicit image can still be a semantic failure if site, implement, actor, or count is wrong.

## 3. Main failure modes

### `WRONG_BODY_SITE`
The model renders the requested implement/action but at a different opening/body region.

This is a classic binding failure, not evidence that the implement tag is unsupported.

### `OBJECT_PRESENT_RELATION_FAIL`
The requested object/toy is visible, but not functionally connected to the target site.

### `WRONG_COUNT`
For double/multiple/triple concepts, the image contains too few or too many implements/actors, or renders them sequentially rather than simultaneously.

### `SITE_OCCLUDED`
The relation may be correct but cannot be judged because the site is cropped or covered. Route to `VISIBILITY_UNCLEAR`, not automatic failure.

### `ANATOMY_COLLAPSE`
Unusual geometry is replaced by generic anatomy, fused anatomy, implausible openings, or collapsed limbs.

### `CONCEPT_COLLAPSE_TO_BROAD_PARENT`
A rare/specific concept collapses to a frequent broad scene: e.g., a count-specific insertion becomes generic sex/insertion.

### `NEGATIVE_COLLISION`
A broad anatomy/count negative suppresses the very unusual geometry required by the target.

### `POSTPROCESS_RESCUE`
Hires/inpaint/ADetailer repairs the final anatomy. This is not base Prompt success.

## 4. Visibility vs intrinsic meaning

Camera/framing is usually not intrinsic to `anal` identity.

Possible visibility supports may include rear/side/close framing, but their role is **observability**, not semantic definition.

Audit rule:
- never promote a successful camera angle into canonical meaning;
- if a support changes body pose materially, record both Visibility and Geometry effects;
- if one framing support hides other required actors/implements, it can become anti-support.

## 5. Broad + specific support

Candidate pattern:
`specific Special` vs `specific Special + broad parent/constituent`.

Potential benefits:
- exposes a more frequent learned concept when the rare specific token is weak;
- can stabilize object/site class.

Potential harms:
- broad parent can dominate the rare modifier;
- can increase concept competition;
- can collapse multi/count-specific semantics into the broad common case.

Therefore status: `TEST_REQUIRED`, never automatic.

Required paired conditions:
1. specific only
2. specific + one broad parent
3. same predetermined seeds
4. score site/action/count separately

## 6. Negative Prompt interaction

General negative-conditioning research shows that negative concepts can actively cancel positive concepts through latent neutralization.

High-risk cases:
- unusual opening/state changes
- large/multiple insertion
- count-changing configurations
- anatomy that departs from ordinary body priors

Do not certify failure under a broad anatomy/count Negative until at least:
- `N0`: minimal author-model Negative
- `N1`: + anatomy negative
- `N2`: + count/extra-limb negative if relevant

Compare target retention and collateral-error reduction separately.

## 7. Rare concept / seed sensitivity

Rare concept generation literature shows long-tail concepts are underrepresented and success can vary materially with seed.

Consequences:
- `triple anal` (94) or `self fisting` (60) failing at one seed is only E0 case evidence;
- predetermined multi-seed repeats are needed before a reliability claim;
- a lucky seed is not evidence of robust support;
- a bad seed is not evidence of model ignorance.

## 8. Model-family notes

### WAI Illustrious v17
Exact author baseline should remain the starting point. The author warns against oversized quality/aesthetic and Negative stacks, and Hires may repair limbs.

Anal/insertion audit therefore requires:
- base image retained before Hires;
- minimal official Negative baseline;
- no automatic `bad anatomy / extra limbs` stack for unusual/count-changing cases;
- hard relation success judged before Hires repair.

### NoobAI XL 1.1 EPS
Native caption structure places Special before General. Full Danbooru/e621 training makes broad adult-concept exposure plausible, but exact current rare/Semantic labels are not guaranteed.

Use:
- Special anchor before large general blocks;
- keep current Alias/Semantic distinction;
- do not use SFW-oriented `safe` positive / `nsfw` negative as the hard-adult test baseline.

### Anima
Because Anima supports tags + natural language and multiple-character descriptions, relation-heavy cases are candidates for controlled comparison:
- tag-only anchor
- tag + concise factual actor/site/relation clause

Do not turn the latter into a universal requirement before exact-case testing.

For multiple actors, stable IDs/names and explicit relation ownership are higher-information than synonym stacks.

## 9. Evaluator design

### Unary Tagger use
Good for broad evidence such as object/state presence when the vocabulary actually contains the target.

Insufficient for:
- exact body-site relation
- actor ownership
- simultaneous insertion count
- imminent vs actual vs after-state
- subtle state change.

### Decomposed judgement
Score at least:
- `SITE_OK`
- `ACTION_OK`
- `IMPLEMENT_OK`
- `COUNT_OK`
- `ACTOR_TARGET_OK`
- `VISIBILITY_OK`

Final target success requires all predicates intrinsic to that Special.

### WD EVA02 limitation
WD EVA02 v3 filtered tags below 600 images. Several project rows are below that level or Semantic-only; non-detection must route to `EVALUATOR_UNCOVERED/REVIEW`, not generated-image FAIL.

## 10. Test ladder

For a representative hard insertion case:

1. `S_ONLY_MINIMAL`
2. `S + person/count identity`
3. `+ one visibility support`
4. `+ one geometry/binding support`
5. specific vs `+ broad parent` A/B
6. Negative baseline vs anatomy/count Negative A/B
7. predetermined multi-seed repeatability
8. second hard Special only after single-target baseline established
9. assisted-control lane only after bounded Prompt support is exhausted
10. LoRA-assisted lane separately if used

## 11. Evidence labels

- `DIRECT_COMMON`
- `DIRECT_RARE`
- `ALIAS_TRIGGER_TEST`
- `SEMANTIC_DECOMPOSE`
- `BODY_SITE_BINDING`
- `COUNT_BINDING`
- `ANATOMY_NEGATIVE_AB`
- `RELATION_REVIEW`
- `POSTPROCESS_RESCUE`
- `ASSISTED_ONLY`
- `HUMAN_ONLY`

## 12. HOLD / image-test backlog

- WAI v17 exact rare anal/count-specific response rates
- NoobAI EPS exact canonical vs Alias response for the anal cluster
- family-specific benefit/harm of broad `penetration` support
- family-specific visibility phrases/angle tags
- anatomy-Negative effect size
- multi-insertion count ceiling by model family
- automatic evaluator reliability for site/count relations

## Sources

Primary/general:
- WAI v17 author card: https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md
- NoobAI XL 1.1 model card: https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- Anima author card: https://huggingface.co/circlestone-labs/Anima
- Rare concept generation: https://arxiv.org/abs/2304.14530
- Rare-to-Frequent: https://arxiv.org/abs/2410.22376
- T2I-CompBench: https://arxiv.org/abs/2307.06350
- Negative prompt mechanism: https://arxiv.org/abs/2406.02965

Project dictionary:
- `data/special2788/prompt_reference/04_性行為・性的刺激.txt`
- `data/special2788/prompt_reference/05_挿入・性具・機械.txt`
