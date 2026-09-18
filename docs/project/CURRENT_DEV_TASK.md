# CURRENT DEV TASK — ISSUE #117 UNIFIED GENERAL/SPECIAL BROWSE + #118 CONTENT INTENT

最終同期: 2026-09-18

## Routing status

- Active DEV Issue: #117 `[DEV][UI][DISCOVERY] Implement unified General/Special browse navigation`.
- Status: **MERGED TO MAIN / CLOUD VALIDATED / LOCAL RUNTIME REBUILD + SMOKE PENDING**.
- PR: **#125** `[#117] Unified browse navigation + content intent filter` — **MERGED** at `2ada80b4611b64ac5717924ae634ba917e3d0b95`.
- Feature branch: `codex/issue117-unified-browse-content-intent`.
- Live main now contains #117/#118 integration at merge commit `2ada80b4611b64ac5717924ae634ba917e3d0b95`.
- #118 research is frozen; authority remains `docs/issue118/FINAL_DESIGN_CHECKPOINT.md`, research commit `4cacb1fea4aaf46552da3837f50712293a6d4440`, Issue comment `5725346261`.
- Do not restart #118 research.
- Merge approval was granted and PR #125 is integrated. Do not repeat or re-merge this branch.

## Final validated source

Validated product/test source checkpoint:

`5c08cb442804b8c49166b7d6055c29b54c693382`

Final review validation run:

`35314061974`

Validation:

- restore: PASS
- Release build: **PASS**
- full Release tests: **185 total / 178 passed / 7 skipped / 0 failed**
- focused `Issue117UnifiedBrowse*`: **20 / 20 passed**
- production-sized synthetic unified-browse characterization: PASS, approximately **0.9–1.0 s** for the complete 31,752-identity characterization test on GitHub Windows runner
- `git diff --check origin/main...HEAD`: **PASS**
- temporary review workflow removed after PASS; it is not product source.

Any commit after `5c08cb...` is allowed only for validation-workflow cleanup / management-document synchronization unless a later checkpoint explicitly states otherwise.

## Implemented user-facing contract

### Left navigation

No visible `General` / `◆ Special` roots.

Frozen ordinary navigation is presented under three **presentation-only** headings:

- 何を描く
- 動き・状態
- 画面・表現

They contain exactly the 19 frozen #117 ordinary discovery labels.

Below them remain dedicated scopes:

- キャラクター
- 作品
- 作者

The three headings are not semantic filters. They default expanded and selecting a heading does not change browse state.

Neutral Tags state has no ordinary route selected.

### Unified ordinary identity

- General/Special remain provenance/membership metadata internally.
- one canonical ordinary identity -> one result card;
- overlap is deduplicated in browse and search;
- existing RuntimeCatalogIndex/SearchEngine ranking remains authoritative;
- filtering removes candidates only and does not rerank survivors.

### Unified browse state

DictionaryWorkspaceViewModel owns:

- scope;
- primary route;
- local subroute;
- body-site facets;
- theme facets;
- deep-only;
- content intent;
- one-step browse history.

Behavior:

- query survives route/facet/scope changes;
- changing primary route clears only old local subroute;
- body/theme/deep/content constraints survive primary changes;
- Character/Copyright/Artist temporarily ignore ordinary content intent while preserving it;
- `クリア` is query-only;
- `全解除` resets unified browse constraints/content intent to All while preserving query;
- neutral Tags + empty query + no constraints shows guidance and does not enumerate the ordinary population;
- clearing to neutral also clears the left route selection highlight.

New UI state defaults directly to `tags`. Legacy persisted browse states retain bounded migration.

Legacy explicit Special kind state maps to the corresponding unified route with `DeepOnly=true`; legacy body/theme states migrate to unified cross-facets.

### Generic center refinements

Tags scope supports:

- relevant local classification chips;
- 部位;
- テーマ;
- `◆ 深掘りのみ`;
- `内容 [すべて] [一般向け] [性的]`;
- `1つ戻す`;
- `全解除`.

Zero-count unselected facets are hidden. A selected facet remains visible at zero so it can be removed.

### #118 frozen content intent

Visible mapping:

- `すべて` -> SEXUAL + NON_SEXUAL + CONTEXTUAL + UNCLASSIFIED
- `一般向け` -> NON_SEXUAL + CONTEXTUAL
- `性的` -> SEXUAL + CONTEXTUAL
- UNCLASSIFIED -> `すべて` only

Frozen identity authority validated:

- total 31,752
- SEXUAL 2,037
- CONTEXTUAL 1,951
- NON_SEXUAL 27,759
- UNCLASSIFIED 5
- AUTO_HIGH_CONF 22,371
- HUMAN_REVIEWED 9,376

Normal startup does not parse the #118 research corpus. The accepted sidecar is consumed only during explicit catalog build and serialized into CatalogEntry metadata.

The catalog build report now states sexual-intent counts at **identity level**, avoiding confusion with backing General/Special row counts.

### Browseability vs searchability

Final review found and fixed an important boundary:

- #64 UNRESOLVED General rows remain searchable but are not made browseable by unified/content-only browsing;
- #76 ReferenceOnlyNoDirectBrowse / other non-direct Special rows remain searchable/reference-capable where existing rules allow, but do not become route/content browse rows;
- secondary unified route metadata is consumed only from accepted direct-browse backing;
- `◆ 深掘りのみ` requires accepted direct-browse Special backing.

This preserves #64/#76 visibility/status semantics instead of using unified navigation to bypass them.

### Exact Special route enrichment

The exact six-row reviewed override asset is enforced by Special ID + canonical identity.

Tests cover:

- exactly six unique IDs;
- identity mismatch -> fail closed;
- only ADD_SECONDARY;
- pose -> POSE_POSITION;
- camera -> COMPOSITION_CAMERA;
- scene -> SCENE_BACKGROUND;
- no broad REACTION_STATE -> EXPRESSION_GAZE inference.

### UI cleanup

- old visible Special tree removed;
- left `← 戻る` removed;
- Special-tree expansion code-behind removed;
- obsolete Special facet XAML resources removed;
- details use discovery-oriented `探せる場所` / `発見サポート`;
- ◆ is identity-level deep-discovery status, not raw IsSpecial;
- neutral guidance matches frozen wording:
  `左からカテゴリを選ぶか、タグ名を検索してください。`
- selected workspace-tab blue-edge seam cosmetic fix included.

## #114 performance/architecture invariants

Preserved:

- RuntimeCatalogIndex/SearchEngine ranking;
- one-time unified index construction;
- no per-keystroke classification/index rebuild;
- no eager 30k+ neutral card creation;
- WPF recycling virtualization;
- accepted wide/two-column result composition;
- no synchronous per-keystroke user.db persistence;
- dictionary semantics remain in DictionaryWorkspaceViewModel rather than MainWindow/MainViewModel.

Synthetic 31,752-identity characterization is now part of the focused regression surface.

## Source-contract limitation discovered in final review

#117 design text describes General derivation as:

- people/count-group -> PEOPLE_COUNT
- people/role-person -> RELATION_ROLE

However, the accepted #64 production taxonomy currently has a single `PERSON_COUNT` genre with **no accepted count-group / role-person subgenres**.

Therefore v1 deliberately does **not** invent a new General semantic split:

- accepted General `PERSON_COUNT` -> PEOPLE_COUNT;
- RELATION_ROLE receives accepted #76 Special `PERSON_RELATION` backing;
- no heuristic reclassification of the 30,629 General rows was introduced.

This is a bounded source-contract limitation, not permission to restart #64 or #118. A future General role/count split requires an explicit accepted data decision.

## Protected-boundary audit

No product mutation of:

- live production/main;
- General/Special production membership;
- #64/#76 authority;
- #70 translation/data authority;
- Prompt parser/output/profile semantics;
- SearchEngine ranking;
- tracked/real `catalog.db`;
- `UserData/user.db`;
- user.db schema/reset.

The #70-named diff is test-only, updating query-preservation expectations.

Production/workstation catalog rebuild and practical workstation smoke are **not claimed** by this cloud DEV validation; explicit catalog build still requires the protected local source inputs.

## Next action

**MERGE COMPLETE.**

PR #125 merged to live main at:

`2ada80b4611b64ac5717924ae634ba917e3d0b95`

Remaining gate is local/runtime only:

1. explicitly rebuild the production catalog using the protected local source inputs;
2. refresh the local WPF runtime from merged main;
3. smoke the unified navigation, content filters, dedicated scopes, search/query persistence, deep-only, and two-column layout;
4. confirm real `UserData/user.db` remains untouched;
5. then close #117 and mark the runtime integration complete.

Do not repeat completed #117 implementation/research and do not restart #118 research.
