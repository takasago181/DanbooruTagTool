# CHAT START PROTOCOL

Purpose: recover the live task quickly without making every Codex/ChatGPT session reread the whole project history.

## 1. Cold start

For a new session or changed lane:

1. fetch live `main`;
2. read `docs/project/CURRENT_ROUTING.json`;
3. read the selected live Issue and latest relevant checkpoint/result;
4. read `docs/project/PERMANENT_RULES.md`;
5. read only the task-specific contract/spec needed for the work.

Read `NOW.md`, `CURRENT_STATE.md`, `PRODUCT_GOAL_LOCK.md`, Decisions, history, or old Issue material only when needed to resolve current scope/behavior.

Do not require a fixed ceremonial output such as TEAM_ID/ROLE/HEAD tables unless it helps the actual task.

## 2. Warm resume

When the lane and contract are unchanged:

1. verify the live target still exists and is not superseded;
2. inspect changed files/checkpoints/results since the last stable point;
3. continue from the next useful work unit.

Do not reread unchanged global policy/spec documents by default.

## 3. Contradictions

Not every stale line is a blocker.

Resolve harmless stale dashboards/pointers from the higher-authority live state and continue.

Stop for clarification or fail closed only when an unresolved contradiction could materially alter:
- the requested mutation;
- protected/UserData handling;
- accepted semantic authority;
- production source/runtime;
- the intended feature contract.

Record/fix stale management text when it is part of the current task; do not make routine progress wait on unrelated documentation cleanup.

## 4. Checkpoints

Leave a GitHub checkpoint when:
- a durable implementation/audit result is reached;
- a blocker or important decision would otherwise be lost;
- work is handed off;
- recovery cost would be high without it.

Keep it concise:
- result;
- evidence/commit;
- remaining blocker or next decision.

Do not checkpoint every minor substep.

## 5. Chat/lane handoff

The user should not need to write a long manual handoff.

Before a major handoff, ensure the live Issue/branch contains enough evidence to resume. A new session should reconstruct state from GitHub, not from copied chat history.

## 6. Roles

DEV/Codex:
- implements/reviews the selected product task within the live contract.

KNOWLEDGE:
- maintains research/generation knowledge; it does not silently change production authority.

AUDIT:
- on-demand independent review when a task requires it.

TEMP:
- bounded environment/setup work.

Detailed role history belongs in historical docs, not this startup protocol.

## 7. Protected safety

Startup simplification never weakens:
- UserData protection;
- destructive cleanup prohibitions;
- production provenance/rollback;
- accepted semantic authority boundaries.

See `PERMANENT_RULES.md`.
