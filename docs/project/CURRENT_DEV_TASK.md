# CURRENT DEV TASK — ISSUE #117 UNIFIED GENERAL/SPECIAL BROWSE + #118 CONTENT INTENT

最終同期: 2026-09-18

## Routing status

- Active DEV Issue: #117 `[DEV][UI][DISCOVERY] Implement unified General/Special browse navigation`.
- #118 research is complete and frozen. Final authority:
  - `docs/issue118/FINAL_DESIGN_CHECKPOINT.md`
  - research branch `research/issue118-cluster-triage-v8`
  - frozen commit `4cacb1fea4aaf46552da3837f50712293a6d4440`
  - Issue #118 Final design freeze v2.0 comment `5725346261`.
- Implementation branch: `codex/issue117-unified-browse-content-intent`.
- Base live-main SHA: `07f6e05c7300831a9c4f52fe3857043594b8413b`.
- Recovered implementation head before this management-doc sync: `87001ae0670f635aafb7ade660c6b59da273d2ca`.
- Branch was verified 12 commits ahead / 0 behind main at recovery time.
- Stop before merge. No direct main implementation.

## Recovered implementation state

Completed or materially started on the feature branch:

1. Core unified browse contracts/state/index scaffold.
2. General/Special identity-level route aggregation scaffold.
3. Exact Special route override asset/loader work.
4. #118 frozen sexual-intent production-candidate sidecar added as explicit build input.
5. CatalogEntry sexual-intent metadata fields and build overlay wiring started.
6. Runtime unified index can consume existing Special Browse v2 metadata.

Not yet completed at recovery:

- DictionaryWorkspaceViewModel migration to unified browse state;
- shallow left navigation and generic center refinement UI;
- removal of legacy Special-tree/back-history behavior;
- details/deep-discovery presentation;
- focused/full regression tests for #117/#118;
- Release build / full test / performance characterization;
- final protected-boundary audit and DEV return checkpoint.

## #118 frozen visible behavior

```text
内容
[すべて] [一般向け] [性的]
```

Mapping:

- `すべて` -> SEXUAL + NON_SEXUAL + CONTEXTUAL + UNCLASSIFIED
- `一般向け` -> NON_SEXUAL + CONTEXTUAL
- `性的` -> SEXUAL + CONTEXTUAL
- UNCLASSIFIED -> `すべて` only

Ordinary identity authority:

- total 31,752
- SEXUAL 2,037
- CONTEXTUAL 1,951
- NON_SEXUAL 27,759
- UNCLASSIFIED 5
- AUTO_HIGH_CONF 22,371
- HUMAN_REVIEWED 9,376

Character / Copyright / Artist ignore contentIntent in v1 while preserving the user's selected Tags-scope content filter for restoration on return.

## Protected boundaries

Do not mutate:

- production/main before review/merge;
- General/Special production membership;
- #64/#76 source taxonomy semantics;
- #70 translation/data authority;
- Prompt parser/output/profile semantics;
- `catalog.db` or `UserData/user.db` as DEV validation data;
- user.db schema/reset;
- SearchEngine ranking.

Preserve #114/post-hotfix invariants:

- RuntimeCatalogIndex/SearchEngine ranking behavior;
- WPF recycling virtualization;
- two-column wide result surface and second-card visibility;
- no eager 30k+ card creation in neutral empty Tags state;
- no per-keystroke unified index rebuild/classification;
- no synchronous per-keystroke user.db persistence;
- dictionary semantics remain owned by DictionaryWorkspaceViewModel, not MainViewModel/code-behind.

## Resume order

Resume from the recovered boundary, not from research:

1. verify feature branch HEAD and main divergence;
2. complete DictionaryWorkspaceViewModel unified state/query/filter composition;
3. add focused Core/ViewModel tests before broad UI changes;
4. implement shallow left navigation + generic center refinements including content intent;
5. remove legacy Special-tree/back-history behavior;
6. details/deep presentation and tab underline cosmetic fix;
7. full/focused tests, Release build, diff check, available performance characterization;
8. Issue #117 DEV return checkpoint; stop before merge.

## Anti-freeze execution rule

Use bounded slices. Each slice should:

- change one coherent layer/behavior;
- create a stable commit;
- leave an Issue #117 checkpoint with last success, remaining work, next action, branch/commit/evidence;
- avoid re-reading or regenerating completed #118 research;
- avoid long polling loops or repeated full-repository scans.

If a chat/session stops, restore from live main + this file + Issue #117 latest checkpoint + feature branch HEAD.
