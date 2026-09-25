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
1. run the flat validator and find the first uncovered lane-local index;
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

## Historical compatibility

Keep existing:
- checkpoint CSVs
- checkpoint correction overlays
- historical staging windows
- staging repair overlays

Do not promote staging into checkpoints. Do not rewrite historical source files. The flat validator resolves the effective historical state.

New forward work does not create:
- write-request files
- deferred marker files
- checkpoint promotion files
- lane status caches
- coordinator/repair status caches

## Repair

Repair the smallest exact target. Preserve already-correct bound decisions. Historical fixes remain append-only overlays.

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
