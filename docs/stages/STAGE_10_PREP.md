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
- WD14その他TaggerをSpecial Core Dictionaryの完全なground truthとして扱わない。
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
- real Tk E2E baseline: full suite 285 passed / exit 0 at accepted checkpoint

### Forge Neo comparison environment — Issue #6

**PASS_WITH_NOTE / completed**

- Multi Prompt Slots fixed SHA: `b3f45b17e5a24a20b4fa04edac74e6a4fec23dfe`
- Forge Neo Infinite Image Browsing fixed SHA: `ced039479c2e1463c9bdb136d355e01b3dfc9279`
- fixed-seed A/B: PASS
- generated-image Prompt/PNG metadata traceability: PASS
- regular-generation regression: PASS

### Issue #30 infrastructure baseline

**PASS_PIPELINE**

- evidence branch: `codex/issue30-automation-dry-run-20260908`
- evidence commit: `f2fc7acb15f996630c9f008284d80cf3261fb32f`
- Forge Neo API `neo-2.29`
- fixed model baseline `waiIllustriousSDXL_v170` / hash `f116b0c78f`
- generation -> PNG SHA-256 -> `/sdapi/v1/png-info` -> evaluator raw output path demonstrated
- user manual operations: 0 for demonstrated plumbing path
- generic golden set retained as plumbing/evaluator fixture only
- Special-representative routing direction adopted via #37

### Special Core Dictionary validation / promotion / freeze

**SATISFIED / completed**

- #32 full 2,788-entry validation completed
- #48 independent promotion audit completed
- #49 audited production-safe fixes promoted and post-write audited
- #43 formal concept naming/freeze completed
- formal concept: `Special Core Dictionary`
- historical/snapshot compatibility identifier: `Special2788`
- user-selected nucleus: `Core Tag Set`
- production profile SHA-256: `55490940378e15d8e41454e701d0c202abbab307a08fb6e56841171e0edec1fd`
- rows / unique SpecialID / order: 2,788 / 2,788 / unchanged

Parked evidence remains available:
- Special REVIEW: 305
- Special IMAGE_TEST_REQUIRED: 17
- semantic-support IMAGE_TEST_REQUIRED: 33 rows

## Special-representative calibration direction

Generic `standing / sitting / long_hair / smile` evidence is plumbing-only and must not define production thresholds.

Representative calibration must include categories such as:

1. direct Special Core Entry presence/absence
2. rare / niche Special
3. relation / actor-target / body-site binding
4. multiple-Special simultaneous retention
5. support-tag ON/OFF affecting observability/visibility while Special identity stays fixed
6. canonical/Alias identity-sensitive behavior where relevant

Each pair follows **one experiment = one question**.

For unusual-anatomy Special tests, anatomy-sensitive Negative Prompt terms are not mechanically fixed. Their interaction with the target Special is a separate controlled question.

## Current remaining gates

### Gate A — #46 -> #36 UI-JA final convergence

Status: **READY NOW / REMAINS**

1. #46 run/resume authorized 30,629 orchestration
2. durable Resolver / Challenger / Repair / Final-Audit artifacts returned to #36
3. #36 V3.1 revalidation
4. if eligible, separate independent production-promotion audit
5. post-promotion real Windows/UI verification where required

#46 full-execution authorization is not production-promotion authority.

### Gate B — #44 evaluator coverage

Status: **READY NOW / REMAINS**

Final dictionary freeze prerequisite is satisfied.

Compare finalized 2,788-entry Special Core Dictionary against:
- WD14 / `wd-eva02-large-tagger-v3`
- Kagami-24k
- CL Tagger v2 stable/fixed release

At minimum return:
- raw vocabulary coverage
- Core / Extended / Alias / Semantic coverage separately where applicable
- post-count-band coverage
- raw Alias coverage vs canonical-target coverage
- representative-image evaluator disagreement when available
- evaluator capability limitations relevant to AUTO/REVIEW routing

### Gate C — #34 remaining parent UI/search concerns

Status: **REMAINS**

#36 translation convergence is not identical to all #34 concerns.
Before #42 activation, material bilingual-search/search-noise/UI issues that can change the evaluated product must be completed or explicitly separated from the Stage10 Gate.

### Gate D — #30 final representative calibration

Status: **WAITS #44 COVERAGE**

After Gate B:
- finalize representative Special case list
- assign evaluator responsibility by capability
- calibrate `AUTO / REVIEW / BLOCKED`
- define only evidence-supported candidate `A_WIN / B_WIN`
- verify user primarily handles REVIEW cases
- preserve fixed-seed / actual Prompt / metadata traceability

### Gate E — #42 product-purpose improvement pass

Status: **RESERVED / UI-JA-DATA GATED**

Dictionary freeze prerequisite is satisfied.
Activate only after material #36/#34 UI-JA/data homework is completed or explicitly separated.

Review:
- Japanese intent variation/search robustness
- Special/support conflicts
- model-family ineffective/harmful guidance
- failure diagnosis
- Prompt bloat/pruning
- minimum sufficient Prompt
- simple deterministic local success/failure history if useful
- parked REVIEW/IMAGE_TEST_REQUIRED questions that need controlled images

Final verdict: `READY_FOR_STAGE10_EVALUATION` or `HOLD_PRE_STAGE10`.

### Gate F — #5 formal Prompt handoff

Status: **WAITS #44 + #30 + #42**

Formal handoff must integrate:
- frozen Special Core Dictionary snapshot identity/count/hash
- evaluator coverage/capability
- representative cases and routing
- #42 Prompt-design changes / IMAGE_TEST_REQUIRED questions
- one-question experiment isolation
- model-family differences
- A/B fixed conditions
- human REVIEW boundary
- canonical-English final Prompt payload

#42 completes before #5 is finalized.

### Gate G — local protected-data maintenance #24

Status: **OPEN SAFETY DEBT / PARALLEL**

This is not the Stage10 experiment definition itself, but it remains visible because GitHub is not a backup for local protected data.
Required: backup coverage/freshness, manifest, rebuildability, representative non-destructive restore, deletion guardrails.

## Canonical dependency order

Parallel now:

- `#46 -> #36 -> independent UI-JA promotion gate`
- `#44 evaluator coverage`
- cross-cutting/maintenance: `#34`, `#24`

Then:

`#44 coverage -> #30 representative calibration -> #42 product-purpose improvement -> #5 formal Prompt handoff -> remaining final checks -> Stage10 production A/B`

#42 additionally requires material #34/#36 UI-JA/data homework to be completed or explicitly separated.

## Stage10開始前チェック

- [x] Stage9 overall Gate完了
- [x] Automated E2E functional test PASS（#28）
- [x] Forge Neo比較環境導入・動作確認（#6）
- [x] Forge API -> fixed-seed A/B -> PNG actual metadata -> evaluator raw pipeline（#30 baseline）
- [x] generic golden setをplumbing fixtureへ降格
- [x] Special-representative test/routing direction採用（#37）
- [x] Special Core Dictionary full validation（#32）
- [x] production-safe fix promotion + audit（#48/#49）
- [x] final Special Core Dictionary naming/freeze（#43）
- [ ] #46 full execution -> #36 revalidation -> independent promotion gate
- [ ] #34 material remaining UI/search concerns resolve or explicit separation
- [ ] #44 final evaluator coverage comparison
- [ ] #30 final representative case selection
- [ ] #30 capability-aware AUTO/REVIEW/BLOCKED calibration
- [ ] #42 product-purpose improvement pass
- [ ] #5 formal Prompt handoff
- [ ] A/B fixed conditions final definition
- [ ] model-family Prompt grammar differences preserved without unsupported flattening
- [ ] representative Special setでREVIEW-only human workflow確認
- [ ] final Stage10 start authorization

## Current state

Stage10 production A/B is **NOT STARTED**.

The dictionary-validation/promotion/freeze lane is complete. The immediate executable lanes are #46/#36 UI-JA and #44 evaluator coverage. #30 waits on #44. #42 waits on material UI-JA/data completion or explicit separation. #5 final handoff waits on #44 + #30 + #42.

Current routing authority: `docs/project/CURRENT_STATE.md`.
