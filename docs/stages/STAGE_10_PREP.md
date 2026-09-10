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

### Issue #30 representative evaluator calibration

**SATISFIED / COMPLETED / HANDOFF READY**

Infrastructure baseline:
- Forge Neo API `neo-2.29`
- fixed model baseline `waiIllustriousSDXL_v170` / hash `f116b0c78f`
- generation -> PNG SHA-256 -> png-info -> evaluator raw output path verified

Controlled pilot:
- 32 representative Special cases × 4 = 128 unique images
- WD14 128/128
- Kagami 128/128
- CL v2.00 128/128
- no Stage10 production A/B
- no 2,788-image sweep
- no production `data/**` / #32 / canonical change

Overlapping screening counts:
- LOW_CONFIDENCE: 93
- RELATION_OR_BINDING: 92
- COMPONENT_ONLY: 84
- DISAGREEMENT: 38
- BLOCKED: 20
- HIGH_CONFIDENCE_AUTO_LIKELY: 1

Minimal human review:
- 19 high-information images
- target present 16 / absent 1 / unclear 2
- provisional AUTO-support 8
- HUMAN_REVIEW_ONLY 9
- BLOCKED 2
- UNRESOLVED 1

Final #30 policy:
- Taggers remain assistive triage, not complete Special semantic authority.
- direct / non-relation / simple unary may remain optional targeted-validation candidates.
- relation/binding / actor-object / body-site / quantity / spatial / insertion / contact / restraint / compound / component-only / disagreement / low-confidence default to HUMAN REVIEW.
- gray/unreadable/corrupt/hash/metadata/provenance failures are BLOCKED before semantic scoring.
- invalid target/contrast generation is experiment-validity failure, not evaluator failure.

Important observed failures:
- invalid contrast realization (`exposed genitals` contrast)
- gray/unobservable image artifact
- body-site ambiguity (`anal object insertion`)
- restraint-state ambiguity (`bound penis`)

Full restore/handoff:
`docs/project/ISSUE30_HANDOFF_20260910.md`

## Current remaining gates

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

### Gate C — #30 final representative calibration

Status: **SATISFIED / COMPLETED**

Carry-forward evaluator rule:
- use Taggers for pre-screening, disagreement/low-confidence detection, review prioritization and narrow simple-unary support only
- do not use direct tag detection as proof of structural Special semantics
- do not restart the 128-image pilot without a narrow regression/evaluator-change reason

### Gate D — #42 product-purpose improvement pass

Status: **RESERVED / #30 SATISFIED / UI-JA-SEARCH GATED**

Satisfied:
- dictionary freeze
- #44 evaluator coverage
- #30 representative calibration

Still required before activation:
- #36 V5 material UI-JA/data homework complete or explicitly separated
- #34 material search/UI concerns complete or explicitly separated

#42 must consume #30 results as:
- Tagger-assisted triage, not full AUTO
- HUMAN REVIEW boundary for structural Special semantics
- artifact-quality gate before semantic scoring
- experiment-validity failure separated from evaluator failure
- manual-work reduction by abstention/prioritization rather than forced binary verdict

Review targets remain:
- Japanese intent variation/search robustness
- Special/support conflicts
- model-family ineffective/harmful guidance
- failure diagnosis
- Prompt bloat/pruning
- minimum sufficient Prompt
- optional deterministic local history
- parked REVIEW/IMAGE_TEST_REQUIRED questions requiring controlled images

Final verdict: `READY_FOR_STAGE10_EVALUATION` or `HOLD_PRE_STAGE10`.

### Gate E — #5 formal Prompt handoff

Status: **WAITS #42**

#30 prerequisite is now satisfied.
Formal handoff must integrate:
- frozen Special Core Dictionary identity/count
- evaluator capability and HUMAN REVIEW boundary
- #42 Prompt-design changes / IMAGE_TEST_REQUIRED questions
- one-question experiment isolation
- model-family differences
- A/B fixed conditions
- canonical-English final Prompt payload

### Gate F — local protected-data maintenance #24

Status: **OPEN SAFETY DEBT / PARALLEL**

Required: backup coverage/freshness, manifest, rebuildability, representative non-destructive restore, deletion guardrails.

## Canonical dependency order

Parallel now:
- `#36 V5 repair/audit -> integration/revalidation -> independent promotion gate`
- `#34 bilingual search relevance`
- `#24 protected-data safety`
- current core DEV: `NONE / MANAGEMENT_HANDOFF`

#30 is complete.

Then, when #36/#34 material work is complete or explicitly separated:
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
- [x] #30 controlled representative calibration complete
- [x] #30 Tagger-assisted triage / HUMAN REVIEW boundary defined
- [ ] #36 V5 repair/audit -> integration/revalidation -> independent promotion gate
- [ ] #34 material remaining UI/search concerns resolve or explicit separation
- [ ] #42 product-purpose improvement pass
- [ ] #5 formal Prompt handoff
- [ ] A/B fixed conditions final definition
- [ ] model-family Prompt grammar differences preserved without unsupported flattening
- [ ] final Stage10 start authorization

## Current state

Stage10 production A/B is **NOT STARTED**。

#30 is complete and no core DEV is currently selected. #42 is the intended next product-purpose pass once #36/#34 material prerequisites are complete or explicitly separated.

Current routing authority: `docs/project/CURRENT_STATE.md`.
