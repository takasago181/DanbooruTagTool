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
- Issue #114 focused tests: `5 passed / 0 skipped / 0 failed` (including the full 12-query equivalence test and synthetic measurement)
- Issue73 / Issue74 / Issue76 / DataAndViewModel focused regressions: `36 passed / 1 skipped / 0 failed`
- `git diff --check`: PASS

The seven skipped tests are existing opt-in production/protected-catalog tests. The current workstation catalog was not rebuilt from the protected Issue #70 inputs, so this report makes no claim that the current `artifacts/current/Data/catalog.db` is the accepted 126,427-entry production catalog.

## Synthetic production-sized measurement

The performance test creates exactly 126,427 lightweight catalog entries with the target category counts: General 30,629, Special 3,059, Character 35,890, Copyright 8,536, and Artist 48,313.

| Path | Before / baseline | Current |
| --- | ---: | ---: |
| Catalog/index construction time | 783.349 ms (pre-optimization runtime index) | 509.628 ms |
| Runtime index transient allocation | 311,254,608 bytes (pre-optimization runtime index) | 235,964,400 bytes |
| Runtime index retained heap delta | not measured in the earlier run | 85,315,664 bytes |
| Pre-#114 canonical-only index build / transient / retained | 110.609 ms / 76,281,904 bytes / 24,642,808 bytes | — |
| Indexed search, four representative queries | 830.237 ms (pre-optimization indexed search) | 526.742 ms |
| Legacy full normalization + rank, four queries | 1,693.125 ms (earlier run) | 1,629.462 ms |
| Indexed Character browse | 0.279 ms (pre-optimization indexed browse) | 0.271 ms |
| Legacy Character filter scan | 2.355 ms (earlier run) | 2.188 ms |

The current transient allocation is measured after the synthetic `entries` array already exists, so it is runtime-index/search-document construction allocation only; it does not include the synthetic entry payload. The retained-heap measurement keeps both the synthetic entries and resulting `Catalog` strongly reachable across forced full GC and reports the post-build live-heap delta. Both numbers are separate from WPF container and steady-state UI measurements. The pre-#114 baseline is the old canonical-only catalog dictionary; live-heap values are process-level GC measurements and are reported without an arbitrary pass threshold.

The new and test-local pre-#114 legacy search paths returned identical full `(entry ID, rank)` sequences for all 12 required characterization queries, including aliases, JapaneseSearch, General/Special canonical duplication, substring candidates, fuzzy candidates, and `anal` false-positive suppression.

## Protected data and scope

- Original `artifacts/current/Data/catalog.db` SHA-256: `6FAB99AF6707AC49FCE44241A7F0645468F7195D2A0AF477E824E6B7F663E4FC`
- Original `artifacts/current/UserData/user.db` SHA-256: `665CD62C774F708EAC966BF646EEA1A56DD885419DB7F9FBCF5560F6DB0EFC35`
- The protected workstation catalog and user database were read-only inspected and not modified.
- Issue #70 source/results, accepted rows, translation status, canonical identity, import content, taxonomy, and database schemas were not changed.
- No WPF production-catalog click-through or real WPF container realization measurement was performed in this validation.

## Conclusion

Phase 1 runtime index behavior is test-validated on synthetic production-sized data. Production 126,427 catalog validation and practical WPF realization remain a separate workstation acceptance step.

READY FOR DEV ARCHITECTURE AUDIT / NOT MERGED
