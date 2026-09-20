# Post-#131 runtime optimization audit

Date: 2026-09-20
Authority: `origin/main` at `e2d9afa88539e8a275a4f3ecab446b42b7a95af8`
Branch: `codex/runtime-optimization-post-audit`

## Scope

This audit covers only post-#131 runtime maintenance and the measurable cost of
selection/detail projection. Catalog contents, PromptToken semantics, search
ranking, taxonomy, #70 data, Issue #118 authority, ForgeBridge, and real
UserData were not changed.

The existing A/B rendering evidence remains the authority for SoftwareOnly:
idle CPU and disk settled to approximately zero, idle GPU engine was zero, and
the automatic-render candidate used more private memory without a clear CPU or
total-system-load win. This work therefore keeps automatic WPF render selection.

## Static audit disposition

| Candidate | Disposition | Evidence |
| --- | --- | --- |
| `EntryViewModel.DiscoverySupport` | Removed | No production, XAML, command, test, keyboard, persistence, or #70 reference. |
| `RightDetailsTabItem` style | Removed | No XAML consumer after the #131 right-pane removal. |
| `Related`, `RelatedFor`, `Detail`, `DetailsTabIndex`, `InspectEntry`, `Breadcrumb`, `DetailAddLabel` | Retained | Existing tests, forwarding API, Prompt-chip inspection, browse restore, and #70 compatibility still consume them. |
| `activeResultIndex` related rows | Retained with lazy materialization | Prompt-state refresh still needs the index when `Related` is explicitly accessed. |
| search/geometry/copy timers | Retained | Existing 150 ms/400 ms/2 s debounce timers stop after their work and were idle-safe in the prior audit. |
| catalog/index/facet/search refresh paths | Retained | No new evidence of an idle loop or semantic-preserving hot-path defect. |
| SoftwareOnly render override | Not reintroduced | The current automatic-render baseline is retained. |

## Adopted changes

`RelatedFor` is now lazy and cached. Selecting a result invalidates the cache;
explicit access still produces the same related rows and rebuilds the active
result index. When the UI does not consume related rows (the normal post-#131
path), selection no longer constructs those view models or scans the related
catalog set. `PromptEditorViewModel.RefreshFromWorkspace` now refreshes Undo /
Redo command CanExecute state after a Prompt mutation, preserving the existing
Prompt history behavior in the UI.

## Measurement

The selection benchmark used the production catalog and the same ViewModel
fixture. Twenty selections of one Special row produced:

| Build | Elapsed | Allocated |
| --- | ---: | ---: |
| eager Related baseline | 7.722 ms | 2,449,672 B |
| lazy Related candidate | 1.081 ms | 21,688 B |

The candidate therefore reduced this measured selection path by approximately
86% elapsed time and 99% allocation. The final explicit `Related` access still
returned the same six rows.

The 10-cycle UI operation loop used a copied UserData database in a staging
runtime. Five seconds of settle time followed each cycle. The candidate trace
was:

| Cycle | Private MB | Working MB | Threads | Handles | CPU % |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 257.414 | 300.387 | 22 | 682 | 2.9762 |
| 2 | 261.008 | 306.758 | 21 | 679 | 1.4045 |
| 3 | 257.824 | 303.570 | 20 | 676 | 1.0926 |
| 4 | 258.250 | 304.086 | 19 | 674 | 0.9410 |
| 5 | 261.832 | 308.500 | 19 | 674 | 0.8809 |
| 6 | 266.625 | 314.043 | 19 | 674 | 0.8707 |
| 7 | 263.641 | 310.957 | 15 | 666 | 0.8821 |
| 8 | 263.055 | 310.805 | 15 | 668 | 0.9161 |
| 9 | 260.957 | 309.551 | 15 | 668 | 0.8476 |
| 10 | 269.246 | 317.996 | 15 | 668 | 0.7006 |

The prior same-condition eager baseline ended at 269.203 MB private memory,
318.141 MB working set, 15 threads, and 664 handles. Both traces plateaued;
there was no monotonic thread/handle growth or leak signature. Disk activity in
the loop was bounded UserData persistence activity, not an idle loop. The
previous full scenario audit measured idle GPU engine at 0%; this optimization
does not alter rendering selection.

## Validation artifacts

- `scripts/performance/run_leak_cycles.ps1` — staging-only 10-cycle process
  metrics runner.
- `scripts/performance/run_targeted_smoke.ps1` — staging-only UI Automation
  smoke for search, Prompt add/undo/redo, editor navigation, and copy.
- Full scenario UI smoke was run against the candidate staging runtime for
  launch, idle, long-result scroll, Japanese/English/mixed search, category,
  body/theme/content filters, DeepOnly, Prompt add/remove/reorder, ordered /
  category display, Prompt search, resize, and post-operation idle.

The catalog and copied UserData passed read-only SQLite `quick_check`,
`integrity_check`, and `foreign_key_check`. Catalog SHA remained
`DFDC93581F2E8E3041FBC497F9A1C5CFD458977EF57462E05902F27D29B97CF9`.
