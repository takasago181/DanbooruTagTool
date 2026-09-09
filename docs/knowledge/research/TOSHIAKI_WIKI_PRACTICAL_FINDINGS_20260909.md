# としあきdiffusion Wiki — DanbooruTagTool向け実践知抽出

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-09

Status: `PRACTICAL_EXTRACTION_V1 / VIDEO_EXCLUDED`

Companion audit:
`docs/knowledge/research/TOSHIAKI_WIKI_SITE_AUDIT_20260909.md`

## 0. Purpose

としあきdiffusion Wikiから、DanbooruTagToolの現在目的に再利用できる **実生成・運用・失敗診断・実験設計の知識**を抽出する。

これはWikiのPromptをそのまま移植するレシピ集ではない。

採用条件:
- canonical meaningと分離する
- exact model/version scopeを保持する
- tool syntaxとmodel semanticsを分離する
- legacy情報を現行モデルへ一般化しない
- operation/postprocess/controlをbase Prompt capabilityと分離する
- fixed-seed一枚比較をreliability証拠へ昇格させない

---

# 1. Reproducibility / traceability

## Finding

Wiki FAQは、同じPromptでも checkpoint、設定、ライブラリ/ツール差などで出力が変わることを繰り返し注意し、model hashやPNG metadata確認を勧める。

## Durable adoption

`ADOPT_PRACTICAL`

Stage10/監査 evidence identity は最低限:
- checkpoint exact name + hash
- architecture/family/version/profile
- UI/tool build when material
- sampler/scheduler
- steps/CFG
- width/height
- seed
- positive actual Prompt
- negative actual Prompt
- LoRA/adapters + weights
- Hires/img2img/ADetailer/control state
- generated-image metadata

を保存する。

### Why it matters

“同じPromptなのに再現しない”をsemantic failureと誤認しない。

---

# 2. Prompt failure diagnosis before `tag unknown`

## Finding

Wiki FAQには、action/poseが出ない原因として、タグの学習上の使われ方、画像内での可視性、別の構図・服装・身体状態等との競合を疑う実践例がある。

## Durable adoption

`ADOPT_PRACTICAL -> reinforces Batch A`

Diagnostic order:
1. canonical/trigger spelling
2. model/version
3. unary concept activation
4. relation/actor-target/body-site
5. visibility/crop/occlusion
6. pose/composition conflict
7. Negative collision
8. Prompt density/weight conflict
9. seed sensitivity
10. LoRA/postprocess/control confound
11. only then `model may not know target`

---

# 3. Prompt syntax is not learned model grammar

## Finding

Wiki syntax pages document A1111/WebUI concepts such as `BREAK`, `AND`, comments, weighting, parser behavior.

## Durable adoption

`ADOPT_TOOL_LAYER_RULE`

Maintain separate layers:
- canonical tag identity
- model prompt surface / learned trigger
- UI/parser syntax
- extension syntax

Examples:
- `BREAK` may move text to another token chunk or alter parser conditioning; it is not proof of learned character separation.
- `# comment` handling is UI/tool behavior.
- composable `AND` behavior belongs to implementation/version scope.

### Audit rule

Never infer semantic meaning from parser syntax alone.

---

# 4. Canonical underscore and model-space surface

## Finding

Danbooru語 page distinguishes website canonical spelling such as underscore form from model prompt practice using spaces.

## Durable adoption

`ADOPT_PRACTICAL`

Persist separately:
- `canonical_tag`: canonical identity with canonical spelling
- `model_surface`: tested model-facing rendering
- `alias/history`: search/identity bridge
- `free_relation_phrase`: generation intervention

Do not rewrite canonical because a model prefers spaces.

---

# 5. Anima: explicit relation description is a serious test lane

## Finding

Wiki’s Anima page contains practical examples for:
- left/center/right actor descriptions
- named/identified actors
- explicit hand/body relation
- replacing vague Danbooru relation tags with explicit factual relation sentences in some cases
- avoiding inherited BREAK-style multi-character tricks

Current official Anima card corroborates key structural premises:
- tag + NL + mixed prompts supported
- pure NL should be descriptive; around 2+ sentences recommended
- multi-character prompts should identify characters/basic appearance
- Gelbooru form may be preferred when Danbooru/Gelbooru differ
- tags are dropped during training

## Durable adoption

`ADOPT_EXPERIMENT_PATTERN / NOT UNIVERSAL RULE`

For relation-heavy Anima cases compare same predetermined seeds:
- A: tag-only
- B: tag anchor + concise factual relation clause
- C: if necessary, explicit actor identities + relation clause

Judge:
- target relation
- actor ownership
- body-site
- collateral identity/style bleed
- visibility

Do not infer that longer NL is always better; only that **explicit structure is a valid controlled intervention**.

---

# 6. Old Illustrious/WAI Negative habits are a risk source

## Finding

Wiki contains long negative recipes inherited from older model generations and generic Illustrious guidance.

WAI v17 author guidance is much more compact and warns against overloading quality/aesthetic/Negative.

## Durable adoption

`REJECT_DEFAULT_STACK / ADOPT_ABLATION`

For WAI v17:
1. start exact author baseline
2. add one Negative function at a time only when needed
3. if target changes anatomy/count, compare anatomy-negative OFF/ON
4. record Special retention and collateral quality separately

For other families, use exact author/card baseline rather than borrowing WAI.

---

# 7. Hires.fix / img2img is evidence-changing intervention

## Finding

Wiki explains Hires as two-stage generation and denoise as controlling second-stage change. FAQ also records that Hires can change composition/details.

## Durable adoption

`ADOPT_PRACTICAL`

Evidence labels:
- `BASE_PROMPT_SUCCESS`
- `HIRES_PRESERVED`
- `HIRES_RESCUE`
- `HIRES_REGRESSION`

An anatomy/geometry relation claim requires base output if final image used Hires.

Exact WAI v17 relevance:
author explicitly says Hires can repair limbs/hands/feet, so final corrected anatomy is not proof of base generation correctness.

---

# 8. ControlNet / regional prompting remains assisted control

## Finding

Wiki has extensive ControlNet and regional-prompting guidance, with many pages spanning SD1.x to modern environments.

## Durable adoption

`ADOPT_CAPABILITY / VERSION_GATE_PARAMETERS`

Use control tools to answer:
- can spatial geometry be rescued?
- can actor regions be isolated?
- is Prompt-only the actual bottleneck?

Do not use assisted success to claim:
- base model understands target relation
- Special support grammar is sufficient
- unary tag exposure is adequate

Legacy SD1.5 ControlNet model names/values: `LEGACY` unless current project stack verifies them.

---

# 9. Forge Neo compatibility is a moving target

## Finding

Wiki Forge Neo page is recently updated and correctly emphasizes that extension/model compatibility can change. It contains some point-in-time limitations for Anima/control/regional extensions.

Official Forge Neo has continued adding Anima/LLLite/Region ControlNet support.

## Durable adoption

`ADOPT_VERSION_CHECK_RULE`

Never encode “Forge Neo cannot do X” as durable rule without exact build/date.

Capability evidence identity:
- Forge Neo commit/release/build
- extension commit/version
- model family
- runtime backend

---

# 10. Dynamic Prompts is useful for controlled enumeration

## Finding

Wiki Dynamic Prompts page documents combinatorial expansion and template patterns. Upstream extension also supports wildcard/template enumeration and repeated generations.

## Durable adoption

`ADOPT_TOOL_CANDIDATE`

Strong uses for DanbooruTagTool knowledge experiments:
- enumerate candidate support `{none|visibility|geometry|broad-parent}`
- keep Prompt skeleton constant
- generate paired seed sets
- preserve exact variant text in metadata

### Boundary

Dynamic Prompts does not solve evaluation and is not semantic authority.

---

# 11. Seed: comparison control, not reliability proof

## Finding

Wiki seed guide correctly teaches fixed-seed comparison.

## Durable adoption

`ADOPT_BASIC / EXTEND_WITH_BATCH_C`

- fixed seed = useful for one-variable visual comparison
- multiple predetermined paired seeds = repeatability evidence
- one seed = case/counterexample only

Do not return to “seed固定一枚で優劣確定”.

---

# 12. LoRA: version compatibility and entanglement are more important than recipes

## Finding

Wiki LoRA pages repeatedly expose practical truths:
- base architecture compatibility matters
- captions decide which features remain associated
- multi-concept training can mix concepts
- dataset composition can dominate output behavior
- experimenting under fixed conditions helps diagnosis

## Durable adoption

`ADOPT_PRACTICAL`

For generation audit:
- LoRA state is evidence identity
- adapter trigger bundle is not canonical definition
- LoRA-assisted success does not prove base checkpoint capability
- adapter may inject pose/style/background priors

For training research:
- exact image counts, loss thresholds, “80–90% dataset quality” etc remain heuristics unless separately tested.

---

# 13. Caption/tag training knowledge: useful but inference transfer must be bounded

## Finding

Wiki caption/tag pages discuss:
- no caption/tag -> high image fidelity but lower concept controllability
- over-captioning -> diluted learning / weak association risk
- multi-concept datasets require careful tag separation

Some pages explicitly self-label as personal heuristics, while others cite training research.

## Durable adoption

`ADOPT_MECHANISM_CAUTION`

Useful for explaining why:
- broad tags can dominate rare specifics
- style/context can become entangled
- trigger spelling may not equal current canonical

Do not convert training-caption heuristics directly into inference Prompt ordering without evidence.

---

# 14. FAQ anatomy/hand practical observations

## Finding

Wiki FAQ reports cases where:
- too many prompts/negatives/weights can blur/degrade
- strong LoRA can cause malformed output
- hand-related negative prompts may hide hands rather than fix them
- resolution/composition can affect anatomy visibility

## Durable adoption

`PRACTICAL / TEST_REQUIRED`

For Special needing hand/body-site visibility:
- do not assume `bad hands` etc is harmless
- compare visible-target retention
- separate “error removed because body part disappeared” from real repair

This is highly relevant to hard/niche Special evaluation.

---

# 15. Legacy universal prompt lists are historical evidence only

## Finding

2022-era pages contain giant “universal” positive/negative stacks.

## Durable adoption

`LEGACY_ONLY`

They are valuable to explain where many community habits came from, but should not seed current WAI/NoobAI/Anima defaults.

Especially avoid copying:
- broad anatomy suppression
- giant quality synonym piles
- old artist/style token assumptions
- SD1.x-specific token tricks

into modern exact-model tests.

---

# 16. Practical findings relevant to current hard/niche research

The Wiki reinforces several existing hard-fetish rules indirectly:

1. **Visibility can masquerade as semantic failure.**
2. **Wrong relation can occur even when nouns are present.**
3. **Negative can hide a hard-to-render body part instead of repairing it.**
4. **Hires can rescue malformed anatomy and must be labeled separately.**
5. **regional/ControlNet can rescue geometry but is assisted.**
6. **old universal negative stacks are particularly risky for unusual anatomy/count.**
7. **model/version/extension drift can change whether a recipe works.**
8. **Prompt syntax hacks are not substitutes for actor/target relation semantics.**

These are cross-source corroborations, not new canonical facts.

---

# 17. Project-facing source-ranking rule

When Wiki advice conflicts with another source, prefer:
1. exact current model/tool author
2. exact current documentation/source code
3. primary research
4. controlled exact-version practical comparison
5. current Wiki practical
6. old Wiki practical
7. generic community recipe

Wiki is especially valuable at levels 4–6 because it captures Japanese workflow reality and failure modes that model cards usually omit.

---

# 18. Current high-value hypotheses from Wiki for later image testing

Keep as `TEST_REQUIRED`:
- Anima tag-only vs explicit concise relation NL for Special binding
- actor identity/position descriptions for multi-character relation
- anatomy/body-site negative OFF/ON
- visibility support vs crop/pose collateral
- broad parent + rare specific interaction
- Hires preservation vs rescue rate on unusual anatomy
- Dynamic Prompts enumeration as low-manual-work A/B generation harness
- exact current Forge Neo regional/control capability under target build

No downstream team handoff is performed in independence mode.
