# CURRENT DEV TASK — COMPATIBILITY ROUTING POINTER

This file exists only for older workflows that still look for `CURRENT_DEV_TASK.md`.

Do not duplicate current lane history or fixed HEADs here.

## Current authority

1. live GitHub `main`
2. `docs/project/CURRENT_ROUTING.json`
3. selected live Issue + latest relevant checkpoint/result
4. `docs/project/PERMANENT_RULES.md`
5. task-specific contract/spec

Human dashboard:
- `docs/project/NOW.md`

Historical state:
- `docs/project/CURRENT_STATE_HISTORY.md`

## Resume policy

Cold start:
- use `CHAT_START_PROTOCOL.md`;
- recover only the minimum live authority needed for the selected task;
- expand to dashboards/history/specs only when materially useful.

Warm resume:
- verify the same lane/contract;
- inspect changed state and immutable progress;
- continue without rereading unchanged global docs.

Protected/destructive/production work still uses provenance and recovery checks appropriate to actual personal-workstation risk. Distribution/other-PC packaging gates are not implied.

## Codex autonomy

The project fixes the requested outcome, protected boundaries, and acceptance conditions.

Codex chooses implementation method, internal work order, helper tooling, and refactor granularity unless the selected Issue explicitly makes a procedure a hard requirement.

Do not infer current work from fixed examples in this compatibility file.

## Production pointers

- production LKG: `docs/project/LAST_KNOWN_GOOD.json`
- runtime pipeline: `docs/maintenance/PORTABLE_RUNTIME_PIPELINE.md`
- Release skip inventory: `docs/project/RELEASE_TEST_SKIP_INVENTORY.json`

Always resolve the actual current runtime/source from live LKG/checkpoints rather than a fixed SHA copied here.
