# Issue #36 bounded wrapper cleanup — bounded rework

- Triggering independent audit comment: `5599075517`
- Contract: `translation_quarantine/r3/BOUNDED_WRAPPER_CLEANUP_CONTRACT.md` at `caf489ed6523da911c67d9d56466a5692445d47e`
- Bounded target rows: **2434**
- Classification: `{'TRANSLATABLE_DISPLAY': 1546, 'TRUE_ORIGINAL_FORM_EXCEPTION': 888}`
- Residual fallback: **1714**; ledger `translation_quarantine/bounded_wrapper_cleanup_20260909/fallback_exceptions.jsonl` (count-checked)
- Fallback reason classes: `{'SYMBOL_OR_EMOTICON': 126, 'PROPER_NAME_OR_QUALIFIED_LABEL': 975, 'PRODUCT_OR_SERVICE_NAME': 68, 'OPAQUE_SOURCE_STRING': 366, 'CODE_OR_PRODUCT_IDENTIFIER': 179}`
- Final merged table: **30629 unique canonicals**
- Meaningful display coverage: **26449/30629 (86.35%)**; search: **26449/30629 (86.35%)**
- Generic REVIEW/PENDING: **0**

## Representative repaired labels

- `kickstand` → `キックスタンド`
- `legjob` → `レッグジョブ`
- `dominator_(bdsm)` → `支配する側（BDSM）`
- `implied_cheating_(relationship)` → `浮気を示唆する関係`
- `alternate_ass_size_(larger)` → `大きめの尻差分`
- `heavy_chromatic_aberration` → `強い色収差`
- `no_magazine_(weapon)` → `弾倉なし（武器）`
- `newt` → `イモリ`

## Phrase-level semantic repairs

- `painting_fingernails` → `爪に色を塗る`
- `painting_toenails` → `足の爪に色を塗る`
- `hydraulic_press` → `油圧プレス`
- `press_conference` → `記者会見`
- `taking_notes` → `メモを取る`
- `hugging_ass` → `尻を抱く`
- `opening_window` → `窓を開ける`
- `riding_motorcycle` → `オートバイに乗る`
- `two-handed_masturbation` → `両手での自慰`
- `three-finger_salute` → `3本指の敬礼`
- `two-page_spread` → `見開き2ページ`

## Classification policy

- A Japanese wrapper or a Japanese fragment beside an untranslated semantic base is not meaningful coverage.
- Phrase overrides take precedence when a compound's action, object, state, direction, count, or part of speech cannot be preserved by token concatenation.
- Ordinary/general, adult/niche, relation, direction, count, and action-state concepts are translated when a glanceable Japanese label is available.
- Acronyms and identity-bearing qualifiers may remain in original form when the Japanese descriptive meaning is still clear; true identity/code/symbol/opaque rows remain narrow exceptions.

## Verification

- Replay: **PASS**; protected boundary: **PASS**; `production_modified: NO`.
- Focused bounded-wrapper tests: **12 passed**; Issue #36/R3/qualified regression: **102 passed**.
- Full pytest: **393 tests passed at assertion level; 61 known Windows TEMP ACL setup errors and pytest session-finalize PermissionError**; this is not classified as an overall suite PASS and no product/assertion failures were observed.

## Boundaries

Only quarantine/tests changed; no production data, #32/#35/CURRENT_DEV_TASK/main/Stage10 A/B changes; promotion is `NOT_AUTHORIZED`.
