# CURRENT DEV TASK — ISSUE #68 MIRROR

> This file routes the next DEV maintenance lane after #66 practical-v1 acceptance. Always read `CURRENT_STATE.md` first, then fetch the live Issue and latest DEV comment. The first #68 pass is inventory/report only and must stop for review before moving or deleting anything.

最終同期: 2026-09-14

## Source

- Source Issue: **#68**
- Issue title: **[MAINT][POST-V1][CLEANUP] Repository/workspace cleanup and root normalization**
- Issue state: **OPEN / NEXT ACTIVE MAINTENANCE LANE**
- Current DEV state: **INVENTORY / REPORT ONLY; STOP FOR REVIEW BEFORE MOVES OR DELETIONS**
- Completed #66 practical-v1 acceptance: DEV comment **`5662680719`**, accepted live main **`1486fc242d2eadf9ca24ed803e50ad7af7294004`**
- Issue #64 General taxonomy: accepted, integrated, and complete
- Stage10 #65: **PAUSED BY USER PRIORITY until the #68 inventory-first cleanup lane is completed, unless reprioritized by the user**

## Goal

Make the repository/workspace easier to understand and operate without weakening production data, audit provenance, recovery ability, or the accepted practical-v1 app.

## First pass — inventory only, no deletion

Before any move or deletion:
1. Inventory root files/directories and relevant ignored/untracked local-only directories.
2. Classify each item as `KEEP_ACTIVE`, `MOVE_ACTIVE`, `ARCHIVE`, `DELETE_CANDIDATE`, `PROTECTED / DO_NOT_TOUCH`, or `NEEDS_REVIEW`.
3. Find code/docs/tests/scripts that reference each move candidate.
4. Record tracked/ignored/protected-local/rebuildable/audit-provenance/user-state status.
5. Record disk-size impact for major local directories where available.
6. Return the inventory, dependency findings, proposed target tree, risks, and recommended cleanup batches; then stop for review.

## Protected boundaries

- Do not delete, regenerate, reclassify, or silently relocate protected/local source data, accepted #56/#63/#64 assets, canonical/Japanese overlay data, user `UserData`, audit provenance, or the current WPF `src/` baseline.
- Do not relocate Git/worktree metadata for cosmetic cleanup; assess stale worktrees only after confirming they contain no unique work.
- Never use `git clean -fdx` or `git clean -fdX`.
- Do not start Stage10 or cleanup execution in the inventory-only pass.

## Validation / stop

For each later user-reviewed cleanup batch, require `git status` to show only intentional local/protected items, `git diff --check` PASS, Debug/Release build and .NET tests PASS, and relevant accepted #64/#63 hash validation PASS. The first inventory pass makes no file changes beyond its reviewed report and does not authorize deletion.
