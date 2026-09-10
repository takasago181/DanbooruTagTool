# Repository Cleanup Audit — 2026-09-11

Status: **AUDIT ONLY / NO DELETE / NO MOVE / NO RENAME EXECUTED**

Purpose: classify repository clutter before any cleanup. This file is not routing authority and does not replace `CURRENT_STATE.md`, live Issues, or `CURRENT_DEV_TASK.md`.

## Classification

- `KEEP_ACTIVE`: current runtime/source-of-truth/active work.
- `KEEP_EVIDENCE`: completed but still useful as audit, rollback, reproduction, or historical evidence.
- `ARCHIVE_CANDIDATE`: not current operation; move under a clearly historical/archive area after reference audit.
- `DELETE_CANDIDATE_AFTER_PROOF`: likely removable only after proving no unique evidence/reference remains.
- `STALE_CURRENT_LOOKING`: especially risky because it looks current but contains obsolete routing/organization.
- `VERIFY_FIRST`: cannot safely classify further without dependency/reference check.

Conservative rule: uncertainty => keep.

---

## A. Current management / routing files

### KEEP_ACTIVE
- `docs/project/CURRENT_STATE.md`
- `docs/project/PERMANENT_RULES.md`
- `docs/project/CURRENT_DEV_TASK.md`
- `docs/project/DECISIONS.md`
- `docs/project/CHAT_START_PROTOCOL.md`
- `docs/project/WORKFLOW.md`
- `AGENTS.md`

### STALE_CURRENT_LOOKING / high priority cleanup review

1. `docs/project/WORKSTREAMS.md`
   - human-facing dashboard but currently contains stale routing such as historical #46 flow and older #30/#44 sequence.
   - risk: future human/agent may treat it as current despite its non-authority disclaimer.
   - recommendation: either regenerate from current state or archive/remove the dashboard role entirely.

2. `docs/project/BRANCH_INVENTORY_20260910.md`
   - inventory itself is now stale; e.g. historical #46 branch was classified active before V5 superseded it.
   - recommendation: replace with a fresh evidence/reference-aware inventory before any branch deletion.

3. `README_MANAGEMENT.md`
   - still describes AUDIT as a permanent team and reflects an older team model.
   - recommendation: update or archive after confirming nothing treats it as a runtime/start authority.

### ARCHIVE_CANDIDATE
- `PROJECT_BOARD_SETUP.md`
- `docs/project/CONTROL_BOARD_POLICY.md`
- `docs/project/CONTROL_BOARD_MIGRATION_DESIGN.md`

Reason: Issue #47 closed the GitHub Project rollout as NOT PLANNED. Preserve history, but these should not sit near active operational guidance indefinitely.

---

## B. Root historical start-pack files

### ARCHIVE_CANDIDATE
- `FIRST_CODEX_REQUEST.txt`
- `README_最初に読む.txt`
- `PACKAGE_MANIFEST.json`
- possibly `README_MANAGEMENT.md` after replacement/update decision

Notes:
- `FIRST_CODEX_REQUEST.txt` is already clearly marked historical/do-not-use.
- `README_最初に読む.txt` is internally safe but its filename strongly implies current authority.
- `PACKAGE_MANIFEST.json` is the old `1.3-final` pack manifest and can look like current package authority from the root.

Suggested future archive area (not executed):
`docs/archive/codex_pack_v1_3/`

### VERIFY_FIRST
- `FILE_HASHES.json`
- `README_MANAGEMENT.md`

`FILE_HASHES.json` may still be part of protected integrity tests and must not be moved/removed based on age or naming alone.

---

## C. Historical Stage documentation

### KEEP_EVIDENCE, but strong archive-structure candidates

Historical completed-stage directories:
- `docs/ruleset2/`
- `docs/stage8c_finalization/`
- `docs/stage8c_pilot001/`
- `docs/stage8c_test_only_correction/`
- most of `docs/stage_reports/`
- completed reports in `docs/stage9/`

These are not junk. They preserve why Stage8/9 decisions exist, prior audit evidence, screenshots, and reproduction records.

Risk is **placement**, not existence: completed evidence is mixed with current-stage materials.

Recommended future direction:
- keep current/future active stage contracts in `docs/stages/` / relevant current locations;
- move immutable completed-stage evidence to a clearly historical path such as `docs/archive/stages/...` only after path-reference audit.

### VERIFY_FIRST
- `docs/stage9/STAGE9_PROMPT_COMPOSER_SPEC_v1.md`
- any schema/decision document still imported or directly referenced by active #30/#42/#5 contracts

Do not archive a completed-looking spec just because Stage9 is complete if current Stage10 code/contracts still cite it.

---

## D. Architecture, decisions, schemas

### KEEP_EVIDENCE / generally keep in place

- `docs/architecture/**`
- `docs/decisions/**`
- root schema/policy documents such as:
  - `docs/PRODUCT_GOAL_LOCK.md`
  - `docs/GENERATION_PROFILE_SCHEMA.md`
  - `docs/GENERATION_RECOMMENDATION_SEMANTICS_SCHEMA.md`
  - `docs/SEMANTIC_BRIDGE_SCHEMA.md`
  - `docs/SEMANTIC_SUPPORT_KNOWLEDGE_SCHEMA.md`
  - `docs/TESTING_POLICY.md`
  - `docs/STATISTICS_POLICY.md`
  - `docs/TARGET_ENVIRONMENT.md`

These may be old, but they explain stable architecture and are more valuable than ordinary progress reports. Cleanup should target stale routing/progress docs first, not architectural decisions.

### VERIFY_FIRST
- `docs/CODEX_IMPLEMENTATION_SPEC_JA_v1.3.md`
- `docs/CHATGPT_CODEX_HANDOFF.md`

Both may have historical content yet still be referenced as fallback/procedure. Classify after reference search.

---

## E. Runtime code / tests / tools

### KEEP_ACTIVE by default

Do **not** delete or archive merely because filenames contain old Stage numbers:
- `danbooru_tag_tool/**`
- `tests/**`
- `tools/**`
- `conftest.py`
- `pytest.ini`
- `requirements-dev.txt`
- `START_DANBOORU_TAG_TOOL.bat`

Old Stage-numbered modules can still be imported by the current application or regression suite. Code cleanup requires dependency/import analysis, not document-age reasoning.

### VERIFY_FIRST
- old one-shot tooling under `tools/` such as Stage5/6/7/8 smoke/report builders

Some are probably reproduction-only. They may later become archive/delete candidates, but only after code-search + test/reference checks.

---

## F. Data committed to main

### KEEP_ACTIVE / protected by default

- `data/generation/**`
- `data/semantic/**`
- `data/special2788/**`

No cleanup action should be taken on committed production/semantic data during repository decluttering unless a separate data-specific audit proves redundancy.

Historical-looking Stage8C CSVs under `data/semantic/` may still be required for audit/regression/reproducibility. Treat as protected evidence unless proven otherwise.

---

## G. Reference code

### KEEP_EVIDENCE / ARCHIVE_CANDIDATE by structure, not deletion

- `references/legacy_prototype_code/**`
- `references/trial_v0.2_code/**`

These are already correctly namespaced under `references/`, so they are low-risk clutter. No urgent cleanup needed. They are examples of how historical material should be isolated.

---

## H. GitHub Issues

### Active/currently meaningful
- #5 Prompt formal handoff (gated)
- #24 protected-data backup/restore maintenance
- #30 current core DEV / Stage10 prep
- #34 bilingual search/search-noise parent
- #36 V5 Japanese-overlay repair
- #42 reserved final product-purpose improvement
- #44 ongoing knowledge corpus

### Completed/superseded evidence — keep closed
Examples:
- #2, #3, #4, #6, #17, #18, #22, #26, #28, #32, #35, #37, #38, #39, #40, #41, #43, #45, #46, #47, #48, #49

These should generally remain because Issue history is useful evidence. Closing is enough; deleting historical Issues is not recommended.

### Clear accidental/duplicate Issues
- #11, #12, #13 — duplicates of #10
- #19 — duplicate of #18
- #20 — accidental DO NOT USE
- #25 — accidental placeholder

Recommendation: leave closed, optionally normalize labels/state reason later. No need to erase history.

---

## I. Branches — preliminary classification

### KEEP_ACTIVE
- `main`
- `codex/issue30-calibration-design`
- `knowledge/generation-corpus`
- `ui-ja/issue36-relaxed-v5-chatgpt-repair`

### KEEP_EVIDENCE until current dependent work is complete
- `dict-validation/quarantine`
- `ui-ja/japanese-overlay-quarantine`
- `ui-ja/issue36-final-agent-convergence`
- `ui-ja/issue36-machine-convergence`
- `ui-ja/issue36-r3-bulk-canary`
- `ui-ja/issue41-pilot`
- `ui-ja/r3-test-engine`
- `ui-ja/issue35-ui-only`
- `codex/issue46-orchestrator`
- `docs/stage10-ab-automation-temp`
- `prompt/audit-knowledge-reservoir-20260909`
- `prompt/current-purpose-audit-20260909`

### DELETE_CANDIDATE_AFTER_PROOF / likely merged or completed work branches
The following are strong candidates for a per-branch `compare main...branch` + reference audit. No deletion is authorized yet:
- `codex/issue6-preflight-check`
- `codex/issue28-e2e-verdict`
- `codex/issue30-automation-dry-run-20260908`
- `codex/issue43-special-core-dictionary`
- `codex/issue49-dict-promotion`
- `codex/issue49-dict-promotion-latest-main`
- `codex/stage9b-main-integration`
- `codex/stage9b-runtime-composer`
- `codex/stage9c9d-completion`
- `management/chat-start-protocol`
- `management/close-handoff-gaps`
- `management/codex-gh-issue-access`
- `management/current-dev-task-mirror`
- `management/current-state-issues`
- `management/final-governance-hardening`
- `management/proactive-chat-handoff`
- `management/setup`
- `management/stage9-final-audit-gate`
- `docs/organize-agent-rules-no-semantic-change`

### VERIFY_FIRST
- `codex/issue30-calibration-design` active, so keep.
- any branch named by an open Issue/checkpoint/restore contract must remain even if fully merged.
- branches with unique historical commits should preferably be converted to durable main-side evidence/tag/reference before deletion.

---

## J. GitHub Actions / templates

### KEEP_ACTIVE
- `.github/ISSUE_TEMPLATE/dev.yml`
- `.github/ISSUE_TEMPLATE/knowledge.yml`
- `.github/ISSUE_TEMPLATE/prompt.yml`
- `.github/ISSUE_TEMPLATE/audit.yml`

AUDIT is on-demand rather than permanent, but the audit template remains useful for future Gate-specific audit Issues.

### VERIFY_FIRST
- `.github/workflows/issue44_evaluator_coverage.yml`

Coverage was completed, but #44 is ongoing and may need reproducible reruns. Keep until #44 explicitly says the workflow is no longer useful.

---

## Highest-risk clutter findings

Priority order:

1. **Stale documents that still look current** (`WORKSTREAMS.md`, old branch inventory, `README_MANAGEMENT.md`).
2. **Root historical pack files with authoritative-looking names** (`README_最初に読む.txt`, `PACKAGE_MANIFEST.json`, `FIRST_CODEX_REQUEST.txt`).
3. **Many completed feature/management branches** that should eventually be proven redundant and pruned.
4. **Completed Stage evidence mixed with active docs**; likely better archived than deleted.
5. **Duplicate/accidental Issues** are cosmetic clutter only; they are not the main risk.

## What should NOT be done

- no bulk branch deletion
- no file deletion based on filename/age alone
- no movement of protected data
- no moving current code because it has old Stage names
- no rewrite of historical Issues
- no cleanup that changes product/runtime semantics
- no `git clean -fdx` / `git clean -fdX`

## Proposed cleanup execution order — still not authorized

Phase C1 — current-looking stale docs
1. decide whether `WORKSTREAMS.md` should be regenerated or retired;
2. refresh branch inventory using current V5/#30 state;
3. update/archive `README_MANAGEMENT.md`;
4. isolate old root start-pack documents.

Phase C2 — branch proof audit
1. for each candidate branch compare against current main;
2. search open Issues/docs for branch/commit references;
3. verify unique evidence is durable elsewhere;
4. only then mark `SAFE_TO_DELETE_BRANCH`.

Phase C3 — historical docs archive
1. build path-reference map;
2. move only immutable completed-stage evidence whose links can be updated safely;
3. keep architectural decisions/schemas in place unless clearly obsolete.

Phase C4 — one-shot tools/artifacts
1. code-search imports/references;
2. retain reproducibility-critical tools;
3. mark true dead one-shot tooling for optional deletion.

## Current audit conclusion

The repository is **not suffering from dangerous data bloat**, but it has meaningful **authority/routing clutter**. The safest cleanup target is stale current-looking documentation and fully superseded branches—not production code/data and not historical evidence itself.

No deletion, movement, branch removal, Issue closure, or production change was performed by this audit.
