# CURRENT DEV TASK — NONE ASSIGNED

最終同期: 2026-09-14

## Routing status

- **Active Codex DEV implementation Issue: none assigned.** Do not promote an unrelated open Issue into the current DEV lane.
- Issue #68, **[MAINT][POST-V1][CLEANUP] Repository/workspace cleanup and root normalization**, is complete. The tracked root is normalized at `e9dae6d82b6db9fe22afe3f123b50405883801a4`; Phase 2E was reviewed and accepted as a safe no-op. The old #64 shell checkout's local-only `benchmarks/`, `backups/`, and `_handoff/` remain in place because their consumers or protected provenance remain active.
- The next user route is Stage10 learning Issue #65. It may resume and is a practical image-generation learning lane, **not a Codex implementation task** unless the user separately assigns implementation work.

## Current WPF daily launch

The current WPF app was published under local `artifacts/current/` with its required runtime files and production `Data/catalog.db`. The local root shortcut `DanbooruTagTool.lnk` targets that WPF executable. Both are workstation-local convenience artifacts and are not tracked product files. The app uses its adjacent `UserData/user.db` for user state.

## Boundaries

- Read `CURRENT_STATE.md` first, then fetch the live Issue and latest DEV comment before any newly assigned work.
- Preserve protected/local source data, accepted #56/#63/#64 assets, audit provenance, and user `UserData`.
- Never use `git clean -fdx` or `git clean -fdX`.
- Stage10 learning is user-directed and must not be reclassified as a DEV implementation gate.
