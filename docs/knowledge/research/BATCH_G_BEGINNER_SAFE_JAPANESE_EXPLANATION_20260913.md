# Batch G — Beginner-Safe Japanese Explanation Rules

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-13

Backlog item: `K-RB-03 Beginner-safe Japanese explanation rules`

Status: `RESEARCH_PASS_V1 / NO_PRODUCT_PROMOTION`

## Purpose

Batch E determined what kind of Prompt surface exists. Batch F determined what semantic role the content plays.

This batch defines how safely identified meaning should be explained in Japanese for a beginner without:

- changing canonical identity
- flattening actor/target/body-site/count distinctions
- confusing Alias/implication/related relationships
- pretending uncertain meaning is certain
- turning a display translation into generation authority

The target is **understandable Japanese + canonical English traceability**, not literary translation.

---

## 1. Existing project authority

Issue #36 already established durable Japanese-overlay policy:

- Japanese + English search must remain available
- Japanese candidate display should be understandable
- canonical English identity and traceability must remain intact
- final Prompt payload remains canonical English
- Japanese wording is supplemental UI/search assistance, never canonical semantic authority
- clear semantic mistranslation, actor-target inversion, malformed labels and non-Japanese residue are repair-worthy defects
- merely awkward but understandable Japanese does not justify endless stylistic rewriting
- unresolved/ambiguous rows should remain explicit rather than guessed for coverage statistics

Issue #35 also established the presentation pattern:

`日本語 / canonical English`

with explicit fallback when Japanese is unavailable.

These are strong project-level constraints for explanation design.

Related project sources:
- Issue #36 Japanese overlay V5 repair/final convergence
- Issue #35 Japanese-first desktop UI pass
- `docs/PRODUCT_GOAL_LOCK.md`
- `docs/project/PERMANENT_RULES.md`
- `DANBOORU_WIKI_SEMANTIC_AUDIT_20260909.md`

---

## 2. Explanation has three different jobs

Do not overload one Japanese string.

### A. `display_label_ja`

Short, scannable UI label.

Purpose:
- identify the concept quickly
- support search/list reading

Example:
`上からの視点`

### B. `explanation_ja`

One short sentence explaining what the concept actually means.

Purpose:
- resolve ambiguity
- preserve semantic predicates that cannot fit in the label

Example:
`カメラが被写体を上から見下ろす構図です。`

### C. `search_synonyms_ja`

Words a Japanese user may type to discover the concept.

Purpose:
- retrieval only

Important:
A search synonym does not become the displayed definition and does not become canonical identity.

Example:
A broad colloquial Japanese search term may lead to several precise canonical concepts rather than silently defining one of them.

---

## 3. Canonical English must stay visible

Default beginner-facing identity pattern:

```text
日本語表示 / canonical_english
```

Why:
- user learns what will actually be placed in the Prompt
- translation mistakes remain auditable
- similar Japanese concepts can still be distinguished
- final copy payload stays traceable

For runtime syntax/non-Danbooru surfaces, show the raw surface instead of inventing a canonical tag.

Example:

```text
LoRA指定 / <lora:Rella_Style:0.7>
```

not:

```text
Rella風 / rella_style
```

unless `rella_style` is independently established as a canonical/known semantic surface.

---

## 4. Prefer practical visible meaning over misleading literal decomposition

A literal word-by-word Japanese translation can be wrong even when every English word was translated correctly.

Use the canonical/wiki meaning as the explanation target.

Examples of risk classes:

- idiomatic tag names
- historical names retained through Alias
- relation tags whose word order hides actor/target
- body-site-specific concepts
- topology/connectivity concepts
- tags whose English surface is broader/narrower than a familiar Japanese term

Rule:

> Translate the concept, not merely the token spelling.

But keep the canonical English visible so the explanation does not replace identity.

---

## 5. Preserve intrinsic semantic predicates

If a canonical concept requires any of the following, Japanese explanation must retain them when relevant:

- actor
- receiver/target
- owner
- body site
- object/implement
- exact or bounded count
- direction/orientation
- source/destination
- topology/connectivity
- state vs action

### Actor / target

Bad:
`脚を持つ`

when the canonical meaning specifically requires holding **another person's** legs.

Better:
`相手の両脚を持つ`

### Body site

Bad:
`縛られている`

when canonical requires wrists specifically.

Better:
`両手首がまとめて縛られている状態`

### Count

Bad:
`複数の女の子`

for an exact-count concept if exact count is intrinsic.

Better:
`女の子が2人`

### Source / destination

Bad:
`液体がある`

when the concept requires where it comes from or lands.

Better:
include source/destination when canonical meaning does.

These rules reuse the existing hard/niche semantic audit rather than creating adult-specific translation logic.

---

## 6. Distinguish state, object and action

Japanese often allows a short noun to blur these distinctions.

Keep separate where canonical semantics separate them:

- object present
- object worn/attached
- person in a state
- action occurring
- relation between participants

Example family:
- `gag` = object
- `gagged` = wearer state
- `gagging` = different action/state meaning

Do not collapse them all to one Japanese label such as `猿ぐつわ` without detail when the distinction matters.

---

## 7. Do not collapse relation types

### Alias
Explain as:
`別名・旧名。現在は同じcanonical identityに統合される。`

### Implication
Explain as:
`より具体的な概念なので、上位概念も含む/伴う関係。別名ではない。`

### Related / co-occurrence
Explain as:
`一緒に出やすい/意味的に近い候補。同じ意味とは限らない。`

### Japanese search synonym
Explain as:
`検索のための言い換え。canonical Aliasとは限らない。`

### Model trigger alternative
Explain as:
`特定モデル向けの入力候補。Danbooru上のcanonical identityとは別。`

This distinction should be available in detail/help text rather than overloading the display label.

---

## 8. Ambiguous Japanese needs qualifiers, not forced certainty

When one Japanese phrase can refer to multiple canonical concepts:

- do not choose one silently
- add a short qualifier
- keep canonical English visible
- if still uncertain, use an explicit ambiguity state

Useful qualifier dimensions:
- body site
- actor/target
- object type
- posture
- viewpoint
- exact count
- state vs action

Example pattern:

```text
縛られた手首 / bound_wrists
両手首を一緒に拘束した状態。
```

rather than a broader label that could also mean arms, hands or wrists bound apart.

---

## 9. Proper nouns and identity surfaces

Character / Copyright / Artist are identity surfaces, not ordinary descriptive vocabulary.

Guidance:
- use established Japanese name when confidently available
- retain canonical English/tag identity visibly
- do not machine-literal-translate proper nouns
- do not convert artist identity into a Japanese style adjective automatically
- when Japanese name is unavailable, explicit fallback is better than invented translation

Project-approved fallback concept from Issue #35:

`日本語未登録 / canonical`

For beginner explanation, add role:

`役割: キャラクター指定` / `作品・シリーズ指定` / `作者・絵師名`

---

## 10. Runtime syntax should be explained as runtime syntax

Do not translate structural syntax as though it were image content.

Examples:

### `(word:1.2)`
Explain:
`中の語を強める重み指定。中身の意味とは別の実行構文です。`

### `BREAK`
Explain:
`A1111系でPromptのチャンクを区切る実行用キーワードです。画像内容を表すDanbooruタグではありません。`

### `<lora:name:0.7>`
Explain:
`LoRAを読み込む指定です。LoRA名そのものをDanbooruタグとして解釈しません。`

### `__wildcard__`
Explain:
`Dynamic Prompts等で生成前に別テキストへ置き換えるテンプレート指定です。`

Only give an exact tool explanation when runtime/extension identity is known. Otherwise use `実行構文の可能性` / ambiguity.

---

## 11. Keep uncertainty visible

Recommended confidence language:

### Exact
`Danbooru canonicalと一致`

### Alias
`既知のAliasからcanonicalへ対応`

### Runtime-known
`既知のA1111/extension構文`

### Model-scoped
`特定モデル向けの既知surface`

### Ambiguous
`意味候補はあるが確定できない`

### Unknown
`現在の辞書・既知構文では判定できない`

Avoid:
- pretending fuzzy candidate = identity
- inventing Japanese definitions for unknown local embedding names
- interpreting every English phrase as one Danbooru tag

---

## 12. Concision rule

Beginner-facing Japanese should be short, but shortening must stop before semantic damage.

Recommended levels:

### Level 1 — list label
Very short.

`相手の両脚を持つ`

### Level 2 — one-line explanation
Include the missing relation detail.

`別の人物の両脚を手で持っている状態です。`

### Level 3 — detail only when needed
Show Alias/history/implication/body-site distinctions or nearby confusing concept.

This avoids putting wiki-length prose into every candidate row while preserving access to exact meaning.

---

## 13. Repair threshold

Reuse Issue #36's successful practical rule:

### Must repair
- semantic mistranslation
- actor/target inversion
- body-site mismatch
- count mismatch
- state/action confusion
- raw non-Japanese residue where Japanese display is expected
- malformed machine-composed Japanese that obscures meaning

### May remain
- slightly stiff wording
- stylistic preference differences
- synonyms that preserve exact meaning clearly

Do not create an endless translation-polish project when the label is already clear and semantically safe.

---

## 14. Suggested explanation record

Not a production schema.

```text
canonical_or_raw_surface
display_label_ja
explanation_ja
semantic_role
canonical_status
alias/history note?
important predicates: actor / target / body_site / count / relation / orientation
confidence
search_synonyms_ja[]
warning/detail?
```

Search synonyms remain outside canonical/display authority.

---

## 15. Examples

### Canonical visual tag

```text
上からの視点 / from_above
役割: 構図・画角・視点
被写体を上から見下ろすカメラ視点です。
```

### Character identity

```text
初音ミク / hatsune_miku
役割: キャラクター指定
描くキャラクターの指定です。
```

### Relation-heavy concept

```text
相手の両脚を持つ / holding_another's_legs
役割: 行為・接触・関係
別の人物の両脚を持っている状態です。
注意: 自分の脚を持つ意味ではありません。
```

### Runtime syntax

```text
重み指定 / (smile:1.2)
役割: 実行構文
`smile`を強めるA1111系の重み指定です。
中の `smile` は別に意味解析します。
```

### Unknown

```text
some_local_token
役割: 未判定
現在のcanonical辞書・Alias・既知構文では意味を確定できません。
元の文字列はそのまま保持します。
```

---

## 16. What this batch does NOT establish

- final UI copy/layout
- bulk rewrite of production Japanese overlay
- automatic Prompt correction
- generation-effectiveness of any Japanese wording
- model-specific quality-token interpretation
- definitive search synonym inventory

Issue #36 production overlay remains frozen evidence; this batch does not reopen or rewrite it.

---

## 17. Durable conclusions proposed for Claim review

Candidate durable statements:

1. Beginner Japanese explanation should preserve canonical English traceability.
2. Display label, explanation text and search synonyms are separate authority layers.
3. Translation must preserve intrinsic actor/target/body-site/count/relation predicates when canonical meaning requires them.
4. Proper-noun identity surfaces should not be machine-literal-translated or collapsed into descriptive style roles.
5. Runtime syntax should be explained as runtime syntax rather than image-semantic content.
6. Ambiguous/unknown should remain explicit instead of being guessed for coverage.
7. Slightly awkward but semantically clear Japanese does not require endless stylistic repair.

After Batch E/F/G, these statements are ready for one combined current-Claim/Catalog consolidation review rather than three fragmented registry edits.

---

## 18. Next step

Before moving to K-RB-04, perform a combined **E/F/G consolidation review**:

- identify which statements are durable enough for `CLAIM_REGISTRY.csv`
- add one compact current catalog section for existing-Prompt understanding
- keep implementation/product schema decisions out of KNOWLEDGE

Then continue:
`K-RB-04 Danbooru tag-type/category meaning for Prompt comprehension`.
