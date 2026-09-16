# Issue #114 Phase 3 validation report

Date: 2026-09-16  
Branch: `codex/issue114-phase3-wpf-performance`  
Base accepted Phase 2: `f2a8bfa0e1b898723d6f2b453320beca2e9579a2`

## Implementation

- `DictionaryWorkspaceViewModel` keeps `Results` as the flat semantic sequence and exposes `DictionaryRows` as a display-only projection of existing `EntryViewModel` references.
- Dictionary results use a vertical `VirtualizingStackPanel`, recycling, and `ScrollViewer.CanContentScroll=True`; row selection is reset and `SelectedEntry` is the only selection authority.
- Prompt refresh captures canonical counts, diffs changed canonicals, refreshes only indexed affected result/related instances, and separately refreshes a detached `SelectedEntry` with the same canonical.
- Query changes no longer persist from the setter or internal `RefreshResults` selection restoration. Explicit selection, browse/clear operations, Prompt changes, Forge/Preset saves, and window UI save paths retain durable persistence behavior.
- Column-aware navigation is owned by `DictionaryWorkspaceViewModel`; the view handles PreviewKeyDown and brings the selected display row into view.
- `DictionaryWorkspaceView` owns dictionary search/facet/result view behavior. `PromptEditorView` owns Prompt editor bindings and editor-only pointer/drag/focus behavior. `MainWindow.xaml` is now the shell plus remaining shared detail/header surfaces.
- General browse Paths remain supplied by the Phase 1 cached provider; no second cache was added.

## Tests and measurements

- Release build: PASS, 0 warnings / 0 errors.
- Full .NET tests: `145 passed / 7 skipped / 0 failed` (`152 total`).
- Issue #114 focused tests: `16 passed / 0 skipped / 0 failed`.
- Phase 3 focused tests: `6 passed / 0 skipped / 0 failed`.
- Issue73 / Issue74 / Issue76 / DataAndViewModel / preset / Forge regressions: `55 passed / 1 skipped / 0 failed`.
- `git diff --check`: PASS.

Synthetic Phase 3 characterization used 126,427 existing lightweight `EntryViewModel` references:

| Measurement | Result |
| --- | ---: |
| Flat entries → two-column rows | 126,427 → 63,214 |
| Projection time | 2.09 ms |
| Projection allocation | 2,528,656 bytes |
| Additional `EntryViewModel` instances during projection | 0 |
| Prompt changed canonical result rows refreshed | 1 |
| Detached selected instance refreshed | 1 |
| Query setter + `RefreshResults()` save-count delta | 0 |

The Phase 1 production-sized runtime-index characterization was also rerun: 126,427 synthetic catalog entries, runtime index build `488.867 ms`, transient allocation `234,876,568 bytes`, retained heap delta `85,315,664 bytes`, four-query indexed search `536.195 ms`, and indexed Character browse `0.319 ms`. These are runtime/index measurements, not WPF container realization measurements. No production workstation claim is made for a real 126,427-entry WPF catalog; that remains Phase 4 practical acceptance.

## Scope protection

- Issue #70 result contents, statuses, source/result identities, review decisions, and importer data: untouched.
- Taxonomy and canonical identity: untouched.
- `catalog.db` and `user.db` schemas: untouched.
- PromptWorkspace semantics, Forge protocol, preset semantics, FTS, SoftwareOnly, and build-catalog extraction: untouched.
- `MainViewModel` was 107 lines at the accepted Phase 2 base and is 117 lines after Phase 3; the remaining forwarding surface is retained only for the shell's shared detail/header/dialog compatibility and existing regression tests. Dictionary/Prompt editor bindings no longer depend on those proxies.
- Original `artifacts/current` protected data was not modified.

## Phase #113 absorption

| #113 item | Phase 3 disposition |
| --- | --- |
| Result virtualization / row projection | absorbed |
| Targeted canonical refresh | absorbed |
| General Paths cache | already satisfied by Phase 1 |
| Query persistence correction | absorbed |
| Detached selection refresh | absorbed |
| Keyboard navigation authority | absorbed |

Working tree is clean after the implementation commits. Main remains unmerged and unchanged.

READY FOR DEV PHASE 3 AUDIT / NOT MERGED
