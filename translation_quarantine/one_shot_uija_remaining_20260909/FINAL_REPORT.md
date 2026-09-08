# Issue #36 one-shot remaining UI-JA completion

- Campaign: `issue36-one-shot-uija-remaining-20260909-v1`
- Contract: `translation_quarantine/r3/ONE_SHOT_UIJA_REMAINING_COMPLETION_CONTRACT.md` at `4b6d9a813092715537c1e2b386c3b431f7995ed1`
- Measurable universe: **30629**
- Prior completed/deduplicated: **556**
- Newly processed: **30073**
- Terminal P0/P1/P2: **{'P0': 1025, 'P1': 4910, 'P2': 24694}**
- Final states: `{'ENGLISH_FALLBACK_EXCEPTION': 8048, 'JA_ACCEPT_EXISTING': 547, 'JA_ACCEPT_MACHINE': 19267, 'JA_ACCEPT_STRICT': 2767}`
- Lightweight accepted: **19267**; bounded strict routed: **10806**; English fallback: **8048**
- Generic REVIEW/PENDING: **0**
- Japanese display coverage: **22584/30629 (73.73%)**
- Japanese search coverage: **22584/30629 (73.73%)**
- Corrected labels: `finger_to_mouth → 口に指`, `pauldrons → 肩当て`, `simple_background → シンプルな背景`.
- Replay: **PASS**; protected boundary: **PASS**; `production_modified: NO`.
- Focused tests: recorded by the completion checkpoint after execution.

## Complete table

- `final_translation_table.csv` and `final_translation_table.md` contain every measurable row.
- `coverage_recount.json` records the deduplicated P0/P1/P2 remainder and input hashes.
- `fallback_exceptions.jsonl` records every explicit English fallback reason.

## Boundaries

Only quarantine artifacts and focused tests are changed. No production data, #32, #35, CURRENT_DEV_TASK, main, or Stage10 production A/B state is modified; promotion is `NOT_AUTHORIZED`.
