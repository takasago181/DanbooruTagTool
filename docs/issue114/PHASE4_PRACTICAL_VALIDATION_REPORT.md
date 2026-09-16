# Issue #114 Phase 4 — Practical Workstation Validation

Date: 2026-09-16  
Branch: `codex/issue114-phase3-wpf-performance`  
Validated branch tip: `a20cc61549c68ab779b1322531946df9bb098a65`  
Base `origin/main`: `a8d19e23483f10c4eb7c87b3a0dfa89ff24e4f41`

## Result

`PERFORMANCE FOLLOW-UP REQUIRED / NOT MERGED`

The branch-tip WPF executable starts successfully, and a measurement-only STA harness confirms that the Dictionary ListBox uses WPF virtualization. However, the real branch-tip `DictionaryWorkspaceView` has a binding blocker: its root binding is `Path=Dictionary` relative to the `Window`, while `MainWindow` exposes no `Dictionary` property. The live view therefore has `DataContext=null` and no Dictionary ListBox items. The harness assigned the expected child ViewModel only for measuring the virtualization implementation; those measurements are not an end-to-end UI acceptance result.

## Protected runtime preflight

The protected workstation runtime was not overwritten.

| Input | SHA-256 before | SHA-256 after |
| --- | --- | --- |
| `artifacts/current/Data/catalog.db` | `6FAB99AF6707AC49FCE44241A7F0645468F7195D2A0AF477E824E6B7F663E4FC` | `6FAB99AF6707AC49FCE44241A7F0645468F7195D2A0AF477E824E6B7F663E4FC` |
| `artifacts/current/UserData/user.db` | `665CD62C774F708EAC966BF646EEA1A56DD885419DB7F9FBCF5560F6DB0EFC35` | `665CD62C774F708EAC966BF646EEA1A56DD885419DB7F9FBCF5560F6DB0EFC35` |

The test runtime was published to `C:\Users\takas\AppData\Local\Temp\DanbooruTagTool-Phase4-a20cc615` with copies of those two inputs. The original `artifacts/current` files were not changed. The scratch `user.db` was the only writable user-state database used by the validation.

Runtime: Windows x64, OS `10.0.26200`, .NET SDK `10.0.401`, MSBuild `18.9.11`, .NET runtime `10.0.12`.

## Catalog availability

The protected workstation catalog contains `33,688` entries:

- General: `30,629`
- Special: `3,059`
- Character: unavailable (`0` in this catalog)
- Copyright: unavailable (`0` in this catalog)
- Artist: unavailable (`0` in this catalog)

The accepted #70 production catalog size `126,427` was not available and was not rebuilt. No 126,427-entry WPF workstation claim is made.

## Release startup and process health

`dotnet publish ... --configuration Release --runtime win-x64 --self-contained false` passed from the validated branch tip. The published `DanbooruTagTool.exe` was launched three times from scratch:

| Run | Window ready | Startup to main window | CPU time at sample | Working set | Private bytes | Responding |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | yes | 1,518.3 ms | 1,500.0 ms | 227.0 MB | 166.8 MB | yes |
| 2 | yes | 1,320.1 ms | 1,328.1 ms | 227.8 MB | 167.7 MB | yes |
| 3 | yes | 1,328.2 ms | 1,343.8 ms | 226.6 MB | 166.8 MB | yes |

No startup exception or unresponsive window was observed in these process-level runs.

## WPF virtualization measurement

The STA harness created the real `MainWindow`, `DictionaryWorkspaceView`, `ListBox`, templates, and layout. Before measurement it observed the production binding blocker (`DictionaryWorkspaceView.DataContext=null`). It then explicitly assigned `vm.Dictionary` to the view only to inspect the already-built virtualization path.

With General browse results (`30,629` entries, `28,222` result rows after the current accepted General browse eligibility), the harness measured:

- WPF `VirtualizingStackPanel.IsVirtualizing`: `True`
- virtualization mode: `Recycling`
- `ScrollViewer.CanContentScroll`: `True`
- WPF layout/startup sample: `250.7 ms`
- realized `ListBoxItem` containers initially: `6`
- realized containers after scrolling: `7`
- two-column projection: `14,111` rows
- one-column projection: `28,222` rows
- selected EntryViewModel identity preserved across column changes: `yes`

This is strong evidence that the intended virtualization structure is active once the view is correctly wired, but it is not a pass for the current production UI because of the unresolved DataContext binding.

## Browse, search, Prompt, and persistence smoke

The same measurement-only wiring exercised the ViewModel workflow against the current workstation catalog:

- General source/category population: `30,629`
- Special source/category population: `3,059`
- Search result counts: `blue_hair=3`, `青い髪=2`, `hair=616`, `青い hair=3`, `anal=29`
- Prompt add/remove for a real General result: pass
- Query setter followed by `RefreshResults()`: scratch `user.db` hash unchanged
- Character/Copyright/Artist: unavailable in the current catalog, so no claim is made for those categories

Live mouse/keyboard typing and click automation was unavailable on this workstation because the Windows UI helper exposed no native app surface. Existing focused keyboard tests remain the evidence for the key mapping; this Phase 4 run does not claim live keyboard acceptance. The production Dictionary view binding blocker also prevents an honest end-to-end click/scroll/category acceptance result.

No old-main comparison was run: a safe baseline comparison would not be meaningful while the branch-tip Dictionary view is not bound to its child ViewModel.

## Residual risks observed during validation

The following previously noted concerns remain measurement candidates and were not changed in Phase 4:

1. `Results` still creates the current `EntryViewModel` set eagerly.
2. The existing `RefreshCommands()` full-refresh path remains.
3. `RenderOptions.ProcessRenderMode = SoftwareOnly` remains unchanged.
4. Search remains the accepted Phase 1 precomputed-document/O(N) scan design.

The concrete newly observed blocker is the Dictionary view binding at `src/DanbooruTagTool.App/Views/DictionaryWorkspaceView.xaml:4`.

## Integrity and scope

- `origin/main` remains `a8d19e23483f10c4eb7c87b3a0dfa89ff24e4f41`.
- Issue #70 result data, translation status, source/result identity, and review data were untouched.
- Taxonomy and canonical identity were untouched.
- `catalog.db` and `user.db` schemas were untouched.
- `SoftwareOnly` was not changed.
- No Phase 4 production code change was made; the only branch addition is this validation report.
- `git diff --check`: PASS.
- Working tree: clean after the documentation checkpoint commit.

`PERFORMANCE FOLLOW-UP REQUIRED / NOT MERGED`
