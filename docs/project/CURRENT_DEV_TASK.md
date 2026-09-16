# CURRENT DEV TASK — ISSUE #113 WPF PERFORMANCE PASS (ACTIVE)

最終同期: 2026-09-16

## Routing status

- **Issue #113 — WPF dictionary virtualization and UI responsiveness pass** is the active DEV lane.
- Activation authority: live Issue #113 body and activation comment `5696309332`.
- Base live-main SHA: `a8d19e23483f10c4eb7c87b3a0dfa89ff24e4f41`.
- Implementation branch: `codex/issue113-wpf-performance-pass`.
- `CURRENT_DEV_TASK.md` on live main still mirrors completed Issue #83; that is stale for this activation.
- Do not merge, push to `main`, or close Issue #113 from this task.

## P0 scope lock

1. Keep flat authoritative `Results`, but render display-only one/two-card rows through standard WPF `VirtualizingStackPanel` recycling.
2. Preserve `SelectedEntry` identity, result order, card-level selection, keyboard navigation, add/remove, odd-result handling, and duplicate/raw safety.
3. Diff Prompt canonical counts and refresh only affected active result/detail/related rows.
4. Cache immutable General browse Paths without changing content or order.
5. Stop synchronous SQLite persistence from the per-character `Query` setter while preserving debounce, explicit save, and normal-close persistence.

## Explicitly deferred

Do not change rendering mode, SearchEngine ranking/normalization/index architecture, catalog.db or user.db schemas, Prompt parser/output semantics, Special/General taxonomy, Issue #70 runtime data, or production Special identities.

## Scale and validation boundary

Issue #70 GitHub integration is complete (92,739 overlay rows); the expected rebuilt catalog is 126,427 entries with General 30,629 and Special 3,059. The workstation runtime has not been explicitly rebuilt with #70 in this task environment, so no workstation 126,427-entry performance claim is permitted.

Pre-edit baseline on the clean branch used the bundled SDK `10.0.401`:

- Release solution build: PASS, 4,264 ms.
- Release full .NET tests: 129 passed / 7 skipped / 0 failed, 3,878 ms.
- No production catalog was supplied; production facts remained skipped.

## Current implementation checkpoint

- Implementation commit: `223f8a5f` (`perf: virtualize WPF dictionary results`).
- Release solution build: PASS, 0 warnings / 0 errors.
- Full .NET tests: 136 passed / 7 skipped / 0 failed.
- Focused: Issue #113 7/7; Issue73 6/6; Issue74 2/2; Issue76 13 passed / 1 skipped; DataAndViewModel 15/15; Production facts 3 skipped because the protected catalog was not supplied.
- Synthetic 126,427-entry projection: 63,214 display rows in 2.03 ms; row projection creates no WPF card/container instances.
- WPF actual realized-container inspection was not available because the provided CUA helper lacked the target-app binding API; no workstation 126,427-entry claim is made.
- `git diff --check`: PASS; #70 data/importer, canonical data, taxonomy, catalog.db schema, and user.db schema are untouched.
