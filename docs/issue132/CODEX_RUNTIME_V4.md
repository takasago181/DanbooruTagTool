# Issue #132 — Codex Autonomous Runtime V4

Status: **ACTIVE AUTONOMOUS EXECUTION GUIDE**

This is the ordinary execution authority for Issue #132. The goal is to finish the remaining population with **three forward Codex workers plus one independent Codex QA/Repair role**, without repeatedly handing work back to the user or ChatGPT.

Old Luna/ChatGPT-Automation worker cards, coordinator cards, write-request protocols, checkpoint-promotion instructions and older handoff prose are forensic history only.

## Read order

1. `docs/issue132/parallel/RUNTIME_AUTHORITY.json`
2. this file
3. semantic contract named by authority
4. `docs/issue132/parallel/CODEX_QA_STATE.json`
5. the work/QA packet produced by the helper for the current role

## Roles

Use four independent Codex worktrees:

- **CODEX-L1** — Lane 1 forward semantic review
- **CODEX-L2** — Lane 2 forward semantic review
- **CODEX-L3** — Lane 3 forward semantic review
- **CODEX-QA-REPAIR** — independent semantic QA, baseline debt repair, targeted forward repair, CI/schema repair

All publish only to `research/taxonomy-usability-audit` using fetch/rebase/revalidate/fast-forward push. Never force-push. Never touch `main` or production.

## Forward worker loop

For lane N:

1. run `python scripts/issue132/codex_next_batch.py --lane N --out /tmp/issue132-laneN.json`;
2. if status is `READY`, inspect every identity individually;
3. classify obvious meaning directly as `CHECKED`;
4. research only material ambiguity;
5. after bounded useful research, unresolved meaning becomes `RESEARCHED + SEMANTIC_UNRESOLVED` rather than a guess or ordinary HOLD;
6. create one local decision JSON for the returned packet;
7. run `python scripts/issue132/codex_stage_window.py --decisions <file>`;
8. run `python scripts/issue132/validate_flat_pass_a.py`;
9. commit the generated canonical staging window;
10. fetch/rebase canonical, rerun validation, fast-forward push;
11. request the next packet and continue.

### Internal QA gate

If `codex_next_batch.py` returns `INTERNAL_QA_GATE`, **do not ask the user or ChatGPT to continue**.

Instead:
- leave that lane paused;
- CODEX-QA-REPAIR runs its next QA packet for the lane;
- repairs any confirmed defects;
- advances the internal QA cursor with `codex_qa_advance.py`;
- the lane then resumes automatically.

The internal gate exists only to prevent thousands of unchecked decisions from accumulating. It is not a human handoff.

## Forward decision JSON

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

Do not include identity text, identity hash or review_seq. The staging helper binds them from frozen neutral input.

A `RESEARCHED` row must carry direct evidence URLs.

Holds are exceptional:
- lane_local_index
- reason_code
- research_attempt_codes

Do not use HOLD for ordinary semantic uncertainty.

## Internal QA epochs

Each lane has an independent QA cursor in `CODEX_QA_STATE.json`.

Default:
- QA epoch = **1,000 new lane-local identities**
- maximum unaudited lead = **2,000 identities per lane**

This means the three forward lanes usually produce about **3,000 new identities between QA epochs**, while CODEX-QA-REPAIR works independently.

For each due epoch, run:

`python scripts/issue132/codex_qa_packet.py --lane N --out /tmp/issue132-qa-laneN.json`

The packet includes:
- all RESEARCHED rows;
- all MIXED rows;
- all SEMANTIC_UNRESOLVED rows;
- all vocabulary-gap rows;
- all multi-route/SUPPORTING rows;
- all body/theme facet rows;
- rows in known high-risk semantic families;
- deterministic ordinary CHECKED sample.

CODEX-QA-REPAIR must inspect every selected row independently. Do not simply trust the forward worker's reasoning.

Known high-risk families include:
- cosplay / named costume;
- named weapon / prop / device;
- clothing-state;
- ACTION_CONTACT vs POSE_POSITION vs RELATION_ROLE;
- body hair / nails / body-site feature;
- color/pattern siblings;
- object-vs-scene;
- body/theme facets.

If defects are found:
1. repair the smallest exact baseline/direct window target;
2. rerun the flat validator;
3. continue QA until the epoch is clean.

After the epoch is clean:

`python scripts/issue132/codex_qa_advance.py --lane N --through <epoch_end>`

Commit the QA-state update together with any repairs, rebase, validate, and fast-forward push.

Do **not** widen QA state beyond a packet actually audited.

## When to contact the user / ChatGPT before the end

Only for a true specification blocker, for example:
- frozen taxonomy vocabulary is insufficient and a taxonomy change is required;
- two frozen rules directly contradict each other;
- source identity binding/frozen hashes are invalid;
- repository/CI cannot be safely recovered;
- a systematic semantic defect cannot be resolved under the existing contract.

Do not return merely because:
- an epoch is due;
- one row is difficult;
- research produced no answer;
- one lane reaches an internal QA gate;
- a routine repair is needed.

## Frozen pre-Codex baseline

The pre-Codex saved population is flattened into:
- `docs/issue132/parallel/codex-baseline/manifest.json`
- one compact baseline JSON per lane.

Forward starts:
- L1: 1126
- L2: 1226
- L3: 1201

Historical HOLD/lint debt is handled by CODEX-QA-REPAIR and does not move forward frontiers backward.

## Repair

Baseline debt:

`python scripts/issue132/codex_repair_baseline.py --repairs <file>`

Direct forward windows use the smallest exact targeted edit followed by full validation. Git history is the repair audit trail.

Old forensic checkpoint/staging source files remain untouched.

## Completion before returning to ChatGPT

Codex continues until all of the following are true:
- all 31,003 slots are processed;
- accepted_total = 31,003;
- baseline HOLD debt = 0;
- baseline semantic-lint debt = 0;
- forward HOLD debt = 0;
- invalid windows = 0;
- duplicates = 0;
- fatal contract errors = 0;
- every lane's internal QA cursor reaches lane end;
- final internal Codex QA passes.

Then set `final_internal_qa_passed=true` and stop.

At that point the user returns once to ChatGPT for final independent semantic audit. ChatGPT does **not** need to intervene at each epoch.

No merge, Pass B promotion or production apply is authorized.
