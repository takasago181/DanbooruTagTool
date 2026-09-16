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

## Required evidence before handoff

- Release build and full .NET regression.
- Focused Issue #113 plus Issue73/Issue74/Issue76/DataAndViewModel/Production test coverage.
- Synthetic large-result projection measurement and available responsiveness/persistence measurements.
- `git diff --check`, protected/canonical/taxonomy/schema boundary confirmation, and clean working-tree status.
