# Issue #114 Phase 2 architecture checkpoint

Branch: `codex/issue114-viewmodel-phase2`

Phase 2 base: corrected Phase 1 tip `7d858895051dded33f4f9462f0c70f8e263a1584`

## Structure

- `DictionaryWorkspaceViewModel` owns dictionary query, browse, facets, results, related entries, selection, detail, navigation and restore state. It is the only App feature owner that calls `IRuntimeCatalogQuery`.
- `PromptEditorViewModel` owns chip presentation, selection, find, direct edit, category projection, output profile and Prompt editing commands. Core `PromptWorkspace` remains unchanged.
- `GenerationPresetsViewModel` owns preset collection, selection, CRUD, apply and copy operations.
- `ForgeViewModel` owns Forge settings and bridge commands. The Forge protocol remains in Core.
- `UserStateCoordinator` owns UserState load, UI snapshot construction and save. Phase 2 preserves existing save timing; timing optimization remains Phase 3.
- `MainViewModel` is a composition root and narrow cross-feature coordinator. Its compatibility forwarding surface remains temporarily because `MainWindow.xaml` and existing public regression tests are intentionally not split until Phase 3.

Cross-feature wiring uses the shared Core `PromptWorkspace`: dictionary add/inspect flows into it, its `Changed` callback refreshes Prompt and dictionary display state, and the coordinator snapshots all child state. No event bus, service locator or global state was added.

## Size and verification

- MainViewModel: 614 lines before, 107 lines after.
- Release build: PASS, 0 warnings / 0 errors.
- Full .NET tests: `138 passed / 7 skipped / 0 failed` (`145 total`).
- Phase 2 focused tests: `4 passed / 0 skipped / 0 failed`.
- Phase 1/runtime-index and existing Issue 73/74/76/DataAndViewModel behavior is covered by the full run; no Phase 1 runtime-index source was changed.
- `git diff --check`: PASS.

Phase 2 does not include Issue #113 virtualization, targeted refresh, Query persistence, keyboard navigation or MainWindow decomposition. Runtime performance numbers remain the corrected Phase 1 numbers and were not reinterpreted as Phase 2 measurements.

Issue #70 result data, taxonomy, canonical identity, catalog.db schema and user.db schema are untouched.
