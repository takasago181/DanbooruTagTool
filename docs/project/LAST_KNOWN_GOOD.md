# Last Known Good deployed runtime snapshot

Captured after user-authorized Issue #179 promotion on 2026-10-01. Machine-readable hashes and prior rollback baseline: `LAST_KNOWN_GOOD.json`. This is a deployed operational snapshot; visual appearance was not verified because Windows capture returned a white client area on both the prior runtime and new candidates.

## Source and runtime

- Runtime source main: `a317efdc831b45b2a088fb9d4cdeb7873472253e` (PR #220/#221).
- Production: `C:\Codex\DanbooruTagTool-App`.
- Clean Release, self-contained win-x64, single-file; native extraction; no trimming or debug symbols.
- Manifest schema 3; 7 total files, 5 managed payload files, 324,466,706 bytes; DLL/PDB 0.
- Later documentation commits do not change this release's recorded build source.

| Artifact | SHA256 |
| --- | --- |
| EXE | `E14C3DAD00034C5E19EBFB57245BB609889328E1DAEC3C0127751787134511F2` |
| Catalog | `FF98CA4E952907B1A9021DA21CDB7DEE867A42DD1ABA1D47619BB901A7C462C5` |
| Manifest | `CFDE7116F32EB0DCB91CF52619FA4CBA65B133D359F741780AD9273E09B60B0A` |

## Catalog and protected state

124,895 entries: Character 35,278; Copyright 7,616; Artist 48,313; General 30,629; Special 3,059. Identities and HOME changed 0. Reviewed quality overlay changes 1,215 rows: Japanese display 221 / search 1,000, plus 221 derived Labels. Other payload changes 0. Formal HOME 25,533; additional reviewed Browse fallback 7,409; no usable HOME 2,336. Formal authority decisions changed 0; missing runtime roots 0.

UserData was excluded from managed copy and remained byte-identical across promotion and final read-only workstation startup. The saved 13-tag Prompt restored. README.txt (108 bytes) and user.db (24,576 bytes) exact hashes remain in JSON. ForgeBridge hashes are unchanged. Protected source/artifact files were not moved or deleted.

## Validation and limitation

- Python #216/#180: 121 PASS.
- Standard Windows: 236 PASS / 19 opt-in SKIP / 255 total.
- Final candidate and installed catalog independently: 252 PASS / 3 opt-in SKIP / 255 total.
- Dedicated final #199 performance: PASS; retained managed delta -128,040 bytes; all blocker flags false.
- Main CI run 36845903186: PASS.
- Publisher source contract, SQLite integrity/quick checks, manifest, shape, disposable and real UserData health, installed WPF launch/title: PASS.
- Installed saved Prompt verified through accessibility. Candidate formal/fallback Browse paths checked through accessibility and WPF tests.
- Visual UI appearance: NOT VERIFIED. White screenshot capture also affected the pre-existing runtime; later coordinate input reported geometry unavailable. No rendering configuration was changed.

Exact results: `docs/issue179/PRODUCTION_CHECKPOINT_2026-10-01.json`. Canonical deployment path: `scripts/maintenance/publish_portable_runtime.ps1` -> candidate smoke/shape -> `promote_portable_runtime.ps1`. Remaining verification is a human visual check; deployment and regression work is complete.
