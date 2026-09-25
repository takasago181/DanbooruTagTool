# Issue #132 — Codex Runtime V3

Status: ACTIVE EXECUTION GUIDE

This is the only prose execution guide Codex needs for Issue #132. Old Luna/Automation worker cards, coordinator cards, write-request protocols, checkpoint-promotion instructions and old handoff prose are forensic history, not runtime authority.

## Read order

1. `docs/issue132/parallel/RUNTIME_AUTHORITY.json`
2. this file
3. semantic contract named by authority
4. `docs/issue132/parallel/CODEX_QA_STATE.json`
5. the work packet produced by `scripts/issue132/codex_next_batch.py`

Do not read old Automation cards during ordinary forward review or ordinary repair.

## Roles

Use four independent Codex worktrees:
- L1: Lane 1 forward review
- L2: Lane 2 forward review
- L3: Lane 3 forward review
- REPAIR: baseline HOLD/lint debt, targeted ChatGPT QA repairs, or mechanical CI defects

All publish to `research/taxonomy-usability-audit` by normal fetch/rebase/revalidate/fast-forward push. Never force-push. Never touch main or production.

## Forward review

For a lane:

1. run `python scripts/issue132/codex_next_batch.py --lane N --out /tmp/issue132-laneN.json`;
2. if status is `QA_GATE`, stop that lane and report it;
3. if status is `READY`, inspect every identity in the packet individually;
4. classify obvious meaning directly as `CHECKED`;
5. research only material ambiguity; unresolved after bounded useful research becomes `RESEARCHED + SEMANTIC_UNRESOLVED`;
6. prepare one local decision JSON covering the packet;
7. run `python scripts/issue132/codex_stage_window.py --decisions <file>`;
8. run `python scripts/issue132/validate_flat_pass_a.py`;
9. commit the generated staging window, fetch/rebase the canonical branch, rerun validation, and fast-forward push;
10. request the next packet and continue until QA gate or lane completion.

The packet and decision JSON are local scratch files and are not committed.

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

Do not include identity text, identity hash or review_seq. The staging helper binds those deterministically from frozen neutral input.

A `RESEARCHED` row must carry direct evidence URLs. Holds are exceptional and contain only:
- lane_local_index
- reason_code
- research_attempt_codes

Do not use a HOLD for ordinary semantic uncertainty. After bounded useful research, use `SEMANTIC_UNRESOLVED` and continue.

## Why windows are up to 100 rows

The old 25-row write-request/materializer design existed to survive ChatGPT Automation write-policy limits. Codex works in a local worktree and can commit directly, so up to 100 decisions become one canonical staging window. Semantic decisions remain per identity; only persistence overhead is reduced.

## QA watermarks

Codex cannot create forward work beyond `allowed_forward_end_by_lane` in `CODEX_QA_STATE.json`.

Initial calibration:
- Lane 1: 1126–1225
- Lane 2: 1226–1325
- Lane 3: 1201–1300

ChatGPT reviews all first 100 new rows per lane. After calibration, a lane can advance by at most 500 new rows between ChatGPT QA passes.

Steady-state QA focuses on:
- all RESEARCHED
- all MIXED
- all SEMANTIC_UNRESOLVED
- all vocabulary gaps
- all multi-route / SUPPORTING rows
- all body/theme facets
- sibling/family consistency
- a deterministic ordinary-CHECKED sample

Codex never edits the QA watermark.

## Frozen pre-Codex baseline

The manually audited pre-Codex saved population is flattened into:
- `docs/issue132/parallel/codex-baseline/manifest.json`
- one compact baseline JSON per lane

Normal Codex execution and normal CI read this baseline, not the old checkpoint/correction/staging/repair chain.

Forward starts are fixed by the baseline:
- L1: 1126
- L2: 1226
- L3: 1201

Historical HOLD and legacy semantic-lint debt are visible as repair debt but do not move those forward frontiers backward. They still must be zero before final Pass-A completion.

Old Automation-era files remain immutable forensic evidence.

## Repair

For pre-Codex debt, use:
`python scripts/issue132/codex_repair_baseline.py --repairs <file>`

For a new direct Codex window, repair the smallest exact canonical window, validate, and commit normally. Git history is the audit trail; no new repair-overlay chain is required.

Do not rewrite old forensic checkpoint/staging files. Taxonomy-policy questions go to ChatGPT/user. Mechanical/schema/CI defects may be fixed directly with tests.

## New forward work never creates

- write-request files
- materialization requests
- deferred markers
- checkpoint files
- checkpoint promotion
- worker/coordinator status caches
- Automation task state
- ordinary repair overlays

## Completion

Pass A completes only when the flat validator reports:
- processed_slot_total = 31,003
- accepted_total = 31,003
- baseline HOLD debt = 0
- baseline semantic-lint debt = 0
- forward HOLD debt = 0
- invalid windows = 0
- duplicate coverage = 0
- QA watermark violations = 0
- fatal contract errors = 0
- final_semantic_qa_passed = true

Then stop. No merge, Pass B promotion or production apply without separate authorization.
