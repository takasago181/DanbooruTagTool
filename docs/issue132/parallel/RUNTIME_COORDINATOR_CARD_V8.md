# Issue132 Runtime QA-Coordinator Card V8 — Codex semantic QA

Status: CURRENT QA AUTHORITY when selected by live `RUNTIME_AUTHORITY.json`.

ChatGPT is the external specification/QA supervisor. ChatGPT Automations remain paused during Codex execution.

## Read

1. `RUNTIME_AUTHORITY.json`
2. this file
3. `CODEX_QA_STATE.json`
4. current semantic guardrail policy
5. latest flat-validator snapshot
6. exact accepted rows/ranges needed for QA

Repository files remain truth.

## Mechanical QA

Mechanical validation covers 100% of accepted output.

Track:
- accepted unique identities by lane and total;
- pending materialization slots/ranges;
- deferred slots/ranges;
- invalid windows;
- holds;
- duplicate coverage;
- missing ranges;
- policy-version metadata;
- QA watermark compliance.

A bad early range does not erase later valid progress.

## First Codex calibration gate

The first new 100 accepted rows in each lane after the manually audited baseline are a mandatory calibration batch.

Baseline:
- Lane 1: 1125
- Lane 2: 1225
- Lane 3: 1200

Calibration end:
- Lane 1: 1225
- Lane 2: 1325
- Lane 3: 1300

Before widening the QA watermark:
- semantically inspect all 300 new calibration rows;
- check all guardrail families;
- verify reason-code trace quality;
- confirm no systematic drift from the manually audited baseline.

If a systematic defect exists:
- do not widen the affected lane watermark;
- identify exact family/ranges;
- repair only affected accepted output;
- re-QA after repair.

## Steady-state QA

After calibration, each lane may advance at most 500 accepted rows beyond its last ChatGPT semantic-QA watermark.

For each bounded QA interval inspect:
- ALL RESEARCHED;
- ALL MIXED;
- ALL SEMANTIC_UNRESOLVED;
- ALL route_vocabulary_gap=YES;
- ALL 2-3 route rows;
- ALL SUPPORTING route rows;
- ALL body/theme facet rows;
- every detected sibling/family inconsistency;
- deterministic stratified ordinary CHECKED sample, minimum 50 per lane per 500-row interval when available.

Family scan explicitly covers:
- cosplay/named costume;
- named weapon/prop/device;
- clothing-state;
- action/contact/object-use;
- pose/position;
- role/relation;
- body-hair/nails/body-site;
- color/pattern siblings;
- object-vs-scene;
- body/theme facets.

Adult/sexual content alone is not a risk signal.

## Advancing the QA state

Only ChatGPT QA may advance `CODEX_QA_STATE.json`.

After an interval passes:
- set each audited lane's `last_chatgpt_semantic_qa_by_lane` to the highest accepted lane-local index actually covered by QA;
- set `allowed_forward_end_by_lane` to at most last-QA + 500, capped at lane length;
- after calibration passes, set status to `STEADY_STATE`.

Do not advance a lane merely because Codex produced rows.

## Final semantic QA

After all 31,003 identities are mechanically accepted:
- run full-population distribution checks;
- run final cross-family consistency audit;
- inspect remaining unresolved/gap clusters;
- confirm no unresolved systematic semantic defect.

Only then set `final_semantic_qa_passed=true`.

## Completion gate

Pass A is complete only when all are true:
- accepted_total = 31,003;
- invalid_window_count = 0;
- hold_window_count = 0;
- missing written identities/ranges = 0;
- duplicate coverage = 0;
- fatal contract errors = 0;
- pending_materialization_count = 0;
- deferred_range_count = 0;
- QA watermark violations = 0;
- final_semantic_qa_passed = true.

No merge or production apply is authorized.
