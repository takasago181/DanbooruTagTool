# #256 Batch 2 — restoration fidelity and explicit derivative generation

Baseline main `8cb36279a05f368ea3385c8a461a1dbede10d3df`: PR #265 merged after reviewing its bounded diff/checkpoint and reusing existing tests/Forge/CI evidence. Merge-main CI PASS: https://github.com/takasago181/DanbooruTagTool/actions/runs/37111681241 . Main entry clean. Batch 1 remains undeployed.

## Selection and reuse

Use the existing 35-checkpoint reconciliation / 142-row adoption matrix; no repeated ecosystem audit. After Batch 1 authenticates the checkpoint, the next concrete gap is that PNG conditions outside the nine-field Recipe projection disappear on save/reopen. Clip skip, Hires, RNG, VAE, LoRA hashes and extension parameters can affect results while the old adapter reports only typed-field verification. Batch 2 preserves that evidence and makes derivative generation an explicit user choice, using the existing Library → Create → Preset → Forge → Library route.

REUSE: existing parser's ordered name/value records, raw infotext in Library, .NET JSON, SQLite BackupDatabase/transaction, Forge capability probe/one-POST adapter, Create snapshot, and independent Prompt workspaces. No new dependency, copied external code, semantic authority, Foundation redesign, or second state store. The matrix's pinned sd-parsers model/name/hash design remains reference only.

Inspected installed Forge upstream https://github.com/Haoming02/sd-webui-forge-classic at `97b26fb404314a11dad7cdde2706da57ea53f4f2`, `modules/processing.py` SHA256 `FD51851EE7DDBD36691F868EFEF97560C6D32BF24306A6805C484600188C3F54`. Its actual `create_infotext` emits RNG, model-specific Clip skip, modules and extension parameters. REUSE that existing envelope; do not forward arbitrary source keys as overrides. Clip skip scalar support alone would not cover this SDXL workflow (the installed writer emits it only for SD1). Full profiles/Comfy/lineage remain deferred.

## Behavior

- Imported Recipe stores all ordered source parameter names/values, including duplicates and unknown fields. Library retains the exact raw infotext as before. Preset edit/save/restart keeps source parameters while current typed values remain editable.
- Only the existing applied field names are recognized. Duplicate applied names/scheduler aliases and invalid/unprojected values remain warnings. Version/User/Time taken are informational; all other fields are conservatively unapplied.
- Library and Create display the gap. Direct Library/Preset Recipe generation refuses unapplied evidence; Create requires a visible, unchecked derivative-consent checkbox. API also rejects before any network call unless explicitly authorized by the request. Reload/restart never inherits consent; consent is session-only and absent from saved UserData.
- Accepted derivatives use the same one-request/one-image path. Unknown keys are never sent as overrides. Model hash, P/N and other requested typed fields still verify against actual PNG; mismatches retain output without retries. Success says derivative/typed-field verification, not image equivalence.
- UserData schema/payload 4 protects source evidence from Batch 1/older clients. Schema2/3 migration backs up SQLite, preserves exact existing JSON and commits version changes transactionally. Failure rolls back. Only isolated fixtures migrated; production remains Foundation/schema2.

## Validation

- Clean Release solution build: 0 warnings/errors. Initial no-restore build lacked this new worktree's Maintenance assets; restoring existing packages resolved it. No dependency changes.
- Targeted final: 78 PASS / 1 existing opt-in live test SKIP / 0 FAIL. Real Forge is independently exercised below.
- One final full regression: 386 PASS / 25 existing opt-in SKIP / 0 FAIL (39s). New cases cover unknown/extension fields, duplicate/quoted ordered evidence, malformed values, pre-network refusal, consent, typed mismatch/output retention, Library/Create/Preset/restart, schema3 backup and future-version refusal. Existing migration-failure test now covers schema2 and schema3.
- Real Forge already running: PASS. Copied prior Foundation PNG into isolated source root; preserved RNG CPU and model hash f116b0c78f. Unconsented API/network 0; Create blocked. Save/reopen keeps evidence and resets consent. Explicit derivative red ceramic teapot, seed25420261004, 8steps, Euler/Karras, CFG4.75, 512x640: one POST PASS; actual PNG typed verification/model restoration PASS; automatic isolated Library ingest and raw readback PASS; result→Create restores RNG/hash and resets consent. Image viewed. No primary-button GUI automation claim.
- Actual development WPF fixture at 900/1400 widths: PASS warning/checkbox binding, default block, explicit enable; renders inspected. This is the existing isolated executable hook, not real production data.
- Production managed5 + real UserData14 + Forge config2: all21 files byte-identical after smoke. No production promotion. Forge left running.
- Evidence retained at `C:/Codex/DanbooruTagTool/_local/task-artifacts/issue256-batch2/`: test TRX, live-result/result.json and PNG, protected snapshots, WPF renders. The full suite predates only a validation-hook scroll/render adjustment; product behavior is the same, final CI validates the committed tree.
- New worktree checkout introduced CRLF-only differences; restored only files proven equal to HEAD after CRLF normalization. No unrelated/source-content change, reset/clean, legacy worktree retirement or protected cleanup.

## Limits / rollback / stop

This Batch prevents silent loss and supports explicitly acknowledged derivatives; it does not implement the unapplied fields or promise pixel-identical regeneration. Old presets without source evidence retain behavior and cannot recover metadata already lost. A source can omit real backend settings; absence of warnings is not proof of completeness.

Rollback code by reverting this Batch commit. Future schema4 deployment rollback requires the pre-migration backup or a matching runtime before using schema3/2; current real data remains schema2, so production rollback is unaffected. Prior Foundation production LKG/tag and #245 backup remain intact.

STOP after Batch 2 PR/checks. #256 stays open; Batch 3 is ready for its next authorized selection, not started. No production apply, #230 or #231.
