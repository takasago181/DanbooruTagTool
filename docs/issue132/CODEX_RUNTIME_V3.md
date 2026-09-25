# Issue #132 — Codex Runtime V3

Status: ACTIVE EXECUTION GUIDE

This is the only prose execution guide Codex needs for Issue #132. Old Luna/Automation cards, checkpoint promotion instructions, write-request protocols and old handoff prose are historical compatibility material, not runtime authority.

## Read order

1. `docs/issue132/parallel/RUNTIME_AUTHORITY.json`
2. this file
3. semantic contract named by authority
4. `docs/issue132/parallel/CODEX_QA_STATE.json`
5. exact neutral shard(s) needed for the lane/range

Do not read old Worker/Coordinator/Repair cards unless repairing historical data.

## Roles

Use four independent Codex worktrees:
- L1: Lane 1 forward review
- L2: Lane 2 forward review
- L3: Lane 3 forward review
- REPAIR: only concrete historical invalidity, CI/validator defects, or targeted semantic repairs requested by ChatGPT QA

All publish to `research/taxonomy-usability-audit` by normal fetch/rebase/revalidate/fast-forward push. Never force-push. Never touch main or production.

## Forward review

Current starting points are recovered from validated repository truth, not chat history.

For each lane:
1. run the flat validator and use the reported forward frontier; baseline HOLD/lint debt does not change it;
2. read the one 300-row neutral shard containing the next identities;
3. inspect every identity individually;
4. classify obvious meaning directly as CHECKED;
5. research only material ambiguity; unresolved after bounded useful research becomes RESEARCHED + SEMANTIC_UNRESOLVED;
6. prepare one local decision JSON for up to 100 consecutive lane-local identities;
7. run `python scripts/issue132/codex_stage_window.py --decisions <file>`;
8. run `python scripts/issue132/validate_flat_pass_a.py`;
9. commit the canonical staging window, rebase current canonical branch, rerun the validator, and fast-forward push;
10. continue until the current ChatGPT QA watermark is reached.

The decision JSON is local scratch input and is not committed. The generated canonical staging JSON is committed.

## Why windows are 100 rows

The old 25-row write-request/materializer design existed to limit ChatGPT Automation write-policy failures. Codex writes in a local worktree, so new forward work uses up to 100 rows per canonical window. This cuts file count, commits and CI churn without changing semantic granularity.

## Decision JSON

Schema: `issue132-codex-decision-window-v1`

Top-level:
- schema_version
- lane
- lane_local_start
- lane_local_end
- rows
- holds

Each semantic row:
- lane_local_index
- discovery_mode
- routes: list of {id,strength}, max 3
- local_refinement_ids
- body_site_ids
- theme_ids
- route_vocabulary_gap
- review_depth
- evidence_urls
- decision_reason_codes

Do not include identity text, identity hash or review_seq; the staging tool binds these from frozen neutral input.

Holds are exceptional and contain:
- lane_local_index
- reason_code
- research_attempt_codes

Do not use a hold for ordinary semantic uncertainty. Use SEMANTIC_UNRESOLVED after completed bounded research.

## QA watermarks

Codex may not generate a new staging window beyond its lane's `allowed_forward_end_by_lane` in `CODEX_QA_STATE.json`.

Initial calibration:
- Lane 1 through 1225
- Lane 2 through 1325
- Lane 3 through 1300

ChatGPT reviews all first 100 new rows per lane. After calibration, ChatGPT advances each lane in at most 500-row QA intervals.

Steady-state QA:
- all RESEARCHED
- all MIXED
- all SEMANTIC_UNRESOLVED
- all vocabulary gaps
- all multi-route/SUPPORTING rows
- all body/theme facets
- sibling/family consistency scan
- deterministic stratified ordinary CHECKED sample, at least 50 per lane per 500 rows when available

Codex never edits the QA watermark on its own.

## Frozen pre-Codex baseline

The manually audited pre-Codex saved population is flattened once into:
- `docs/issue132/parallel/codex-baseline/manifest.json`
- one compact baseline JSON per lane.

The old checkpoint/correction/staging/repair files remain untouched as forensic history, but normal Codex execution and normal CI do not reconstruct them.

Historical HOLD slots and legacy semantic-lint debt are recorded in the baseline and do **not** move the forward frontier backward. Forward review starts after the frozen saved end:
- L1 1126
- L2 1226
- L3 1201

They still must be resolved before final Pass-A completion.

New forward work does not create:
- write-request files
- deferred marker files
- checkpoint files or checkpoint promotion;
- status caches;
- repair overlays for ordinary new Codex windows.

## Repair

CODEX-REPAIR works against the compact Codex baseline or a direct Codex staging window, not the old Automation chain.

For baseline HOLD/lint debt, use the baseline-repair helper selected by authority. For a new direct window, make the smallest targeted file repair, validate, and commit it normally. Git history is the repair audit trail.

Do not rewrite the old forensic checkpoint/staging source files.
A taxonomy-policy question is escalated to ChatGPT/user. A mechanical/schema/CI defect may be fixed directly with tests.

## Completion

Pass A completes only when the flat validator reports:
- accepted_total = 31,003
- invalid windows = 0
- hold windows = 0
- missing identities = 0
- duplicate coverage = 0
- QA watermark violations = 0
- fatal contract errors = 0
- final_semantic_qa_passed = true

Then stop. No merge, Pass B promotion or production apply without separate authorization.
