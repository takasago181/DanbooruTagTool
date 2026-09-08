# Issue #36 fallback UI-JA closure

- Campaign: `issue36-fallback-uija-closure-20260909-v1`
- Contract: `translation_quarantine/r3/FALLBACK_UIJA_CLOSURE_CONTRACT.md` at `2a4f2c3c2c06e0f31465786ab9c7039302878c3a`
- Input fallbacks: **8048**; source ledger count: **8048**
- Auto-filled/lightweight accepted: **290**; lightweight rejected: **3**
- Strict review routed: **7758**; strict accepted: **6**
- Residual English fallback: **7752**
- Final merged table: **30629 unique canonicals**
- Final states: `{'ENGLISH_FALLBACK_EXCEPTION': 7752, 'JA_ACCEPT_MACHINE': 19557, 'JA_ACCEPT_STRICT': 2773}` plus 547 carried `JA_ACCEPT_EXISTING` rows
- Generic REVIEW/PENDING: **0**
- Japanese display coverage: **22877/30629 (74.69%)**
- Japanese search coverage: **22877/30629 (74.69%)**
- Obvious corrections carried forward: `finger_to_mouth → 口に指`, `pauldrons → 肩当て`, `simple_background → シンプルな背景`.
- Actual fallback ledger: `translation_quarantine/fallback_uija_closure_20260909/fallback_exceptions.jsonl` (**7752 rows; count-checked**)
- Replay: **PASS**; protected boundary: **PASS**; `production_modified: NO`.

## Tests

- Closure focused tests: **6 passed**.
- Combined closure + prior campaign/R3 safety tests: **29 passed**; closure + E2E set: **37 passed**.
- E2E functional/verdict tests: **8 passed**.
- Full pytest: **301 passed, 61 environment setup errors** caused by Windows TEMP ACL `WinError 5`; exit 1 is an environment result, not a product/R3 assertion failure.

## Artifacts

- `source_fallback_ledger.jsonl` freezes all 8,048 inputs.
- `candidate_provenance_ledger.jsonl`, `lightweight_audit_decisions.jsonl`, and `strict_review_decisions.jsonl` record every route.
- `final_translation_table.csv` and `.md` contain the complete 30,629-row merged result.
- `fallback_exceptions.jsonl` contains only residual explicit English exceptions.

## Boundaries

Only `translation_quarantine/**` and focused tests are changed. No production `data/**`, #32, #35, CURRENT_DEV_TASK, main, or Stage10 A/B changes; promotion is `NOT_AUTHORIZED`.
