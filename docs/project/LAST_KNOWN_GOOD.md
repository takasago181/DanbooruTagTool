# Last Known Good deployed runtime snapshot

Captured after user-authorized Issue #216 promotion on 2026-10-01. Machine-readable hashes and prior rollback baseline: `LAST_KNOWN_GOOD.json`. This is a deployed operational snapshot; visual appearance was not verified because Windows capture returned a white client area on both the prior runtime and new candidates.

## Source and runtime

- Runtime source main: `cbfab29134ed41e15c25ba24e1426c8411d65207` (PR #217/#218).
- Production: `C:\Codex\DanbooruTagTool-App`.
- Clean Release, self-contained win-x64, single-file; native extraction; no trimming or debug symbols.
- Manifest schema 3; 7 total files, 5 managed payload files, 324,577,163 bytes; DLL/PDB 0.
- Later documentation commits do not change this release's recorded build source.

| Artifact | SHA256 |
| --- | --- |
| EXE | `1CF2A2E4CA9924E9372F6CDD8FCFA8B45C47F96A48079BBAEE325BD8A0652313` |
| Catalog | `72E81FF3123FF6872F4F7136C1EE19B9BC42BF58B5DC4CB96B49120893539A8C` |
| Manifest | `83ACA3FDB3E9CFA00B1D38505EF269B9285DE213741A2072021EB2C4109E6CCF` |

## Catalog and protected state

124,895 entries: Character 35,278; Copyright 7,616; Artist 48,313; General 30,629; Special 3,059. Identities and non-HOME payloads changed 0. Formal HOME 25,533; additional reviewed Browse fallback 7,409; no usable HOME 2,336. Formal authority decisions changed 0; missing runtime roots 0.

UserData was excluded from managed copy and remained byte-identical across promotion and final read-only workstation startup. The saved 13-tag Prompt restored. README.txt (108 bytes) and user.db (24,576 bytes) exact hashes remain in JSON. ForgeBridge hashes are unchanged. Protected source/artifact files were not moved or deleted.

## Validation and limitation

- Python #216/#180: 121 PASS.
- Standard Windows: 233 PASS / 19 opt-in SKIP / 252 total.
- Final candidate and installed catalog independently: 249 PASS / 3 opt-in SKIP / 252 total.
- Dedicated final #199 performance: PASS; retained managed delta 518,392 bytes; all blocker flags false.
- Main CI run 36831518328: PASS.
- Publisher source contract, SQLite integrity/quick checks, manifest, shape, disposable and real UserData health, installed WPF launch/title: PASS.
- Installed saved Prompt verified through accessibility. Candidate formal/fallback Browse paths checked through accessibility and WPF tests.
- Visual UI appearance: NOT VERIFIED. White screenshot capture also affected the pre-existing runtime; later coordinate input reported geometry unavailable. No rendering configuration was changed.

Exact results: `docs/issue216/PRODUCTION_PROMOTION_2026-10-01.json`. Canonical deployment path: `scripts/maintenance/publish_portable_runtime.ps1` -> candidate smoke/shape -> `promote_portable_runtime.ps1`. Remaining verification is a human visual check; deployment and regression work is complete.
