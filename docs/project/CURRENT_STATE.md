# CURRENT STATE

最終更新: 2026-09-10

## Current Stage

Stage 9 overall Gate 完了 / Stage10 準備Gate実施中 / automated E2E PASS / Special Core Dictionary freeze 完了

本ファイルは現在地のrouting正本。task contract / completion criteria / result evidenceは対応Issueを正本とし、更新競合時はlive Issue / branch / checkpointを優先して同期する。

## Current Core DEV

**NONE / MANAGEMENT_HANDOFF**

Issue #30 representative evaluator calibrationは完了し、Taggerの最終役割・human-review境界・失敗分類をhandoff化した。
次のcore DEVを管理が明示選択するまでCodexは新しいDEVを推測して開始しない。

Issue #42は次のproduct-purpose improvement候補だが、#36 V5 / #34 material UI-JA・search concernの完了またはStage10 Gateからの明示分離が残るため、現時点では自動activateしない。

Issue #30 completion handoff:
- `docs/project/ISSUE30_HANDOFF_20260910.md`
- branch `codex/issue30-calibration-design`
- pilot/cache commit `8ff9ef142e6b7c25ae601589a82c136d96748991`
- minimal review result commit `5ea66ec69a7b9aeefde359997428ca5e243daf4b`

## Workstreams Registry

| TEAM_ID | Status | Issue / scope | Branch / locator | Current phase | Restore anchor |
| --- | --- | --- | --- | --- | --- |
| `DICT:#32:R2` | COMPLETED / PROMOTED / CARRY_FORWARD_ONLY | #32 Special Core Dictionary historical validation | `dict-validation/quarantine` | 2,788/2,788 validation complete。approved effective subsetは#49でproduction反映済み。REVIEW/ITRはparked evidenceとして保持 | Issue #32 + #48 + #49 + #43 freeze |
| `KNOWLEDGE:#44` | ACTIVE / ONGOING / COVERAGE_COMPLETE | persistent generation knowledge corpus | `knowledge/generation-corpus` | 2,788 × WD14 / Kagami-24k / CL Tagger v2.00 desk coverage完了。#30 handoff済み。必要な追加知識/校正返却を担当 | Issue #44 correction checkpoint `5614819866` + commit `557aa4c` |
| `UIJA:#36:V5` | ACTIVE / CHATGPT_LED_REPAIR | Japanese overlay final convergence / semantic repair | `ui-ja/issue36-relaxed-v5-chatgpt-repair` | 30,629 rowsを既存31 audit shardsへ分割し、ChatGPT側で明確な翻訳・意味欠陥を修正/監査。V4はimmutable evidenceとして保持 | Issue #36 latest V5 checkpoint |
| `UIJA-ORCH:#46` | SUPERSEDED / CLOSED | historical independent Codex orchestration for V3.1/V4 | Issue #46 / `codex/issue46-orchestrator` | historical evidence only | Issue #46 superseded checkpoint |
| `UIJA-PARENT:#34` | OPEN / CROSS-CUTTING / SEARCH_RELEVANCE_REMAINS | bilingual search relevance and remaining parent UI concerns | Issue #34 | `anal -> piano/analog...` 等のsubstring/fuzzy search noiseが主要残件 | Issue #34 current body |
| `TEMP:#30` | COMPLETED / CLOSED-CANDIDATE / HANDOFF_READY | Forge Neo evaluator calibration & A/B automation | `codex/issue30-calibration-design` | 128-image controlled pilot + 19-image minimal review完了。Tagger-assisted triage policy確定 | `docs/project/ISSUE30_HANDOFF_20260910.md` |
| `PREP:#42` | RESERVED / GATED | Stage10 pre-evaluation product-purpose improvement | Issue #42 | #30 prerequisite satisfied。#36/#34 material homework完了または明示分離後にactivate | Issue #42 |
| `PROMPT:#5` | GATED | Stage10 formal Prompt handoff | Issue #5 | #42 result後にformal handoff | Issue #5 |
| `MAINT:#24` | OPEN / SAFETY_DEBT | Local protected data backup / restore verification | Issue #24 | GitHub外protected dataのbackup/restore・manifest・非破壊restore検証 | Issue #24 |

## Completed

- Stage9 overall Gate: **PASS / completed**
- Issue #28 automated E2E: **PASS / completed**
- Issue #6 Forge Neo comparison environment: **PASS_WITH_NOTE / completed**
- Issue #35 Japanese-first desktop UI: **ISSUE35_FINAL_COMPLETION_PASS / completed / closed**
- Issue #32 dictionary validation: **completed**
- Issue #48 independent final promotion audit: **completed**
- Issue #49 production promotion: **completed / post-write audited / merged**
  - changed production cells: 246 across 171 Special rows
  - exact row count / identity / order: 2,788 maintained
- Issue #43 Special Core Dictionary naming/freeze: **PASS_ISSUE43_FREEZE / completed**
- Issue #44 final evaluator desk coverage: **SATISFIED / HANDOFF COMPLETE**
  - WD14 direct: 658 / 2,788 (23.60%)
  - Kagami direct: 1,412 / 2,788 (50.65%)
  - CL Tagger v2.00 direct: 1,704 / 2,788 (61.12%)
  - 3-evaluator direct union: 1,725 / 2,788 (61.87%)
  - observable including components: 1,957 / 2,788 (70.19%)
  - AUTO_CANDIDATE 939 / REVIEW_REQUIRED 1,018 / BLOCKED 831
  - relation/binding structural risk: 918
- Issue #30 representative evaluator calibration: **COMPLETED / HANDOFF READY**
  - 32 Special cases × 4 = 128 unique images
  - WD14 / Kagami / CL: each 128/128 executed
  - overlapping screening: LOW_CONFIDENCE 93 / RELATION_OR_BINDING 92 / COMPONENT_ONLY 84 / DISAGREEMENT 38 / BLOCKED 20 / HIGH_CONFIDENCE_AUTO_LIKELY 1
  - minimal human review: 19 high-information images
  - human result: target present 16 / absent 1 / unclear 2
  - provisional AUTO-support 8 / HUMAN_REVIEW_ONLY 9 / BLOCKED 2 / UNRESOLVED 1
  - final policy: Taggers are assistive triage only; broad Special semantic AUTO is rejected
  - direct/non-relation/simple-unary may remain optional targeted-validation candidates
  - relation/binding/actor-object/body-site/count/spatial/insertion/contact/restraint/compound/component-only/disagreement/low-confidence default to HUMAN REVIEW
  - gray/unobservable/metadata failures -> artifact BLOCKED before semantic scoring
  - invalid contrast -> generation/experiment-validity failure, not evaluator failure
- Issue #46 historical orchestration: **superseded / closed**

## Frozen terminology

- formal concept: **`Special Core Dictionary`**
- historical snapshot/corpus / compatibility identifier: `Special2788`
- user-selected nucleus: `Core Tag Set`
- per-entry: `Special` where unambiguous; `Special Core Entry` in explicit prose when useful
- relationship: `Special Core Dictionary -> Core Tag Set -> Auxiliary/support -> Prompt`

## Quarantine carry-forward rule — DO NOT DISCARD

#32でproductionへpromotionしなかった項目は将来の検証資産として保持する。

- Special REVIEW: 305
- Special IMAGE_TEST_REQUIRED: 17
- semantic-support IMAGE_TEST_REQUIRED: 33 rows
- その他、証拠不足 / model-family依存 / controlled image evidence待ちでparkされた候補

非promotionは非破棄。#42 / Stage10 controlled tests等で必要に応じて再評価する。

## Issue #30 final evaluator policy — carry forward

TaggerはSpecial Core Dictionaryの完全なsemantic ground truthにしない。

Allowed role:
- automatic pre-screening
- direct/non-relation/simple-unaryの補助候補
- disagreement / low-confidence detection
- review prioritization
- safe abstention / HUMAN REVIEW routing

Default HUMAN REVIEW:
- relation / binding
- actor/subject/object
- body-part ownership/site
- quantity / multi-person assignment
- spatial topology/direction
- insertion / contact / restraint
- compound retention
- component-only
- evaluator disagreement / weak confidence

Artifact/experiment separation:
- gray/unreadable/corrupt/hash/metadata/provenance failure -> BLOCKED before semantic evaluation
- target/contrast generation不成立 -> experiment validity failure; evaluator精度と混同しない

Full details: `docs/project/ISSUE30_HANDOFF_20260910.md`。

## Active / Ready Work

### #36 UI-JA V5 — ChatGPT-led repair/audit

Current policy:
- GitHub remains canonical; chat history is not canonical.
- V4 artifacts remain frozen as evidence. V5 is a separate repair lane.
- current branch: `ui-ja/issue36-relaxed-v5-chatgpt-repair`
- 30,629-row table is processed through the existing 31 audit shards.
- ChatGPT performs translation/semantic repair review directly.
- Codex/Luna is not used for translation-quality judgment or semantic audit in the current lane.
- after all shards: integration/revalidation -> separate independent production-promotion gate.

### #34 UI-JA parent remaining concerns

Primary remaining concern is bilingual search relevance/noise, including substring/fuzzy collisions such as `anal -> piano / analog_clock / analogous_colors`.
Before #42 activation, material concern must be completed or explicitly separated from the Stage10 Gate.

### #24 protected-data maintenance

GitHub外local protected dataについて、backup location / freshness / manifest / restore verification / rebuildabilityを明示する。
本件はcore DEVを自動的に占有しない。

## WAITING / GATED

### #42 Stage10 pre-evaluation product-purpose improvement

Dictionary promotion/freeze prerequisite: **SATISFIED**。
#44 evaluator coverage prerequisite: **SATISFIED**。
#30 representative calibration prerequisite: **SATISFIED**。

残るactivation Gate:
- #36 V5 material UI-JA/data homework complete or explicitly separated
- #34 material bilingual-search/search-noise concern complete or explicitly separated

#42 consumes #30 policy as Tagger-assisted triage, not full AUTO semantic scoring.

### #5 PROMPT formal handoff

Formal completionは以下の後:
1. #43 final freeze handoff — SATISFIED
2. #44 evaluator coverage return — SATISFIED
3. #30 representative routing/calibration — SATISFIED
4. #42 product-purpose improvement result — REMAINS

## Current Gates

1. Stage9 overall Gate — SATISFIED
2. #28 automated E2E — SATISFIED
3. Stage10 KNOWLEDGE handoff base — SATISFIED
4. #6 Forge Neo comparison environment — SATISFIED / PASS_WITH_NOTE
5. #30 infrastructure plumbing — SATISFIED / PASS_PIPELINE
6. #35 completion — SATISFIED
7. #32 validation + independent promotion audit — SATISFIED
8. #49 production FIX implementation + post-write audit + production merge — SATISFIED
9. #43 naming/final dictionary freeze — SATISFIED
10. #44 final evaluator coverage — SATISFIED
11. #30 controlled representative calibration + minimal review — **SATISFIED / HANDOFF READY**
12. #36 V5 repair/audit -> integration/revalidation -> independent promotion gate — **ACTIVE**
13. #34 bilingual search relevance/noise — **REMAINS / resolve or explicitly separate before #42**
14. #42 product-purpose improvement pass — REMAINS
15. #5 formal Prompt handoff — REMAINS / after #42
16. `docs/stages/STAGE_10_PREP.md` remaining checks — REMAINS
17. Stage10 production A/B — NOT STARTED

## Canonical dependency order

Parallel now:
- UI-JA lane: `#36 V5 repair/audit -> integration/revalidation -> independent promotion gate`
- cross-cutting: `#34 bilingual search relevance`, `#24 protected-data safety`
- core DEV: **NONE / management handoff**

#30 is complete.

Then, after #36/#34 material work is complete or explicitly separated:
`activate #42 product-purpose improvement -> #5 formal Prompt handoff -> remaining STAGE_10_PREP checks -> Stage10 production A/B`

## Next Actions

1. #36 V5 workをGitHub正本へ継続反映
2. #34 bilingual search relevance/noiseをresolveまたはStage10 Gateから明示分離
3. managementがGate確認後に#42をcurrent core DEVとして明示activate
4. #42 product-purpose improvement passで#30 Tagger-assisted triage policyを統合
5. #5 formal Prompt handoff
6. `STAGE_10_PREP.md` remaining checksをclose
7. 全Gate完了後のみ Stage10 production A/B
8. parallel safety debt: #24 protected-data backup / restore verification

## Source-of-Truth Rule

- current core DEV = **NONE / MANAGEMENT_HANDOFF** until explicit activation
- `CURRENT_DEV_TASK.md` must also say Source Issue = NONE while no core DEV is selected
- Issue #30 = completed evidence/handoff; do not restart its 128-image pilot
- `docs/project/ISSUE30_HANDOFF_20260910.md` is the compact #30 restore/handoff anchor
- final formal concept name = **`Special Core Dictionary`**
- #32/#48/#49/#43 dictionary validation/promotion/freeze chain is completed; do not restart it
- #32 parked REVIEW / IMAGE_TEST_REQUIRED evidence is carry-forward asset and must not be discarded
- #44 exact evaluator desk coverage is completed
- #30 Tagger policy = assistive triage, not broad Special semantic authority
- Issue #46 is superseded historical evidence; current UI-JA route = Issue #36 V5
- DEV切替時は Issue + CURRENT_STATE + CURRENT_DEV_TASK を同一管理操作で同期する
- completion reportだけで次Gateへ進まない。live GitHub stateを再確認する
