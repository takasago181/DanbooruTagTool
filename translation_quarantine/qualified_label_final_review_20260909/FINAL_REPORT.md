# Issue #36 qualified-label final review

- Contract: `translation_quarantine/r3/QUALIFIED_LABEL_FINAL_REVIEW_CONTRACT.md` at `60fc740a0c6463f9aeef40293bd006c0037493da`
- Input residual fallback: **876**
- Qualified rows reviewed: **731**
- Ordinary qualified concepts translated: **50**
- Residual true exceptions: **826**
- Final merged table: **30629 unique canonicals**
- Final states: `{'ENGLISH_FALLBACK_EXCEPTION': 826, 'JA_ACCEPT_EXISTING': 547, 'JA_ACCEPT_MACHINE': 25418, 'JA_ACCEPT_STRICT': 3838}`
- Generic REVIEW/PENDING: **0**
- Display coverage: **29803/30629 (97.30%)**; search coverage: **29803/30629 (97.30%)**
- Fallback ledger: `translation_quarantine/qualified_label_final_review_20260909/fallback_exceptions.jsonl` (**826 rows; count-checked)

## Required repairs

- `human_(warcraft)` → `人間（Warcraft）`
- `hydro_symbol_(genshin_impact)` → `水元素のシンボル（Genshin Impact）`
- `advanced_ship_(eve_online)` → `先進型艦船（EVE Online）`
- Parentheses, underscores, and franchise qualifiers alone never force English fallback.
- Character/cosplay names, artist/style identities, named artifacts, products, models/codes, symbols, and opaque strings remain original-form exceptions.

## Verification

- Replay: **PASS**; protected boundary: **PASS**; `production_modified: NO`.
- Focused qualified-review tests: **7 passed**; combined regression: **56 passed**.
- Full pytest: **313 passed, 61 environment setup errors** caused by Windows TEMP ACL `WinError 5`; no product/R3 assertion failures in setup errors.

## Boundaries

Only quarantine/tests changed; no production data, #32/#35/CURRENT_DEV_TASK/main/Stage10 A/B changes; promotion is `NOT_AUTHORIZED`. 
