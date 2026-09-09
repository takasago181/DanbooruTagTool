# Issue #36 bounded wrapper cleanup — bounded rework

- Triggering independent audit comment: `5599660765`
- Current accepted rows re-gated: **1546**; prior bounded exceptions preserved.
- Contract: `translation_quarantine/r3/BOUNDED_WRAPPER_CLEANUP_CONTRACT.md` at `caf489ed6523da911c67d9d56466a5692445d47e`
- Bounded target rows: **2434**
- Classification: `{'TRANSLATABLE_DISPLAY': 374, 'TRUE_ORIGINAL_FORM_EXCEPTION': 2060}`
- Fallback reason classes: `{'SYMBOL_OR_EMOTICON': 76, 'PHRASE_SEMANTICS_UNRESOLVED': 1677, 'PROPER_NAME_OR_QUALIFIED_LABEL': 897, 'PRODUCT_OR_SERVICE_NAME': 68, 'CODE_OR_PRODUCT_IDENTIFIER': 98, 'OPAQUE_SOURCE_STRING': 70}`
- Gate demotion samples: `shooting_star_(symbol)`, `shot_glass`, `shredded_muscles`, `building_snowman`, and `break_action` → `PHRASE_SEMANTICS_UNRESOLVED`.
- Residual fallback: **2886**; ledger `translation_quarantine/bounded_wrapper_cleanup_20260909/fallback_exceptions.jsonl` (count-checked)
- Final merged table: **30629 unique canonicals**
- Meaningful display coverage: **25277/30629 (82.53%)**; search: **25277/30629 (82.53%)**
- Generic REVIEW/PENDING: **0**
- Phrase-semantic gate: **1795** multi-token candidates; **1677** demoted without exact/validated phrase semantics.

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
- Every multi-token base concept requires an explicit/validated phrase mapping or a trusted whole-phrase label; token-only composition is a terminal narrow exception.
- Ordinary/general, adult/niche, relation, direction, count, and action-state concepts are translated when a glanceable Japanese label is available as a singleton or validated phrase.
- Acronyms and identity-bearing qualifiers may remain in original form when the Japanese descriptive meaning is still clear; true identity/code/symbol/opaque rows remain narrow exceptions.

## Verification

- Replay: **PASS**; protected boundary: **PASS**; `production_modified: NO`.
- Focused bounded-wrapper tests: **13 passed**; Issue #36/R3/qualified regression: **20 passed**.
- Full pytest: **333 tests passed at assertion level; 61 known Windows TEMP ACL setup errors and pytest session-finalize PermissionError**; this is not classified as an overall suite PASS and no product/assertion failures were observed.

## Boundaries

Only quarantine/tests changed; no production data, #32/#35/CURRENT_DEV_TASK/main/Stage10 A/B changes; promotion is `NOT_AUTHORIZED`.
