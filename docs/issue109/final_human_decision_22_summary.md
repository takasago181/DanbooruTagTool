# Issue #109 Final Human Decision — 22 rows

Status: decision evidence only. No production mutation or deletion was performed.

## Scope

- Reviewed only the 22 rows that remained `HUMAN_DECISION_REQUIRED` after the 87-row production decision gate.
- No other Special row was re-evaluated.
- Definitions, tag existence, and alias relations were checked against the live Danbooru wiki/tag/alias endpoints on 2026-09-16.
- General route evidence was recomputed from the current #64 effective sidecar and current Japanese overlay.

## Final decisions

- `REMOVE_FROM_SPECIAL_CONFIRMED`: 12
- `KEEP_SPECIAL_CONFIRMED`: 10
- `USER_CHOICE_REQUIRED`: 0

### REMOVE_FROM_SPECIAL_CONFIRMED

`835,875,876,950,1055,1084,1166,1577,2358,2483,2519,2626`

These are broad/context/meta concepts, work-specific object/reference identities, stale or invalid alias identities, or a nonsexual meme/reference. An unresolved General browse row was not treated as a reason to keep them in Special.

### KEEP_SPECIAL_CONFIRMED

`49,57,1052,1122,1139,1171,1173,1186,1204,1747`

These definitions resolve to specific sexual presentation, sexual gesture, sexual meme/template, insertion/topology, fluid state, sexual relation, or sexual position concepts with independent Special discovery value.

## Aggregate with the prior 87-row gate

Prior gate: REMOVE 57, KEEP 8, HUMAN 22.

- `FINAL_REMOVE_COUNT`: 69
- `FINAL_KEEP_FROM_GATE_COUNT`: 18
- `USER_CHOICE_REQUIRED_COUNT`: 0
- `FINAL_PROJECTED_SPECIAL_COUNT`: 3019 (`3088 - 69`; no production change performed)

The projected count is an audit calculation only. It does not authorize deletion, ID compaction, renumbering, catalog rebuild, or local integration.

## Validation

- Input human-decision IDs: exactly 22
- Output rows: exactly 22
- Duplicate IDs: 0
- Missing input IDs: 0
- Allowed final decisions only: `REMOVE_FROM_SPECIAL_CONFIRMED`, `KEEP_SPECIAL_CONFIRMED`, `USER_CHOICE_REQUIRED`
- Blank definition evidence: 0
- Blank General route evidence: 0
- Blank final reasons: 0
- `git diff --check`: required before commit

## Boundary

- production Special mutated: NO
- production Special deleted: NO
- Special IDs deleted/renumbered/compacted: NO
- local catalog / `catalog.db` mutated: NO
- local 3,088 integration performed: NO
- Issue #70 mutated: NO
- General production mutated: NO
- UserData mutated: NO
