# Issue #36 exception classifier repair

- Contract: `translation_quarantine/r3/EXCEPTION_CLASSIFIER_REPAIR_CONTRACT.md` at `e365165b4e5be9a1a6433b933bca8e2f0cbb67d7`
- Input residual fallback: **1,768**
- Japanese display created: **892**
- Residual true exceptions: **876**
- Final merged table: **30629 unique canonicals**
- Final states: `{'ENGLISH_FALLBACK_EXCEPTION': 876, 'JA_ACCEPT_EXISTING': 547, 'JA_ACCEPT_MACHINE': 25375, 'JA_ACCEPT_STRICT': 3831}`
- Generic REVIEW/PENDING: **0**
- Display coverage: **29753/30629 (97.14%)**; search coverage: **29753/30629 (97.14%)**
- Fallback ledger: `translation_quarantine/exception_classifier_repair_20260909/fallback_exceptions.jsonl` (**876 rows; count-checked**)
- Parentheses/underscore alone never forced proper-name fallback; ordinary qualified concepts were repaired.
- Replay: **PASS**; protected boundary: **PASS**; `production_modified: NO`.

## Tests

- Focused repair tests: **6 passed**.
- Prior forced-JA tests: **43 passed**.
- Full pytest: **313 passed, 61 environment setup errors** caused by Windows TEMP ACL `WinError 5`; no product/R3 assertion failures in setup errors.

## Exception policy

- Residual ledger contains only symbols/emoticons, true names/qualified franchise labels, product/code identifiers, and explicitly opaque source strings.
- Adult/sexual meaning, compound structure, imperfect wording, and token-dictionary gaps are not fallback reasons.

## Artifacts

- `source_residual_exception_ledger.jsonl`, `reclassified_candidate_ledger.jsonl`, `final_rows.jsonl`, `fallback_exceptions.jsonl`.
- `final_translation_table.csv` and `.md` contain all 30,629 rows.

## Boundaries

Only quarantine/tests changed; no production data, #32/#35/CURRENT_DEV_TASK/main/Stage10 A/B changes; promotion is `NOT_AUTHORIZED`.
