# #276 COMPLETE — final optimization and DTT cleanup

2026-10-04. PR #277 merged. Product source / final production: `bf94b3f00617865a445182e1bd7a373ec14e83af`. This closeout is documentation only; valid tests/CI/runtime evidence is reused for identical product code. No UI redesign or next feature phase started.

## Outcome

- Search internal array iteration / multilingual predicate loops eliminate per-row enumerators and closures. Ordinary, Japanese and mixed ranking/identity/suppression/tie ordering are protected; all 17 current full-catalog ordered signatures agree.
- Personal exclusions reuse weakly held immutable match tokens; active model scope is evaluated each use. Alias/weight/raw fallback, replacements, warn/hide/block and malformed/future-version guards stay intact.
- Three atomic JSON save implementations share a small helper, retaining domain-owned validation/version checks, formats and .bak recovery. Tagger Git discovery drains both pipes and has bounded timeout. Legacy autocrlf contamination is fixed before initial checkout.
- Shared verified Recipe/Forge generation remains the canonical execution path for Create, Library derivative, Experiment and Regional. Compatibility bridge sends, regional compilation, wildcard expansion and identity/provenance retain distinct semantics. No new framework/dependency, payload change, schema migration or merged authority domain.
- Audit decisions across architecture, DB/I/O, memory/startup, failure handling, tests/scripts/dependencies and local ownership are in [audit](FINAL_OPTIMIZATION_AUDIT.md). No unused product service or major responsibility violation was proven that justified a speculative rewrite. Removed duplicate persistence and allocation-heavy execution paths; retained meaningful parity/live contracts and research replay evidence.

## Current baseline comparison

| Measurement | Before | After |
|---|---:|---:|
| Ordinary `blue_hair` median | 31.96 ms / 38,035,328 B | 24.70 ms / 5,552 B |
| Japanese `青い髪` median | 23.02 ms / 18,986,056 B | 17.60 ms / 3,424 B |
| 2,000 candidates × 256 personal rules | 229.42 ms / 559,916,408 B | 12.77 ms / 75,280 B |
| Five-launch startup median | 2.988 s | 3.011 s |
| Startup working-set median | 417.63 MB | 416.95 MB |
| EXE | 176,216,156 B | 176,220,764 B |

Startup delta +0.8% is within observed noise; no meaningful performance/memory regression. [Raw samples, allocation, load, ordered signatures and publish size](PERFORMANCE_COMPARISON.json).

## Acceptance

Clean build / final local regression **469 PASS / 26 SKIP / 0 FAIL**, run once. The 26 skips are historical opt-in checks plus the new explicit performance benchmark; actual required local services were not skipped. Targeted contracts/search PASS; maintenance 23 checks / one existing skip, workspace lifecycle three PASS. [PR CI](https://github.com/takasago181/DanbooruTagTool/actions/runs/37136968602) and [main CI at product source](https://github.com/takasago181/DanbooruTagTool/actions/runs/37137200892) PASS.

Candidate actual EXE: two Template/Experiment Forge POSTs + WD14 9,041 tags + blacklist/hints + explicit selected-tag add/Undo + Recipe/personal settings restart PASS. Separate Regional/LoRA acceptance: four real POSTs, ordinary/horizontal/vertical comparisons, request/metadata/identity/Recipe/Library restoration PASS. Installed final EXE: one ordinary Forge POST + WD14 9,058 tags + explicit add/Undo + Recipe/personal restart PASS. Isolated UserData only for E2E; generated images/receipts retained.

Regional Prompter automatically changed its own `lastrun` record during acceptance. The protection gate blocked promotion, retained the observed delta and restored the exact pre-task backup bytes before continuing. Final Forge config/ui/Regional settings hashes match the baseline. This external side effect is resolved, not a silently changed user preference.

All **16 actual UserData files**, including Library/LoRA/Experiment DB and tagger profile, have identical inventory/bytes/SHA256 before and after promotion/smoke. No new production preference file or DB migration. Read-only catalog hash unchanged, 124,895 entries. Full raw pre-promotion backup plus consistent SQLite backup/integrity/FK checks PASS.

## Cleanup and recovery

Logical C:/Codex capacity **45.3646 → 18.5962 GB**, net **26.7684 GB reclaimed**, including all newly retained recovery archives/backup/LKG. Repository **41.0994 → 12.7850 GB**. [Exact capacity/disposition](CLEANUP_RESULTS.json).

Deleted 121 superseded staging EXE/catalog files (companion UserData/research/metadata retained), retired 22 old merged DTT worktrees plus the completed #276 task, cleaned active checkout build outputs, and compacted Git with `--no-prune` / no reflog expiry (337 refs unchanged). Ten superseded top-level runtime/LKG/nonmigration backup directories were fully archived and removed. No force Git removal/push, ref/history deletion or broad ignored-data cleanup.

Every deleted file has prior path/bytes/hash/reason plus exact verified file/ZIP recovery. Local manifests and compressed exact bytes: `C:/Codex/DanbooruTagTool-Recovery-final-optimization-20261004` (3.84 GB). Original PreFoundation/pre256 migration backups, active research/unique work, Foundation .local evidence, legacy root/data and app-managed worktrees remain intact. Unrelated `sidejob` and unproven `pytest-temp` were untouched. Capacity excludes an access-denied legacy pytest backup subtree and the unrelated sidejob reparse target, consistently before/after; both were retained without ACL changes.

## Final rollback chain

1. Current final production: `C:/Codex/DanbooruTagTool-App`, source `bf94b3f0`.
2. Latest final LKG: `C:/Codex/DanbooruTagTool-Production-LKG-20261004-bf94b3f0`, tag `lkg/production-final-optimization-20261004-bf94b3f0`.
3. Immediate practical rollback: `C:/Codex/DanbooruTagTool-Production-LKG-20261004-97c4cb74`, tag `lkg/production-practical-20261004-97c4cb74`.

Keep `C:/Codex/DanbooruTagTool-Backup-pre276-20261004-bf94b3f0` for exact pre-task runtime/UserData, consistent DBs and Forge/Regional settings. PreFoundation and pre256 migration backups remain original. Older #231/other LKG and pre230/pre231/pre234235236 backups remain fully recoverable from verified full-root ZIPs. Rollback replaces only five managed runtime files; never mirror historical UserData over current UserData.

[Production complete hashes / inventory / LKG](FINAL_PRODUCTION_LKG.json). EXE SHA256 `84542ABEFF7F8BDD8A8F2D98FBBAB74941BD165CB2F1FAAC4E8E19925F8263AC`; catalog SHA256 `F0BEC5AEDBBB4B1D26010EFFE582C2E0C26D33748DC19CC7C90206097697AC29`.

Local raw TRX/samples/inventories, backup/protection/promotion records and real candidate/Regional/production E2E images/receipts: `C:/Codex/DanbooruTagTool/_local/task-artifacts/final-optimization-20261004-bf94b3f0`. Main entry is clean; completed worktree/branch disposition is recorded; branch refs are retained. No unresolved product blocker. STOP; UI/UX phase requires the next user instruction.
