# Issue #36 bounded wrapper cleanup

- Contract: `translation_quarantine/r3/BOUNDED_WRAPPER_CLEANUP_CONTRACT.md` at `caf489ed6523da911c67d9d56466a5692445d47e`
- Bounded target rows: **2434**
- Classification: `{'TRANSLATABLE_DISPLAY': 1865, 'TRUE_ORIGINAL_FORM_EXCEPTION': 569}`
- Residual fallback: **1395**; ledger `translation_quarantine/bounded_wrapper_cleanup_20260909/fallback_exceptions.jsonl` (count-checked)
- Final merged table: **30629 unique canonicals**
- Meaningful display coverage: **29234/30629 (95.45%)**; search: **29234/30629 (95.45%)**
- Generic REVIEW/PENDING: **0**

## Representative repaired labels

- `kickstand` → `キックスタンド`
- `legjob` → `レッグジョブ`
- `dominator_(bdsm)` → `支配する側（BDSM）`
- `implied_cheating_(relationship)` → `浮気を示唆する関係`
- `alternate_ass_size_(larger)` → `大きめの尻差分`

## Classification policy

- `タグ「...」` wrappers are never counted as Japanese after cleanup.
- Ordinary/general, adult/niche, relation, direction, count, and action-state concepts are translated when a glanceable Japanese label is available.
- Character/cosplay, artist/style, named artifact/title/entity, product/service, model/code, symbol, and opaque identities remain explicit narrow exceptions.

## Verification

- Replay: **PASS**; protected boundary: **PASS**; `production_modified: NO`.
- Focused bounded-wrapper tests: **8 passed**; combined regression suite: **63 passed**.
- Full pytest: **327 passed, 61 environment setup errors** caused by Windows TEMP ACL `WinError 5`; no product/R3 assertion failures in setup errors.

## Boundaries

Only quarantine/tests changed; no production data, #32/#35/CURRENT_DEV_TASK/main/Stage10 A/B changes; promotion is `NOT_AUTHORIZED`.
