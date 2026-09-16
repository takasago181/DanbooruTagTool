# Issue #114 Phase 1 validation report

Date: 2026-09-16
Branch: `codex/issue114-runtime-index-phase1`
Base live-main: `a8d19e23483f10c4eb7c87b3a0dfa89ff24e4f41`

## Environment

- Windows x64
- .NET SDK `10.0.401`
- .NET runtime `10.0.12`
- Release configuration
- Test execution was limited to one MSBuild node (`-m:1`) for reproducible output.

## Build and tests

- Release build: PASS, 0 warnings / 0 errors
- Full .NET tests: `141 passed / 7 skipped / 0 failed` (`148 total`)
- Issue #114 focused tests: `12 passed / 0 skipped / 0 failed`
- Issue73 / Issue74 / Issue76 / DataAndViewModel focused regressions: `36 passed / 1 skipped / 0 failed`
- `git diff --check`: PASS

The seven skipped tests are existing opt-in production/protected-catalog tests. The current workstation catalog was not rebuilt from the protected Issue #70 inputs, so this report makes no claim that the current `artifacts/current/Data/catalog.db` is the accepted 126,427-entry production catalog.

## Synthetic production-sized measurement

The performance test creates exactly 126,427 lightweight catalog entries with the target category counts: General 30,629, Special 3,059, Character 35,890, Copyright 8,536, and Artist 48,313.

| Path | Measurement |
| --- | ---: |
| One-time `RuntimeCatalogIndex` construction | 783.349 ms |
| Index construction allocations | 311,254,608 bytes |
| Indexed search, four representative queries | 830.237 ms |
| Legacy full-entry normalization + rank, four queries | 1,693.125 ms |
| Indexed Character browse | 0.279 ms |
| Legacy Character filter scan | 2.355 ms |

The new and legacy search paths returned identical `(entry ID, rank)` sequences for all four synthetic queries. The allocation number includes the synthetic entry payload and all one-time immutable index/search-document structures; it is not a WPF container or steady-state heap measurement.

## Protected data and scope

- Original `artifacts/current/Data/catalog.db` SHA-256: `6FAB99AF6707AC49FCE44241A7F0645468F7195D2A0AF477E824E6B7F663E4FC`
- Original `artifacts/current/UserData/user.db` SHA-256: `665CD62C774F708EAC966BF646EEA1A56DD885419DB7F9FBCF5560F6DB0EFC35`
- The protected workstation catalog and user database were read-only inspected and not modified.
- Issue #70 source/results, accepted rows, translation status, canonical identity, import content, taxonomy, and database schemas were not changed.
- No WPF production-catalog click-through or real WPF container realization measurement was performed in this validation.

## Conclusion

Phase 1 runtime index behavior is test-validated on synthetic production-sized data. Production 126,427 catalog validation and practical WPF realization remain a separate workstation acceptance step.

READY FOR DEV ARCHITECTURE AUDIT / NOT MERGED
