# CURRENT DEV TASK — ISSUE #117 UNIFIED GENERAL/SPECIAL BROWSE + #118 CONTENT INTENT

最終同期: 2026-09-18

## Routing status

- Active DEV Issue: #117 `[DEV][UI][DISCOVERY] Implement unified General/Special browse navigation`.
- Implementation status: **DEV IMPLEMENTATION COMPLETE / VALIDATED / STOP BEFORE MERGE**.
- Draft PR: **#125** `[WIP][#117] Unified browse navigation + content intent filter`.
- Implementation branch: `codex/issue117-unified-browse-content-intent`.
- Live-main base remains `07f6e05c7300831a9c4f52fe3857043594b8413b`.
- Branch was verified ahead of main and 0 behind immediately before finalization.
- #118 research/design remains frozen authority; do not restart classification research.
- Do not merge without explicit review/approval.

## Validated source checkpoint

Source validation checkpoint:

`47a263ed05800fc47c3a29c5867172ab8700c3a9`

GitHub Actions validation run:

`35312382053`

Results:

- `dotnet restore src/DanbooruTagTool.sln`: PASS
- Release build: **PASS**
- full Release tests: **178 total / 171 passed / 7 skipped / 0 failed**
- focused `Issue117UnifiedBrowseTests`: **13 / 13 passed**
- `git diff --check origin/main...HEAD`: **PASS**
- temporary validation workflows were removed after PASS and are not part of the final product diff.

Any commits after the validated source checkpoint are management-doc or validation-workflow cleanup only unless a later checkpoint explicitly says otherwise.

## Implemented #117 behavior

### Unified ordinary discovery

Visible General/Special roots are removed from the browse UI.

Ordinary Tags discovery uses exactly the frozen 19 top-level labels from #117, followed by dedicated:

- キャラクター
- 作品
- 作者

General and Special remain source/provenance categories internally; they are not exposed as separate browse roots.

### Identity-level dedupe

- one ordinary canonical identity -> one result card;
- General/Special overlap is deduplicated both in browse and search results;
- search keeps the existing RuntimeCatalogIndex/SearchEngine order and only removes non-matching/duplicate survivors;
- unified filtering does not rerank search.

### Unified browse state

DictionaryWorkspaceViewModel owns:

- scope;
- primary route;
- local subroute;
- body-site facets;
- theme facets;
- deep-only toggle;
- content-intent filter;
- one-step unified browse history.

Legacy persisted browse keys have compatibility migration into the unified state.

Query text survives route/facet/scope changes.

Neutral empty Tags state does not eagerly enumerate the ordinary population and instead shows guidance.

### Generic center refinements

Tags scope exposes the common refinement area:

- optional local classification;
- 部位;
- テーマ;
- `◆ 深掘りのみ`;
- `内容 [すべて] [一般向け] [性的]`;
- `1つ戻す`;
- `全解除`.

Selected zero-count facets remain visible so the user can remove them.

### #118 content intent

Frozen visible mapping:

- `すべて` -> SEXUAL + NON_SEXUAL + CONTEXTUAL + UNCLASSIFIED
- `一般向け` -> NON_SEXUAL + CONTEXTUAL
- `性的` -> SEXUAL + CONTEXTUAL
- UNCLASSIFIED -> `すべて` only

Frozen ordinary identity authority validated in focused tests:

- total 31,752
- SEXUAL 2,037
- CONTEXTUAL 1,951
- NON_SEXUAL 27,759
- UNCLASSIFIED 5
- AUTO_HIGH_CONF 22,371
- HUMAN_REVIEWED 9,376

Character / Copyright / Artist ignore ordinary contentIntent matching in v1 while the Tags-scope selection is preserved for restoration.

Normal startup does **not** parse the #118 research CSV. The frozen authority is consumed only at explicit catalog-build time and serialized into CatalogEntry metadata.

### Deep discovery

`◆ 深掘りのみ` is identity-level and requires direct-browse Special backing.

Reference-only Special evidence does not make an identity deep-discoverable.

### Exact Special route enrichments

The exact six-row override asset is validated by Special ID + canonical identity and only adds the frozen secondary route.

Acceptance tests cover:

- exactly six unique override IDs;
- ID/canonical mismatch -> fail closed;
- POSE -> POSE_POSITION;
- camera -> COMPOSITION_CAMERA;
- scene -> SCENE_BACKGROUND;
- no broad REACTION_STATE -> EXPRESSION_GAZE remap.

### UI cleanup

- legacy visible Special tree removed;
- legacy left `← 戻る` removed;
- old Special-specific tree expansion code-behind removed;
- details now show discovery-oriented metadata such as `探せる場所` / `発見サポート`;
- ◆ display is based on identity-level deep-discovery status rather than raw `IsSpecial`;
- top workspace tab selected blue-edge seam received the approved cosmetic fix.

## #114 responsiveness invariants preserved

Validated implementation preserves the intended architecture/performance boundaries:

- RuntimeCatalogIndex/SearchEngine ranking remains the search authority;
- no per-keystroke unified index rebuild/classification;
- content filter is applied after existing search;
- facet counts refresh on browse-state changes, not every query keystroke;
- neutral empty Tags state does not create 30k+ ordinary result cards;
- WPF dictionary recycling virtualization remains;
- dictionary semantics remain owned by DictionaryWorkspaceViewModel;
- no synchronous per-keystroke user.db persistence was introduced;
- two-column wide-surface composition regression remains covered.

## Protected-boundary audit

Final branch diff audit found no product mutation of:

- production/main;
- General/Special production membership;
- #70 translation/data authority;
- Prompt parser/output/profile semantics;
- `catalog.db`;
- `UserData/user.db`;
- user.db schema/reset;
- SearchEngine ranking.

The only #70-named source diff is an integration-test adjustment for the newly required query-preservation behavior; #70 data is untouched.

## Next action

**Stop before merge.**

Next human/reviewer action is to review Draft PR #125 / Issue #117 DEV return evidence.

If accepted:

1. merge/fast-forward according to repository policy;
2. re-check live main;
3. sync CURRENT_STATE to merged main commit;
4. close #117 only after the merged state is confirmed.

Do not restart #118 research and do not redo completed #117 implementation slices.
