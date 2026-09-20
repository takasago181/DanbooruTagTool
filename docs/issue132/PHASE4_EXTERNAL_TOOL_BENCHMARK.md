# Issue #132 Phase 4 — External prompt/tag support tool benchmark

Date: 2026-09-20
Status: RESEARCH ONLY / NO PRODUCT CHANGE

## Purpose

実際の成人向け画像生成で Danbooru タグを発見・選択・Prompt化するUXを改善するため、2026-09-20時点で利用可能な他のタグ探索 / Prompt支援ツールを比較した。

比較軸:
- unknown-tag discovery
- Japanese discovery
- category/facet structure
- related/co-occurrence discovery
- NSFW/adult handling
- prompt workspace
- model-aware output
- ambiguity/context handling

Phase 3 の `intent-first / multi-axis scene discovery` 仮説が、既存ツールの実装慣行と整合するかを見る。

---

## 1. Tools reviewed

### SD WebUI Tag Autocomplete

Pattern:
- type-first autocomplete
- exact Danbooru/e621 tag inventory
- translations
- keyboard-first insertion

Strength:
- 既知タグ / 部分的に名前を知っているタグは非常に速い

Weakness:
- 「概念は知っているがタグ名を知らない」発見には弱い
- scene constructionの次元を案内しない

Lesson:
- autocompleteは必須のfast pathだが、browse UXの代替にはならない

### NovelAI built-in tag suggestions

Pattern:
- 入力中にknown tag候補
- tag knowledge indicator
- Japanese input -> relevant tag suggestion
- prompt length/context budget visible

Strength:
- taxonomyを学ばせず、入力行動の中で候補を返す
- model-side knowledgeを可視化

Lesson:
- ユーザーに分類構造を先に理解させない
- tag confidence/usage evidenceを候補横に出す考えは有効
- prompt overloadを可視化する考えも有効

### Danbooru Tag Explorer

Pattern:
- category tree
- JP/EN full text search
- post-count sorting
- wiki hover
- related-tag traversal
- scratchpad
- favorites/pins
- optional LLM Japanese -> Danbooru tag
- browse history

Strength:
- treeだけでなく search / related / scratchpad を併用
- discoveryとprompt assemblyを分離

Weakness:
- tree自体はDanbooru wiki/group由来でmechanical classification errorsを含みうると作者自身が注意
- deep treeはunknown-tag explorationでbacktrackingを起こしやすい

Lesson:
- taxonomyは入口の一つ
- wiki/related/scratchpad/historyの方が日常UXに効く

### JP Tag Assistant

Pattern:
- Japanese keyword search
- alias search
- ambiguous-word expansion
- post count
- co-occurrence related tags
- related modes:
  - Auto
  - Recommended
  - Person
  - Scene / Objects
  - Style / Quality
  - NSFW
  - All
  - Off
- related back/forward history
- click insert/removal

Most relevant point:
- `Auto` chooses a related direction from the selected tag
- e.g. missionary -> NSFW
- categories are intentionally non-exclusive

Lesson:
- **selected-tag-aware next discovery** is already a practical pattern
- adult discovery can be a mode/lens rather than a standalone exclusive taxonomy
- back/forward is important for exploratory search

### DanbooruSearch / ComfyUI DanbooruSearcher

Pattern:
- semantic search from natural/multilingual description
- distinct search modes:
  - precise lookup
  - concept explore
  - subject describe
  - full scene
- automatic phrase segmentation
- co-occurrence related recommendations
- selected-tag workspace
- prompt weight editing
- undo/redo/history/favorites/import/backup
- category hard filter

Most relevant point:
- exact lookup, concept exploration and full-scene discovery are treated as different tasks
- selected tags drive follow-up related recommendations
- search and workspace are distinct

Lesson:
- one universal search box/ranking should not be forced to satisfy all discovery intents
- DanbooruTagTool should distinguish at least:
  - exact tag lookup
  - concept discovery
  - scene completion

### dbtagger

Pattern:
- start with one tag
- related tags based on real-post co-occurrence
- Typical / Focused / Exploratory ranking
- curate into a positive draft
- reorder/remove afterwards
- clearly warns:
  co-occurrence != semantic similarity != model knowledge

Lesson:
- related suggestions need provenance labels
- do not present co-occurrence as "correct Prompt companion"
- exploration breadth should be adjustable

### Prompt All-in-One

Pattern:
- bilingual prompt editor
- automatic translation
- history
- favorites
- drag reorder
- weight increase/decrease
- disable/delete
- batch operations
- one-click prompt word addition

Lesson:
- once a tag is found, editing ergonomics matter as much as taxonomy
- history/favorites/reorder belong to the Prompt workspace, not to classification

### BooruTagCart

Pattern:
- search / autocomplete / filtering
- selected-tag cart
- drag reorder
- formatting
- translation
- popularity / aliases / category metadata
- prompt import

Lesson:
- "shopping cart" metaphor works:
  discovery list and selected Prompt list are separate states
- selected state should persist while user keeps exploring

### Danbooru 标签超市 (tags.novelai.dev)

Pattern:
- category browse
- explanations / images
- positive and negative carts
- drag order
- weight controls
- prompt syntax formatting
- restricted flag

Lesson:
- category browse is useful when accompanied by visual/reference explanation and a cart
- category alone is not the full workflow

### N.STUDIO Danbooru Prompt Builder

Especially relevant to adult-generation workflow.

Sections:
1. base/quality
2. people/count
3. copyright/character
4. female appearance
5. female clothing/state
6. pose/orientation
7. sexual acts/positions
8. expression/gaze
9. camera/composition
10. background/light
11. other

Other behavior:
- model-family selection
- cross-item filtering
- per-section search
- automatic dedupe
- browser temporary save
- explicit warning to start with a small number of tags because conflicting pose/action/count/composition tags can cause malformed results

Lesson:
- scene-construction sections are intuitive
- adult actions/positions deserve direct discovery
- but flat sections alone still become large shelves unless search/facets are strong
- "few tags first, add iteratively" agrees with #44 minimum-sufficient guidance

### Illustrious Danbooru Prompt Tool

Prompt editor sections:
- style
- composition/action
- subject
- appearance
- clothing
- background/lighting
- other
- negative

Also:
- hierarchical dictionary filtering
- general / NSFW classification
- favorites
- recent tags
- paste/import organization

Lesson:
- semantic browsing and final prompt organization can use different groupings
- "NSFW" is often a content lens/filter, not the complete taxonomy

---

## 2. Cross-tool patterns

### Pattern A — search is the primary fast path

Almost every mature tool keeps immediate text/autocomplete search.

Conclusion:
DanbooruTagTool must not make browse classification mandatory.

### Pattern B — taxonomy is only one discovery path

Strong tools combine:
- exact search
- semantic/translated search
- category browse
- related/co-occurrence
- history/favorites

Conclusion:
19 vs 8 vs 9 top-level categories is not the decisive UX question.

### Pattern C — selected state is separated from discovery state

Common:
- scratchpad
- cart
- selected-tag workspace
- final prompt editor

Conclusion:
A user should be able to continue browsing while current scene selections remain visible.

### Pattern D — follow-up suggestions react to current selection

Seen strongly in:
- JP Tag Assistant Auto related mode
- DanbooruSearch co-occurrence refresh
- dbtagger related exploration

Conclusion:
Phase 3 adaptive-next-dimension is aligned with real tools.

### Pattern E — related does not mean semantic truth

Co-occurrence-based tools explicitly distinguish:
- statistically co-occurring
- semantically related
- model-known/effective

Conclusion:
DanbooruTagTool must label suggestion provenance.

Suggested buckets:
- 同じ意味・近い候補
- シーンを完成させる候補
- Danbooruで一緒に使われやすい

Do not merge these into one "おすすめ".

### Pattern F — adult handling is generally a lens/mode + adult-specific entry

Examples:
- JP Tag Assistant NSFW related mode
- Illustrious Prompt Tool general/NSFW
- N.STUDIO dedicated sexual acts/positions section
- prompt supermarket restricted flag

Conclusion:
Existing #118 `性的` lens is the right base.
Inside it, adult-specific scene axes should be promoted.

### Pattern G — Prompt assembly is iterative, not bulk taxonomy dumping

N.STUDIO explicitly warns against selecting many conflicting pose/action/count/composition tags.
NovelAI exposes context budget.
Prompt editors emphasize manual removal/reordering.

Conclusion:
do not auto-add every related tag.
Discovery should suggest; user chooses.

---

## 3. Recommended DanbooruTagTool product direction

### Keep

Existing strengths:
- Japanese display/search
- canonical identity
- #118 all/general/sexual lens
- #76 kind/body/theme
- Prompt workspace
- presets
- search ranking
- post count

### Do not build

1. one giant replacement taxonomy
2. a deeper permanent sexual-act tree
3. automatic insertion of related/co-occurring tags
4. a single opaque "recommended tags" list
5. an LLM-required normal browse path
6. model Prompt ordering hardwired into human browse order

### Add as research candidate

#### A. Discovery modes

Use one search surface, but expose purpose:

- `タグを探す` — exact / Japanese / alias
- `意味から探す` — broader concept discovery
- `シーンを続ける` — based on current selected tags

Initially this can be implemented without embeddings/LLM:
- existing Japanese dictionary
- taxonomy/facet metadata
- Special metadata
- exact token family rules
- optional co-occurrence later

#### B. Sexual lens scene axes

When `内容 = 性的`:

**シーンの核**
- 人物・役割
- 行為・状態
- 身体部位
- 体位・配置
- 道具
- テーマ

**見た目・仕上げ**
- 衣装・露出
- 表情・視線
- 構図・見せ方
- 場所・背景・光

These are non-exclusive facets/entry paths.

#### C. Adaptive "次に探す"

Examples:

selected = breast site
- 行為
- 衣装/露出
- 道具
- role
- framing

selected = BDSM
- role
- device
- body site
- topology/pose
- visibility

selected = device
- target
- body site
- action/relation
- position
- visibility

#### D. Suggestion provenance

Display chips in separate blocks:

1. `意味が近い`
2. `このシーンで次に決める`
3. `一緒に使われやすい`

The third requires co-occurrence evidence and must be labeled statistical.

#### E. Browse history

Adopt lightweight back/forward:
- previous selected discovery state
- next state

This is especially useful for "try body site -> action -> back -> different action" exploration.

#### F. Current Prompt roles

Do not replace current Prompt editor.
Consider view-only grouping:
- Core
- Refinement
- Support

Tags remain ordinary PromptTokens.
Role metadata is UI/discovery metadata, not canonical identity mutation.

---

## 4. What external tools do not solve

No reviewed tool fully solves:
- exact actor/target ownership
- body-site binding
- topology
- source/destination fluid relation
- hard multi-person assignment
- model-specific compositional failure

Most tools stop at:
- find tag
- suggest nearby/related tag
- add to prompt

This is where DanbooruTagTool can be better by reusing #44 structural knowledge.

A useful differentiator is therefore not "more categories".
It is:

> after I choose one hard adult concept, tell me which semantic dimension is still unspecified.

---

## 5. Updated product hypothesis

Leading hypothesis after external benchmark:

`Japanese intent/search -> canonical tags -> adaptive scene completion -> curated Prompt workspace -> model-specific output/diagnosis`

not:

`taxonomy tree -> pick tags -> dump prompt`

For adult generation specifically:

`性的 lens -> start from action/site/position/device/theme -> intersect -> scene-completion suggestions -> appearance/visibility finish -> prompt`

This matches:
- project #44 scene-planning knowledge
- #76 multi-axis Special browse
- #118 sexual intent lens
- current external tool UX patterns

---

## 6. Next bounded prototype test

Do not implement production yet.

Compare three candidate experiences on the same tasks:

A. current taxonomy-first
B. flat coarse taxonomy
C. search + adaptive scene-axis

Tasks:
1. sexual action known, tag unknown
2. body site known, action undecided
3. position known, action undecided
4. sex toy/device known
5. BDSM theme known
6. fluid outcome known
7. clothing/exposure idea known
8. multi-person actor/receiver idea known

Measure:
- clicks
- typing required
- backtracks
- search fallback
- irrelevant result count
- accidental prompt bloat
- whether final chosen tags express actor/site/position correctly

If C does not clearly beat A/B, reject it before production.

---

## Protected boundary

No production/main/catalog/UserData changes.
No #64/#76/#118 authority mutation.
No #70/#131/Performance changes.
No search ranking changes.
No Japanese production overlay changes.
No merge / production apply.
