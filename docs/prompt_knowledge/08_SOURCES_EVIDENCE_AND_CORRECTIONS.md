# 08 Sources, evidence and corrections

Owner: PROMPT / Issue #5
Status: evidence-routing knowledge summary. Not production specification.

## 目的

「どこに書いてあったか」ではなく、**その主張を何の種類の証拠として使えるか**を整理する。

## 5層source backbone

### 1. Semantic authority
用途:
- canonical meaning
- alias / implication
- broad vs specific
- body-site / relation / poseの語義

主:
- Danbooru Wiki / tag groups / alias / implication

補助:
- e621 Wiki（non-human/creature taxonomy限定）

### 2. Model authority
用途:
- caption structure
- recommended settings
- quality/meta/safety
- natural-language対応
- version差

主:
- exact model/version Hugging Face model card
- model author official page / author Civitai

### 3. Runtime authority
用途:
- parser syntax
- regional conditioning
- ControlNet
- ADetailer
- Dynamic Prompts
- Forge Couple

主:
- exact extension/runtime official GitHub

### 4. Failure research
用途:
- semantic neglect
- attribute binding
- relation/composition failure
- spatial control
- evaluator設計の背景

主:
- arXiv / primary research

### 5. Community evidence
用途:
- 日本語実践知
- real workflow
- failure examples
- model-specific tips候補

主:
- としあきdiffusion Wiki
- AIArtRecipe
- Note
- Reddit等

communityは候補を増やすために重要だがproduction truthへ直昇格しない。

## 主張別の優先権

- タグの意味 -> Danbooru semantic authority
- exact model behavior/settings -> exact model author
- extension/parser -> official repo
- general failure mechanism -> research
- practical trick -> community + controlled reproduction

一つのglobal rankingで全部を比べない。

## Evidence labels

- `OFFICIAL_FACT`
- `AUTHOR_GUIDE`
- `OFFICIAL_RUNTIME_FACT`
- `SEMANTIC_AUTHORITY`
- `RESEARCH_BACKGROUND`
- `CONTROLLED_PRACTICAL`
- `COMMUNITY_JA_STRONG`
- `COMMUNITY_CANDIDATE`
- `MODEL_LOCAL_OBSERVATION`
- `PROJECT_HYPOTHESIS`
- `HOLD`
- `CONFLICT`
- `CONTRADICTED_BY_OFFICIAL`
- `RATIONALE_INCORRECT`
- `HISTORICAL_ONLY`
- `TIME_SENSITIVE_TOOL_NOTE`

## Official model sources

### WAI Illustrious v17
- author-linked Civitai / author instruction mirror
- current project exact local model: WAI v17

Use for:
- Forge Neo recommendation
- Steps/CFG/Euler a
- VAE integrated
- resolution/Hires examples
- lean quality/Negative warning

### NoobAI XL 1.1
- https://huggingface.co/Laxhar/noobai-XL-1.1

Use for:
- native caption order
- Special before General baseline
- Danbooru/e621 training statement
- official generation settings

### Illustrious XL
- https://huggingface.co/OnomaAIResearch/Illustrious-XL-v1.1
- official Illustrious platform

Use for:
- exact version behavior
- NL support direction
- WAI derivativeとbaseの分離

### Anima
- https://huggingface.co/circlestone-labs/Anima

Use for:
- tags/NL/hybrid
- tag section order
- `1girl`等のcount validity
- appearance anchors for multiple characters
- profile-specific quality/weighting

## Danbooru / e621

### Danbooru
DanbooruTagTool canonical semantic authority。

重要:
- broad conceptとrender-critical subtypeを分ける
- alias/implicationはsemantic relation
- model response equivalenceの証明ではない

### e621
`SUPPLEMENTAL_NONHUMAN_TAXONOMY`のみ。

- NoobAIがe621をtrainingに使ったため調査価値あり
- Danbooru canonicalへ自動昇格しない
- scope/fandom semantics差を確認

## Research ledger

保持している研究:
- Attend-and-Excite
- T2I-CompBench
- Object-Attribute Binding in T2I
- MultiDiffusion
- Concept Conductor

研究から採用する一般原則:
- token presentは十分条件ではない
- target missingとwrong bindingは別failure
- multi-object/relationはdistinct difficulty class
- attribute leakageは既知problem
- spatial controlはPrompt-only layout failureへの合理的intervention候補

研究が証明しないもの:
- WAI/NoobAI/Animaのexact prompt order
- exact support tag
- canonical vs Alias response
- exact Negative
- AUTO threshold

## AIArtRecipeの扱い

総評:
- 日本語実践アイデア: 高価値
- Prompt候補発見: 高価値
- failure examples: 高価値
- model comparison: 条件付き有用
- canonical正確性: 要検証
- legal/license: 正本として不適

分類:
`COMMUNITY_JA_CANDIDATE_CORPUS`

強い用途:
- failure example reservoir
- niche support/camera/object候補
- Prompt-only ceiling実例
- assisted workflow実例

注意例:
- typoから「modelが理解しない」と結論したケース
- `tan`の意味幅の内部矛盾
- `flat chest`等の日本語意訳のsemantic圧縮
- natural-language phraseとcanonical tagの混在
- local weight値の一般化

安全/範囲外項目はreusable Prompt corpusへ取り込まない。

詳細:
- `docs/stages/STAGE_10_PROMPT_AIARTRECIPE_SITE_AUDIT_20260909.md`
- `...AIARTRECIPE_INGESTION_RULES_20260909.md`
- `...AIARTRECIPE_COVERAGE_LEDGER_20260909.md`

## としあきdiffusion Wikiの扱い

総評:
- Prompt構造、Forge運用、model差、failure切り分けに非常に有用
- ただし旧SD/NAI/SDXL/Illustrious/Animaの知識が同居
- 更新日だけでcurrent validityを判断しない

重要訂正:
1. Anima count tag: tag modeは公式 `1girl/1boy`。`1 girl` global defaultは不採用
2. Anima Qwen 1k token固定説明: rationale incorrect
3. Illustrious generic long NegativeをWAI17へ継承しない
4. BREAK: model factでなくparser/environment scoped
5. underscore/canonical identityとrender surfaceを分離
6. Danbooru tag exists != usable/effective Prompt
7. related tags reinforcementはcommunity candidate
8. generic quality/Negative inheritance禁止
9. weighting syntaxとweight値を分離
10. tagger rankingはdated
11. old万能長文テンプレはhistorical only
12. Anima short relation supportはofficial directional supportあり、ただしNL万能ではない

詳細:
- `docs/stages/STAGE_10_PROMPT_TOSHIAKI_WIKI_AUDIT_20260909.md`
- `...TOSHIAKI_WIKI_CORRECTIONS_20260909.md`
- `...TOSHIAKI_WIKI_COVERAGE_LEDGER_20260909.md`
- `...TOSHIAKI_WIKI_INGESTION_RULES_20260909.md`

## Community ingestion checklist

外部siteからPrompt知識を採る前に:
1. spelling/canonical check
2. canonical tag / alias / NL phrase / observed triggerを分類
3. model/version確認
4. seed/settings/sample条件確認
5. successだけでなくfailure確認
6. safety/out-of-scope分離
7. officialと衝突確認
8. evidence label
9. ADOPT/HOLD/CONFLICT
10. production behaviorに影響するならStage10 A/B

## Conflict policy

Wiki/communityとofficialが食い違う場合:
1. community observationを削除せず保持
2. exact scopeを付ける
3. conflict label
4. officialをbaselineにする
5. version-pinned controlled reproductionでcommunity exceptionが再現した場合のみ再昇格

## 詳細 backbone

- `docs/stages/STAGE_10_PROMPT_PRIMARY_SOURCE_BACKBONE_20260909.md`
- `docs/stages/STAGE_10_PROMPT_MODEL_OFFICIAL_SOURCE_MATRIX_20260909.md`
- `docs/stages/STAGE_10_PROMPT_SEMANTIC_AUTHORITY_DANBOORU_E621_20260909.md`
- `docs/stages/STAGE_10_PROMPT_COMPOSITIONAL_FAILURE_RESEARCH_LEDGER_20260909.md`
