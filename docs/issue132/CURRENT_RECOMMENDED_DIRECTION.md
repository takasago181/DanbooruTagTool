# Issue #132 — Current recommended direction

Date: 2026-09-22
Status: **RESEARCH DIRECTION v2 / NO PRODUCTION CHANGE**

This document supersedes the previous adaptive scene-completion proposal as the leading #132 direction.

The goal is not to make the tool "smart". The goal is to make a large Danbooru dictionary **easy to search and browse without sacrificing correctness**.

---

## 1. Product goal

A Japanese-speaking user who does not know the exact Danbooru tag should be able to reach the correct canonical tag with:

1. Japanese / English search, or
2. a small number of understandable browse choices.

The user must not need to understand the internal taxonomy.

Primary flow:

`検索 -> 候補確認 -> 選択 -> 既存Prompt workspace`

Browse is a fallback / discovery aid, not a mandatory wizard.

---

## 2. Optimization principles

### Accuracy over cleverness

- Do not infer what the user "should choose next".
- Do not generate adaptive scene-completion advice from incomplete semantic metadata.
- Do not treat co-occurrence as guidance.
- Do not auto-insert tags.
- Do not require an LLM, embeddings, or live external services for normal use.
- A missing browse route is preferable to a confidently wrong browse route.

### Keep runtime behavior deterministic

Normal runtime should be driven by audited static metadata.

The same tag + same filter state should produce the same browse placement.

### Search stays primary

Existing Japanese / English / alias / canonical search remains the fastest path and must not be weakened by #132.

---

## 3. What remains useful from Phase 1–4

Keep the following findings:

- many "classification conflicts" are not wrong tags; they are tags that are naturally discoverable from more than one route;
- forcing one visible semantic home per tag creates unnecessary ambiguity;
- the current 19-route structure can remain useful as internal metadata even if it is not the ideal user mental model;
- #76 Special `種類 / 部位 / テーマ` already provides useful multi-axis discovery;
- #118 `すべて / 一般向け / 性的` remains the correct content lens;
- external tools support the broader conclusion that search and browse should coexist;
- selected Prompt state should remain separate from browse/search results.

Discard as the leading UX:

- adaptive "next discovery";
- scene-completion inference;
- a new giant scene-planning system;
- the flat 8/9-category replacement taxonomy.

Those remain historical research evidence only.

---

## 4. Leading UX

### A. Search first

Keep one normal search entry point.

Supported:
- Japanese
- canonical English
- approved aliases
- mixed input
- current ranking/post-count behavior

No separate "AI search" mode is required for #132.

### B. Keep the existing content lens

`内容 [すべて] [一般向け] [性的]`

This limits what the user is browsing without changing canonical identity.

### C. Browse by a small number of stable entrances

Do not expose every internal classification route as a top-level decision.

For Special, preserve the already accepted #76 entrances:

- 種類
- 部位
- テーマ

For General, reuse #64 metadata but present only stable, understandable browse entrances already supported by accepted data. Do not invent a new universal hierarchy solely for #132.

### D. Allow multiple browse entrances for the same tag

A tag may be discoverable from more than one valid place.

This is the main #132 change.

Example principle:

- one canonical tag identity;
- zero, one, or several audited discovery paths;
- discovery paths do not change PromptToken or taxonomy authority.

A route is a lookup aid, not a declaration that the tag "belongs only here".

### E. Use local narrowing, not global mega-categories

After entering an existing category, small local chips/subroutes may narrow the current result set.

Do not build a permanent screen full of 10+ semantic axes.

The user should see only the choices relevant to the route they deliberately opened.

---

## 5. No recommendation engine

#132 v2 explicitly rejects an opaque recommendation layer.

Do not show:

- "おすすめタグ"
- "次に必要"
- "このタグと一緒に使うべき"
- confidence percentages derived from co-occurrence

unless a future independent feature is explicitly researched and approved.

Co-occurrence may remain available as research evidence, but it is not #132 runtime guidance.

---

## 6. Minimal data model

Do not rewrite #64 / #76 / #118.

If extra discovery metadata is needed, add a separate auditable overlay.

Conceptual shape:

```
canonical_tag
discovery_axis
discovery_path
source_authority
review_status
```

Rules:

- multiple rows per canonical tag are allowed;
- only confirmed routes become user-visible;
- unresolved routes remain absent;
- overlay does not alter canonical identity, Japanese overlay, PromptToken, Special ID, #64 taxonomy, #76 authority, or #118 intent;
- runtime does not infer missing routes dynamically.

Start only with high-value / high-friction populations. Do not classify all 31k+ ordinary identities merely for completeness.

---

## 7. Scope of new classification work

Prioritize rows where browse placement materially helps because Japanese direct search alone is insufficient or ambiguous.

Priority candidates:

1. General-only rows visible in the sexual/contextual lens;
2. recurring Phase 1 mismatch clusters;
3. tags users naturally search from multiple valid concepts;
4. high-use tags with demonstrable browse friction.

Do not spend effort adding redundant paths to tags already easy to find by search or existing #76 metadata.

---

## 8. UI changes should be small

Do not redesign MainWindow first.

Prototype by reusing:

- current search box;
- current content-intent filter;
- current result cards;
- current Prompt workspace;
- current Special browse behavior.

Add only what is required to prove multi-entry browse.

A valid first prototype can be as small as:

```
内容: [性的]

探し方:
[種類] [部位] [テーマ] [General補助]

<opened route>
[small local choices]

<normal result cards>
```

The exact labels are prototype material, not frozen production wording.

---

## 9. Prototype comparison

Compare only:

### A. Current UI
Current taxonomy/search behavior.

### B. Simplified #132 v2
Current search + existing browse + audited multi-entry discovery overlay.

Do not prototype adaptive scene completion unless the user explicitly reopens that idea later.

Use real image-generation discovery tasks where the exact Danbooru tag is initially unknown.

Measure:

- whether the correct canonical tag is found;
- number of browse decisions;
- number of backtracks;
- amount of typing needed;
- irrelevant result volume;
- whether the user needed prior Danbooru vocabulary;
- whether direct search became worse;
- whether any browse path was misleading.

The prototype wins only if it makes unknown-tag discovery easier **without introducing misleading classification**.

---

## 10. Acceptance rule

Prefer a smaller accurate improvement over a broad clever system.

Production candidate requirements:

- existing direct search has no material regression;
- existing #76 / #118 behavior remains valid;
- added browse routes are deterministic and auditable;
- no automatic Prompt additions;
- no co-occurrence guidance;
- no LLM/runtime inference dependency;
- common test tasks require fewer wrong turns or less prior tag knowledge than the current UI;
- misleading routes found in testing are removed rather than rationalized.

If the simplified overlay does not clearly improve real tasks, #132 should stop rather than add more abstraction.

---

## 11. Implementation order if the prototype passes

1. Freeze a small prototype task set.
2. Build a bounded discovery-overlay sample.
3. Compare current UI vs v2 prototype.
4. Remove misleading or redundant routes.
5. Freeze the minimal overlay schema.
6. Extend only to demonstrated high-value populations.
7. Add compact UI support.
8. Regression-test search, #76, #118, Prompt selection, catalog build, and UserData safety.
9. Only then consider production integration.

No full-population semantic rewrite is required.

---

## 12. Explicitly rejected / deferred

### REJECT for #132 v2

- adaptive scene completion;
- "next thing to decide" inference;
- co-occurrence-driven recommendations;
- automatic related-tag insertion;
- deep permanent sex-act tree;
- one visible home per tag;
- replacement 8/9-category mega-taxonomy;
- LLM-required normal browse;
- runtime semantic guessing;
- broad General reclassification for completeness.

### DEFER

- embeddings/vector search;
- LLM Japanese-to-tag inference;
- live Danbooru co-occurrence;
- model-specific generation-effectiveness ranking;
- automatic Prompt rewrite.

These need separate evidence and must not be smuggled into #132.

---

## 13. Current decision

Leading direction:

`Japanese/English search + existing intent lens + existing browse + small audited multi-entry discovery overlay -> current Prompt workspace`

For the sexual lens:

`性的 -> 種類 / 部位 / テーマ / bounded General supplement -> canonical tag -> Prompt`

The optimization target is **finding the correct tag with less knowledge and fewer wrong turns**, not predicting the user's scene.

---


## 15. Phase 5 update — first prototype should be data-only

The bounded 24-task route-coverage comparison found that the current app already has the key runtime mechanism needed for multi-entry discovery: `CatalogEntry.UnifiedBrowseRouteIds` is unioned into the existing Unified browse identity.

On the targeted HIGH-confidence cohort (T01–T20):
- current tested alternate-route coverage: 8 HIT / 12 MISS;
- with only audited secondary routes: 20 HIT / 0 MISS;
- all 8 existing-route controls remain HIT.

This is a targeted known-gap cohort, not a population-wide success-rate claim.

Therefore the first #132 prototype is now:

1. no UI redesign;
2. small static HIGH-confidence route overlay only;
3. reuse the existing Unified browse UI;
4. regression tests for alternate-route reachability, original-route preservation, intent filtering, dedupe, and unchanged search;
5. medium/low-confidence candidates remain REVIEW/UNRESOLVED.

Evidence:
- `docs/issue132/PHASE5_BOUNDED_TASK_COMPARISON.md`
- `docs/issue132/phase5_task_matrix_v1.csv`

Only if the existing UI cannot expose the proven routes cleanly should a UI addition be considered.

---

## 14. Protected boundaries

Research only until prototype acceptance.

No changes to:

- main
- production taxonomy
- #64 authority
- #76 authority
- #118 authority
- canonical identity
- PromptToken
- Japanese production overlay
- Special IDs
- Character/Copyright/Artist lanes
- search ranking
- production catalog.db
- UserData
- production runtime

No merge.
No production apply.
