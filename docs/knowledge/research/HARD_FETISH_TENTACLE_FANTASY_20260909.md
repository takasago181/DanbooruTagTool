# Hard Fetish Generation Knowledge — Tentacle / Nonhuman Appendage Fantasy

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `DEEP_RESEARCH_V1 / evidence-reference`

## 1. Scope

対象は成人ファンタジーとしての tentacle / living-clothes / nonhuman-appendage 関係。現実動物との性的行為は本ファイルの生成最適化対象外。

Representative project rows:
- `tentacle sex` ID325 Core / 14853
- `tentacle masturbation` ID326 Extended / 92
- `imminent tentacle sex` ID327 Extended / 351
- `consensual tentacles` ID331 Core / 1857
- `tentacle dildo` ID333 Extended / 50
- `penis tentacle` ID613 Core / 1086
- `tentacle on penis` ID614 Extended / 669
- `mechanical tentacles` ID1847 Extended / 463
- `tentacle pit` ID1848 Core / 3726
- `tentacles` ID1849 Core / 60661
- `tentacles on male` ID1850 Core / 1677
- `tentacles under clothes` ID1851 Core / 2130
- `tentacle clothes` ID1853 Extended / 477
- `tentacle in mouth` ID1862 Core / 2301
- `grabbed by tentacles` ID1866 Core / 4889
- `living clothes` ID1870 Core / 1937
- `suction tentacles` ID1878 Extended / 229
- `tentacle around neck` ID1879 Extended / 235
- `tentacle hair` ID1881 Core / 41815
- `tentacle in ear` ID1883 Extended / 153
- `tentacle legs` ID1884 Extended / 76
- `tentacle tail` ID1885 Extended / 942
- `tentacles as hands` ID1889 Extended / 235
- `tentacle` Alias -> `tentacles`

## 2. Why tentacle concepts need subtypes

`tentaсles present` is a weak condition. The same visual primitive can play several completely different roles:

- external actor/appendage
- body part of a monster/person
- hair replacement
- tail/legs/hands
- clothing/living garment
- tool/implement
- restraint/grabbing appendage
- mechanical appendage
- environment/pit/background mass

Therefore ownership/source and function are intrinsic to many tentacle Specials.

## 3. Semantic decomposition

### Source / ownership
- external creature
- character's own appendage
- machine
- garment/living clothes
- environment mass.

### Appendage role
- generic tentacle
- hand/leg/tail/hair substitute
- implement/tool-like appendage
- restraint/grab appendage.

### Target
- person
- specific body site
- clothing layer
- object.

### Action/relation
- presence
- contact
- grabbing/restraint
- insertion/sexual relation
- entering under clothing
- surrounding/covering.

### Count/density
- one/few/many
- useful count vs uncontrolled proliferation.

## 4. Main failure modes

### `TENTACLE_PRESENT_RELATION_FAIL`
Many tentacles are visible but none performs the intended relation.

### `OWNERSHIP_SWAP`
The tentacles become the character's hair/tail/body part when an external actor was intended, or vice versa.

### `HAIR_CONFUSION`
`tentaсle hair` learned distribution dominates an external-tentacle request.

### `COUNT_EXPLOSION`
The model produces excessive tentacles that obscure targets and make relation auditing impossible.

### `TARGET_OCCLUSION`
Tentacles cover the relevant body site; a visually busy image becomes `VISIBILITY_UNCLEAR` rather than PASS.

### `WRONG_TARGET`
In multi-actor scenes, appendages interact with the wrong person/site.

### `RESTRAINT_WITHOUT_RELATION`
The person appears trapped/surrounded, but the specific requested grab/body-site relation is absent.

### `MECHANICAL_ORGANIC_BLEND`
Mechanical tentacles become generic robot arms/cables or organic tentacles lose the intended mechanical identity.

### `STYLE_CONTEXT_LEAK`
A strong tentacle tag/LoRA pulls horror/slime/background/style priors that were not requested.

### `GARMENT_COLLAPSE`
`tentaсle clothes/living clothes` becomes normal clothing with tentacle motifs, or external tentacles rather than garment topology.

## 5. Practical LoRA ecosystem lessons

Concept LoRAs for `tentacle clothes`, `tentacles under clothes`, and related Illustrious concepts show several recurring patterns:

- dedicated concept adapters exist because base-model reliability is imperfect for some rare relations;
- adapter authors often pair the trigger with broad `tentacles`, restraint or quality tags;
- one tentacle-clothes adapter explicitly used multiple artists to reduce style fixation and improve concept flexibility, which is practical evidence that a narrow concept dataset can entangle style/context;
- family-specific versions/weights differ, so trigger+weight must be part of evidence identity.

Durable conclusion:
`LoRA trigger bundle != canonical meaning != universal support set`.

## 6. Relation and visibility pressure

Tentacle scenes have a special failure pattern: adding more visible tentacles can increase concept-presence confidence while decreasing relation readability.

Therefore optimize two metrics separately:
- `APPENDAGE_PRESENCE`
- `TARGET_RELATION_READABILITY`

Do not reward count/density if it hides the target relation.

Potential support sequence:
1. target tentacle Special
2. actor/source identity if ambiguous
3. one target/body-site relation clarification
4. one visibility/frame clarification
5. resource separation for multiple actors

Do not automatically add `multiple tentacles/too many tentacles` as strength boosters.

## 7. Model-family notes

### WAI Illustrious v17
- broad `tentacles` exposure is likely strong given Danbooru ecosystem, but exact rare relation reliability remains unbenchmarked;
- start from exact author minimal quality/Negative baseline;
- Hires may alter limb/tentacle-human intersections, so base vs final evidence separated.

### NoobAI XL 1.1 EPS
- Danbooru + e621 native-caption training plausibly supports nonhuman appendage vocabulary broadly;
- that does not establish current Semantic labels or every rare relation;
- Special-before-General structure remains relevant for direct learned Specials.

### Anima
- strong learned concepts can bleed into other characters/context in multi-character discussions;
- factual subject/source/relation descriptions are a controlled candidate for relation-heavy tentacle scenes;
- stable names/IDs are preferable to pronouns when multiple actors or appendage owners exist;
- exact tag-only vs hybrid advantage remains TEST_REQUIRED.

## 8. Multiple-actor binding

Tentacle scenes combine two kinds of multiplicity:
- person count
- appendage count.

This creates a resource-allocation problem.

Minimum metadata for tests:
- person count
- tentacle source count
- intended target per source
- intended body site(s)
- intended relation count
- visible appendage count bucket rather than exact count if exact count is not intrinsic.

Diagnostic sequence:
1. each human/character alone if identity matters
2. tentacle concept alone
3. human + tentacle minimal relation
4. multiple humans only after step 3 works
5. extra tentacle-related Special only after ownership is stable.

## 9. Mechanical tentacles as a cross-class case

`mechanical tentacles` is not just `tentacles + machine` semantically. It can fail in several ways:
- organic tentacle with metal texture
- generic robot arm/cable
- machine background plus organic tentacles
- wrong actuator target.

Evaluate both:
- appendage identity
- mechanical identity
- relation.

If the combination only works under a specific LoRA, record `LORA_ASSISTED_ONLY` until base evidence improves.

## 10. Evaluator design

Unary tagger output such as `tentacles` is useful only for appendage presence.

It is insufficient for:
- external vs own-body ownership
- under-clothes relation
- grabbed-by relation
- target body site
- mechanical vs organic function when subtle
- count-specific relation.

Use decomposed predicates:
- `TENTACLE_PRESENT`
- `SOURCE_OK`
- `TARGET_OK`
- `RELATION_OK`
- `BODY_SITE_OK`
- `MECHANICAL_ORGANIC_OK`
- `VISIBILITY_OK`
- `COUNT_DENSITY_ACCEPTABLE`

## 11. Negative Prompt considerations

Hard tentacle scenes may produce extra limbs/fused anatomy. However, negatives aimed at `extra limbs/arms` can plausibly interfere with deliberate multiple appendages or unusual anatomy.

Required strategy:
- minimal family-author baseline first;
- anatomy/count Negative ON/OFF when appendage multiplicity is intrinsic;
- score unwanted human-limb errors separately from intended appendage retention.

Do not use one global anatomy-negative verdict.

## 12. Assisted-control boundary

- regional prompting: useful to keep multiple people/source regions separate;
- pose control: useful for human geometry, not tentacle semantics;
- inpaint: useful for relation/contact repairs;
- open-vocabulary detection: side evidence for object/appendage presence, not final relation.

Forge Couple documentation itself warns that regional conditioning cannot make a checkpoint understand a composition it does not understand.

## 13. Representative test tiers

### Common unary-to-relation
`tentaсles` -> `grabbed by tentacles`

### Clothing relation
`tentaсles` -> `tentacles under clothes` / `tentacle clothes`

### Body-site relation
`tentaсle in mouth` / other target-site examples

### Ownership transformation
`tentaсle hair` / `tentacle tail` / `tentacles as hands`

### Mechanical cross-class
`mechanical tentacles`

### Rare hard composite
one tentacle relation + one independent hard Special, only after each works alone.

## 14. HOLD backlog

- exact WAI v17 rare tentacle-relation success rates
- NoobAI EPS old/current trigger differences for tentacle Semantic/Alias terms
- exact Anima tag-only vs concise NL relation benefit
- reliable automatic ownership/relation evaluator
- best density/count range before visibility collapses
- anatomy-negative interference magnitude
- concept-LoRA style/context leakage by adapter

## Sources

- Project dictionary: `data/special2788/prompt_reference/08_異形・触手・非人間.txt`
- WAI v17: https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170/blob/main/README.md
- NoobAI 1.1: https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- Anima: https://huggingface.co/circlestone-labs/Anima
- Anima multi-character discussion: https://huggingface.co/circlestone-labs/Anima/discussions/93
- T2I-CompBench: https://arxiv.org/abs/2307.06350
- ConceptMix: https://arxiv.org/abs/2408.14339
- Forge Couple: https://github.com/Haoming02/sd-forge-couple
