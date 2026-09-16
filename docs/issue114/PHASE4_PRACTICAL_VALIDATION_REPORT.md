# Issue #114 Phase 4 — Practical Workstation Validation

Date: 2026-09-16  
Branch: `codex/issue114-phase3-wpf-performance`  
Corrected validation tip: `eb25c6b3a9258a93f8b7fd31169219b0dc048133`
Base `origin/main`: `a8d19e23483f10c4eb7c87b3a0dfa89ff24e4f41`

## Result

`READY FOR DEV PHASE 4 ACCEPTANCE / NOT MERGED`

The Phase 4 blocker from comment `5699528689` is fixed. `MainWindow` now explicitly injects `Dictionary` and `Prompt` into the two child views, and both root UserControls no longer use Window-relative child bindings. The natural-binding STA composition test and the corrected branch-tip WPF runtime both pass.

## Protected runtime and environment

The protected workstation runtime was never overwritten.

| Input | SHA-256 before | SHA-256 after |
| --- | --- | --- |
| `artifacts/current/Data/catalog.db` | `6FAB99AF6707AC49FCE44241A7F0645468F7195D2A0AF477E824E6B7F663E4FC` | `6FAB99AF6707AC49FCE44241A7F0645468F7195D2A0AF477E824E6B7F663E4FC` |
| `artifacts/current/UserData/user.db` | `665CD62C774F708EAC966BF646EEA1A56DD885419DB7F9FBCF5560F6DB0EFC35` | `665CD62C774F708EAC966BF646EEA1A56DD885419DB7F9FBCF5560F6DB0EFC35` |

Validation used an external scratch runtime at `C:\Users\takas\AppData\Local\Temp\DanbooruTagTool-Phase4-eb25c6b3` with copies of the protected inputs. The scratch `user.db` was the only writable user-state database.

Runtime: Windows x64, OS `10.0.26200`, .NET SDK `10.0.401`, MSBuild `18.9.11`, .NET runtime `10.0.12`.

## Catalog availability

The available workstation catalog contains `33,688` entries:

- General: `30,629`
- Special: `3,059`
- Character/Copyright/Artist: absent from this workstation catalog

The accepted #70 production catalog size `126,427` was unavailable and was not rebuilt. No 126,427-entry WPF workstation claim is made.

## Release startup and process health

`dotnet publish --configuration Release --runtime win-x64 --self-contained false` passed from corrected tip `eb25c6b3...`. The published `DanbooruTagTool.exe` was launched three times from scratch:

| Run | Window ready | Startup | CPU time at sample | Working set | Private bytes | Responding |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | yes | 1,858.2 ms | 1,750.0 ms | 229.7 MB | 168.3 MB | yes |
| 2 | yes | 1,723.3 ms | 1,984.4 ms | 230.9 MB | 168.4 MB | yes |
| 3 | yes | 1,452.0 ms | 1,500.0 ms | 228.4 MB | 169.4 MB | yes |

No startup exception or unresponsive window was observed.

## Natural-binding WPF measurement

The STA harness created the real `MainWindow` and used only the production XAML bindings; it did not assign or override either child view's `DataContext`.

- `DictionaryWorkspace.DataContext == vm.Dictionary`: PASS
- `PromptEditor.DataContext == vm.Prompt`: PASS
- Dictionary ListBox items: `28,222` rows, matching `DictionaryRows`
- WPF `VirtualizingStackPanel.IsVirtualizing`: `True`
- virtualization mode: `Recycling`
- `ScrollViewer.CanContentScroll`: `True`
- realized `ListBoxItem` containers initially: `6`
- realized containers after scrolling: `7`
- two-column projection: `14,111` rows
- one-column projection: `28,222` rows
- selected EntryViewModel identity across 2→1 column change: preserved

This corrected result replaces the previous measurement-only result that used a temporary DataContext assignment.

## Browse, search, Prompt, and persistence smoke

With natural bindings and the available catalog:

- General browse source: `30,629`; displayed eligible rows: `28,222`
- Special catalog population: `3,059`
- Search counts: `blue_hair=3`, `青い髪=2`, `hair=616`, `青い hair=3`, `anal=29`
- Prompt add/remove for a real General result: PASS
- Query followed by `RefreshResults()`: scratch `user.db` hash unchanged
- Prompt and Dictionary child bindings: PASS
- Character/Copyright/Artist browse: unavailable because those identities are absent from the protected catalog

The Windows UI helper exposed no native app surface, so live mouse/keyboard injection was unavailable. Existing focused keyboard mapping tests remain PASS; this run does not claim live key-by-key acceptance. Card click was not injected live, but the existing `ResolveCardEntry` characterization and natural ListBox composition passed.

No old-main comparison was run. The corrected branch is validated against the same available catalog; a separate baseline run was not necessary to establish the blocker fix and would not be safe to infer for the unavailable 126,427 catalog.

## Residual Phase 4 measurement limits

These accepted follow-up candidates were not changed:

1. `Results` still eagerly creates the current `EntryViewModel` set.
2. The existing `RefreshCommands()` full-refresh path remains.
3. `RenderOptions.ProcessRenderMode = SoftwareOnly` remains unchanged.
4. Search remains the accepted precomputed-document/O(N) Phase 1 design.

## Integrity and scope

- `origin/main`: `a8d19e23483f10c4eb7c87b3a0dfa89ff24e4f41`, unchanged.
- Issue #70 data, translation status, source/result identity, review data: untouched.
- Taxonomy and canonical identity: untouched.
- `catalog.db` and `user.db` schemas: untouched.
- Original `artifacts/current` hashes: unchanged after validation.
- `git diff --check`: PASS.
- Working tree: clean after the documentation checkpoint commit.
- Main was not merged to or pushed to. Issue #114 and #113 remain open.

`READY FOR DEV PHASE 4 ACCEPTANCE / NOT MERGED`
