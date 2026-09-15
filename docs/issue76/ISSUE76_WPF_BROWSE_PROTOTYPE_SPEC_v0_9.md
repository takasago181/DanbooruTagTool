# Issue #76 WPF browse/filter prototype spec v0.9

Status: **NON-PRODUCTION PROTOTYPE SPEC / KNOWLEDGE-FIRST / READY FOR ISOLATED IMPLEMENTATION**

Date: 2026-09-15 JST

## 1. Purpose

Test whether the accepted Issue #76 v0.8 browse model is actually easier to use in the current WPF application before any production taxonomy replacement.

This prototype is deliberately constrained:

- preserve canonical Special / Alias / General / search-ranking authority;
- use the v0.8 `種類 / 部位 / テーマ` sidecar only as a discovery index;
- do not restore the old 38 visible subgenres;
- do not add actor/count/camera/visibility as permanent taxonomy shelves;
- do not mutate Issue #75 visual-only scope;
- do not replace production v1 data yet.

Primary evidence order remains:

1. KNOWLEDGE #44 current Claim/HOLD/practical guide;
2. exact current model/author/primary sources;
3. current Japanese practical knowledge;
4. full 2,788 semantics/findability;
5. historical local image tests only as supplementary evidence.

## 2. Current WPF constraints found in live branch

Current implementation is optimized around one selected path:

- `NavigationNode(Key, Label, Children)` builds a `TreeView` from `CatalogEntry.Paths`;
- `browse` is one string key;
- `RefreshResults()` filters Special rows by one path;
- search currently replaces browse filtering and uses the existing `SearchEngine` ranking;
- browse sort is usage descending or Japanese label;
- left navigation is ~300px and center result pane already has room for a compact filter row;
- result cards and Prompt actions can remain unchanged.

Therefore the prototype should **not** rewrite the whole screen. It should replace only the Special browse-state model while preserving the current result list, details pane, Prompt actions, search engine, and General browse path.

## 3. Proposed interaction

### Left navigation = starting route, not the whole filter system

```text
◆ Special
  ▸ 種類から探す
      行為・接触
      衣服・露出
      道具・物
      身体・状態
      体液・排泄
      ポーズ・構図・場面
      人物・関係
      異形・変形
      表現・メタ
  ▸ 部位から探す
      男性器
      乳房・乳首
      女性器
      口・口内
      尻・肛門
      尿道
  ▸ テーマから探す
      拘束・BDSM
      損傷・R18G
      生殖・妊娠・授乳
```

General navigation remains unchanged.

Selecting a Special leaf from the tree starts a new browse context:

- clear prior Special facets;
- apply that one selected facet;
- show results immediately;
- expose additional facet chips in the result pane for intersection.

This avoids carrying invisible stale filters when the user intentionally chooses a new route from the tree.

### Center result pane additions

Between search row and result list:

1. `適用中` removable chips;
2. `すべて解除` button when one or more facets are active;
3. compact `絞り込み` area with three groups:
   - 種類
   - 部位
   - テーマ
4. each option shows current result count when cheap to compute, e.g. `道具・物 14` after `尻・肛門` is active.

Do not create another hierarchy. These are flat toggle chips.

## 4. Filter semantics

Keep the mental model simple:

> **選んだ条件を全部含むタグを表示する。**

### 種類

- zero or one selected;
- selecting another kind replaces the old kind;
- reason: every browse-visible row has at most one semantic kind/home, and multi-kind OR adds UI complexity without helping the target workflow.

### 部位

- zero or multiple selected;
- multiple selected body-site chips use **AND**;
- example: `口・口内 + 男性器` means concepts intrinsically involving both, not the union of oral concepts and male-genital concepts.

This is important for generation-oriented discovery such as fellatio-like relations.

### テーマ

- zero or multiple selected;
- multiple selected themes also use **AND**;
- theme intersections are rare, but this keeps one consistent rule: every active chip is a required condition.

Do not add an AND/OR mode toggle in v1 prototype. It would recreate complexity before a real need is demonstrated.

### Across axes

Always **AND**.

Examples:

- `尻・肛門` + `道具・物` -> anal-related objects/tools only;
- `拘束・BDSM` + `口・口内` + `道具・物` -> mouth-related BDSM devices;
- `損傷・R18G` + `行為・接触` -> injury/R18G actions.

## 5. Search interaction

Do not change the `SearchEngine` ranking algorithm.

Prototype rule:

- no active facets -> current global search behavior unchanged;
- active Special facets + query -> run the current search normally, then retain only hits satisfying every active facet;
- relative ordering of surviving hits stays exactly as returned by `SearchEngine`;
- clearing the query keeps active facets;
- clearing facets keeps the query.

This provides shelf-local discovery without inventing a second search engine or changing ranking weights.

## 6. Sorting

Preserve current behavior:

- browse/no query: `使用数 ↓` or `日本語名`;
- query present: `関連度順` from existing search engine;
- facet counts must not affect ranking.

## 7. Browse state model

Prototype state should become explicit instead of encoding all Special state in one `browse` string.

Suggested non-production model:

```csharp
public sealed record SpecialBrowseFilter(
    string? KindId,
    IReadOnlySet<string> BodySiteIds,
    IReadOnlySet<string> ThemeIds);
```

Required helpers:

```text
Matches(entryId, filter)
ApplyKind(kindId?)
ToggleBodySite(bodySiteId)
ToggleTheme(themeId)
ClearFacets()
StartFromTree(axis, value)   // resets then applies one facet
```

The existing `browse` string may remain for General and top-level navigation during prototype work.

## 8. Sidecar direction

Runtime prototype should consume a generated **UI-side** sidecar, not canonical Special rows.

Logical schema:

```text
special_id
kind_id?            # optional
body_sites[]
themes[]
v2_status
classification_reason
```

Source for generation:

`tools/issue76_build_v2_integrated.py`

Accepted prototype browse statuses:

- `AUTO_CANDIDATE`
- `HUMAN_RESOLVED`

Non-default browse statuses remain excluded from normal facet results:

- `REFERENCE_ONLY_NO_DIRECT_BROWSE`
- `DEFER_PRODUCT_FIT_REVIEW`
- `OUT_OF_SCOPE_NO_BROWSE`

They remain reachable according to their existing search/reference policy and must not be silently deleted from canonical data.

## 9. Facet labels

Use short Japanese labels already accepted by v0.8.

Do not expose internal IDs in normal UI.

Keep `尻・肛門` as one visible facet. The 62-row audit did not justify a separate permanent `尻` vs `肛門` shelf.

## 10. Detail pane

Do not overload the existing `分類階層` field with a fake hierarchy.

Prototype display direction for Special detail:

```text
種類: 道具・物
部位: 尻・肛門
テーマ: —
```

or compact chips.

This is display-only; canonical identity and English output remain untouched.

## 11. Related Special

Do not redesign Related in the first prototype.

Current Related uses shared legacy `Paths`. Keep it as-is or hide it in an isolated prototype if route semantics become misleading. A separate relatedness redesign is not required to validate the browse model.

## 12. Back / state behavior

Current back stack stores only a browse key. For the prototype, back navigation must restore the complete browse snapshot:

```text
SpecialBrowseFilter
Query
Selected entry
Scroll position
```

At minimum, do not allow Back to restore a label while silently leaving newer facets active.

Persisted user state migration is **out of production scope** for the isolated prototype. Test with transient state first.

## 13. Performance expectations

2,788 Special rows are small enough for simple in-memory facet sets.

Suggested representation:

- `Dictionary<string, HashSet<string>>` / ID-indexed lookup for prototype clarity;
- precompute per-entry facet IDs once at load;
- compute result counts from current candidate set;
- do not introduce SQLite schema migration merely for this prototype.

Only optimize further if profiling shows a real issue.

## 14. What the prototype must prove

The prototype passes only if:

- a user can reach cross-cutting concepts without knowing the old ontology;
- a body-site route finds objects as well as actions/anatomy;
- multi-site concepts can be intentionally intersected;
- theme-native rows remain discoverable without a fake kind;
- the 907-row action shelf remains usable through facets + normal search, without restoring old action subgenres;
- active filters are always visible and removable;
- search ranking itself is unchanged;
- no canonical/Prompt output behavior changes;
- General browsing remains unchanged.

## 15. Explicit non-goals

Do not implement in this prototype:

- automatic Prompt optimization;
- model-specific generation-success scoring;
- actor/target/count/camera taxonomy shelves;
- new General taxonomy;
- Character/Copyright/Artist browse changes;
- search-ranking tuning;
- production data migration;
- full visual polish (#75 responsibility).

## 16. Next implementation slice

Implement only an isolated Special v2 browse/filter path behind the Issue #76 branch/prototype boundary:

1. generated v2 sidecar loader/index;
2. `SpecialBrowseFilter` state + deterministic matching;
3. flat facet groups + applied chips;
4. search-result intersection preserving existing order;
5. task-matrix tests;
6. no main merge / no production replacement until user review.
