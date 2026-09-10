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
- real Tk E2E baseline accepted

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

## Special-representative calibration direction

Generic `standing / sitting / long_hair / smile` evidence is plumbing-only and must not define production thresholds.

Current #30 representative design uses 32 cases × 4 images = planned 128 images. All planned images are screened first by WD14 / Kagami / CL Tagger v2.00, while human review is concentrated on protected-route anchors, evaluator exceptions and a small stratified AUTO-likely sample.

Representative calibration includes categories such as:
1. direct Special Core Entry presence/absence
2. rare / niche Special
3. relation / actor-target / body-site binding
4. multiple-Special simultaneous retention
5. support-tag ON/OFF affecting observability/visibility while Special identity stays fixed
6. canonical/Alias identity-sensitive behavior where relevant

Each pair follows **one experiment = one question**.

## Current remaining gates

### Gate A — #36 UI-JA V5 final convergence

Status: **ACTIVE**

Current route:
1. branch `ui-ja/issue36-relaxed-v5-chatgpt-repair`
2. preserve V4 as immutable evidence
3. split/process the 30,629-row table through the existing 31 audit shards
4. ChatGPT performs translation/semantic repair review directly
5. Codex/Luna is not used for translation-quality judgment or semantic audit in the current lane
6. repair clear defects only: non-Japanese/Chinese residue, raw English debris, obvious mistranslation, relation inversion, broken machine-composed labels
7. return every shard result/progress to GitHub/#36; shard chats are not source of truth
8. after all shards: integration/revalidation
9. if eligible: separate independent production-promotion audit
10. post-promotion real Windows/UI verification where required

Historical Issue #46 orchestration is superseded and must not be treated as the current execution path.

### Gate B — #34 remaining parent UI/search concerns

Status: **REMAINS**

#36 translation convergence is not identical to all #34 concerns.
Before #42 activation, material bilingual-search/search-noise/UI issues that can change the evaluated product must be completed or explicitly separated from the Stage10 Gate.

### Gate C — #30 final representative calibration

Status: **ACTIVE / CURRENT CORE DEV**

- finalize/review representative Special case manifest
- execute controlled 128-image calibration design as authorized by #30 task contract, not Stage10 production A/B
- compare WD14 / Kagami / CL Tagger v2.00 with human image-level judgments
- calibrate `AUTO / HUMAN REVIEW / BLOCKED`
- define only evidence-supported candidate `A_WIN / B_WIN`
- relation/binding and other structural-risk cases remain conservative human-review candidates unless evidence supports narrower automation
- preserve fixed-seed / actual Prompt / metadata traceability
- prioritize false-positive suppression over maximum automation rate

### Gate D — #42 product-purpose improvement pass

Status: **RESERVED / UI-JA-DATA GATED**

Dictionary freeze and #44 evaluator coverage prerequisites are satisfied.
Activate only after #30 representative calibration and material #36/#34 UI-JA/data homework are completed or explicitly separated.

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

### Gate E — #5 formal Prompt handoff

Status: **WAITS #30 + #42**

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

### Gate F — local protected-data maintenance #24

Status: **OPEN SAFETY DEBT / PARALLEL**

This is not the Stage10 experiment definition itself, but remains visible because GitHub is not a backup for local protected data.
Required: backup coverage/freshness, manifest, rebuildability, representative non-destructive restore, deletion guardrails.

## Canonical dependency order

Parallel now:
- `#30 representative calibration`
- `#36 V5 ChatGPT-led 31-shard repair/audit -> integration/revalidation -> independent promotion gate`
- cross-cutting/maintenance: `#34`, `#24`
- #44 remains ongoing only for scoped follow-up; its evaluator coverage Gate is complete

Then:
`#30 calibration -> #42 product-purpose improvement -> #5 formal Prompt handoff -> remaining final checks -> Stage10 production A/B`

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
- [x] #44 final evaluator coverage comparison
- [ ] #36 V5 31-shard repair/audit -> integration/revalidation -> independent promotion gate
- [ ] #34 material remaining UI/search concerns resolve or explicit separation
- [ ] #30 controlled representative calibration complete
- [ ] #42 product-purpose improvement pass
- [ ] #5 formal Prompt handoff
- [ ] A/B fixed conditions final definition
- [ ] model-family Prompt grammar differences preserved without unsupported flattening
- [ ] representative Special setでREVIEW-only human workflow確認
- [ ] final Stage10 start authorization

## Current state

Stage10 production A/B is **NOT STARTED**。

The dictionary validation/promotion/freeze lane and #44 evaluator desk coverage are complete. Immediate active lanes are #30 representative calibration preparation/execution and #36 V5 ChatGPT-led UI-JA repair. #42 waits on #30 plus material UI-JA/data completion or explicit separation. #5 waits on #30 + #42.

Current routing authority: `docs/project/CURRENT_STATE.md`.
