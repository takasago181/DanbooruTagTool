# Issue #36 — full accepted-quality + fallback reconciliation contract

Status: EXECUTION CONTRACT FOR CODEX / QUARANTINE ONLY

## Authority / start gate

Read in this order before implementation:
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #36 latest comments, especially audit correction checkpoint `5599883613`
4. Issue #41 final `PASS_PILOT` checkpoint `5589825869` as validated R3 quality-method evidence only; **do not reopen or rerun #41**
5. this contract

Branch: `ui-ja/issue36-machine-convergence`

Fixed audited source implementation/artifact HEAD:
`1f069d050909425dbcc5c2965951fd0c920a2205`

Execution must begin from the branch HEAD containing this contract (contract commit `0f0cdd8657aeb03ee13cf1968fb86980fe4f604e` or its direct contract-fix descendant), with the fixed source artifact below treated as input. Do not reset the branch back to `1f069d...`.

Source artifact:
`translation_quarantine/bounded_wrapper_cleanup_20260909/final_translation_table.csv`

Fixed source facts:
- 30,629 unique canonicals
- 27,743 `JA_ACCEPT_*` rows
- 2,886 `ENGLISH_FALLBACK_EXCEPTION` rows
- stricter display/search recount: 25,277 / 30,629
- fallback contains 1,677 `PHRASE_SEMANTICS_UNRESOLVED`
- production modified: NO

The earlier `PASS_FOR_PROMOTION` is superseded by Issue #36 checkpoint `5599883613`. Promotion remains **NOT_AUTHORIZED** until a new independent audit passes.

## User intent

The Japanese overlay exists so the user can glance at a tag and understand its meaning in Japanese.

Priority:
1. semantic correctness
2. actually Japanese / readable Japanese
3. coverage
4. stylistic polish

Awkward but correct Japanese is acceptable. Misleading Japanese is not. Do not preserve coverage by accepting Chinese wording, raw-English semantic cores, malformed labels, or scope-changing translations.

## Why this pass exists

The bounded wrapper cleanup fixed its own target, but older accepted rows elsewhere still include defects such as:
- `:p` -> `闭嘴吐舌`
- `^_^` -> `闭眼笑`
- `anal_object_insertion` -> `肛门物体插入`
- `imminent_anal` -> `即将插入肛门`
- `presenting_own_anus` -> `展示自己的肛门`
- `presenting_own_foot` -> `見せる・own・足`
- `vibrator_on_clitoris` -> `阴蒂上的震动器`
- `imminent_penetration` -> `事前`
- `android` -> `メカバレ`
- `a_(phrase)` -> `フレーズ）`

The old generic CJK test `[ぁ-んァ-ン一-龥]` is not a language detector; Chinese Han text can pass it as Japanese.

This task reconciles the **whole accepted layer plus current fallback layer**, but it is not a blind 30,629-row retranslation.

# Phase A — screen all 27,743 accepted rows

Screen every `JA_ACCEPT_EXISTING` / `JA_ACCEPT_MACHINE` / `JA_ACCEPT_STRICT` row deterministically. Screening all rows is required; semantic retranslation is only required for the suspicious set.

Flag at minimum:

### A1 Non-Japanese / Chinese-risk
- simplified-Chinese-specific characters or strong Chinese lexical/grammatical patterns
- Han-only labels without trusted Japanese provenance / explicit validation
- routes that reused wording without language validation

Do **not** blanket-reject Han-only labels. Pure-kanji Japanese such as `肛門` or `妊娠検査` may be valid, but need trusted Japanese evidence or explicit validation rather than a generic CJK-character test.

### A2 Raw-English semantic-core risk
Flag ASCII English semantic tokens left in Japanese display/search, except explicitly permitted identity-bearing material such as standard acronym/code or proper/franchise qualifier when the descriptive base is still clear Japanese.

Fixture: `presenting_own_foot` must not remain `見せる・own・足`.

### A3 Malformed-label risk
Flag unmatched/duplicated brackets, broken qualifier formatting, wrapper remnants, or empty/near-empty descriptive bodies hidden by punctuation.

Fixture: `a_(phrase)` -> `フレーズ）` must not remain accepted as-is.

### A4 Semantic-scope risk
Flag possible changes/omissions in:
- actor / owner
- target / body site
- direction / spatial relation
- count / cardinality
- action vs state
- noun vs verb / object vs action
- negation
- required modifier / qualifier
- canonical concept width

Fixtures:
- `imminent_penetration` -> `事前` is insufficient.
- `android` -> `メカバレ` must be checked against exact canonical meaning.

Do not use the Japanese wording itself as semantic authority.

### A5 Route/source-risk
Surface accepted rows produced by historically weak lexical/token composition, lightweight reuse, machine direct translation, strict carryover, or any route lacking exact-canonical Japanese semantic proof. Route risk triggers review; it is not automatic failure.

# Phase B — reconcile all 2,886 fallback rows

Do not assume every fallback is a permanent true exception.

### B1 Revisit all 1,677 `PHRASE_SEMANTICS_UNRESOLVED`
These are translation homework, not automatically "English is fine".

For each:
- establish exact-canonical semantic scope using the conservative evidence principles validated by #41;
- produce concise Japanese display/search when supportable;
- accept only if phrase-level meaning is preserved;
- otherwise keep fallback with an explicit unresolved/evidence reason.

Do not return to per-token concatenation.

### B2 Validate all other exception classes
Screen current:
- `PROPER_NAME_OR_QUALIFIED_LABEL`
- `PRODUCT_OR_SERVICE_NAME`
- `CODE_OR_PRODUCT_IDENTIFIER`
- `OPAQUE_SOURCE_STRING`
- `SYMBOL_OR_EMOTICON`

Rows left untranslated after this pass must be defensible original-form/unresolved exceptions, not ordinary translatable concepts parked by a mechanical heuristic.

Do not force genuine proper names, codes, symbols, titles, companies, products, or opaque strings into artificial Japanese merely to raise coverage.

# Phase C — R3-style semantic resolution of the candidate set

Reuse the **quality method** proven by Issue #41 `PASS_PILOT`; do not reopen its sample/state.

For each candidate needing semantic review preserve, as applicable:
- canonical identity/scope
- count/cardinality
- actor/ownership
- target/body-site
- action vs state
- intrinsic relation / pose / spatial requirement
- required modifiers/qualifiers / meaning width

Evidence order:
1. exact-canonical trusted Japanese evidence
2. exact-canonical local authoritative assets / exact identity references
3. exact-canonical semantic evidence already frozen by R3/#41 where applicable
4. directly traceable authoritative meaning reference when ambiguity remains
5. only then conservative generated wording

HIGH/CRITICAL ambiguity without sufficient exact-canonical evidence must not auto-READY.

# Final outcomes

Every row entering the reconciliation candidate set must end as either:

- `JA_ACCEPT_EXISTING` / `JA_ACCEPT_MACHINE` / `JA_ACCEPT_STRICT`
  - real Japanese UI wording
  - semantically adequate for glance-understanding
  - evidence/reason recorded

or

- `ENGLISH_FALLBACK_EXCEPTION`
  - defensible identity/code/symbol/product/proper-name exception, or
  - genuinely unresolved after conservative evidence review
  - explicit reason recorded

No generic REVIEW/PENDING may remain.

# Hard invariants

1. Final table exactly 30,629 unique canonicals.
2. Canonical English unchanged and authoritative.
3. Production data untouched.
4. No wrapper fake Japanese.
5. No accepted Chinese-only wording masquerading as Japanese.
6. No accepted raw-English semantic-core leakage except explicit allowed acronym/code/proper qualifier cases.
7. No malformed accepted display/search label.
8. No material actor/target/body/direction/count/action-state/negation/qualifier reversal or omission.
9. No per-token multi-word composition accepted merely because every token has a dictionary entry.
10. No blanket `CJK = Japanese` rule.
11. No blanket `ASCII = invalid` rule.
12. No giant exact-map expansion just to preserve coverage.
13. Honest lower coverage is preferable to misleading Japanese.
14. Remaining fallback ledger count-checked and reason-classified.
15. `REVIEW/PENDING = 0`.
16. Deterministic replay PASS.
17. Protected boundary PASS / `production_modified: NO`.

# Mandatory fixtures

Must explicitly test at least:

Chinese/non-Japanese:
- `:p`
- `^_^`
- `anal_object_insertion`
- `imminent_anal`
- `presenting_own_anus`
- `presenting_own_ass`
- `presenting_own_pussy`
- `vibrator_bulge`
- `vibrator_cord`
- `vibrator_in_anus`
- `vibrator_on_clitoris`
- `vibrator_on_nipple`
- `vibrator_on_penis`

Raw-English/malformed:
- `presenting_own_foot`
- `a_(phrase)`

Semantic scope:
- `imminent_penetration`
- `android`

Preserve prior correct repairs:
- `kickstand` -> `キックスタンド`
- `legjob` -> `レッグジョブ`
- `dominator_(bdsm)` -> `支配する側（BDSM）`
- `implied_cheating_(relationship)` -> `浮気を示唆する関係`
- `alternate_ass_size_(larger)` -> `大きめの尻差分`
- `heavy_chromatic_aberration` -> `強い色収差`
- `no_magazine_(weapon)` -> `弾倉なし（武器）`
- `newt` -> `イモリ`
- `painting_fingernails` -> `爪に色を塗る`
- `hydraulic_press` -> `油圧プレス`
- `press_conference` -> `記者会見`
- `taking_notes` -> `メモを取る`

Also add allowed-original-form/Latin controls to prevent over-filtering.

# Outputs

Use a new root; do not overwrite old evidence as the only copy:
`translation_quarantine/full_accepted_quality_sweep_20260909/`

At minimum:
- `candidate_screen.jsonl`
- `accepted_revalidation.jsonl`
- `fallback_reconciliation.jsonl`
- `final_translation_table.csv`
- `final_translation_table.md`
- `coverage_recount_before_after.json`
- `language_quality_summary.json`
- `semantic_quality_summary.json`
- `fallback_summary.json`
- `replay_verification.json`
- `protected_boundary.json`
- `run_summary.json`
- `FINAL_REPORT.md`

Record deterministic counts for:
- accepted rows screened
- suspicious accepted rows by reason
- Chinese/non-Japanese candidates
- raw-English candidates
- malformed candidates
- semantic-scope candidates
- fallback rows revisited
- `PHRASE_SEMANTICS_UNRESOLVED` resolved to Japanese
- fallback rows retained by reason
- final Japanese display/search count and percentage
- final fallback count
- final state counts

# Tests

Required:
1. focused language/semantic/fallback reconciliation tests
2. previous Issue #36 bounded-wrapper regressions
3. relevant R3 / qualified-label regressions
4. deterministic replay
5. protected-boundary verification
6. full pytest

Full pytest reporting rule: if Windows TEMP ACL / `WinError 5` setup errors remain, report exact pass/setup-error counts and do not call the full suite PASS.

# Allowed writes

Only:
- `translation_quarantine/**`
- tests directly required for this #36 quarantine reconciliation

# Forbidden

Do not modify:
- production `data/**`
- `data/runtime/japanese_overlay.json`
- runtime production indexes
- canonical English identities
- Prompt / cooccur / recommendation behavior
- semantic-support production data
- generation metadata
- #32 data/verdicts
- #35 UI
- #41 artifacts/state except read-only evidence reuse
- `docs/project/CURRENT_DEV_TASK.md`
- main
- Stage10 production A/B

No production promotion in this task.

# Completion / stop

Commit and push implementation, tests, and quarantine evidence to `ui-ja/issue36-machine-convergence`, then STOP.

Report:
- execution start HEAD
- fixed source HEAD `1f069d...`
- final HEAD
- changed files/scope
- all deterministic counts above
- representative repairs
- remaining exception reason classes/counts
- replay verdict
- protected boundary verdict
- focused/regression/full pytest results
- production_modified
- explicit `promotion: NOT_AUTHORIZED`

A fresh independent ChatGPT audit is required before production promotion.
