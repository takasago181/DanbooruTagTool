# CURRENT DEV TASK — ISSUE #83 AGGRESSIVE LOCAL CLEANUP (COMPLETED / MERGED)

最終同期: 2026-09-15

## Routing status

- **Issue #83 — aggressive local cleanup is completed and integrated into `main`.**
- Implementation branch: `codex/issue83-aggressive-cleanup`.
- Final branch tip: `28ab39f111e438288619781f98311f3414a090ec`.
- Merged PR: `#84`.
- Main merge commit: `7ef69e6c7ffa6a76037f97226a9ed067d59c360d`.
- DEV acceptance: Issue #83 comment `5680343047`.
- No successor active DEV implementation issue is designated by this file.
- Issue #70 translation/data, #65 Stage10 learning, #44 KNOWLEDGE, and #24 safety debt remain separate lanes.

## Accepted cleanup result

Issue #83 retired obsolete/reproducible local and tracked legacy assets after current-dependency proof.

Local disk usage for the measured project-related roots changed from:

- before: `16,183,761,657` bytes
- after: `1,987,919,366` bytes
- reclaimed: `14,195,842,291` bytes (`14.196 GB` / `13.221 GiB`)

Major retired assets included:
- old 11M-post Parquet / runtime source;
- CSR/runtime index data;
- obsolete Python/Tk runtime, launcher, tools, tests and retired workflows;
- old publish/bin/obj and reproducible build scratch;
- obsolete quarantine/archive/handoff/audit/benchmark outputs;
- stale worktrees proven safe to remove.

## Preserved / HOLD boundaries

Preserved:
- current `artifacts/current/Data/catalog.db`;
- current `artifacts/current/UserData/user.db`;
- current catalog build inputs and accepted Special/General/#63/#64/#76 assets;
- active Issue #70 queue/source/results and queue manager;
- current #44/#65 data with concrete or unresolved current dependency;
- current SDK/NuGet required for local builds;
- #24 backups.

HOLD rather than guessed-away:
- `.worktrees/issue64-full-rollout-audit` because tracked modifications exist;
- remaining `.tools` SDK/NuGet state;
- #24 backups;
- small #44/#65 candidate tools without enough evidence for safe deletion.

## Validation

- full .NET: `126 passed / 6 skipped`
- Issue #76 focused: `13 passed / 1 skipped`
- Issue #70 queue: bootstrap/status PASS; 10 tests PASS; claimed `0`
- catalog: Special `3,059` (stable ID space 1..3,088, 29 gaps); General `30,629`; total `33,688`
- WPF startup: PASS (`DanbooruTagTool v1` window confirmed)
- current `user.db` hash: unchanged
- current `catalog.db` hash: unchanged
- `git diff --check`: PASS

## Completion

- Codex final checkpoint: Issue #83 comment `5680261954`.
- DEV acceptance: Issue #83 comment `5680343047`.
- Main integration: PR #84 -> `7ef69e6c7ffa6a76037f97226a9ed067d59c360d`.
- Issue #83: **COMPLETED / CLOSED**.
- No separate AUDIT lane was required.
