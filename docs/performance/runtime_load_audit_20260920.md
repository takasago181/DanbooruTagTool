# Performance / Runtime Load Audit — 2026-09-20

## Verdict

`PERFORMANCE_RUNTIME_AUDIT_COMPLETE`

This audit measured the application process in two staging runtimes. No production runtime, production `UserData`, `artifacts/current`, shortcut, catalog, taxonomy, search semantics, #70 data, or classification audit was modified. No optimization was merged or applied.

## Authority and A/B sources

| Item | Value |
|---|---|
| Live `origin/main` | `10d4a8e1e48b75eb37ef97713e93293d2695c5e0` |
| Audit branch | `audit/runtime-performance-post131` |
| A source | `e64f3f7cb02df8f5c5fd65dc4132f0e398769b9d` — `SoftwareOnly` |
| B source | `10d4a8e1e48b75eb37ef97713e93293d2695c5e0` — automatic render selection |
| A staging | `C:\Codex\DanbooruTagTool\.perf-a-softwareonly` |
| B staging | `C:\Codex\DanbooruTagTool\.perf-b-auto-render` |
| A EXE SHA-256 | `82BC4A698688C86F8ACF1866B8239A87AA8834E68E52744705EBC35D7BCF093D` |
| B EXE SHA-256 | `251C4A46B2BE76CB841CC04510B4747349B7079E3462E648A3E9F13EC136BEDB` |
| Shared catalog SHA-256 | `DFDC93581F2E8E3041FBC497F9A1C5CFD458977EF57462E05902F27D29B97CF9` |
| Shared UserData seed SHA-256 | `9A47D5B7840B36D483F0707D1ACF97CB8811E53D22C86BB44EE2EE4274D72149` |

Environment: Windows 11 Home `10.0.26200`, 16 logical processors, 2560×1440. Both runs used the same session, catalog, UserData seed, maximized launch, and the same ordered S1–S18 action sequence. The raw process series used one-second samples. GPU totals used `nvidia-smi` and Windows GPU Engine/Process Memory counters.

The session did not expose `node_repl`/`sky`; therefore the UI sequence used Windows UI Automation with a mouse/SendInput fallback. This fallback was used only against A/B staging and each action was written to the corresponding `*-actions.jsonl` file.

## Scenario CPU result

Values are process CPU percent normalized by logical processor count. `avg / peak` are percentages.

| Scenario | A SoftwareOnly | B AutoRender | Observation |
|---|---:|---:|---|
| S1 launch | 0.263 / 5.679 | 0.185 / 3.724 | B lower launch CPU peak |
| S2 idle | 0.004 / 0.263 | 0.000 / 0.000 | Both settled |
| S3 scroll | 0.877 / 3.683 | 1.013 / 4.658 | B slightly higher |
| S4 Japanese input | 0.451 / 3.405 | 0.355 / 2.914 | B slightly lower |
| S5 English input | 0.141 / 1.591 | 0.133 / 1.400 | Essentially equal |
| S6 mixed input | 0.147 / 1.769 | 0.310 / 3.535 | B higher |
| S7 category switch | 0.405 / 2.210 | 0.800 / 2.662 | B higher |
| S8 body filter | 0.309 / 1.598 | 0.364 / 1.810 | Essentially equal |
| S9 theme filter | 0.389 / 1.630 | 0.405 / 1.771 | Essentially equal |
| S10 content filter | 0.238 / 1.242 | 0.246 / 0.956 | Essentially equal |
| S11 DeepOnly | 0.047 / 0.565 | 0.039 / 0.466 | Essentially equal |
| S12 prompt add/remove | 0.948 / 3.442 | 0.990 / 3.721 | Essentially equal |
| S13 prompt reorder | 0.346 / 2.523 | 0.363 / 2.919 | Essentially equal |
| S14 category display | 0.000 / 0.000 | 0.000 / 0.000 | No measurable load |
| S15 display toggle | 0.016 / 0.187 | 0.024 / 0.283 | No material difference |
| S16 Prompt search | 0.008 / 0.093 | 0.032 / 0.186 | No material difference |
| S17 resize | 0.024 / 0.282 | 0.039 / 0.469 | No material difference |
| S18 post-operation idle | 0.004 / 0.362 | 0.002 / 0.193 | Both settled |

### CPU verdict

Removing `SoftwareOnly` did not produce a material CPU reduction. The result is mixed and very small in absolute process CPU terms: B is lower during launch and some text operations, but higher during scroll, mixed search, category switching, and prompt add/remove. The audit does not justify a CPU optimization claim.

## Idle, memory, threads, handles, and disk

| Metric | A S2 idle | B S2 idle | A S18 idle | B S18 idle |
|---|---:|---:|---:|---:|
| CPU average / peak | 0.004 / 0.263% | 0.000 / 0.000% | 0.004 / 0.362% | 0.002 / 0.193% |
| Private memory first → last | 200.074 → 197.383 MB | 234.043 → 233.793 MB | 208.434 → 206.926 MB | 284.070 → 283.598 MB |
| Working set first → last | 267.734 → 265.461 MB | 265.480 → 265.352 MB | 293.711 → 291.852 MB | 313.441 → 313.102 MB |
| Threads first → last | 18 → 13 | 20 → 15 | 19 → 13 | 21 → 15 |
| Handles first → last | 514 → 502 | 665 → 655 | 561 → 540 | 698 → 695 |
| Process disk read/write while idle | 0 / 0 B/s | 0 / 0 B/s | 0 / 0 B/s | 0 / 0 B/s |

Both runtimes settle to approximately zero process CPU and zero process disk I/O. Threads and handles decrease during idle rather than grow monotonically. B retains a larger private-memory footprint after the operation sequence (about 284 MB versus A about 207 MB), but it is flat throughout the 120-second S18 idle window; this is bounded render/runtime footprint evidence, not proof of a leak. A dedicated 5–10 cycle leak run was not performed, so repeated-cycle leak absence is not claimed.

Transient disk I/O occurred during expected state-changing operations. The largest observed write bursts were prompt add/remove and prompt reorder (approximately 194 KB/s A and 182 KB/s B for add/remove; approximately 146–147 KB/s for reorder). These bursts stopped in S2/S18 idle and are consistent with UserData persistence rather than continuous I/O.

## GPU result

The full S1–S18 GPU files contain host-total GPU samples. Host totals varied because other desktop applications were active; they are not app-attributable. Representative host totals were approximately 6–15% utilization during the sequences, with non-zero GPU memory already present before/after the application operation.

The first full capture exposed an audit-harness issue: PowerShell `ProcessId` conflicted with the automatic `$PID` variable in the GPU collector, leaving process-specific GPU columns empty. The collector was corrected to use `TargetProcessId` and the full action runs were not retroactively misrepresented. Corrected staging idle checks showed:

| Corrected idle check | GPU engine utilization | Process dedicated GPU memory | Process shared GPU memory |
|---|---:|---:|---:|
| A SoftwareOnly | no process counter sample / no allocation observed | no process counter sample | no process counter sample |
| B AutoRender | 0% | about 46.074 MB | about 2.742 MB |

The evidence supports that B allocates a small hardware-rendering GPU memory footprint, but does not show ongoing idle GPU engine activity. Because host GPU load was contaminated by other processes and the corrected process-specific active-operation series was not rerun for every scenario, no precise active-operation GPU A/B advantage is claimed.

Representative host-total samples from the full sequence (not app-only) were:

| Scenario | A host GPU avg / peak | B host GPU avg / peak |
|---|---:|---:|
| S1 launch | 7.25 / 8% | 9.25 / 15% |
| S2 idle | 6.25 / 9% | 8.00 / 9% |
| S3 scroll | 11.50 / 15% | 9.00 / 11% |
| S18 post-operation idle | 7.13 / 8% | 8.07 / 9% |

These values demonstrate why host-total GPU counters alone cannot be used to claim that A or B caused the observed desktop GPU activity.

## System-wide load caveat

Application process CPU was sampled directly and is the reliable A/B metric. Spot checks of Windows total CPU during the session ranged from approximately 4–5% to 92–95% while the application process itself remained near zero. Process inventory showed substantial unrelated activity from DesktopMate, ChatGPT, Codex, browsers, game/launcher tools, and StabilityMatrix. Therefore the observed “PC is working hard” sensation cannot be attributed to DanbooruTagTool from this audit alone. A quiet-session system-wide rerun with nonessential background applications stopped is required before making a total-PC-load claim.

## Timer / event / code audit

- Search debounce: 150 ms `DispatcherTimer`; tick calls `Stop()` before `RefreshResults()`; stopped on view `Unloaded`.
- Geometry persistence: 400 ms `DispatcherTimer`; each queue call stops/restarts it; tick stops before `SaveGeometry()`; window `Closing` stops it and saves once.
- Copy feedback: 2 s timer; tick stops itself; window `Closing` stops it.
- The three timers have no observed idle activity in S2/S18.
- Dictionary result virtualization remains enabled with recycling in `DictionaryWorkspaceView.xaml`.
- Catalog loading is read-only at runtime; UserData writes are tied to prompt/UI state changes and were visible only as transient operation I/O.
- `UnifiedBrowseIndex` is built once during view-model construction. No recurring rebuild was found.
- `Related`/`RelatedFor`, `DetailsTabIndex`, `Detail`, and `activeResultIndex` remain in the view-model and are used by the current selection/keyboard/test/#70-facing surface. They were not removed during a performance-only audit. Selection still computes related rows, so this is a candidate for a separately scoped measurement, not an approved optimization.
- No event unsubscribe change, semantic search change, catalog change, or runtime code optimization was made.

## Files and raw evidence

- `scenario-summary.csv` is the generated process summary.
- `raw/A/` and `raw/B/` contain the valid S1–S18 process/GPU series and UI action logs.
- `raw/gpu-check/` contains the corrected process-specific GPU idle checks.
- `scripts/performance/collect_process_metrics.ps1` collects process CPU, memory, threads, handles, process I/O, GDI/USER counts.
- `scripts/performance/collect_gpu_metrics.ps1` collects process GPU counters and host GPU totals.
- `scripts/performance/run_runtime_scenarios.ps1` drives the identical staging-only scenario sequence.
- `scripts/performance/summarize_runtime_metrics.ps1` generates the summary CSV.

The staging catalog/UserData health check was read-only and passed: catalog `quick_check=ok`, `integrity_check=ok`, `foreign_key_rows=0`, total 33,688, General 30,629, Special 3,059, Character/Copyright/Artist 0; staging UserData also returned `quick_check=ok`, `integrity_check=ok`, and zero foreign-key rows. The checker reported its absolute path, contract `ordinary-catalog-v2-33688-special3059`, and SHA-256 in the command output.

## Decision

`SoftwareOnly` removal is not justified as a CPU or total-system-load improvement by this A/B. B has normal idle behavior and a stable but larger post-operation private-memory/GPU allocation footprint. No additional optimization is adopted. The next evidence-based candidate is a quiet-session system-wide rerun, followed—only if the symptom persists—with a focused measurement of selection-time `RelatedFor`/related-row projection and the B render-memory plateau across repeated cycles. These are candidates only and were not merged or applied.
