# Batch H — Danbooru Category / Relation / Unknown Handling for Prompt Comprehension

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-13

Backlog items:
- `K-RB-04 Danbooru tag-type/category meaning for Prompt comprehension`
- `K-RB-05 Alias / implication / related / co-occurrence beginner distinction`
- `K-RB-06 Unknown / unsupported Prompt token handling`

Status: `P0_RESEARCH_PASS_COMPLETE / NO_PRODUCT_PROMOTION`

## Purpose

Complete the first beginner-first Prompt-understanding research sequence after Batch E/F/G.

This batch answers three remaining questions:

1. What do Danbooru's five tag categories mean to a beginner reading a Prompt?
2. How should Alias / implication / related / co-occurrence / search synonym / model trigger be distinguished?
3. What should happen when a Prompt token cannot be identified confidently?

---

## 1. Danbooru category meanings

Current Danbooru/Safebooru `help:tags` documents five categories:

- General
- Character
- Copyright
- Artist
- Meta

Source:
- https://safebooru.donmai.us/wiki_pages/help%3Atags
- https://safebooru.donmai.us/wiki_pages/howto%3Atag

### General

Danbooru role:
Objective description of image content not covered by the other identity/meta categories.

Beginner explanation:
`画像に見えている特徴・状態・行為などを表す通常タグ`

Examples include appearance, pose, clothing, objects, scene and many relation concepts.

Important:
General is not synonymous with `easy`, `common`, or `generation-safe`.

### Character

Danbooru role:
Identifies a specific character.

Beginner explanation:
`描くキャラクターの指定`

Important:
Character identity is different from appearance. A character tag can carry learned appearance priors in a model, but that is generation behavior, not the semantic category definition.

### Copyright

Danbooru role:
Identifies the source work/series material associated with characters/content.

Beginner explanation:
`作品・シリーズの指定`

Important:
Copyright is not a generic legal/trademark label and is not the same as Character.

### Artist

Danbooru role:
Identifies the creator of the individual artwork.

Beginner explanation:
`作者・絵師の指定`

Important:
Do not automatically translate Artist category into `画風`. A model may learn a stylistic association from an artist surface, but artist identity and style effect are separate claims.

### Meta

Danbooru role:
Generally describes information beyond ordinary depicted content, including technical/source/context metadata.

Beginner explanation:
`画像内容そのもの以外のメタ・技術・出典情報`

Important:
Meta is not synonymous with `quality Prompt token`. Some model quality/rating surfaces may not be Danbooru Meta tags at all.

---

## 2. Category and generation role are separate

A Prompt surface can have:

- a Danbooru category
- a semantic explanation role
- a model-specific generation effect

These are not interchangeable.

Example:

```text
artist_name
Danbooru category: Artist
Explanation role: Artist/creator identity
Generation effect: model/version-specific and separately evidenced
```

Example:

```text
highres
Danbooru category: Meta if current canonical lookup says so
Explanation role: Meta/technical
Generation effect: not implied by category alone
```

This prevents a beginner explanation from turning data classification into generation advice.

---

## 3. Relation types — beginner distinction

Current project semantic audit already establishes the authority boundary.

### Alias

Meaning:
Alternative/historical surface mapped to the **same canonical identity**.

Beginner wording:
`別名・旧名。現在は同じタグとして扱われます。`

Safe behavior:
- show the canonical target
- preserve original surface/history when useful

Unsafe behavior:
- treating implication/related/search synonym as Alias

### Implication

Meaning:
A more specific tag entails/includes a broader tag; it is a hierarchy/subset relationship, not synonymy.

Beginner wording:
`このタグを使うと、より広い上位概念も成り立つ関係です。別名ではありません。`

Example pattern:
`sitting_split -> split` or `sitting`

Safe behavior:
Use to explain hierarchy.

Unsafe behavior:
Automatically add every implied parent to a generation Prompt.

### Related / semantic-near

Meaning:
Concepts are connected/nearby but not identical.

Beginner wording:
`意味が近い・関連する別タグです。同じ意味とは限りません。`

Safe behavior:
Candidate discovery.

Unsafe behavior:
Identity replacement.

### Co-occurrence

Meaning:
Tags often appear together statistically.

Beginner wording:
`一緒に使われることが多いタグです。意味が同じとは限りません。`

Safe behavior:
Optional related discovery.

Unsafe behavior:
Semantic authority or automatic support insertion.

### Japanese search synonym

Meaning:
A retrieval aid allowing Japanese phrasing to find a candidate.

Beginner wording:
Usually no need to expose as an identity relationship; if shown:
`検索用の言い換え`

Safe behavior:
Search bridge only.

Unsafe behavior:
Turning it into a canonical Alias.

### Model trigger alternative

Meaning:
An alternate Prompt surface that may matter for a specific model/version/training history.

Beginner wording:
`特定モデル向けの入力候補。Danbooru上の正式タグとは別です。`

Safe behavior:
Keep model/version/source scope.

Unsafe behavior:
Rewrite canonical identity globally.

---

## 4. Unknown / unsupported token handling

Unknown is a normal state, not a failure that must be hidden.

Recommended interpretation states:

1. `EXACT_CANONICAL`
2. `EXACT_ALIAS`
3. `KNOWN_RUNTIME_SYNTAX`
4. `KNOWN_LOCAL_ASSET` — only when local inventory confirms it
5. `KNOWN_MODEL_SCOPED_SURFACE`
6. `PLAUSIBLE_FREE_PHRASE`
7. `AMBIGUOUS`
8. `UNKNOWN`

### Exact canonical

Exact identity confirmed.

May show:
- Japanese label
- canonical English
- Danbooru category
- semantic role

### Exact Alias

Identity confirmed through Alias.

Show:
- raw/alias surface
- canonical target
- relationship = Alias

### Known runtime syntax

Examples:
- `BREAK`
- `(text:1.2)`
- `<lora:...>`
- Dynamic Prompts syntax when extension context confirms it

Do not send the wrapper/operator itself through Danbooru fuzzy search first.

### Known local asset

Examples:
- textual inversion embedding filename
- LoRA/local network name

Requires environment inventory when inline syntax alone is insufficient.

### Known model-scoped surface

Must carry evidence/model scope.

Do not present as universal Danbooru meaning.

### Plausible free phrase

Natural-language text whose phrase meaning can be explained without pretending it is one canonical tag.

### Ambiguous

More than one credible interpretation exists.

Display:
`意味候補が複数あり、現在は確定できません。`

### Unknown

No safe interpretation.

Display:
`現在の辞書・Alias・既知構文では判定できません。`

Preserve the raw text unchanged.

---

## 5. Exact-first and fail-safe matching

Issue #34 documents a concrete search-noise defect:

`anal` can surface unrelated strings such as `piano`, `analog_clock`, `analogous_colors` through incidental substring/fuzzy matching.

This is directly relevant to Prompt interpretation.

For **identity interpretation**, use a stricter order than candidate discovery:

1. explicit runtime/extension syntax
2. exact canonical
3. exact approved Alias
4. exact confirmed local asset/model surface
5. phrase interpretation
6. ambiguity/unknown

Fuzzy/substring results must remain **candidate suggestions**, not identity verdicts.

Key principle:

> Search can be permissive; interpretation must be conservative.

A fuzzy match may help the user discover a possible tag, but it must not rewrite the pasted Prompt as if the identity were proven.

---

## 6. Preserve raw surface

Every interpreted Prompt element should retain original text even when a canonical match exists.

Reasons:
- Alias/history traceability
- runtime weighting/wrapper reconstruction
- local asset identity
- model-trigger comparison
- user-controlled editing
- debugging misclassification

Example:

```text
raw: (looking_at_viewer:1.2)
canonical payload: looking_at_viewer
wrapper: weight 1.2
```

Do not replace the raw Prompt immediately with normalized canonical output merely because explanation succeeded.

---

## 7. Unknown handling and user control

For v1 beginner-first behavior, safe knowledge principle is:

- explain known parts
- preserve unknown parts
- mark uncertainty
- let the user decide whether to remove/change them

Do not:
- drop unknown tokens silently
- auto-correct to a fuzzy result
- translate local model assets into ordinary words
- treat unsupported text as invalid merely because it is absent from Danbooru

The product's final normalization/edit behavior remains a DEV/product decision. KNOWLEDGE only establishes the semantic safety rule.

---

## 8. P0 Prompt-understanding research set — combined result

Batch E/F/G/H now provides a coherent four-layer understanding model:

### Layer 1 — Surface/runtime type
`BATCH_E_EXISTING_PROMPT_SURFACE_CLASSIFICATION_20260913.md`

Question:
`これはタグなのか、実行構文なのか、LoRAなのか、自然文なのか？`

### Layer 2 — Semantic role
`BATCH_F_PROMPT_SEMANTIC_ROLE_DECOMPOSITION_20260913.md`

Question:
`内容として何を説明しているのか？`

### Layer 3 — Japanese explanation
`BATCH_G_BEGINNER_SAFE_JAPANESE_EXPLANATION_20260913.md`

Question:
`意味を壊さず初心者向け日本語でどう説明するか？`

### Layer 4 — Authority / uncertainty
This batch.

Question:
`canonicalなのかAliasなのか関連候補なのか、そもそも未確定なのか？`

These layers must remain separate.

---

## 9. Durable principles ready for consolidation

The following are strong enough for project KNOWLEDGE current guidance after one management consolidation pass:

1. Existing Prompt text is heterogeneous; not every segment is a Danbooru tag.
2. Runtime/extension syntax and semantic identity must be separated before explanation.
3. Raw surface, wrapper/operator and inner semantic payload should be preserved separately where applicable.
4. Danbooru category, semantic explanation role and generation effect are separate axes.
5. General/Character/Copyright/Artist/Meta should retain their distinct meanings.
6. Alias = identity; implication = hierarchy; related/co-occurrence = association; Japanese synonym = search aid; model trigger = model-scoped surface.
7. Surface classification and semantic role classification are separate.
8. Japanese explanation must preserve intrinsic actor/target/body-site/count/relation predicates.
9. Display label, explanation and search synonyms are separate layers.
10. Exact canonical English traceability should remain visible for known Danbooru identities.
11. Search/fuzzy candidate discovery must not silently become identity interpretation.
12. Unknown/ambiguous is a valid state and raw text should be preserved.
13. Semantic role explains what content means, not how reliably a model generates it.

---

## 10. What remains outside P0 research

Still separate:
- final parser/data schema
- UI implementation
- model-specific quality/rating token catalog (`K-RB-07`)
- artist/style generation effects (`K-RB-08`)
- automatic conflict detection (`K-RB-09`)
- model-family ordering (`K-RB-10`)
- detailed Negative conventions (`K-RB-11`)
- source freshness pass (`K-RB-12`)

No production or runtime behavior is changed by this research.
