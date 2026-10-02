# #245 production checkpoint — 2026-10-03

User-authorized #246 merge → clean merged-main publish → #228/#229/#232/#245 combined production promotion → real Forge generation / Library readback → protection → new LKG completed. Runtime source `b3f48c359a8473c8bbf02347487cba5d8dacf96c`; later documentation commits do not change executable provenance.

## Delivered

- PR246 merged `94bcb81e63e152067f8794ea76384b01d27b3bb8`: B-lite 作成 / タグ探索 / ライブラリ, shared P/N, working Recipe/source, Preset-independent primary Generate, LoRA quick-use, bounded small-window groups. Phase A/B/C/D evidence remains immutable.
- PR257 merged `f815c2eb46b8754c3ecf7fe5858df3baf0beaea1`, PR258 merged `b3f48c359a8473c8bbf02347487cba5d8dacf96c`: scoped Neo API-vs-PNG model spelling compatibility. Capability-declared exact title basename requires a nonempty matching hash for round-trip; PNG-derived request resolution must identify exactly one hash-declared capability. Duplicate/hashless/undeclared aliases fail closed. No fuzzy identity, Gradio or automatic retry.
- Full Release **364 PASS /4 existing SKIP /0 FAIL**; focused **112 PASS /1 existing SKIP /0 FAIL**. PR2469 SUCCESS; PR257/2585 SUCCESS each. Final tested src tree `b85bcdcc6904bbc44a384e1deebc3782bb5717ea` equals merged build. Initial unchanged timeout test failure under UI load is retained in the machine checkpoint; focused/full repeats passed.
- Clean canonical self-contained single-file win-x64 publish/manifest;5 managed files; DLL/PDB0. Actual installed EXE isolated Prompt-intelligence/LoRA/Library hooks all PASS; fixture-only scope and mock requests are explicit in reports.

## Real production smoke

Library image→「作成で使う」→current P/N +8 conditions→primary「生成」→Forge→PNG→Library, **batch_size1 / n_iter1**. UI reports `Forge: idle（生成・照合完了）` and verified metadata success. Library image7 `forge-4f573db27de8430394d9e2192c45d73c.png` readback matched all10 fields and declared model hash.

| Field | Requested / actual |
|---|---|
| Positive | blue ceramic teapot, wooden table, still life |
| Negative | text, watermark |
| Model | waiIllustriousSDXL_v170 (unique API title / declared hash f116b0c78f) |
| Seed | 24520261003 |
| Steps |8|
| Sampler / Scheduler | Euler / Karras |
| CFG |4.75|
| Width / Height |512 /640|

Real PNG viewed as a blue ceramic teapot still life. This verifies execution provenance, not image quality or knowledge truth. Requests this resume total3: first HTTP500 (stale Forge checkpoint startup fallback lacking VAE,0PNG); second1PNG retained as failed model-name round-trip; third1PNG verified. No automatic retry/fallback; original failed trials remain failures. Existing local model selection repaired after config backup; no download/install. Neo exact revision/license/reviewed functions and clean adapter provenance: [compatibility report](NEO_PRODUCTION_SMOKE_COMPATIBILITY.md).

## Protection / recovery

Production `C:\Codex\DanbooruTagTool-App`; EXE SHA256 `C69C83B365C24CBA8B870BA6A5778AC83CE28DEBED779D1D556C1A9B74768F7B`. Catalog unchanged `D91A68186661127F16E2AE102B4DD9F3A96EAE578B3C989A8B4F17169639FC6F`,124895 rows; #179/#180/#216/#223 authority unchanged. No research/legacy/data move/delete, no original dirty-checkout reset/clean/switch.

Full old runtime backup, resumed5 UserData backup, before-correction snapshots, migration backup and completed LKG folder retained locally. Copy touched only5 managed files; **all UserData pre-start byte hashes identical**. Separate real-user disposable migration probe/normal restart passed. Migration is payload1→2 with backup and transactional behavior; no user reset. After smoke, exact human-selected resumed5 items (IDs/raw/order/Recovery), original empty Negative and2 Presets restored transactionally, then normal restart verified. Private Prompt values are not published; the original old13 remain recoverable in the earlier full backup.

All original6 Library-table rows remain exact including annotations; roots2→3/images5→7/metadata4→6/parameters40→60, annotation1 unchanged. LoRA DB and all other original UserData files/thumb hashes unchanged. Both smoke PNGs retained. Final user.db hash differs intentionally because migration and UI smoke serialization; do not mistake semantic preservation for post-smoke byte identity. Final hash inventory and protected-row assertions: [machine checkpoint](PRODUCTION_CHECKPOINT_2026-10-03.json).

New complete LKG runtime/UserData copy: `C:\Codex\DanbooruTagTool\.staging-issue245-LKG-20261003`. Prior LKG archived in `validation/production/previous-LKG.json`; current snapshot is `docs/project/LAST_KNOWN_GOOD.json`.

## Limits / STOP

Native pixel capture still returns white client (previous production also had this limitation): **visual appearance NOT_VERIFIED**. Native accessibility operations, actual success/error feedback, Library metadata and WPF render/tree are verified. No product rendering override or test threshold weakening. Different-PC, physical disconnect, real JPEG/WebP, owned real LoRA generation and installed Forge-extension reinstall/restart not certified. Packaged Bridge companions updated; actual Neo extension remains separately managed. Working conditions are session-only unless saved to Preset.

STOP. #245 closeout; #225 checkpoint. Await user instruction; no #230/#231/new feature.
