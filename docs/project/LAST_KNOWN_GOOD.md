# Last Known Good production baseline

Captured after Issue #210 promotion on 2026-09-27. This is a comparison/rollback snapshot, not a permanent semantic validator or fixed future row-count requirement. Machine-readable record: `LAST_KNOWN_GOOD.json`.

## Source and runtime

- Live main: `a90f5b652d4239709005d020417a236ea9d97ebb` (merged PR #212)
- Production: `C:\Codex\DanbooruTagTool-App`
- Release, self-contained `win-x64`, single-file, native libraries self-extract, trimming disabled, debug symbols/type disabled.
- Manifest schema 3; app version `1.0.0+a90f5b652d4239709005d020417a236ea9d97ebb`.
- Runtime files: 7 total, 5 managed payload files excluding UserData, 306,863,892 bytes; root DLL 0; PDB 0.
- Layout: EXE + manifest + external `Data/`, `UserData/`, and `ForgeBridge/`.

| Artifact | SHA256 |
|---|---|
| EXE | `479EEA2755E2C5707E0F04910D9A9C2EEE30A31DC175EE78ED36685B124FB64A` |
| Catalog | `5759156FF79D794DDC70DD5459AF9B80F8CB204C4527BE16FD368FF40BE9F141` |
| Runtime manifest | `E41F04158E57AE2300371B0050CBCFF337BC908F67EE0CD67D9DB3210C8EFC21` |

## Catalog and validators

- 124,895 rows: Artist 48,313; Character 35,278; Copyright 7,616; General 30,629; Special 3,059.
- SQLite integrity and quick checks: `ok`.
- Structural validator `dtt.catalog-structural-health` v2.0.0; semantic/source contract `dtt.production-source-contract` v2.0.0.
- Key owner baselines: #118 Sexual Intent v2; #132 31,003 ordinary identities; #199 346 General identities / 355 assignments; #201 intent-first scenario QA; #204 live filter refresh/fixed-row layout.

## Validation and UserData

- Release: 242 passed / 4 explicit opt-in skips when protected roots and candidate were supplied. Default suite: 227 passed / 19 skipped; see `RELEASE_TEST_SKIP_INVENTORY.json`.
- #199 performance gate passed; no search, Browse, or managed-memory blocker; retained managed memory delta 0 bytes.
- Isolated WPF launch/catalog startup and disposable UserData health passed. Installed WPF launch/title and post-promotion shape/catalog/manifest checks passed.
- ForgeBridge file hashes and Forge regression tests passed.
- Real UserData was not copied or embedded. The same two files remained byte-identical across promotion: `README.txt` 108 bytes, `user.db` 24,576 bytes. Their exact SHA256 inventory is recorded in the JSON snapshot.

## Canonical maintenance path

Use `scripts/maintenance/publish_portable_runtime.ps1` -> `smoke_candidate_runtime.ps1` -> `check_runtime_shape.ps1` / `validate_runtime_manifest.ps1` -> `promote_portable_runtime.ps1`. See `docs/maintenance/PORTABLE_RUNTIME_PIPELINE.md`. Structural, production source-integrity, and UserData validators are separate authorities.
