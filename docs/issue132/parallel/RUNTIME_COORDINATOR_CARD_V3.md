# Issue132 Runtime Coordinator Card V3

Purpose: monitor workers without consuming worker semantic budget.

## Hot-path reads
Read:
- this card;
- coordinator_status.json;
- all three lane status.json files;
- repair_status.json if present;
- latest Issue132 CI conclusion and staging-validator diagnostics when failed.

Do NOT reread the large CURRENT_AUTOMATION_OPERATION.md during normal cycles.

## Responsibilities
1. Preserve 3 forward workers as primary.
2. Verify each new post-V3 window passes exact tuple alignment.
3. Classify worker stops:
   - 300 NEW / lane complete / evidenced hard blocker / actual forced interruption = acceptable;
   - voluntary 25/50/etc stop with safe continuation = INVALID_STOP.
4. Lane 2 is specifically watched for repeated 25/50-row wrap-up.
5. Do not ask forward workers to clean historical invalid staging. That belongs to the repair automation.
6. Official reviewed progress is immutable checkpoint union only.

## Quality
New windows: watch for recurrent route2 drift using the same independent-browse test as the worker card.
Lane 3 historical 751-1050 route-family remediation remains repair/QA debt until cleared; do not make Worker 3 reread it every forward run.

## Coordinator action
Prefer monitoring and routing over semantic rework. Use coordinator pickup only for a small urgent same-lane gap when repair automation cannot handle it safely.
If CI fails, separate:
- immutable/frozen failure = high priority stop/reconcile;
- staging-only failure = repair debt; do not stall clean forward workers.

Update coordinator_status with concise lane state, latest CI, repair debt trend, and stop classification.
