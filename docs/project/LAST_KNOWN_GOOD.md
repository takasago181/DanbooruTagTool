# Last Known Good deployed runtime snapshot

Captured after user-authorized PR #224 merge and Issue #223 production apply on 2026-10-01.

- Runtime source main: `bbbd6cac7368edab9d6faf096070ec77452cc49b`. Later documentation commits do not change this build provenance.
- Production: `C:\Codex\DanbooruTagTool-App`.
- Clean Release, self-contained win-x64, single-file, manifest schema 3; DLL/PDB 0; 7 total files / 5 managed payload files.
- EXE SHA256: `A65D3056E0BFDD177E1D37B1A4CD9C9FF2FD208725D1311005389E9E7027E21E`.
- Catalog SHA256: `D91A68186661127F16E2AE102B4DD9F3A96EAE578B3C989A8B4F17169639FC6F`.
- Manifest SHA256: `805FDC0EFCDC044F776F1DB0D83699C248C797192808E35BAADC912A40E7DE05`.

124,895 entries: Character 35,278 / Copyright 7,616 / General 30,629 / Special 3,059 / Artist 48,313.
Formal HOME 25,533 / reviewed fallback 7,409 / unresolved 2,336 unchanged. #179 overlay and #70 source unchanged.
Display-only Browse Groups: 7 HOME / 64 groups / 2,467 grouped / 2,072 other-unclassified; HOLD 21 is included in unclassified. No cross-HOME aggregation.

Candidate Release 260 PASS / 2 opt-in SKIP; installed Release 259 PASS / 3 opt-in SKIP (performance tested separately on candidate); Python 124 PASS. Performance Gate and PR CI all PASS. Publisher source contract, manifest, shape, SQLite and UserData health, isolated and installed launch PASS.

UserData excluded from managed copy and byte-identical after promotion and read-only startup. Saved 13-tag Prompt restored. No protected data or legacy paths moved or deleted. ForgeBridge unchanged.

Native pixel appearance remains NOT_VERIFIED due to the existing white capture / coordinate geometry limitation. Actual WPF render at 1200/1500 widths passed; different-PC verification remains NOT_VERIFIED.

Exact provenance and evidence: `docs/issue223/PRODUCTION_CHECKPOINT_2026-10-01.json`, `docs/issue223/validation/production-performance.json`, `LAST_KNOWN_GOOD.json`. Production apply is complete; reopen only for a concrete regression.
