# Issue #36 Production Promotion Handoff

## Purpose
This handoff starts the production-promotion phase after the independent UI-JA V5 promotion audit returned `PROMOTION_AUDIT_PASS`.

The promotion worker must apply the audited V5 Japanese overlay to production safely and deterministically. This is an implementation/promotion task, not another translation campaign and not another semantic audit.

## Authority / prerequisites
Read in this order:
1. live `main` -> `docs/project/CURRENT_STATE.md`
2. live `main` -> `docs/project/PERMANENT_RULES.md`
3. Issue #36 latest comments
4. Independent audit checkpoint comment `5633982018`
5. `translation_quarantine/orchestration/issue36_relaxed_v5_chatgpt_repair/INDEPENDENT_PROMOTION_AUDIT_HANDOFF.md`
6. this file
7. live `ui-ja/issue36-relaxed-v5-chatgpt-repair` HEAD
8. `progress.json`
9. `materialized/materialization_report.json`
10. `materialized/language_sanity_report.json`
11. `materialized/final_translation_table_v5.csv`

At handoff creation time, the audited repair branch HEAD was `ea8762c4b351e9d0fd939687b2aae6617c852d18` and Issue #36 independent audit verdict was `PROMOTION_AUDIT_PASS`. Re-resolve all live refs before acting; do not trust these values if the branch or Issue moved.

## Core rule
Do **not** merge the quarantine/repair branch wholesale into `main` as the production mechanism.

Production implementation must start from the latest live `main` on a dedicated promotion feature branch/worktree. The audited V5 artifact is source evidence/input only.

If project routing requires a dedicated DEV Issue and `CURRENT_DEV_TASK.md` / `CURRENT_STATE.md` synchronization before Codex/local implementation, perform that management routing first according to `PERMANENT_RULES.md`. Do not bypass routing because the audit already passed.

## Intended production target
The historical #36 contract identifies production Japanese overlay as:
- `data/runtime/japanese_overlay.json`

This path is local protected data in normal project operation. Confirm the actual current runtime path/format from live project state before writing. Do not assume Git tracking status, schema, or generator from chat memory.

If the current project uses a deterministic generator/materializer to produce the runtime overlay, use it. Prefer deterministic transformation over manual row-by-row editing.

## Speed principle
Do not re-read all 30,629 translations and do not repeat the completed independent semantic audit.

The independent audit already passed. Promotion work should focus on:
- source artifact identity
- exact row/canonical preservation
- deterministic conversion/mapping
- protected-data safety
- write atomicity
- post-write validation
- real Windows UI acceptance

Only return to semantic review if post-write validation reveals a concrete mismatch.

## Pre-write gates
Before touching production:
1. resolve live `main` HEAD and live repair-branch HEAD;
2. confirm Issue #36 still contains `PROMOTION_AUDIT_PASS` and no newer HOLD/FAIL/superseding checkpoint;
3. confirm audited V5 artifact has not changed since the audit, or if it changed, STOP and require a new independent audit;
4. confirm the target runtime overlay schema/path and the production write mechanism;
5. record pre-write hash/size/row-or-entry count of every protected production file to be touched;
6. create a rollback copy or otherwise prove reversible restoration before write;
7. verify the audited final table is 30,629 rows and matches the audited materialization report;
8. verify canonical identity/order and non-display preservation contract from the audited reports;
9. verify no unrelated #32/#34/#35/Stage10 data or code is part of the planned write.

If any pre-write gate fails, STOP with `HOLD_PRODUCTION_PROMOTION` and do not partially write.

## Promotion implementation
Apply only the audited V5 Japanese overlay payload required for production UI/search support.

Rules:
- preserve canonical English identity exactly;
- do not alter Prompt syntax or generation metadata;
- do not alter recommendation scoring/order;
- do not alter semantic-support data;
- do not alter #32 dictionary verdict/data;
- do not implement Issue #34 search-ranking/fuzzy fixes in this promotion;
- do not change #35 UI code unless an existing deterministic production loader requires a strictly necessary compatibility fix, and if so STOP and report instead of silently expanding scope;
- no Stage10 production A/B work;
- no manual cleanup of proper names/acronyms/ASCII labels merely for appearance.

Where practical, write atomically: materialize to a temporary file, validate it fully, then replace the production file only after validation succeeds.

## Post-write deterministic checks
After production write, verify at minimum:
- production overlay loads/parses successfully;
- expected canonical universe/count matches the production contract;
- no duplicate canonical keys;
- all expected display values are non-empty where required;
- canonical identity/order mapping is preserved where order exists;
- audited V5 -> production mapping is exact for intended promoted fields;
- no unrelated production fields changed;
- pre/post diff is explainable entirely by the audited V5 overlay promotion;
- rollback artifact remains available until final acceptance;
- project integrity/tests relevant to Japanese overlay pass;
- `git diff --check` passes for any tracked promotion scripts/reports/management changes.

Record machine-readable before/after hashes and a concise applied-diff summary. Do not copy protected raw datasets into GitHub.

## Real Windows UI acceptance
After deterministic checks pass, perform a focused real Windows UI acceptance using the actual application/runtime data.

Do not inspect 30,629 labels manually. Check a representative set including:
- ordinary Japanese labels;
- proper nouns / ASCII-intentional labels;
- one or more recent cross-shard repaired rows;
- adult/relation/action examples;
- product/weapon/vehicle or other named-entity examples;
- Japanese search/display behavior where the overlay itself is responsible.

Confirm:
- Japanese labels render without corruption/tofu/encoding issues;
- canonical English identity remains intact underneath;
- app startup/load is normal;
- Japanese display/search data is actually the promoted version;
- no obvious runtime regression caused by the promotion.

Issue #34 search ranking noise such as substring/fuzzy ranking is outside this acceptance unless the promotion itself broke previously working behavior.

## Durable evidence
Create/commit only non-protected evidence needed for review, for example:
- promotion manifest / source SHA references;
- pre/post protected-file hashes and counts;
- exact transformation/mapping report;
- test result summary;
- rollback instructions;
- focused UI acceptance report.

Do not commit the user's protected local runtime datasets solely for audit convenience.

## Stop point / post-write audit
After the production write and focused UI acceptance are complete, do **not** immediately declare the project fully closed if project rules require a separate post-write audit.

Preferred completion verdict from the implementation/promotion worker:
- `READY_FOR_POST_WRITE_AUDIT`
- `HOLD_PRODUCTION_PROMOTION`

A separate fresh post-write auditor should verify the actual promoted state before any final main merge/Issue closure when such a merge is relevant.

Only after post-write audit PASS should management:
- finalize/merge any tracked promotion branch changes as appropriate;
- update `CURRENT_STATE.md` to mark UI-JA #36 completed/promoted;
- close Issue #36 as completed;
- unblock downstream #42 subject to #34 separation/completion policy.

## Important boundaries
- Quarantine artifacts remain evidence; do not rewrite historical V4/V5 results during promotion.
- Never use `git clean -fdx` / `git clean -fdX` around protected local data.
- No unrelated cleanup/refactor during promotion.
- If the production artifact changed concurrently, fail closed and reconcile before writing.
