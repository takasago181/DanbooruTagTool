# Stage10 PROMPT — AIアートのレシピ site-wide audit

最終更新: 2026-09-09
Owner: PROMPT / Issue #5
Source: https://aiartrecipe.com/
Scope: **non-video pages only** per user instruction. Video-focused pages are intentionally excluded.
Status: community-source audit / research reservoir. **Not production specification.**

## 1. Executive verdict

`AIアートのレシピ` は DanbooruTagTool にとって **高価値な日本語コミュニティ実践ソース** である。
ただし、以下の理由から **canonical辞書、model仕様、license/legal判断の正本として丸ごと採用してはいけない**。

### Overall grading

| Dimension | Verdict | Reason |
| --- | --- | --- |
| 日本語での実践アイデア発見 | **A** | ニッチな構図・行為・衣装・camera・supportの候補量が多く、成功/失敗例も豊富 |
| Prompt候補・探索起点 | **A-** | long-tail候補を見つける用途に強い。ただし自然英語phraseとDanbooru tagが混在 |
| 生成失敗知識 | **A** | 「効かなかった」「崩れた」「i2i/Anytestが必要だった」等を率直に記録している記事が多い |
| model比較 | **B+** | 一部記事は共通Prompt/negative/settingsを明示し比較しており有用。sample数・seed固定・version hashが不足する場合あり |
| Danbooru canonical正確性 | **C+** | 正しいtagも多いが、typo、広義/狭義混同、phraseをtag扱いする例がある |
| model普遍則 | **C** | 1 checkpoint / 少数画像の観察を一般化した記述がある |
| 翻訳/UIラベル正確性 | **C** | 分かりやすい意訳は多いが canonical semantic width を保たない例がある |
| tool/platform操作記事 | **C〜B** | 当時の実務には有用だが変更が速い。Prompt knowledgeへは直輸入しない |
| license/legal/policy判断 | **D** | blanketな断定があり、現在の公式規約と再照合必須 |

### PROMPT-side decision

サイト全体を次の扱いとする。

> **`COMMUNITY_JA_CANDIDATE_CORPUS` として採用する。個別知識は必ず canonical / model / version / safety / evidence level を再検証してから昇格する。**

サイトの文章をそのまま「学習済み正解」として扱わない。

---

## 2. Coverage

サイトマップを起点に固定ページ、投稿一覧、カテゴリを確認し、**動画中心の記事を除く掲載記事を横断確認**した。

サイト自身のカテゴリ表示では:
- Prompt: 87
  - プレイ 36
  - シチュ 24
  - キャラ属性 15
  - 部位パーツ 9
- 画像系: 10
- 動画系: 6
- モデル: 2
- ツール: 6
- コラム: 4

カテゴリの表示件数はサイト側の分類であり、記事の主題が複数カテゴリにまたがる可能性はある。
本監査では **動画タイトル/動画生成を主目的とするページは user 指示により除外**した。

Source inventory anchor:
- https://aiartrecipe.com/page-3010
- https://aiartrecipe.com/about
- https://aiartrecipe.com/archives/1756

---

## 3. What is genuinely valuable

### 3.1 Failure evidence is more valuable than the copy-paste Prompt itself

このサイトの最大価値は「成功Prompt集」そのものより、失敗・限界を書いている部分にある。

Examples:
- complex pose がPrompt-onlyで成立せず Anytest を使ったケース
- multiple actor / feet / relationが融合し、i2iへ移行したケース
- Danbooru tagらしき語を入れても特定checkpointで反応しなかったケース
- object / appendage / clothing relationの局所制御が不安定だったケース
- modelを変えると同じPromptでも属性bindingが変わったケース

PROMPT-side use:
- `PROMPT_ONLY_LIMIT`
- `RELATION_FAILURE`
- `BODY_SITE_BINDING_ERROR`
- `OBJECT_DEGRADES`
- `GEOMETRY_FAILURE`
- `MODEL_TRIGGER_MISMATCH`

の実例候補として高価値。

### 3.2 Clothing-aside family is a strong example

記事 `clothing aside / pull` は broad theme と garment-specific tags を分離している。

Site examples include:
- `clothing aside`
- `panties aside`
- `swimsuit aside`
- `bikini bottom aside`
- `leotard aside`
- `fundoshi aside`
- `shorts aside`

Danbooru/Safebooru wiki側でも garment-specific aside family が確認できるため、この部分は **semantic candidateとして強い**。

PROMPT lesson:
- broad themeだけでなく、render-critical subtypeを選ぶ
- `aside` と `pull` の visual result difference を別featureとして扱う

### 3.3 Model-comparison articles are stronger than generic Prompt articles

`Illustrious系NSFWモデルおすすめ8選` は以下を明示している。
- common minimal prompts
- common negative
- resolution 832×1216
- Euler a
- Steps 30
- CFG 5〜7
- hands / feet / multi-person / noise / usability の評価軸

これは一般Prompt記事より再現性が高い。
ただし:
- CFGが単一値ではない
- seed / sample count / exact hash が完全固定ではない
- 各modelのrecommended Prompt grammarへ最適化した比較ではない

ため、`COMMUNITY_JA_STRONG` だが benchmark truth ではない。

### 3.4 Anima vs Illustrious comparison is directionally useful

記事 `自然言語でエロが捗る！Anima vs Illustrious比較検証まとめ` は、same/hybrid Promptを用いて relation / object / location / multiple-character の差を比較している。

方向性は Anima official model card の以下と整合する。
- Danbooru-style tags + natural-language captions + mix
- multiple charactersではcharacter nameだけでなくappearance descriptionが重要
- descriptive natural languageを推奨

PROMPT-side use:
- `TAG_ONLY vs TAG_PLUS_RELATION_SENTENCE`
- `APPEARANCE_ANCHOR`
- `RELATION_BINDING`

のStage10候補。

ただし local small-sample observation であり universal success rate にはしない。

### 3.5 Caption/tagger comparison is useful for evaluator skepticism

`ComfyUIで...プロンプトを考えてもらおう` では DeepDanbooru / WD14 / BLIP / JoyCaption 等を比較し、false positive・冗長・hallucinationのような差を実例で示す。

特に WD14 result に不適切な年齢系labelが混入した例があり、**image taggerをground truthとして扱えない**ことの実践証拠になる。

Official WD EVA02-Large Tagger v3 itself is a classifier supporting ratings/characters/general tagsであり、semantic judgeやrelation judgeではない。

PROMPT/TEMP lesson:
- tagger confidence != semantic truth
- unsupported / ambiguous hard target -> REVIEW
- evaluator errorをPrompt failureとして数えない

---

## 4. Concrete errors and weak points

### 4.1 Typographical errors invalidate some “does not work” conclusions

Master prompt page contains `collorbone` for collarbone.

Fluid-related article lists `ejucalation` and later `ejecalation` while discussing English `ejaculation`, then concludes the prompt has no effect.

Decision:
- `REJECT_ERROR`
- misspelled tokenからmodel understandingを評価しない
- site token must pass spelling/canonical normalization before use

### 4.2 Internal semantic inconsistency: tan

Master page maps:
- `tan` -> 「褐色肌」

Dedicated 2026 tan article separately explains:
- `tan` -> 日焼け
- `dark skin` -> 褐色肌
- `light brown skin` -> 小麦色

Danbooru skin-color grouping also distinguishes `tan` and `dark skin` as separate natural skin categories.

Decision:
- dedicated explanation is closer to correct semantic separation
- master dictionary translation is too broad
- Japanese overlay must not import `tan=褐色肌` as exact equivalence

### 4.3 `flat chest = 無乳` is over-compressed

Master page and breast article map `flat chest` to 「無乳」.
Danbooru semantics/history treat `flat chest` as a size/flatness class, not a literal anatomical absence of the chest/breast structures.

Decision:
- useful colloquial gloss only
- **not valid as Japanese UI exact display label**
- #36/#38-style display semantics must preserve width independently

### 4.4 `milf = セクシーな女性` is too broad

Master page maps `milf` to a generic “sexy woman”. This loses age/parental/mature connotation and would create false search matches.

Decision:
- `REJECT_SEMANTIC_BROADENING` for exact dictionary use
- at most community search-language evidence, not canonical display

### 4.5 Misspelled bestiality token and safety contamination

Master page contains `beastiality` rather than `bestiality`.
More importantly, the site mixes adult-consensual candidates with content involving minors, non-consensual acts, sleep/incapacitation, and animal-sex themes.

Decision:
- these rows/articles are **`SAFETY_QUARANTINE / DO_NOT_IMPORT`** into reusable DanbooruTagTool Prompt knowledge.
- site-wide ingestion must filter them before lexical/Prompt adoption.

### 4.6 Phrase vs canonical tag is often unclear

Many entries are plausible English constructions such as `X around Y`, `X in Y`, or scene descriptions.
Some are effective natural-language conditioning, but not necessarily Danbooru canonical tags.

Decision:
Every extracted term receives a type:
- `DANBOORU_CANONICAL_VERIFIED`
- `DANBOORU_ALIAS_VERIFIED`
- `MODEL_TRIGGER_OBSERVED`
- `NATURAL_LANGUAGE_PHRASE`
- `UNKNOWN_TERM`

No phrase is promoted to canonical by site usage alone.

### 4.7 Single-image weights are local tuning, not universal knowledge

The site frequently uses weights like 0.7 / 0.9 / 1.4 / 1.5 and infers stronger/weaker effects.

Decision:
- keep as `MODEL_LOCAL_OBSERVATION`
- never promote numeric weight globally without fixed-seed / multi-seed A/B

---

## 5. Hard-target findings relevant to current product goal

The site materially reinforces the current PROMPT hard-image architecture.

### 5.1 Broad theme vs render-critical decomposition

Machine article supports decomposition into:
- machine identity
- active component
- restraint / support
- pose
- target/site
- visibility

Tentacle article likewise separates:
- appendage identity
- body location / role
- restraint vs insertion role
- multi-site complexity

These are **useful architecture evidence**, even when individual phrases are not canonical.

### 5.2 Multi-role / multi-site scenes become unstable quickly

Across group, double-action, tentacle, machine, multiple-person, 69, foot/hand relation articles, recurring failure modes are:
- role loss
- body-site drift
- actor fusion
- extra/missing people
- appendage/object becomes decorative
- target interaction disappears
- framing hides the intended act

This strongly supports current PROMPT failure taxonomy instead of simple tag-presence scoring.

### 5.3 Prompt-only ceiling is real and observable

The site sometimes explicitly resorts to:
- Anytest / ControlNet
- img2img
- LoRA
- manual face/object correction

when Prompt-only cannot hold geometry or relation.

Decision:
- these are positive evidence for `ASSISTED_CONTROL_CANDIDATE`
- **do not count the final assisted image as evidence that the Prompt itself succeeded**

### 5.4 Generic negative templates should not be universalized

A repeated site default is approximately:
`bad quality, worst quality, worst detail, sketch, text/watermark`.

This is useful as a local controlled baseline, but not a universal optimum.
Existing family evidence says:
- WAI author guidance warns against overly long negative / excessive aesthetic instructions
- Anima has profile-specific quality/meta behavior

Decision:
- retain as `SITE_BASELINE_NEGATIVE`
- do not make production global default solely from this site.

---

## 6. Tool / platform content

### Useful but volatile

SeaArt, RunPod, ComfyUI cloud workflows, Qwen image-edit, search workarounds and similar pages can be useful operational snapshots.

They are not stable Prompt semantics because:
- UI changes
- model availability changes
- moderation changes
- cost/limits change
- extension names/version behavior changes

Classification:
- `TIME_SENSITIVE_TOOL_NOTE`
- re-check before recommendation

### Safeguard-bypass pages

The site includes pages describing methods intended to circumvent platform NSFW filters or blocked prompt words.

Decision:
- **not imported into DanbooruTagTool Prompt corpus**
- classify `OUT_OF_SCOPE_PLATFORM_CIRCUMVENTION`
- local Prompt semantics learned elsewhere remain separable from bypass procedures

---

## 7. License / policy audit

Article `Stable Diffusionのエロ規制後もSDXLでやります` is not reliable enough for legal/ToS decisions.

Site argument broadly treats old model-license status as meaning later restrictions pose no legal/ToS risk.
That is too categorical.

Current official Stability AI AUP page (effective July 31, 2025 at current rendered page) states that the AUP applies to Stability Technology including self-hosting under named Stability licenses and explicitly prohibits sexually explicit acts. The Stability license page separately describes current Community/Enterprise licensing for current Core Models.

Important nuance:
- exact obligations depend on **exact artifact, model version, original license, derivative license, and applicable policy version**
- old SDXL/OpenRAIL artifacts should not be legally classified from a generic current AUP alone either
- therefore neither “everything is prohibited” nor “there is zero legal/ToS risk” should be inferred without exact license review

Decision:
- site legal article -> `LEGAL_RECHECK_REQUIRED`
- no production decision based on it

### Anima license example

Official Anima model card currently states:
- model / derivatives under CircleStone non-commercial license
- generated outputs may be used commercially under the stated model-card conditions

Therefore a generic site claim that an Anima-derived setup is simply “commercially OK” requires exact checkpoint/license review.

---

## 8. Reliability classes for site ingestion

### `COMMUNITY_JA_STRONG`
Use when:
- model/version disclosed
- settings disclosed
- A/B or several comparable samples
- failures reported
- claim limited to observed result

Examples:
- Illustrious 8-model comparison
- Anima vs Illustrious relation comparison
- caption/tagger comparison

### `COMMUNITY_JA_USEFUL`
Use when:
- practical example is clear
- semantics plausible
- limited sample / single checkpoint

Most dedicated Prompt articles fall here.

### `COMMUNITY_JA_WEAK`
Use when:
- single image
- no seed/settings/model pin
- causal claim inferred from appearance

### `HOLD_CANONICAL`
Use when:
- word/phrase may work but Danbooru canonical status not verified

### `MODEL_LOCAL_OBSERVATION`
Use when:
- model-specific side effect or weight is observed
- no cross-model/multi-seed evidence

### `REJECT_ERROR`
Use for:
- spelling mistakes
- impossible/contradictory semantic mapping
- unsupported exact-equivalence

### `TIME_SENSITIVE_TOOL_NOTE`
Use for:
- SeaArt / cloud / API / extension state

### `LEGAL_RECHECK_REQUIRED`
Use for:
- licensing, ToS, commercial-use claims not independently verified

### `SAFETY_QUARANTINE`
Use for:
- sexual content involving minors or ambiguous minors
- non-consensual sexual scenarios
- incapacitated/sleeping victim scenarios
- animal-sex themes
- other content outside this project’s adult-consensual reusable corpus

---

## 9. Adopt candidates from the site

The following *types of knowledge* are worth preserving:

1. **Japanese terminology / user-intent vocabulary**
   - excellent search-intent evidence, after semantic review
2. **long-tail scene candidates**
   - strong source of Stage10 stress-test ideas
3. **failure patterns**
   - especially relation, geometry, object, multi-actor
4. **Prompt-only limit reports**
5. **support-role decomposition candidates**
   - frame, viewpoint, pose, visibility, object/site support
6. **model-local observations**
   - only with model/version metadata
7. **negative side-effect observations**
8. **tagger/captioner limitations**

Do not directly adopt:
- the site master dictionary as canonical
- Japanese display translations as authoritative
- generic weight numbers
- one universal negative
- one universal quality prefix
- commercial-use labels
- platform bypass recipes
- safety-quarantined sexual themes

---

## 10. Site influence on Stage10 planning

AIアートのレシピ increases the priority of the following Stage10 questions:

1. `CANONICAL vs MODEL_TRIGGER vs NL_PHRASE`
2. broad tag vs specific/render-critical decomposition
3. single role vs multi-role appendage/object
4. tag-only vs short relation sentence by family
5. visibility support and unintended composition shift
6. minimal negative vs site generic negative
7. weight off vs local suggested weight
8. Prompt-only vs assisted-control escalation
9. evaluator false-positive / false-negative handling
10. Japanese user-intent search vocabulary vs exact display semantics

---

## 11. Final PROMPT verdict

**ADOPT THE SITE AS A LARGE COMMUNITY EVIDENCE SOURCE; DO NOT ADOPT IT AS TRUTH.**

Best use:
- idea mining
- Japanese intent vocabulary
- failure mining
- hard-target stress-case mining
- model-local hypothesis generation

Worst use:
- canonical dictionary import
- exact Japanese UI translation import
- legal/license decisions
- global model grammar
- universal weights/negative templates

The correct ingestion pipeline is:

`AIartrecipe observation`
→ `spell/term normalization`
→ `safety quarantine`
→ `Danbooru canonical/alias verification`
→ `model/version attribution`
→ `evidence class`
→ `Stage10 A/B when material`
→ only then `PROMPT adopt / HOLD / reject`.

---

## 12. External verification anchors

Primary / authoritative references used for validation:

- AIアートのレシピ sitemap: https://aiartrecipe.com/page-3010
- AIアートのレシピ master prompt page: https://aiartrecipe.com/archives/1756
- Anima official model card/license: https://huggingface.co/circlestone-labs/Anima
- NoobAI XL 1.1 official model card: https://huggingface.co/Laxhar/noobai-XL-1.1
- WD EVA02-Large Tagger v3: https://huggingface.co/SmilingWolf/wd-eva02-large-tagger-v3
- JoyCaption official repository: https://github.com/fpgaminer/joycaption
- Stability AI AUP: https://stability.ai/use-policy
- Stability AI license page: https://stability.ai/license
- Danbooru/Safebooru wiki surfaces for tag semantic verification: https://safebooru.donmai.us/wiki_pages

## Boundary

- PROMPT branch only.
- KNOWLEDGE #44 not modified.
- Production data/spec not modified.
- Stage10 production A/B not started.
- Site contents are not copied wholesale; only audit summaries / observations / source references are stored.
