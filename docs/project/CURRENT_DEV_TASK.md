# CURRENT DEV TASK — ISSUE #114 RUNTIME CATALOG INDEX PHASE 1 (ACTIVE)

最終同期: 2026-09-16

## Routing status

- Issue #114 `[DEV][ARCH][PERF] WPF architecture stabilization and runtime catalog index refactor` is the active DEV implementation lane.
- Phase 1 branch: `codex/issue114-runtime-index-phase1`.
- Base live-main SHA: `a8d19e23483f10c4eb7c87b3a0dfa89ff24e4f41`.
- Activation authority: Issue #114 activation comment `5697124968`.
- Issue #113 branch `codex/issue113-wpf-performance-pass` at `9cfad5d8c21fe379badc88c7831e61359865a919` is reference-only and is not a base or merge source.
- Phase 1 scope is the small runtime catalog/query/index boundary: one-time lookup/category/path/relation indexes and precomputed search documents, with existing behavior and schemas preserved.
- MainViewModel full split, WPF virtualization, targeted Prompt refresh, query persistence, FTS, catalog schema changes, and #70 data changes are out of scope.
- Do not merge or close Issue #114 from this branch.

## Protected boundaries

- Issue #70 source/results, accepted rows, translation status, canonical identity, and import content remain untouched.
- `catalog.db` schema v1 and `user.db` schema remain unchanged.
- General and Special taxonomy, Prompt parser/output semantics, Forge protocol, and SoftwareOnly remain unchanged.

## Validation target

- Preserve SearchEngine ranking and characterization queries (`blue_hair`, `青い髪`, `anal`, `a`, `s`, `hair`, `blue hair`, `青い hair`, `anal_sex`, `blu`, `lue`, `blie hair`).
- Preserve General top/genre/subgenre, Special, Character, Copyright, Artist, and Character↔Copyright result membership/order.
- Record Release build, full/focused .NET tests, `git diff --check`, and index/search/browse before/after measurements when the workstation SDK/runtime allows them.
- If protected production catalog inputs or the .NET SDK are unavailable, report that limitation explicitly; do not infer workstation performance.
