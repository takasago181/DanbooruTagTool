# Issue #36 — full accepted-quality + fallback reconciliation contract

Status: EXECUTION CONTRACT FOR CODEX / QUARANTINE ONLY

## Authority and fixed starting point

Read before doing any work:
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #36 latest comments, especially audit correction checkpoint `5599883613`
4. Issue #41 final `PASS_PILOT` checkpoint `5589825869` only as validated R3 quality-method evidence; **do not reopen or rerun Issue #41**
5. this contract

Required branch:
`ui-ja/issue36-machine-convergence`

Required starting HEAD:
`1f069d050909425dbcc5c2965951fd0c920a2205`

Current source artifact:
`translation_quarantine/bounded_wrapper_cleanup_20260909/final_translation_table.csv`

Current table facts at the fixed starting point:
- 30,629 unique canonicals
- 27,743 rows in `JA_ACCEPT_EXISTING` / `JA_ACCEPT_MACHINE` / `JA_ACCEPT_STRICT`
- 2,886 rows in `ENGLISH_FALLBACK_EXCEPTION`
- current stricter display/search recount: 25,277 / 30,629
- current fallback includes 1,677 `PHRASE_SEMANTICS_UNRESOLVED`
- production modified: NO

The previous `PASS_FOR_PROMOTION` is superseded by Issue #36 checkpoint `5599883613`. Promotion is **NOT_AUTHORIZED** until a new independent audit passes.

## User intent

The Japanese overlay exists so the user can glance at a tag and understand its meaning in Japanese.

Quality priorities:
1. semantic correctness
2. actually Japanese / readable Japanese
3. coverage
4. stylistic polish

Awkward Japanese is acceptable when meaning is clear. Misleading Japanese is not.

Do not preserve a high coverage number by accepting Chinese text, untranslated English semantic cores, malformed labels, or semantically over-compressed/wrong labels.

## Why this pass exists

The prior bounded wrapper cleanup correctly stopped token-concatenated multi-word false Japanese in its target set, but the merged table still contains older accepted rows outside that bounded cleanup with defects such as:

- `:p` -> `闭嘴吐舌`
- `^_^` -> `闭眼笑`
- `anal_object_insertion` -> `肛门物体插入`
- `imminent_anal` -> `即将插入肛门`
- `presenting_own_anus` -> `展示自己的肛门`
- `presenting_own_foot` -> `見せる・own・足`
- `vibrator_on_clitoris` -> `阴蒂上的震动器`
- `imminent_penetration` -> `事前`
- `android` -> `メカバレ`
- malformed forms such as `a_(phrase)` -> `フレーズ）`

The old broad CJK check `[ぁ-んァ-ン一-龥]` is not a language detector: Chinese Han text can pass it as if it were Japanese.

This execution must therefore reconcile the **whole accepted layer and the current fallback layer**, while avoiding a blind 30,629-row retranslation.

# Scope

## Phase A — deterministic screen of all 27,743 accepted rows

Screen every current `JA_ACCEPT_*` row. This is a **screen**, not automatic retranslation of all 27,743.

Create deterministic candidate reasons. At minimum detect:

### A1. Non-Japanese / Chinese-risk
Flag accepted rows when any of the following applies:
- simplified-Chinese-specific characters or known Chinese-only lexical forms occur;
- Chinese grammatical/function-word patterns strongly indicate Chinese wording;
- the label is Han-only and has no trusted Japanese provenance / explicit validation;
- the source route reused non-Japanese wording without language validation.

Important: do **not** treat all Han-only strings as invalid. Pure-kanji Japanese terms such as `肛門`, `妊娠検査`, etc. may be valid, but they require trusted Japanese evidence or explicit validation rather than a generic CJK-character test.

### A2. Raw-English semantic-core risk
Flag rows containing ASCII English semantic tokens in the Japanese display/search label, except explicitly permitted identity-bearing material such as:
- standard acronym/code (`BDSM`, `3D`, `FBI`, etc.)
- product/franchise/proper-name qualifier when the descriptive base is still glanceable Japanese
- canonical identity that is intentionally original-form and should instead be an exception when appropriate

Known fixture:
- `presenting_own_foot` must not remain `見せる・own・足`.

### A3. Malformed-label risk
Flag:
- unmatched / duplicated brackets or punctuation
- broken qualifier formatting
- wrapper remnants
- empty/near-empty descriptive body hidden by punctuation

Known fixture:
- `a_(phrase)` -> `フレーズ）` must not remain accepted as-is.

### A4. Semantic-scope risk
Flag accepted rows where the Japanese label may materially change or erase canonical meaning, including:
- actor / owner
- target / body site
- direction / spatial relation
- count / cardinality
- action vs state
- object vs action / noun vs verb
- negation
- required modifier / qualifier
- canonical concept width

Known fixtures:
- `imminent_penetration` -> `事前` is not sufficient.
- `android` -> `メカバレ` must be rechecked against exact canonical meaning.

Do not use the Japanese wording itself as semantic authority.

### A5. Route/source-risk screen
Independently surface accepted rows produced by historically weak routes such as token/lexical composition, lightweight reuse, machine direct translation, strict wording carryover, or any route that did not prove exact-canonical Japanese semantics.

Route risk is a review trigger, not an automatic failure. Pre-existing trusted Japanese labels can remain accepted when evidence supports them.

## Phase B — reconcile current 2,886 fallback rows

Do not assume every fallback is a true permanent exception.

### B1. Actively revisit all 1,677 `PHRASE_SEMANTICS_UNRESOLVED`
These are translation homework, not automatically "English is fine".

For each row:
- obtain/derive exact-canonical semantic scope using the same conservative evidence principles proven by Issue #41;
- produce a concise Japanese display/search candidate when meaning is supportable;
- accept only if phrase-level semantics are preserved;
- otherwise keep fallback with an explicit unresolved/evidence reason.

Do **not** fall back to per-token concatenation.

### B2. Validate the remaining exception classes
Screen all current:
- `PROPER_NAME_OR_QUALIFIED_LABEL`
- `PRODUCT_OR_SERVICE_NAME`
- `CODE_OR_PRODUCT_IDENTIFIER`
- `OPAQUE_SOURCE_STRING`
- `SYMBOL_OR_EMOTICON`

Goal: the rows left untranslated after this pass should be defensible original-form / unresolved exceptions, not ordinary translatable concepts accidentally parked by mechanical heuristics.

Do not force proper names, model codes, symbols, titles, companies, or genuinely opaque strings into artificial Japanese merely to raise coverage.

## Phase C — R3-style semantic resolution of the suspicious set

Reuse the **quality method** validated by Issue #41 `PASS_PILOT`; do not reopen its sample or state.

For each candidate needing semantic review, preserve the following dimensions as applicable:
- canonical identity/scope
- count/cardinality
- actor/ownership
- target/body-site
- action vs state
- intrinsic relation / pose / spatial requirement
- required modifiers/qualifiers / meaning width

Evidence order:
1. exact-canonical existing trusted Japanese evidence
2. exact-canonical local authoritative assets / exact identity references
3. exact-canonical semantic evidence already frozen by R3/#41 where applicable
4. directly traceable authoritative meaning reference when ambiguity remains
5. only then conservative generated wording

HIGH/CRITICAL ambiguity without sufficient exact-canonical evidence must not auto-READY.

# Required final state classes

Each current accepted/fallback row that enters the reconciliation candidate set must end in exactly one auditable outcome:

- `JA_ACCEPT_EXISTING` / `JA_ACCEPT_MACHINE` / `JA_ACCEPT_STRICT`
  - real Japanese UI wording
  - semantically adequate for glance-understanding
  - evidence/reason recorded

or

- `ENGLISH_FALLBACK_EXCEPTION`
  - true identity/code/symbol/product/proper-name exception, or
  - genuinely unresolved after conservative evidence review
  - explicit reason recorded

No generic REVIEW/PENDING may remain in the final artifact.

# Hard acceptance invariants

1. Exactly 30,629 unique canonicals in final merged table.
2. Canonical English identity unchanged and authoritative.
3. No production data modification.
4. No wrapper-style fake Japanese.
5. No accepted Chinese-only wording masquerading as Japanese.
6. No accepted raw-English semantic-core leakage except explicit allowed acronym/code/proper qualifier cases.
7. No malformed accepted display/search labels.
8. No material actor/target/body/direction/count/action-state/negation/qualifier reversal or omission.
9. No per-token multi-word composition accepted merely because every word has a dictionary entry.
10. No blanket `CJK character = Japanese` rule.
11. No blanket `ASCII = invalid` rule.
12. No giant exact-map expansion merely to preserve coverage.
13. Honest lower coverage is preferable to misleading Japanese.
14. Remaining fallback ledger must be count-checked and reason-classified.
15. `REVIEW/PENDING = 0` in final artifact.
16. Deterministic replay PASS.
17. Protected boundary PASS / `production_modified: NO`.

# Mandatory regression fixtures

The final tests must explicitly cover at least these defects:

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

Preserve previous correct repairs:
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

Allowed-original-form / Latin controls must also be tested so over-filtering does not occur.

# Required outputs

Use a new quarantine root; do not overwrite the prior evidence as the only copy.
Preferred root:
`translation_quarantine/full_accepted_quality_sweep_20260909/`

At minimum produce:
- `candidate_screen.jsonl` — every screened/reconciliation candidate with trigger reason(s)
- `accepted_revalidation.jsonl` — reviewed accepted rows + evidence/reason
- `fallback_reconciliation.jsonl` — old/new fallback classification and reason
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
- suspicious accepted candidates by reason class
- Chinese/non-Japanese candidates
- raw-English candidates
- malformed candidates
- semantic-scope candidates
- current fallback rows revisited
- `PHRASE_SEMANTICS_UNRESOLVED` resolved to Japanese
- fallback rows retained and reason classes
- final Japanese display/search count and percentage
- final fallback count
- final state counts

# Tests

Required:
1. focused tests for screen/language/semantic/fallback reconciliation
2. previous Issue #36 bounded-wrapper regressions
3. relevant R3 / qualified-label regressions
4. deterministic replay
5. protected-boundary verification
6. full pytest

Full pytest reporting rule:
- if Windows TEMP ACL / `WinError 5` setup errors remain, report exact passed/setup-error counts;
- never call the full suite PASS unless it actually exits cleanly without those setup errors.

# Allowed writes

Only:
- `translation_quarantine/**`
- tests directly required for this #36 quarantine reconciliation

# Forbidden

Do not modify:
- production `data/**`
- `data/runtime/japanese_overlay.json`
- runtime overlay / production indexes
- canonical English identities
- Prompt / cooccur / recommendation behavior
- semantic-support production data
- generation metadata
- Issue #32 data/verdicts
- Issue #35 UI
- Issue #41 artifacts/state except read-only evidence reuse
- `docs/project/CURRENT_DEV_TASK.md`
- main
- Stage10 production A/B

Do not perform production promotion in this task.

# Completion / stop condition

Commit and push the reconciliation implementation, tests, and all quarantine evidence to `ui-ja/issue36-machine-convergence`.

Then STOP and report:
- starting HEAD
- final HEAD
- changed files/scope
- all deterministic counts listed above
- representative repaired rows
- remaining exception classes and counts
- replay verdict
- protected boundary verdict
- focused/regression/full pytest results
- production_modified
- explicit `promotion: NOT_AUTHORIZED`

A fresh independent audit by ChatGPT is required before production promotion.
