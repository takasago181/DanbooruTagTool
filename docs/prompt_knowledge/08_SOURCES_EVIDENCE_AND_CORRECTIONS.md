# 08 Sources, evidence and corrections

Owner: PROMPT / Issue #5
Status: evidence-routing knowledge summary. Not production specification.

Current claim authority: `CLAIM_REGISTRY.md`
Label schema: `00_KNOWLEDGE_GOVERNANCE.md`
Legacy label translation: `LABEL_MIGRATION_MAP.md`
Freshness: `VERSION_AND_FRESHNESS.md`

## 目的

「どこに書いてあったか」ではなく、**その主張を何の種類の証拠として使えるか**を整理する。

---

## 5層source backbone

### 1. Semantic authority
SOURCE_CLASS: `SEMANTIC_AUTHORITY`

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
SOURCE_CLASS: `OFFICIAL_MODEL` / `AUTHOR_GUIDE`

用途:
- caption structure
- recommended settings
- quality/meta/safety
- natural-language対応
- version差

主:
- exact model/version Hugging Face model card
- model author official page / author Civitai

重要:
公式記述そのものは`ACCEPTED`でも、そこから導く「hard-target最適化」は別claimで`CANDIDATE`になり得る。

### 3. Runtime authority
SOURCE_CLASS: `OFFICIAL_RUNTIME`

用途:
- parser syntax
- regional conditioning
- ControlNet
- ADetailer
- Dynamic Prompts
- Forge Couple

主:
- exact extension/runtime official GitHub

Local applicabilityは`VALIDATED_LOCAL`または`LOCAL_RECHECK`を別管理。

### 4. Failure research
SOURCE_CLASS: `RESEARCH`

用途:
- semantic neglect
- attribute binding
- relation/composition failure
- spatial control
- evaluator設計の背景

主:
- arXiv / primary research

研究はfailure mechanism/taxonomyには使えるが、exact WAI/NoobAI/Anima挙動の証明にはしない。

### 5. Community evidence
SOURCE_CLASS: `COMMUNITY`

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

communityは候補を増やすために重要だが、通常STATUSは`CANDIDATE`から開始する。

---

## Current STATUS vocabulary

現在の採用状態は次だけをcurrent labelとして使う。

- `ACCEPTED`
- `CANDIDATE`
- `HOLD`
- `CONFLICT`
- `REJECTED`
- `HISTORICAL`

旧 `OFFICIAL_FACT / COMMUNITY_JA_STRONG / RATIONALE_INCORRECT...` 等はlegacy evidence labelとして残り、`LABEL_MIGRATION_MAP.md` で読み替える。

---

## 主張別の優先権

- タグの意味 -> Danbooru semantic authority
- exact model behavior/settings -> exact model author
- extension/parser -> official repo
- general failure mechanism -> research
- practical trick -> community + controlled reproduction

一つのglobal rankingで全部を比べない。

---

## Official model sources

### WAI Illustrious v17
SOURCE_CLASS: `AUTHOR_GUIDE`

- author-linked Civitai / author instruction mirror
- current project exact local model: WAI v17

Use for:
- Forge Neo recommendation
- Steps/CFG/Euler a
- VAE integrated
- resolution/Hires examples
- lean quality/Negative warning

Claim examples:
- author settings facts: `K-WAI-001` ACCEPTED
- long Negative warning: `K-WAI-004` ACCEPTED
- `LEAN_TAG_FIRST` optimum: `K-WAI-005` CANDIDATE

### NoobAI XL 1.1
SOURCE_CLASS: `OFFICIAL_MODEL`

- https://huggingface.co/Laxhar/noobai-XL-1.1

Use for:
- native caption order
- Special before General baseline
- Danbooru/e621 training statement
- official generation settings

Claims: `K-NOOB-*`

### Illustrious XL
SOURCE_CLASS: `OFFICIAL_MODEL`

- https://huggingface.co/OnomaAIResearch/Illustrious-XL-v1.1
- official Illustrious platform

Use for:
- exact version behavior
- NL support direction
- WAI derivativeとbaseの分離

Claims: `K-ILL-*`

### Anima
SOURCE_CLASS: `OFFICIAL_MODEL`

- https://huggingface.co/circlestone-labs/Anima

Use for:
- tags/NL/hybrid
- tag section order
- `1girl`等のcount validity
- appearance anchors for multiple characters
- profile-specific quality/weighting

Claims: `K-ANIMA-*`

---

## Danbooru / e621

### Danbooru
SOURCE_CLASS: `SEMANTIC_AUTHORITY`

DanbooruTagTool canonical semantic authority。

重要:
- broad conceptとrender-critical subtypeを分ける
- alias/implicationはsemantic relation
- model response equivalenceの証明ではない

Claims: `K-SEM-001/002/003/005`

### e621
SOURCE_CLASS: `SEMANTIC_AUTHORITY` with supplemental scope only

`SUPPLEMENTAL_NONHUMAN_TAXONOMY`。

- NoobAIがe621をtrainingに使ったため調査価値あり
- Danbooru canonicalへ自動昇格しない
- scope/fandom semantics差を確認

Claims: `K-SEM-006/007`

---

## Research ledger

SOURCE_CLASS: `RESEARCH`

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

Claims:
- `K-FAIL-001/002/003`
- related evaluator/control principles

研究が証明しないもの:
- WAI/NoobAI/Animaのexact prompt order
- exact support tag
- canonical vs Alias response
- exact Negative
- AUTO threshold

---

## AIArtRecipeの扱い

SOURCE_CLASS: `COMMUNITY`
Default STATUS: `CANDIDATE`

総評:
- 日本語実践アイデア: 高価値
- Prompt候補発見: 高価値
- failure examples: 高価値
- model comparison: 条件付き有用
- canonical正確性: 要検証
- legal/license: 正本として不適

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

---

## としあきdiffusion Wikiの扱い

SOURCE_CLASS: `COMMUNITY`
Default STATUS: `CANDIDATE`

総評:
- Prompt構造、Forge運用、model差、failure切り分けに非常に有用
- ただし旧SD/NAI/SDXL/Illustrious/Animaの知識が同居
- 更新日だけでcurrent validityを判断しない

重要訂正:
1. Anima count tag: tag modeは公式 `1girl/1boy`。`1 girl` global defaultはREJECTED (`K-ANIMA-004`)
2. Anima Qwen 1k token固定説明: REJECTED (`K-ANIMA-005`)
3. Illustrious generic long NegativeをWAI17へ継承しない
4. BREAK: model factでなくparser/environment scoped (`K-ANIMA-008`)
5. underscore/canonical identityとrender surfaceを分離
6. Danbooru tag exists != usable/effective Prompt
7. related tags reinforcementはcandidate
8. generic quality/Negative inheritance禁止
9. weighting syntaxとweight値を分離
10. tagger rankingはhistorical/time-sensitive
11. old万能長文テンプレはHISTORICAL
12. Anima short relation supportはofficial directional supportあり、最適化claimはCANDIDATE (`K-ANIMA-006`)

詳細:
- `docs/stages/STAGE_10_PROMPT_TOSHIAKI_WIKI_AUDIT_20260909.md`
- `...TOSHIAKI_WIKI_CORRECTIONS_20260909.md`
- `...TOSHIAKI_WIKI_COVERAGE_LEDGER_20260909.md`
- `...TOSHIAKI_WIKI_INGESTION_RULES_20260909.md`

---

## Community ingestion checklist

外部siteからPrompt知識を採る前に:
1. spelling/canonical check
2. canonical tag / alias / NL phrase / observed triggerを分類
3. model/version確認
4. seed/settings/sample条件確認
5. successだけでなくfailure確認
6. safety/out-of-scope分離
7. officialと衝突確認
8. SOURCE_CLASSを付与
9. STATUSを付与
10. SCOPE / VALIDATION_STATEを付与
11. production behaviorに影響するならStage10 A/B
12. material claimならClaim IDを登録

---

## Conflict policy

Wiki/communityとofficialが食い違う場合:
1. community observationを削除せず保持
2. exact scopeを付ける
3. STATUS=`CONFLICT`またはcommunity claim=`REJECTED`を明示
4. officialをbaselineにする
5. version-pinned controlled reproductionでcommunity exceptionが再現した場合のみclaim statusを再評価

---

## Freshness policy

- exact model/version/sourceの確認日は `VERSION_AND_FRESHNESS.md`
- community publish dateだけでcurrent validityを判断しない
- runtime/extensionはlocal version一致を別確認
- WAI17 author primaryはfinal production promotion前に再check

---

## 詳細 backbone

- `docs/stages/STAGE_10_PROMPT_PRIMARY_SOURCE_BACKBONE_20260909.md`
- `docs/stages/STAGE_10_PROMPT_MODEL_OFFICIAL_SOURCE_MATRIX_20260909.md`
- `docs/stages/STAGE_10_PROMPT_SEMANTIC_AUTHORITY_DANBOORU_E621_20260909.md`
- `docs/stages/STAGE_10_PROMPT_COMPOSITIONAL_FAILURE_RESEARCH_LEDGER_20260909.md`
