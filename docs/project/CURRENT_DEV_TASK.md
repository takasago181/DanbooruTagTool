# CURRENT DEV TASK — ISSUE #114 WPF ARCHITECTURE STABILIZATION (COMPLETED)

最終同期: 2026-09-17

## Routing status

- Issue #114 `[DEV][ARCH][PERF] WPF architecture stabilization and runtime catalog index refactor` Phase 1–4 is DEV-accepted and integrated into `main`.
- Accepted implementation branch: `codex/issue114-phase3-wpf-performance`.
- Accepted source tip before main integration: `6880f0a23ca594f8a3e673537a22389543e1124d`.
- Base live-main SHA: `a8d19e23483f10c4eb7c87b3a0dfa89ff24e4f41`.
- Activation authority: Issue #114 activation comment `5697124968`.
- Issue #113 branch `codex/issue113-wpf-performance-pass` at `9cfad5d8c21fe379badc88c7831e61359865a919` is reference-only and is not a base or merge source.
- Completed scope includes the runtime catalog/query/index boundary, precomputed search documents, Dictionary/Prompt/Presets/Forge feature ViewModels, UserState coordination, Dictionary/Prompt view composition, WPF result virtualization, targeted Prompt canonical refresh, Query persistence correction, General Paths cache, and column-aware keyboard navigation.
- Practical WPF validation used the available 33,688-entry catalog. 126,427-entry production WPF workstation validation was not performed and remains a follow-up when the protected production catalog is available.
- Issue #114 is integrated; do not claim 126,427-entry WPF validation from this document.

## Protected boundaries

- Issue #70 source/results, accepted rows, translation status, canonical identity, and import content remain untouched.
- `catalog.db` schema v1 and `user.db` schema remain unchanged.
- General and Special taxonomy, Prompt parser/output semantics, Forge protocol, and SoftwareOnly remain unchanged.

## Validation target

- Preserve SearchEngine ranking and characterization queries (`blue_hair`, `青い髪`, `anal`, `a`, `s`, `hair`, `blue hair`, `青い hair`, `anal_sex`, `blu`, `lue`, `blie hair`).
- Preserve General top/genre/subgenre, Special, Character, Copyright, Artist, and Character↔Copyright result membership/order.
- Record Release build, full/focused .NET tests, `git diff --check`, and index/search/browse before/after measurements when the workstation SDK/runtime allows them.
- If protected production catalog inputs or the .NET SDK are unavailable, report that limitation explicitly; do not infer workstation performance.

## Integrated follow-up candidates

- measure the accepted WPF runtime with the full 126,427-entry production catalog;
- evaluate remaining eager `EntryViewModel` creation and any residual full-refresh path;
- separately assess `SoftwareOnly` and O(N) search tradeoffs.

These follow-ups do not alter the accepted #114 Phase 1–4 scope or the protected #70/data/schema boundaries.
