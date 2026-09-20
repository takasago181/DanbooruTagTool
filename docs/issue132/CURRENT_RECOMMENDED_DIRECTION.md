# Issue #132 — Current consolidated direction

Date: 2026-09-20
Status: **RESEARCH CONSOLIDATION / NO PRODUCTION CHANGE**

This document consolidates Phase 1–4 into one current product direction for improving tag discoverability specifically for **actual adult image generation**.

It supersedes Phase 2's flat coarse-taxonomy proposal as the leading UX candidate.

---

## 1. Product goal

The goal is **not**:

> build the cleanest possible Danbooru taxonomy.

The goal is:

> A Japanese-speaking user who does not know the exact Danbooru tag can start from the image they want to make, find the correct canonical tags, combine only the needed concepts, and move them into Prompt without unnecessary backtracking or prompt bloat.

The workflow should optimize:

`理解 -> 発見 -> 選択 -> Prompt`

for actual generation.

---

## 2. What we learned

### Phase 1 — classification anomalies are real, but many are boundary artifacts

136 bounded candidate rows exposed repeated boundaries:
- action vs body
- pose vs action
- object vs place
- clothing identity vs state
- style/meta vs visual target
- color modifier vs target
- proper noun/meme/event

Important result:
many rows are naturally multi-axis rather than simply "wrong".

### Phase 2 — reducing 19 routes helps some cases, but flat coarse shelves are not enough

A coarse 8-entry experiment removed or reframed many first-level conflicts.

But later actual-data measurement showed that flat coarse shelves create oversized buckets.

Therefore:
**coarse taxonomy remains useful as an internal simplification experiment, not as the preferred final sexual-generation UX.**

### Phase 3 — actual sexual-generation data favors multi-axis discovery

#118 sexual lens:
- 3,988 identities
- Special metadata available on 2,754 = 69.06%
- General-only = 1,234

General PROPOSED rows visible under sexual lens:
- action + pose = 1,224 / 2,835 = 43.17%
- clothing + exposure = 1,080 / 2,835 = 38.10%
- combined = 81.27%

General-only sexual/contextual, PROPOSED:
- 1,146 rows
- clothing-related = 689
- action-related = 312
- combined = 1,001 = 87.35%

Conclusion:
a flat "action" shelf and "clothing" shelf simply become huge.

### Phase 4 — external tools converge on multi-path discovery

External prompt/tag tools commonly combine:
- exact/autocomplete search
- translated/semantic search
- category/facet browse
- related/co-occurrence traversal
- history/favorites
- selected-tag workspace/cart
- prompt editing

They rarely depend on a single taxonomy tree.

Most important patterns:
- exact lookup and concept discovery are separate tasks
- selected tags influence the next suggestions
- selected-tag workspace is separate from discovery results
- NSFW/adult is usually a lens/mode plus adult-specific discovery
- co-occurrence is explicitly different from semantic similarity

---

## 3. Core design principle

### Keep five layers separate

1. **Canonical meaning**
   - what the tag means
2. **Human scene planning**
   - what the user wants to decide
3. **Discovery route**
   - how the user finds the tag
4. **Prompt serialization**
   - how selected concepts are output for a model
5. **Generation diagnosis**
   - why the output succeeds/fails

Do not force one structure to serve all five.

Especially:

**human planning order != browse taxonomy != model Prompt order**

---

## 4. Leading UX structure

### A. Search remains the fastest path

The user should never be forced through browse categories.

Primary search supports:
- Japanese display
- canonical English
- alias
- existing ranking/post count

Future research may distinguish:
- `タグを探す` — exact/direct lookup
- `意味から探す` — concept discovery
- `シーンを続ける` — discovery based on current selections

But the first usable prototype does not require embeddings or an LLM.

### B. #118 content lens remains the scope control

Keep:

`内容 [すべて] [一般向け] [性的]`

When `性的` is active, promote generation-oriented discovery axes.

### C. Sexual-generation discovery is multi-axis, not mutually exclusive

#### Scene Core

- **人物・役割**
- **行為・状態**
- **身体部位**
- **体位・配置**
- **道具**
- **テーマ**

#### Appearance / finishing

- **衣装・露出**
- **表情・視線**
- **構図・見せ方**
- **場所・背景・光**

These are entry paths/facets, not exclusive semantic homes.

One tag can be discoverable from multiple axes.

Examples:

`biting_breast`
- action/contact
- breast body-site

`standing_doggystyle`
- action
- position/geometry

`ball_gag`
- tool/device
- mouth/oral
- BDSM theme

`cum_on_fourth_wall`
- fluid/state
- screen-expression
- possibly action/context

No need to force each into one user-facing route.

---

## 5. Reuse existing data rather than rebuild taxonomy

### Existing data to reuse

#### #118
- sexual/general intent lens
- do not change semantic authority

#### #76 Special v2
Reuse:
- 9 broad kinds
- 6 body-site facets
- 3 themes
- cross-axis AND filtering

This already covers 69.06% of sexual-lens identities through Special membership.

#### #64 General
Reuse:
- accepted primary/subpath classification
- clothing subgenres
- action subgenres
- pose/body/object/composition metadata

Do not rewrite #64 merely to satisfy user-facing discovery.

### New data should be a discovery overlay

The main missing population is General-only sexual/contextual:

- 1,234 identities total
- 1,146 currently PROPOSED
- especially 1,001 clothing/action rows

Add only bounded user-discovery metadata such as:

- body-site target
- position/geometry
- device role
- scene role
- visibility/support role

when useful.

This overlay must not mutate canonical identity, PromptToken, #64 authority, #76 authority, or #118 intent.

---

## 6. Adaptive "next discovery" is the differentiator

Once the user selects a strong intent, preserve it and surface useful missing dimensions.

### Starting from body site

Example: `乳房・乳首`

Next:
- 行為・状態
- 衣装・露出
- 道具
- 人物・役割
- 構図・見せ方

### Starting from BDSM

Next:
- 役割
- 道具
- 身体部位
- 体位・接続
- visibility

### Starting from a device

Next:
- target person
- body site
- functional action/relation
- position
- count
- visibility

### Starting from a fluid/material concept

Next:
- source
- destination
- state/timing
- quantity
- actor/target
- visibility

This is intentionally adaptive rather than one fixed wizard.

---

## 7. Suggestion types must be separated

Do not show one opaque `おすすめ` list.

Use separate concepts:

### 1. 意味が近い
Semantic alternatives / neighboring canonical concepts.

### 2. 次に決める
Generation-structure completion guidance from project knowledge.

Example:
- body site selected but action missing
- restraint selected but device/role/topology missing

### 3. 一緒に使われやすい
Statistical co-occurrence, if later implemented.

Must explicitly state:
- co-occurrence != semantic similarity
- co-occurrence != model knowledge
- co-occurrence != recommendation to automatically insert

No automatic insertion.

---

## 8. Selected tags and discovery results are separate states

Adopt the successful "cart/scratchpad" pattern.

### Discovery side
- search results
- facet results
- next-discovery suggestions
- related/co-occurrence

### Selected/Prompt side
- currently selected tags
- remove
- reorder
- optional weight/edit behavior
- existing Prompt workspace

The selected state must survive continued exploration.

Do not turn the browse tree itself into the Prompt editor.

---

## 9. Prompt role view

Research candidate only:

Group selected Prompt concepts visually as:

### Core
Scene-defining:
- actor/target
- action/state
- body site
- position
- device

### Refinement
Appearance:
- clothing/exposure
- expression
- setting/style

### Support
Visibility/composition support:
- framing
- focus
- simple support pose

This is UI/discovery metadata only.

Do not change PromptToken identity.

Do not auto-add support tags.

---

## 10. Model output stays model-specific

Selected scene concepts are not necessarily emitted in click order.

### NoobAI
Use its own tag/caption conventions.

### Anima
Allow its tag + natural-language / explicit-role conventions.

### WAI / Illustrious-family
Keep composition/support conflict concerns model-scoped.

Therefore:
- one scene selection state
- multiple future serialization strategies

Do not bake model Prompt grammar into browse taxonomy.

---

## 11. What to keep / modify / reject / defer

### KEEP

- Japanese search/display
- canonical identity
- existing search ranking
- post count
- #118 `すべて / 一般向け / 性的`
- #76 kind/body/theme
- current Prompt workspace
- presets
- existing detail view
- General/Special overlap dedupe

### MODIFY

- treat current 19 routes as internal/discovery metadata, not mandatory user mental model
- expose sexual lens through scene axes
- allow multi-route discovery
- preserve selected state while browsing
- add adaptive next-dimension suggestions
- use existing subroutes as local chips rather than top-level permanent shelves

### REJECT

- replacing everything with one new 8/9-category taxonomy
- deep permanent sex-act category tree
- forcing every tag into one visible semantic home
- one opaque `おすすめ` list
- automatic insertion of related/co-occurring tags
- treating co-occurrence as generation guidance
- LLM-required normal browse
- using human click order as universal Prompt order

### DEFER

- embeddings / vector semantic search
- LLM Japanese-to-tag inference
- live Danbooru co-occurrence service
- automatic model-specific Prompt rewrite
- dynamic per-model generation-effectiveness ranking
- broad General population reclassification

These are optional later improvements, not prerequisites.

---

## 12. Minimal prototype concept

Do not redesign the entire MainWindow first.

Prototype only the sexual-lens discovery behavior.

### State

```text
contentIntent = SEXUAL
selectedSceneFacets[]
selectedPromptTags[]
query
```

### UI concept

Search remains top priority.

Under sexual lens:

```text
シーンの核
[人物・役割] [行為・状態] [身体部位] [体位・配置] [道具] [テーマ]

見た目・仕上げ
[衣装・露出] [表情・視線] [構図・見せ方] [場所・背景・光]
```

After any selection:

```text
選択中: 性的 > 乳房・乳首 > 行為・接触

次に絞る:
[役割] [衣装・露出] [道具] [体位] [見せ方]
```

Result cards remain current cards.

Prompt area remains current Prompt area.

---

## 13. Prototype validation tasks

Compare:

A. current taxonomy-first
B. flat coarse taxonomy
C. search + multi-axis adaptive scene discovery

Use the same tasks:

1. user knows a sexual act concept but not tag
2. body site known, action undecided
3. position known, action undecided
4. device/toy known
5. BDSM theme known
6. fluid outcome known
7. clothing/exposure concept known
8. multi-person actor/receiver concept known

Measure:
- clicks to useful candidate
- typing required
- backtracks
- search fallback
- result-set size
- irrelevant result count
- whether actor/site/position semantics remain clear
- whether unnecessary tags are encouraged
- time to add final intended canonical tag set

### Acceptance principle

C should materially reduce backtracking/result overload without hiding direct search.

If it does not, reject or simplify it before production.

---

## 14. Implementation order if prototype passes

1. **No production taxonomy rewrite**
2. define scene-discovery projection schema
3. map existing #76 metadata
4. bounded-map General-only sexual/contextual population
5. add compact sexual-lens facet UI
6. add next-dimension guidance
7. preserve search ranking and existing result cards
8. validate Prompt selection behavior
9. only then consider history/co-occurrence/semantic search enhancements

---

## 15. Current decision

The leading direction is now:

`Japanese intent/search -> canonical tag discovery -> multi-axis scene completion -> selected-tag workspace -> model-specific Prompt handling`

For sexual generation:

`性的 lens -> start from action/site/position/device/theme/etc. -> intersect -> surface missing dimensions -> add appearance/visibility -> Prompt`

The project should optimize **scene construction and canonical-tag discovery**, not taxonomy purity.

---

## 16. Protected boundaries

This is research consolidation only.

No changes to:
- main
- #64 production taxonomy
- #76 production browse authority
- #118 intent authority
- canonical identity
- PromptToken
- Japanese production overlay
- Special IDs
- #70
- #131
- Performance
- search ranking
- catalog.db
- UserData
- artifacts/current

No merge.
No production apply.
