# Repository Cleanup Phase 4 — Reference Audit — 2026-09-11

Status: **AUDIT / SAFE-GUARD ONLY — NO DELETE / NO MOVE / NO BRANCH DELETE**

Authority remains:
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. live GitHub Issues
4. `docs/project/CURRENT_DEV_TASK.md` for current core DEV mirror only

This phase checks whether previously identified cleanup candidates still have obvious live references on the current default branch before any destructive cleanup is considered.

## 1. Governance drift fixed during this phase

### `docs/project/CHAT_START_PROTOCOL.md`
Updated to the current governance model:
- permanent teams = DEV / KNOWLEDGE / PROMPT
- AUDIT = on-demand independent Gate role, not a permanent waiting team/chat
- TEMP = temporary only
- new AUDIT instances restore exact target/Gate from GitHub and retire after recording the verdict

No Stage Gate or independent-audit requirement was weakened.

### `AGENTS.md`
Removed stale concrete lane examples from the generic `NO_CURRENT_DEV` rule.
The rule now points Codex to `CURRENT_STATE.md` + explicit Issue/branch/contract for any independent lane instead of naming historical #46/#36 routing as an example.

No runtime/product behavior was changed.

## 2. Root historical start-pack files — reference scan

Current default-branch code search returned no direct references for the exact filenames below:

- `FIRST_CODEX_REQUEST.txt`
- `README_最初に読む.txt`
- `PACKAGE_MANIFEST.json`
- `PROJECT_BOARD_SETUP.md`

Interpretation:
- this is strong evidence that current default-branch source/docs do not depend on these exact root paths by filename;
- it is **not** by itself authorization to delete or move them because Issue comments, old commits, external/local procedures, or unindexed references may still cite them.

Current classification:

| File | Current role | Phase-4 classification |
| --- | --- | --- |
| `FIRST_CODEX_REQUEST.txt` | Stage0/1 historical Codex request; explicitly DO NOT USE | `ARCHIVE_READY_PENDING_USER_APPROVAL` |
| `README_最初に読む.txt` | v1.3 historical start-pack explanation; filename looks current | `ARCHIVE_READY_PENDING_USER_APPROVAL` |
| `PACKAGE_MANIFEST.json` | v1.3 historical package manifest; now explicitly marked historical | `ARCHIVE_READY_PENDING_USER_APPROVAL` |
| `PROJECT_BOARD_SETUP.md` | historical GitHub Project proposal; #47 NOT PLANNED | `ARCHIVE_READY_PENDING_USER_APPROVAL` |

Recommended destination remains a clearly historical namespace, e.g.:
- `docs/archive/codex_pack_v1_3/` for the first three files
- `docs/archive/management/project_board/` for Project-board material

**No move executed.**

## 3. Control-board documents

- `docs/project/CONTROL_BOARD_POLICY.md`
- `docs/project/CONTROL_BOARD_MIGRATION_DESIGN.md`

Both already state that the GitHub Project plan is NOT PLANNED / SUPERSEDED and retain value as governance history. Their problem is placement, not correctness.

Classification:
`ARCHIVE_CANDIDATE_AFTER_PATH_REFERENCE_CHECK`

No change/move executed in this phase.

## 4. Merged branch candidates — stronger evidence

Previous compare audit established:

- `codex/issue28-e2e-verdict` tip is an ancestor of current `main`.
- `codex/issue43-special-core-dictionary` tip is an ancestor of current `main`.
- `codex/issue49-dict-promotion-latest-main` tip is an ancestor of current `main`.

Phase-4 exact-name default-branch search returned no direct references to those branch names.

Therefore these three move from generic delete-candidate status to:

`BRANCH_DELETE_READY_PENDING_ISSUE_COMMENT_REFERENCE_CHECK_AND_USER_APPROVAL`

Important:
- deleting a branch ref would not delete its commits from `main` because the tips are already ancestors of `main`;
- branch deletion is still not authorized in this audit;
- Issue comments and audit/checkpoint history must still be checked for branch-name restore semantics before deletion.

## 5. Branch that is NOT safe

`codex/issue6-preflight-check` remains **KEEP_EVIDENCE / NOT DELETE READY**.

Reason from compare audit:
- it has diverged from `main`;
- branch contains 9 commits not in current main.

Age/completion is not enough to justify deletion.

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
- `knowledge/generation-corpus` while #44 remains ongoing
- `codex/issue30-calibration-design` while #30 is current core DEV
- `ui-ja/issue36-relaxed-v5-chatgpt-repair` while #36 V5 is active

## 7. Important remaining cleanup risks

1. `README_最初に読む.txt` still has a misleading current-looking filename despite safe historical contents.
2. root `PACKAGE_MANIFEST.json` still looks authoritative to tools that inspect filenames without reading status fields.
3. old Stage evidence remains mixed among active docs; archive mapping requires a path-reference map first.
4. many remote branches are still unclassified by actual ancestry/divergence.
5. Issue comments can contain restore anchors that default-branch code search cannot detect.

## 8. Next safe audit steps

Before any destructive action:

1. inspect Issue comments/checkpoints for the three branch-delete-ready candidates;
2. compare additional completed branches against current main;
3. build an exact archive move map for historical root/management files;
4. only after user approval perform moves/deletions in small reversible batches;
5. never touch local protected ignored data as part of repository cleanup.

## Phase-4 verdict

Repository authority drift has been reduced further. Four root historical files are now strong archive-ready candidates, and three fully merged branches are strong delete-ready candidates **subject to Issue-comment reference audit and explicit user approval**.

No destructive cleanup was performed.