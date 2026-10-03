# #256 complete — production workflow

Production source: `7f57a120bdfbfbff039e115b43851d8635029d4e`. Subsequent closeout is documentation only. [Production LKG / all hashes / rollback](PRODUCTION_LKG_2026-10-03.json).

PR #268 reviewed and merged into `b363d86d`; existing Batch4 validation reused. PR #269 completes Batch5: explicit Forge capability fetch, model/hash Apply, editable sampler/scheduler candidates, safe failed-refresh behavior, actual-executable isolated E2E gate and schema4-aware read-only health. PR #270 fixes only the E2E helper's debounced search read by reusing `RefreshResults`; no product search behavior changed. All three PRs reviewed, CI PASS, merged; main clean before publish.

Existing assets reused: Forge API capability/typed generation client and A1111 PNG fields, .NET JSON/SHA256/HTTP, Microsoft.Data.Sqlite backup/transaction, existing metadata parser, local LoRA inventory/hash, Library/Preset/Create owners. No new dependency or repeated external survey. Model identity is the exact backend hash; LoRA additionally records full local-file SHA256. This is provenance and conditions fidelity, not a guarantee of pixel-identical reproduction across runtime/device versions.

Final scope: Batch1 model identity, Batch2 restoration fidelity/unapplied conditions, Batch3 LoRA provenance, Batch4 parent Recipe + image identity/request/changed-fields, Batch5 explicit capability selection and complete executable workflow. Existing JP/EN/mixed tag discovery, authored Prompt/P-N/Undo/diagnostics, manual intent, local LoRA controls, Library favorites/ratings/notes are KEEP.

All 35 recovered checkpoints and 142 matrix rows have final dispositions in [reconciliation](FINAL_REMAINING_DISPOSITION_2026-10-03.json). Deferred: full Model Profiles/cutoff reconstruction, Comfy graphs, inline autocomplete/automated Intent/LLM/RAG, remote Civitai enrichment, XMP/fast review, reference mining/regional/training tools, batch/ranking/A-B #230, #231. These are optional extensions beyond the completed explicit local Forge workflow; no parallel semantic authority or giant lineage graph is required. Original rejected candidates remain rejected/unnecessary. Anima VAE installation is explicitly excluded by the recovered scope correction.

## Final validation

- Release source `7f57a120`: build 0 warnings/errors; relevant targeted 76 PASS. Earlier broader final targeted 128 PASS/1 SKIP retained.
- Local full regression: 421 PASS /25 SKIP /0 FAIL. The earlier candidate's E2E helper needed correction, so this final release was rebuilt/revalidated; no redundant repeated suite after this PASS.
- PR #269 final CI37122436516, PR #270 CI37123007126, final main CI37123236579 PASS. No manual flaky rerun needed.
- Canonical clean publish: 124895 accepted catalog rows; five runtime payload files, no loose DLL/PDB; production contract/manifest/shape PASS. Semantic catalog hash unchanged.
- Actual Windows normal startup PASS on published candidate and installed production. Real schema2 UserData-copy migration rehearsal PASS before production mutation.
- Published candidate and installed production each made two actual Forge requests (one parent + one explicit derivative). Japanese 青い髪 discovery → canonical blue_hair explicit add → Model/hash and LoRA → PNG → isolated Library → Recipe/Preset restart → changed Prompt/LoRA weight/Seed/Steps → explicit derivative → PNG/receipt/Library → next direct-parent restoration PASS.
- Actual pre-send POST bodies retained as sent-1/2.json. Model `f116b0c78f`, LoRA full SHA256 `ea7c78d35d465961cda9b9b99b25c1403192204712e391bcb8d6dd014bda9e67`, PNG/raw infotext/receipt/provenance/parent/changed-fields checked. Unsupported source RNG remains explicitly not sent; consent resets on reload.
- Missing/changed model or LoRA, mismatched PNG, unapplied conditions, stale capability failure and cancellation/error paths covered by targeted tests and retained Batch1–4 evidence. No silent substitution or hidden Prompt rewrite.

Evidence root: `C:/Codex/DanbooruTagTool/_local/task-artifacts/issue256-final` (tests/TRX, publish logs, candidate-release-e2e, production-e2e, migration/promotion reports; private UserData backup content stays local).

## Protected promotion / recovery

Before mutation: closed DTT; complete old production/UserData copy verified against all19 original file hashes, separate consistent SQLite schema2 backup, Forge config/ui-config copies, baseline and Foundation rollback source retained. Backup: `C:/Codex/DanbooruTagTool-Backup-pre256-20261003-ad14d45f`.

Only five runtime files copied; no UserData overwrite. Existing constructor SQLite backup + transaction migrated schema/payload version2→4. Integrity/foreign-key checks PASS; existing payload JSON byte-identical, all13 other original UserData files byte-identical. New migration backup retained. Installed E2E owns fresh isolated data outside production; production postmigration inventory remains byte-identical after E2E. Forge config.json/ui-config.json byte-identical. No research/semantic authority mutation.

Production EXE SHA256 `272F0BF2824B0D977D4DE116EEB8BDF25DFFF4F562E3CC275FD6D9FCC8184A57`; catalog SHA256 `F0BEC5AEDBBB4B1D26010EFFE582C2E0C26D33748DC19CC7C90206097697AC29`; user.db SHA256 `5232A724EEF36C9A7CE1CE4177EB08C845CB01B23C05E3799E54424873068645`.

New LKG: `C:/Codex/DanbooruTagTool-Production-LKG-20261003-7f57a120`; tag `lkg/production-issue256-20261003-7f57a120`; all20 files copied/hash-verified. Old LKG and backups retained.

Rollback: close DTT, restore old Foundation runtime source `ad14d45f` **and matching pre-migration UserData/DB together** from the backup, verify hashes/integrity, then start the old runtime. Runtime-only rollback after schema4 is unsafe. Keep additive recovery backups. No rollback was required.

#256 completion gate PASS; close with this immutable result. No active next lane. #230 can use parent Recipe/changed-fields as its foundation but #230/#231 were not started.
