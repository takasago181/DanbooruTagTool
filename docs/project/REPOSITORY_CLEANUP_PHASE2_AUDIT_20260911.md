# Repository Cleanup Phase 2 Audit — 2026-09-11

Status: **AUDIT / CLASSIFICATION ONLY**

No file deletion, branch deletion, move, rename, production-data write, or code-semantic change was performed in this phase.

Authority remains:
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. live Issues / current task contracts
4. `docs/project/CURRENT_DEV_TASK.md` for current core DEV Codex mirror

This document extends `REPOSITORY_CLEANUP_AUDIT_20260911.md` with a deeper root/docs/branch review.

---

## 1. Main conclusion

The repository has three different kinds of clutter and they should not be treated the same:

### A. Routing clutter — highest risk
Files that look operational/current but contain old team or workstream state.

### B. Historical evidence clutter — medium visual clutter, low deletion priority
Completed Stage/Issue evidence that is useful for audit/reproduction but sits near active material.

### C. Branch clutter — visually large, but deletion requires proof
Many completed branches are already ancestors of `main`, but branch names are still used as evidence anchors in Issues/docs. They can later be pruned only after reference preservation is proven.

The first cleanup target should therefore remain **misleading current-looking documentation**, not production code/data and not historical evidence.

---

## 2. Root-directory second pass

### KEEP_ACTIVE
- `AGENTS.md`
- `FILE_HASHES.json`
- `START_DANBOORU_TAG_TOOL.bat`
- `conftest.py`
- application/test/tool directories

Reason:
- `AGENTS.md` is still the Codex entrypoint.
- `FILE_HASHES.json` participates in protected integrity behavior and must not be moved by cleanup alone.
- runtime/test launch files are active, regardless of age.

### ARCHIVE_CANDIDATE — strong

#### `FIRST_CODEX_REQUEST.txt`
Current content already begins with `HISTORICAL — DO NOT USE FOR CURRENT TASK` and explicitly redirects Codex to `CURRENT_STATE.md` / `PERMANENT_RULES.md` / `CURRENT_DEV_TASK.md`.

Verdict: **safe conceptually as history, wrong location as root operational-looking file**.
Future action after reference audit: move to `docs/archive/codex_pack_v1_3/` or equivalent. Do not delete merely for clutter.

#### `README_最初に読む.txt`
The file itself correctly says it is a historical Codex Pack v1.3 description and points to current GitHub-first routing, but the filename strongly implies current startup authority.

Verdict: **high-priority archive-by-location candidate**.

#### `PACKAGE_MANIFEST.json`
Now explicitly marked `HISTORICAL_SNAPSHOT_DO_NOT_USE_FOR_CURRENT_ROUTING`. It still describes the 2026-09-04 v1.3 package and old Ruleset2 snapshot.

Verdict: **historical provenance file, no longer a current package manifest**. Strong archive candidate after path-reference audit.

#### `PROJECT_BOARD_SETUP.md`
Now explicitly marked `HISTORICAL / NOT PLANNED`; Issue #47 decided not to adopt GitHub Projects as an additional management authority.

Verdict: **archive candidate, not delete candidate yet**.

### KEEP_IN_PLACE_FOR_NOW

#### `README_MANAGEMENT.md`
This is still useful as a human-readable management entry layer after the team/governance correction. Because it points to the real authority files instead of replacing them, keeping one short human management readme is useful.

Verdict: **do not archive now**. Continue trimming stale duplicated details rather than removing the file.

---

## 3. Critical new finding: active `CHAT_START_PROTOCOL.md` still contains old four-team wording

`docs/project/CHAT_START_PROTOCOL.md` currently starts with:
- `常設4班（DEV / AUDIT / KNOWLEDGE / PROMPT）`
- routing text that treats AUDIT as one of the permanent teams

But current `PERMANENT_RULES.md` says:
- permanent teams = DEV / KNOWLEDGE / PROMPT only
- AUDIT = on-demand independent Gate role

This is a **real active-document contradiction**, not merely historical clutter.

Classification: `STALE_CURRENT_LOOKING / P0 CLEANUP FIX`.

Required future correction:
- change permanent-team wording to 3 teams;
- describe AUDIT as an on-demand role started for an explicit Gate;
- update examples so a future chat does not assume a permanent AUDIT workstream;
- retain the same GitHub-first restore discipline and do not weaken audit independence.

This should be corrected before any broad archive/move pass because `CHAT_START_PROTOCOL.md` is an actual startup guide.

No correction was performed in this phase because a full-file safe update should be made only from the complete latest main version, preserving all unrelated protocol details.

---

## 4. `AGENTS.md` review

### KEEP_ACTIVE
`AGENTS.md` is definitely active and must remain at root.

### Findings
1. Startup authority is sound: it explicitly reads `origin/main` first and prioritizes `CURRENT_STATE.md`, `PERMANENT_RULES.md`, and `CURRENT_DEV_TASK.md`.
2. It still contains some historical concrete examples such as `#46/#36` in the `NO_CURRENT_DEV` explanation. These examples are no longer the current route and can age badly.
3. Section `恒久仕様として読む` still lists `docs/CODEX_IMPLEMENTATION_SPEC_JA_v1.3.md`, so that v1.3 file is **not safe to archive/move yet** without first changing the active AGENTS reference and proving its still-needed invariants are represented elsewhere.
4. `docs/CHATGPT_CODEX_HANDOFF.md` is also explicitly referenced and remains an active fallback procedure.

Classification:
- `AGENTS.md`: KEEP_ACTIVE, small stale-example cleanup candidate.
- `docs/CODEX_IMPLEMENTATION_SPEC_JA_v1.3.md`: KEEP_IN_PLACE / dependency-active despite historical version label.
- `docs/CHATGPT_CODEX_HANDOFF.md`: KEEP_ACTIVE.

Important distinction: a filename containing `v1.3` is not enough to call the file dead when the active Codex protocol still imports it as a permanent specification.

---

## 5. `docs/` top-level classification

### KEEP_IN_PLACE — stable policy/schema layer
Keep these where they are unless a future architecture consolidation proves duplication:
- `ARCHITECTURE_POLICY.md`
- `AUXILIARY_TAG_ROLE_POLICY.md`
- `CORE_TAG_SET_SCHEMA.md`
- `DATASET_CANDIDATES.md`
- `EXISTING_TOOLS_POSITIONING.md`
- `FEATURE_PRIORITY.md`
- `FLOWCHARTS.md`
- `GENERATION_JAPANESE_OVERLAY_SCHEMA.md`
- `GENERATION_PROFILE_SCHEMA.md`
- `GENERATION_RECOMMENDATION_SEMANTICS_SCHEMA.md`
- `PRODUCT_GOAL_LOCK.md`
- `RAW_SOURCE_SCHEMA.md`
- `SEMANTIC_BRIDGE_SCHEMA.md`
- `SEMANTIC_SUPPORT_KNOWLEDGE_SCHEMA.md`
- `STATISTICS_POLICY.md`
- `TARGET_ENVIRONMENT.md`
- `TESTING_POLICY.md`

These are architecture/product contracts, not ordinary progress notes.

### KEEP_IN_PLACE — operational dependency
- `CHATGPT_CODEX_HANDOFF.md`
- `CODEX_IMPLEMENTATION_SPEC_JA_v1.3.md` for now, because `AGENTS.md` still explicitly requires it.

### ARCHIVE_BY_STRUCTURE LATER
Completed-stage report trees remain evidence, but may eventually move as a coherent history set after reference remapping:
- `docs/ruleset2/`
- `docs/stage8c_finalization/`
- `docs/stage8c_pilot001/`
- `docs/stage8c_test_only_correction/`
- completed parts of `docs/stage_reports/`
- completed historical reports under `docs/stage9/`

Do not move these one file at a time. A piecemeal move would break historical links and make the repository harder to audit.

---

## 6. `docs/project/` second pass

### KEEP_ACTIVE
- `CURRENT_STATE.md`
- `PERMANENT_RULES.md`
- `CURRENT_DEV_TASK.md`
- `DECISIONS.md`
- `CHAT_START_PROTOCOL.md` after correcting the stale team wording
- `WORKFLOW.md`
- `EFFICIENT_EXECUTION_RULES.md`

### ACTIVE ISSUE #30 EVIDENCE — keep until #30 is finished
The large number of dated `ISSUE30_*` files currently looks noisy, but #30 is the current core DEV and those files are direct restore/execution/audit anchors.

Therefore **do not archive them while #30 is active**.

After #30 completes, they should be reclassified as one coherent `Issue30 Phase2 historical evidence package`, not individually deleted.

### ARCHIVE_CANDIDATE
- `CONTROL_BOARD_POLICY.md`
- `CONTROL_BOARD_MIGRATION_DESIGN.md`
- `BRANCH_INVENTORY_20260910.md` once replaced by a current inventory or this cleanup audit
- `WORKSTREAMS.md` if the project decides not to maintain a live human dashboard

The first two are already self-marked superseded/not planned. Keeping them in the active `docs/project/` directory has little current operational value.

---

## 7. Branch proof audit — first concrete results

No branch was deleted.

### `codex/issue43-special-core-dictionary`
Compare result against current `main`:
- branch HEAD: `19e2650b14eed73d82cf09912fb6fbf3c2b1237c`
- merge-base with main = the branch HEAD itself
- current main is ahead; branch is behind by 0

Meaning: the branch is fully contained in current main history.

Deletion readiness:
- **technical content redundancy: PASS**
- **reference/evidence preservation: NOT YET PROVEN**

Issue #43 and freeze records still cite this exact branch/commit. Therefore do not delete yet.

### `codex/issue49-dict-promotion-latest-main`
Compare result against current `main`:
- branch HEAD: `490f5653460804c8a40cb48d093b91d5d8dd5d9c`
- merge-base with main = branch HEAD
- branch is fully contained in main history

Deletion readiness:
- **technical content redundancy: PASS**
- **reference/evidence preservation: NOT YET PROVEN**

It remains an audited production-promotion evidence anchor, so keep for now.

### Branch cleanup lesson
A branch being an ancestor of `main` proves the code is not unique, but it does **not** prove the branch name is no longer useful as an evidence locator.

Future safe-prune contract should require both:
1. branch content fully reachable from `main` or another durable ref;
2. current/open restoration/audit documentation no longer requires the branch name itself.

---

## 8. GitHub Issue clutter

Historical/duplicate Issues should generally remain closed instead of being erased.

Clear cosmetic duplicates/accidents:
- #11 / #12 / #13 -> duplicate of #10
- #19 -> duplicate of #18
- #20 -> accidental `DO NOT USE`
- #25 -> accidental placeholder

They are low priority because they do not affect runtime or current routing when closed. File/routing cleanup has higher value.

Completed audit Issues (#3, #22, #40, #45, #48 etc.) are useful evidence and should not be removed.

---

## 9. Updated priority queue

### P0 — fix active contradictions, no archive yet
1. `docs/project/CHAT_START_PROTOCOL.md` four-team wording -> current 3-team + on-demand AUDIT model.
2. review `AGENTS.md` for stale concrete issue examples and replace with generic current-workstream wording where safe.

### P1 — isolate obvious root historical pack files
After reference check, move as one unit rather than delete:
- `FIRST_CODEX_REQUEST.txt`
- `README_最初に読む.txt`
- `PACKAGE_MANIFEST.json`
- `PROJECT_BOARD_SETUP.md`

Suggested destination:
`docs/archive/codex_pack_v1_3/` and/or `docs/archive/management/`.

### P2 — archive superseded management proposals
- `CONTROL_BOARD_POLICY.md`
- `CONTROL_BOARD_MIGRATION_DESIGN.md`
- stale branch inventory
- potentially `WORKSTREAMS.md` if live dashboard maintenance is abandoned

### P3 — branch prune proof
Start with branches already proven ancestors of main, but do not delete until branch-name references are checked.

### P4 — completed Stage evidence relocation
Do only as a coherent migration with reference updates; lowest urgency.

---

## 10. Current stop point

Repository cleanup has now progressed from a broad inventory to a concrete safe-order plan.

No destructive action is authorized or performed.

Next safest action is **P0 active-document consistency repair**, especially `CHAT_START_PROTOCOL.md`, followed by a fresh branch-reference audit. Only after that should archive moves be considered.