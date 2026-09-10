# Repository Cleanup Phase 4 — Reference Audit — 2026-09-11

Status: **EXECUTION STARTED — ROOT ARCHIVE BATCH1 + CONTROL BOARD ARCHIVE COMPLETE**

Authority remains:
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. live GitHub Issues
4. `docs/project/CURRENT_DEV_TASK.md` for current core DEV mirror only

This phase originally checked whether cleanup candidates had live references before destructive action. After user authorization to organize the repository, the proven-safe archive moves below were executed. No production data, local protected data, active source code, current routing authority, or branch ref was removed in this phase.

## 1. Governance drift fixed during audit

### `docs/project/CHAT_START_PROTOCOL.md`
Updated to the current governance model:
- permanent teams = DEV / KNOWLEDGE / PROMPT
- AUDIT = on-demand independent Gate role, not a permanent waiting team/chat
- TEMP = temporary only
- new AUDIT instances restore exact target/Gate from GitHub and retire after recording the verdict

No Stage Gate or independent-audit requirement was weakened.

### `AGENTS.md`
Removed stale concrete lane examples from the generic `NO_CURRENT_DEV` rule.
The rule now points Codex to `CURRENT_STATE.md` + explicit Issue/branch/contract for any independent lane instead of naming historical routing examples.

No runtime/product behavior was changed.

## 2. Root historical start-pack files — archive executed

The following root files were proven to have no current default-branch dependency by exact filename and were moved into `docs/archive/codex_pack_v1_3/`:

- `FIRST_CODEX_REQUEST.txt`
- `README_最初に読む.txt`
- `PACKAGE_MANIFEST.json`
- `PROJECT_BOARD_SETUP.md`

Archive copies were created first and verified, then the root copies were removed. Historical contents remain preserved in Git history and under the archive namespace.

## 3. Control-board documents — archive executed

The following superseded management-board documents were moved out of `docs/project/` into:

`docs/archive/management/project_board/`

- `CONTROL_BOARD_POLICY.md`
- `CONTROL_BOARD_MIGRATION_DESIGN.md`

Reason:
- both are explicitly NOT PLANNED / SUPERSEDED;
- Issue #47 is the durable decision record;
- current management authority is only `CURRENT_STATE.md` + live Issues + `CURRENT_DEV_TASK.md` for current core DEV mirror;
- leaving these files in `docs/project/` made historical management proposals look more current than they are.

The archived policy cross-reference was updated to the archived migration-design path.

## 4. Branch deletion candidates — proof established, not yet deleted

The following branch tips were previously proven to be fully contained in `main` with zero branch-side commits at the time of audit:

1. `codex/issue28-e2e-verdict`
2. `codex/issue43-special-core-dictionary`
3. `codex/issue49-dict-promotion-latest-main`
4. `codex/stage9c9d-completion`
5. `docs/organize-agent-rules-no-semantic-change`
6. `docs/stage10-ab-automation-temp`
7. `codex/issue44-hf-token-gated-dispatch`

These remain candidates for one-by-one branch-ref cleanup only after an immediate final comparison against latest `main` and a check that no active restore contract depends on the branch name.

## 5. Branches that are NOT safe to delete

Examples already confirmed KEEP:
- `codex/issue6-preflight-check` — diverged with branch-side commits
- `dict-validation/quarantine` — large unique evidence history
- `codex/issue30-automation-dry-run-20260908` — unique commits remain
- `codex/issue49-dict-promotion` — unique promotion-history commits remain
- `codex/stage9b-main-integration` — unique commits remain
- `codex/stage9b-runtime-composer` — unique commits remain
- historical `management/*`, `prompt/*`, and older `ui-ja/*` branches with branch-side commits remain KEEP until separately proven redundant

Active branches remain KEEP:
- `main`
- `codex/issue30-calibration-design`
- `knowledge/generation-corpus`
- `ui-ja/issue36-relaxed-v5-chatgpt-repair`

`codex/issue44-checkpoint-sync` currently shares a HEAD with the active KNOWLEDGE branch history but remains KEEP while #44 and branch-name restore semantics may still matter.

## 6. Current active/near-term items — do not clean

Do not delete, move, or archive during repository decluttering:

- `docs/project/CURRENT_STATE.md`
- `docs/project/PERMANENT_RULES.md`
- `docs/project/CURRENT_DEV_TASK.md`
- `docs/project/DECISIONS.md`
- `docs/project/CHAT_START_PROTOCOL.md`
- `AGENTS.md`
- current #30 specs/handoffs used by `CURRENT_STATE.md`
- `danbooru_tag_tool/**`
- `tests/**`
- current production/semantic data
- active branch artifacts

## 7. Safety invariants

- no production `data/**` cleanup
- no local protected-data cleanup
- no `git clean -fdx` / `git clean -fdX`
- no history rewrite / force push
- archive first, remove active-looking copy second
- branch deletion only after latest-main recheck and only one-by-one
- uncertainty => KEEP

## Current verdict

Repository organization has started safely.

Completed:
- root historical v1.3/start-pack clutter moved to archive
- superseded GitHub Project/control-board docs moved out of active `docs/project/`
- governance-current files remain in place
- no branch deletion yet

Next cleanup action:
- final-recheck the seven fully-contained branch candidates against latest `main`;
- delete branch refs one-by-one only if each still has zero branch-side commits and no active restore dependency.
