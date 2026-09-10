# Repository Cleanup Phase 3 — Branch Proof Audit — 2026-09-11

Status: **AUDIT ONLY / NO BRANCH DELETE / NO FILE MOVE / NO PRODUCTION CHANGE**

Purpose: move from name-based cleanup guesses to evidence-based branch classification. `CURRENT_STATE.md` and live Issues remain routing authority.

## Rule used in this pass

A branch may become a deletion candidate only when all of the following are true:

1. it is not active/current routing;
2. its tip is fully contained in current `main` or its unique required evidence is durably preserved elsewhere;
3. no open task depends on the branch as a working branch;
4. branch deletion would not remove the only practical way to reproduce an unresolved audit/result;
5. production/protected data is not being touched by the cleanup itself.

Uncertainty => keep.

---

## A. Proven fully contained in current main

### `codex/issue28-e2e-verdict`

Compare result:
- branch tip is an ancestor of current main
- compare `codex/issue28-e2e-verdict -> main`: `ahead`, main ahead by 190, branch behind by 0
- therefore current main contains the branch tip/history
- Issue #28 is completed
- default-branch code search found no current file reference to the literal branch name

Classification:
**DELETE_CANDIDATE_AFTER_FINAL_REFERENCE_CHECK**

Reason:
The branch is not needed to preserve code content because its tip is already reachable from main. Before deletion, retain the Issue #28 commit SHA as the durable evidence locator.

### `codex/issue43-special-core-dictionary`

Compare result:
- branch tip `19e2650b14eed73d82cf09912fb6fbf3c2b1237c` is an ancestor of current main
- current main is ahead by 116 and behind by 0 relative to that branch tip
- Issue #43 is completed / freeze completed
- naming/freeze evidence exists on main under `docs/decisions/`, `docs/issue43/`, and `docs/project/SPECIAL_CORE_DICTIONARY_FREEZE.md`
- default-branch code search found no current file reference to the literal branch name

Classification:
**DELETE_CANDIDATE_AFTER_FINAL_REFERENCE_CHECK**

Reason:
Required implementation/evidence content is already durable on main. Keep the audited commit SHA in Issue/history even if the branch name is later removed.

### `codex/issue49-dict-promotion-latest-main`

Compare result:
- branch tip `490f5653460804c8a40cb48d093b91d5d8dd5d9c` is an ancestor of current main
- current main is ahead by 123 and behind by 0 relative to that branch tip
- #49 production-promotion evidence is durably represented on main, including `docs/issue49/**`, tests, promotion tool and production result
- default-branch code search found no current file reference to the literal branch name

Classification:
**DELETE_CANDIDATE_AFTER_FINAL_REFERENCE_CHECK**

Reason:
The branch no longer carries unique code history unavailable from main. The exact audited commit must remain recorded in Issue/history before branch deletion.

---

## B. Not safe to delete from simple ancestry evidence

### `codex/issue6-preflight-check`

Compare result:
- compare against current main is `diverged`
- current main is ahead by 186 but branch still has 9 commits not on main from the comparison base

Classification:
**KEEP_EVIDENCE / NEEDS UNIQUE-COMMIT AUDIT**

Reason:
The branch contains unique history. Age/completion of Issue #6 is not enough to prove redundancy. Do not delete until the 9 branch-only commits are individually understood and their required artifacts/evidence are proven durable elsewhere.

---

## C. Active branches — explicitly excluded from deletion review

Do not cleanup while active:

- `main`
- `codex/issue30-calibration-design`
- `knowledge/generation-corpus`
- `ui-ja/issue36-relaxed-v5-chatgpt-repair`

Any branch named by current #30 Batch 2, #36 V5, or #44 restore contracts remains protected from cleanup regardless of whether parts of it have been merged.

---

## D. Current-management consistency defect found during cleanup

`docs/project/CHAT_START_PROTOCOL.md` still contains old wording such as:
- `常設4班（DEV / AUDIT / KNOWLEDGE / PROMPT）`

This conflicts with current `PERMANENT_RULES.md`, which says:
- permanent teams = DEV / KNOWLEDGE / PROMPT only
- AUDIT = on-demand independent Gate role

Classification:
**CURRENT_DOC_FIX_REQUIRED / NOT AN ARCHIVE TARGET**

This is more important than deleting old branches because it can directly mislead a newly started chat. Fix should be semantic-preserving governance synchronization only; no product/task scope changes.

`AGENTS.md` also contains historical concrete examples (`#46/#36`) in the `NO_CURRENT_DEV` explanation. That is lower risk because `AGENTS.md` explicitly says current state comes from `origin/main`, but the examples should later be made generic to avoid future drift.

---

## E. Root historical-pack decision tightened

The following remain **ARCHIVE_CANDIDATE, not DELETE**:

- `FIRST_CODEX_REQUEST.txt`
- `README_最初に読む.txt`
- `PACKAGE_MANIFEST.json`
- `PROJECT_BOARD_SETUP.md`

Why not delete:
- they preserve provenance/history;
- they are small;
- current risk comes from location/name, not storage size;
- each can be isolated under a historical path after reference audit.

`docs/CODEX_IMPLEMENTATION_SPEC_JA_v1.3.md` is **NOT** part of that move yet because current `AGENTS.md` still lists it among documents to read as a durable implementation specification. It requires a semantic/currentness review first.

`docs/CHATGPT_CODEX_HANDOFF.md` remains **KEEP_ACTIVE** because the current GitHub-first workflow still explicitly uses it as the ZIP fallback procedure.

---

## F. Next safe cleanup steps

1. synchronize `CHAT_START_PROTOCOL.md` to the current 3-permanent-team + on-demand-AUDIT model;
2. make `AGENTS.md` historical examples generic without changing its current routing or safety contract;
3. audit literal/path references before moving the four root historical-pack files;
4. continue ancestry + reference checks for completed branches;
5. only after a separate explicit approval perform branch deletion or file moves.

No deletion or move is authorized by this document.