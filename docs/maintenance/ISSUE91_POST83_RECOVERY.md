# Issue #91 post-#83 recovery record

This document records the structural maintenance evidence collected for Issue #91. It does not change product behavior, canonical identity, taxonomy, Prompt behavior, or Issue #70 queue semantics.

## Phase 1 — backup / restore

Fresh local snapshot created on 2026-09-15 at the workspace:

`backups/issue91-post83-20260915-2235/`

The generated `backup_manifest.json` contains 787 file entries, 351,557,886 bytes, and per-file SHA-256 values. The manifest SHA-256 at creation was `1BBD6CDBDA6F3E7B0C264E906AC4FC9628CBFE90BA3B6AA5D201FD505364BEE2`.

Covered classes:

| Class | Current examples | Recovery treatment |
| --- | --- | --- |
| GitHub-authoritative / re-clonable | tracked `src/`, `docs/`, scripts, accepted #64/#76 assets | restore from live main / GitHub |
| Deterministic rebuildable | `artifacts/current/Data/catalog.db`, WPF publish files | rebuild with the explicit catalog build and runtime refresh script |
| Exact-source reacquirable | `data/source/danbooru-2026-09-02.csv`, retained `data/derived/` inputs | reacquire exact source where available; verify recorded hashes |
| Local-only current state | `artifacts/current/UserData/user.db`, active #70 queue/source/results | restore from the local snapshot; never overwrite good state during validation |
| Active WIP / knowledge evidence | `docs/issue70/`, current `data/generation/`, `data/semantic/`, `data/special2788/` | preserve and restore as a unit; do not infer deletion from `.gitignore` |

The convenience copy includes `artifacts/current/`, but `catalog.db` and the generated WPF runtime are not classified as irreplaceable. The production DB hashes captured in the snapshot are:

- `Data/catalog.db`: 33,751,040 bytes, `ACFDA34005E8E3BDD3E915207E1CC278FAB55D26736F6204769FA00073A96410`
- `UserData/user.db`: 24,576 bytes, `F41CCE92BF0E313F2FAEF9C9948E7E8B4C65B7D51AA6658B6627AF460D2EACDF`

Representative restore was copied to a separate disposable Temp directory. Read-only SQLite `quick_check` and `integrity_check` returned `ok` for both restored DBs; the restored overlay JSON and #70 `queue_state.json` parsed successfully. The Temp directory was removed by exact path after the check. No production DB, UserData, accepted result, or queue file was overwritten.

Restore procedure:

1. Restore tracked files from live `origin/main` first.
2. Restore `data/`, `docs/issue70/`, and `artifacts/current/` from the snapshot using the manifest as the byte-level check.
3. Keep `artifacts/current/Data/` and `artifacts/current/UserData/` in place while rebuilding runtime files.
4. Run `scripts/maintenance/check_local_health.ps1` and compare the DB hashes before accepting the restored state.
5. Use the explicit `DanbooruTagTool.exe --build-catalog <repo> <repo> <isolated-output>` command for a new catalog; never use the production `Data/catalog.db` as the test output.

`LIMITATION`: the snapshot is on the same physical disk as the workspace and therefore does not protect against disk loss. It is still useful for accidental deletion, replacement, and local restore verification.

## Phase 2 — retained #64 worktree

Worktree: `.worktrees/issue64-full-rollout-audit` on branch `codex/issue64-bounded-rework`, HEAD `7e10185a311ae8f0239cad0eb1bc879f7c69a2da`.

The three files reported by #86 were the only tracked status entries. Their working-tree bytes matched their worktree HEAD blobs exactly:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `batch003_rows01301-02300_ledger.csv.xz` | 12,820 | `C21D4DEAB36C89FFA83C07D006D7682A0EC0B43B9BACB40FB83879636CE63888` |
| `batch024_rows18401-19400_ledger.csv.xz` | 10,288 | `98934F28C46AF8F4D8FA6095294A8FDB497BE53491E1C076FE521FD4DAF5410D` |
| `batch030_rows24401-25400_ledger.csv.xz` | 9,976 | `FE288F0C59A339CBE8F6E0D711C9AAC7FEDD95E89F0A8B328DAF590E0DCF1007` |

Each decompresses to 1,000 rows. All 3,000 canonical identities are present in the live-main accepted `docs/issue64/production_candidate/effective_sidecar.csv`. Live main retains the accepted 30,629-row sidecar, taxonomy, manifest, and hashes; it does not contain these old full-rollout ledger paths. The ledger-only review/reason fields are not part of the accepted production contract and are not needed by the current catalog importer.

Disposition: duplicate/superseded accepted evidence, safe to retire. The stale worktree was restored to its own HEAD for status resolution and then removed. The remote #64 branch was not deleted and no accepted #64 bytes were changed.

## Guardrails

Never run `git clean -fdx` or `git clean -fdX`. Do not broad-delete ignored data. Before any future cleanup, identify an exact path, classify it, hash it where practical, and prove its current dependency or supersession.
