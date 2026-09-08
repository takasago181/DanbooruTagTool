# Issue #36 forced Japanese display completion

- Campaign: `issue36-forced-ja-display-completion-20260909-v1`
- Contract: `translation_quarantine/r3/FORCED_JA_DISPLAY_COMPLETION_CONTRACT.md` at `cd04a88b2d3d0f1a6b52f7dc9c485a38c9d3f8c1`
- Residual fallback input: **7752**
- Japanese display created: **5984**
- Strict route accepted: **1044**
- Narrow residual English fallback: **1768**
- Final merged table: **30629 unique canonicals**
- Final states: `{'ENGLISH_FALLBACK_EXCEPTION': 1768, 'JA_ACCEPT_EXISTING': 547, 'JA_ACCEPT_MACHINE': 24497, 'JA_ACCEPT_STRICT': 3817}`
- Generic REVIEW/PENDING: **0**
- Japanese display coverage: **28861/30629 (94.23%)**
- Japanese search coverage: **28861/30629 (94.23%)**
- Actual fallback ledger: `translation_quarantine/forced_ja_display_completion_20260909/fallback_exceptions.jsonl` (**1768 rows; count-checked**)
- Fallback reasons are limited to symbols/emoticons, proper/qualified labels, product/code identifiers, and opaque source strings; adult/compound/evidence gaps are not fallback reasons.
- Replay: **PASS**; protected boundary: **PASS**; `production_modified: NO`.

## Tests

- Focused forced-JA tests: **6 passed**.
- Prior closure + E2E tests: **37 passed**.
- Full pytest: **307 passed, 61 environment setup errors** caused by Windows TEMP ACL `WinError 5`; no product/R3 assertion failures in setup errors.

## Artifacts

- `source_residual_fallback_ledger.jsonl` freezes all 7,752 inputs.
- `candidate_provenance_ledger.jsonl`, `strict_review_decisions.jsonl`, and `final_rows.jsonl` record every processed row.
- `final_translation_table.csv` and `.md` contain all 30,629 merged rows.
- `fallback_exceptions.jsonl` is the committed residual ledger.

## Boundaries

Only `translation_quarantine/**` and focused tests are changed. No production `data/**`, #32, #35, CURRENT_DEV_TASK, main, or Stage10 A/B changes; promotion is `NOT_AUTHORIZED`.
