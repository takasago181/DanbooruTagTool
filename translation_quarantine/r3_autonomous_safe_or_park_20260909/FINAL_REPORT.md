# Issue #36 autonomous safe-or-park campaign

- Campaign: `issue36-autonomous-safe-or-park-20260909-v1`
- Input unresolved rows: 556
- SAFE: 14 / READY: 14 / REVIEW: 542 / CONTRADICTION: 0
- Wording gate READY: 14; search gate READY: 14
- False READY: 0; replay: PASS; protected boundary: PASS
- production_modified: False

## Route and safety decisions

All rows were evaluated in one deterministic campaign. Existing frozen routes were reused; no live route was called and exhausted routes were not retried. New READY rows were not used as teachers.

## Residual REVIEW reasons

{"CANONICAL_WIDTH_UNSPECIFIED": 470, "EXACT_CANONICAL_AUTHORITY_UNAVAILABLE": 408, "IDENTITY_OR_TITLE_MISMATCH": 408, "MULTIPLE_WORDING_CANDIDATES": 18, "NO_INDEPENDENT_DISPLAY_CANDIDATE": 119, "PROPOSITION_AMBIGUOUS": 6, "PROPOSITION_INCOMPLETE": 485, "SEMANTIC_SCOPE_NOT_ESTABLISHED": 394, "UNNATURAL_OR_EXPLANATORY_WORDING": 11, "WORDING_GATE_NOT_READY": 542}

## Parked canonical list

See `terminal_states.jsonl`; parked rows: 542.

## Boundaries

#32 v2 was read-only. No production data, #35 UI/code/tests, CURRENT_DEV_TASK, main, or Stage10 production A/B were modified. Promotion is not authorized.
