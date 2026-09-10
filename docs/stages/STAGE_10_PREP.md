# STAGE 10 PREP

最終更新: 2026-09-10

## 目的

Special Core Dictionaryの機能を実画像A/B比較で検証する前に、残るデータ/UI/evaluator/Prompt Gateを完了し、Stage10本番を再現可能・低手作業・評価可能な状態へする。

Stage10 production A/Bは**未開始**。

## 固定原則

- 普段の「良い画像を作るPrompt」とcontrolled test Promptを分ける。
- 1実験につき原則1疑問。
- 比較対象以外の条件を固定する。
- model family差を保持する。
- actual Prompt / seed / model / settings / PNG metadataを追跡可能にする。
- Stage10比較自動化は external / existing tool first。不足箇所だけ薄いglue/harnessを追加する。
- WD14 / Kagami / CL等TaggerをSpecial Core Dictionaryの完全なground truthとして扱わない。
- unsupported / low-confidence evaluator caseはFAILではなくREVIEWへ送る。
- required metadata/traceability/infrastructure欠損はBLOCKED。
- simple tag用thresholdをrelation/composite/rare Specialや別model familyへ共通適用しない。
- REVIEW / IMAGE_TEST_REQUIREDを数値上の都合でPASSへ押し込まない。
- runtime LLM依存を追加しない。

## Completed upstream gates

### Stage9 / E2E

- Stage9A PASS
- Stage9B PASS / independent audit PASS
- Stage9C PASS
- Stage9D PASS
- Stage9 overall Gate PASS / completed
- Issue #28 automated E2E PASS / completed

### Forge Neo comparison environment — Issue #6

**PASS_WITH_NOTE / completed**

- Multi Prompt Slots fixed SHA: `b3f45b17e5a24a20b4fa04edac74e6a4fec23dfe`
- Forge Neo Infinite Image Browsing fixed SHA: `ced039479c2e1463c9bdb136d355e01b3dfc9279`
- fixed-seed A/B: PASS
- generated-image Prompt/PNG metadata traceability: PASS
- regular-generation regression: PASS

### Special Core Dictionary validation / promotion / freeze

**SATISFIED / completed**

- #32 full 2,788-entry validation completed
- #48 independent promotion audit completed
- #49 audited production-safe fixes promoted and post-write audited
- #43 formal concept naming/freeze completed
- formal concept: `Special Core Dictionary`
- production row count / unique identity / order: 2,788 / 2,788 / unchanged

Parked evidence remains available:
- Special REVIEW: 305
- Special IMAGE_TEST_REQUIRED: 17
- semantic-support IMAGE_TEST_REQUIRED: 33 rows

### Issue #44 evaluator coverage

**SATISFIED / HANDOFF COMPLETE**

- WD14 direct: 658 / 2,788 (23.60%)
- Kagami direct: 1,412 / 2,788 (50.65%)
- CL Tagger v2.00 direct: 1,704 / 2,788 (61.12%)
- 3-evaluator direct union: 1,725 / 2,788 (61.87%)
- observable including components: 1,957 / 2,788 (70.19%)
- AUTO_CANDIDATE 939 / REVIEW_REQUIRED 1,018 / BLOCKED 831
- relation/binding structural risk: 918

`AUTO_CANDIDATE` is calibration candidate only, not production automatic approval.

### Issue #30 Phase 1 representative evaluator calibration

**SATISFIED / COMPLETED / FROZEN EVIDENCE**

Infrastructure baseline:
- Forge Neo API `neo-2.29`
- fixed model baseline `waiIllustriousSDXL_v170` / hash `f116b0c78f`
- generation -> PNG SHA-256 -> png-info -> evaluator raw output path verified

Controlled pilot:
- 32 representative Special cases × 4 = 128 unique images
- WD14 128/128
- Kagami 128/128
- CL v2.00 128/128
- minimal human review 19
- provisional AUTO-support 8 / HUMAN_REVIEW_ONLY 9 / BLOCKED 2 / UNRESOLVED 1

Frozen policy:
- Taggers remain assistive triage, not complete Special semantic authority.
- direct / non-relation / simple unary may remain optional targeted-validation candidates.
- relation/binding / actor-object / body-site / quantity / spatial / insertion / contact / restraint / compound / component-only / disagreement / low-confidence default to HUMAN REVIEW.
- gray/unreadable/corrupt/hash/metadata/provenance failures are BLOCKED before semantic scoring.
- invalid target/contrast generation is experiment-validity failure, not evaluator failure.

Phase 1 restore:
- `docs/project/ISSUE30_HANDOFF_20260910.md`

## Current remaining gates / active refinements

### Gate A — #36 UI-JA V5 final convergence

Status: **ACTIVE**

Current route:
- branch `ui-ja/issue36-relaxed-v5-chatgpt-repair`
- preserve V4 as immutable evidence
- process 30,629-row table through existing 31 audit shards
- ChatGPT-led translation/semantic repair
- after all shards: integration/revalidation -> separate independent production-promotion gate

Historical Issue #46 orchestration is superseded.

### Gate B — #34 remaining parent UI/search concerns

Status: **REMAINS**

Before #42 activation, material bilingual-search/search-noise/UI issues that can change evaluated product behavior must be completed or explicitly separated from the Stage10 Gate.

### Refinement C — #30 Phase 2 targeted evaluator refinement

Status: **ACTIVE / CURRENT CORE DEV / OPTIONAL PRE-#42 IMPROVEMENT**

Phase 2 does not invalidate the completed Phase 1 Gate and does not restart broad calibration.

Restore:
- `docs/project/ISSUE30_PHASE2_HANDOFF_20260910.md`

Scope:
- existing 128-image raw outputs / metadata first
- direct / non-relation / simple-unary threshold/agreement refinement
- review prioritization / abstention
- artifact-quality gate
- experiment-validity checks
- additional evaluator / deterministic non-LLM signal only if uniquely useful
- new images only for the smallest explicitly justified targeted question

Do not:
- rerun original 128-image pilot wholesale
- run 2,788-image sweep
- start Stage10 production A/B
- weaken HUMAN REVIEW boundary for structural Special semantics without explicit evidence

Phase 2 stops on diminishing returns. Complexity must not exceed realistic user-work reduction.

### Gate D — #42 product-purpose improvement pass

Status: **RESERVED / #30 PHASE1 SATISFIED / UI-JA-SEARCH GATED**

Satisfied:
- dictionary freeze
- #44 evaluator coverage
- #30 Phase 1 representative calibration

Still required before activation:
- #36 V5 material UI-JA/data homework complete or explicitly separated
- #34 material search/UI concerns complete or explicitly separated

#30 Phase 2 is an optional refinement running during this wait. It must hand off any evidence-backed delta before #42 executes, but Phase 2 itself does not replace the #36/#34 Gate.

#42 must consume #30 results as:
- Tagger-assisted triage, not full AUTO
- HUMAN REVIEW boundary for structural Special semantics
- artifact-quality gate before semantic scoring
- experiment-validity failure separated from evaluator failure
- manual-work reduction by abstention/prioritization rather than forced binary verdict

### Gate E — #5 formal Prompt handoff

Status: **WAITS #42**

#30 Phase 1 prerequisite is satisfied. Any adopted Phase 2 delta must be included before formal Stage10 Prompt handoff is finalized.

### Gate F — local protected-data maintenance #24

Status: **OPEN SAFETY DEBT / PARALLEL**

Required: backup coverage/freshness, manifest, rebuildability, representative non-destructive restore, deletion guardrails.

## Canonical dependency order

Parallel now:
- `#30 Phase 2 targeted evaluator refinement`
- `#36 V5 repair/audit -> integration/revalidation -> independent promotion gate`
- `#34 bilingual search relevance`
- `#24 protected-data safety`

Then, when #36/#34 material work is complete or explicitly separated and #30 Phase 2 has either completed or been explicitly stopped:
`#42 product-purpose improvement -> #5 formal Prompt handoff -> remaining final checks -> Stage10 production A/B`

## Stage10開始前チェック

- [x] Stage9 overall Gate完了
- [x] Automated E2E functional test PASS（#28）
- [x] Forge Neo比較環境導入・動作確認（#6）
- [x] Forge API -> fixed-seed A/B -> PNG metadata -> evaluator raw pipeline
- [x] Special Core Dictionary full validation（#32）
- [x] production-safe fix promotion + audit（#48/#49）
- [x] final Special Core Dictionary naming/freeze（#43）
- [x] #44 final evaluator coverage comparison
- [x] #30 Phase 1 controlled representative calibration complete
- [x] #30 Phase 1 Tagger-assisted triage / HUMAN REVIEW boundary defined
- [ ] #30 Phase 2 targeted refinement complete or explicitly stop on diminishing returns
- [ ] #36 V5 repair/audit -> integration/revalidation -> independent promotion gate
- [ ] #34 material remaining UI/search concerns resolve or explicit separation
- [ ] #42 product-purpose improvement pass
- [ ] #5 formal Prompt handoff
- [ ] A/B fixed conditions final definition
- [ ] model-family Prompt grammar differences preserved without unsupported flattening
- [ ] final Stage10 start authorization

## Current state

Stage10 production A/B is **NOT STARTED**。

Current core DEV is Issue #30 Phase 2 targeted refinement. #36 remains independently active and is still a material prerequisite for #42 unless explicitly separated. #42 is not active yet.

Current routing authority: `docs/project/CURRENT_STATE.md`.
