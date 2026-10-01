# Last Known Good deployed runtime snapshot

Captured after user-authorized PR #238 / Issue #226 production promotion on 2026-10-02 JST.

- Runtime source main: `49963dc129a1725c8a74d7f29aeb960884b67569`. Later documentation commits do not change build provenance.
- Production: `C:\Codex\DanbooruTagTool-App`.
- Clean Release self-contained win-x64, single-file, manifest schema 3; DLL/PDB 0; 13 total files including UserData/cache / 5 managed payload files.
- EXE SHA256: `A805FBBD80B735F354AB0CC2FBFE7F4B24A93436243888A6C6A1A4EAE8431FBE`.
- Catalog SHA256: `D91A68186661127F16E2AE102B4DD9F3A96EAE578B3C989A8B4F17169639FC6F`.
- Manifest SHA256: `776F9733B3DC1181117910400DB337716BD97ACDDFF2A9B9406D6CC4E6C640E9`.
- Final user.db SHA256: `4D1DF299F4E91BC29D7C8612DFF6F86C6E14F02CDDA36AF0D9A1AC704466B5A1`.
- Generation Library schema 1; 2 roots / 5 images / 4 metadata / 1 annotation; thumbnails in `UserData/Cache/GenerationThumbnails`.

Catalog remains byte-identical to #223: 124,895 entries; Character 35,278 / Copyright 7,616 / General 30,629 / Special 3,059 / Artist 48,313. Formal HOME 25,533 / reviewed fallback 7,409 / unresolved 2,336. Display-only Browse Groups 7 HOME / 64 groups / 2,467 grouped / 2,072 other-unclassified including HOLD 21. #179 overlay and #70 source unchanged.

Full Release 276 PASS / 3 opt-in SKIP / 0 FAIL; focused 35 PASS; performance 1 PASS isolated, unchanged thresholds. Actual portable EXE probe and normal Windows startup passed. Native installed visual/Library scan/thumbnail/metadata/UI filters, annotation restart, Prompt restore/Undo/Recovery, existing preset editor, real Bridge send and one successful generation, diff and missing/restore annotation passed. Recipe remains reference-only, current Forge settings used.

Entire old runtime/UserData backed up. Canonical promotion excluded UserData and passed byte identity. After explicit UI smoke, Prompt 13 items/Recovery and Presets 2 exactly equal backup; only Workspace and PromptWidth changed. No reset/recreate/missing original files; README unchanged. Library/cache added intentionally. No legacy/data movement or deletion.

Manual scan, no rename merge; WebP preview WIC-dependent. Actual JPEG/WebP UI, different PC and physical network disconnect remain unverified. No full Recipe apply/A-B/LoRA Library/Region Composer, and #228 not started.

Exact provenance/evidence: `docs/issue226/PRODUCTION_CHECKPOINT_2026-10-02.json`, `.md`, `validation/production-performance.json`, `LAST_KNOWN_GOOD.json`. Previous release remains in `docs/issue223/PRODUCTION_CHECKPOINT_2026-10-01.json`.
