# CURRENT STATE

最終更新: 2026-09-10

## Current Stage

Stage 9 overall Gate 完了 / Stage10 準備Gate実施中 / automated E2E PASS / Special Core Dictionary freeze 完了

本ファイルは現在地のrouting正本。task contract / completion criteria / result evidenceは対応Issueを正本とし、更新競合時はlive Issue / branch / checkpointを優先して同期する。

## Current Core DEV

**Issue #30 / Stage10 representative evaluator calibration design**

Issue #44の3-evaluator desk coverageは完了し、#30へのhandoffも同期済み。current core DEVは #30。
`CURRENT_DEV_TASK.md` は Source Issue #30 に同期済み。Codexはlatest mainを取得し、Issue #30 / CURRENT_STATE / CURRENT_DEV_TASKの一致を確認してから作業開始する。

UI-JA #36 V5 と #44 KNOWLEDGE は独立レーンとして並行可能だが、#30のcore DEV contractを引き継がない。

## Workstreams Registry

| TEAM_ID | Status | Issue / scope | Branch / locator | Current phase | Restore anchor |
| --- | --- | --- | --- | --- | --- |
| `DICT:#32:R2` | COMPLETED / PROMOTED / CARRY_FORWARD_ONLY | #32 Special Core Dictionary historical validation | `dict-validation/quarantine` | 2,788/2,788 validation complete。approved effective subsetは#49でproduction反映済み。REVIEW/ITRはparked evidenceとして保持 | Issue #32 + #48 + #49 + #43 freeze |
| `KNOWLEDGE:#44` | ACTIVE / ONGOING / COVERAGE_COMPLETE | persistent generation knowledge corpus | `knowledge/generation-corpus` | 2,788 × WD14 / Kagami-24k / CL Tagger v2.00 desk coverage完了。#30 handoff済み。必要な追加知識/校正返却を担当 | Issue #44 correction checkpoint `5614819866` + commit `557aa4c` |
| `UIJA:#36:V5` | ACTIVE / CHATGPT_LED_REPAIR | Japanese overlay final convergence / semantic repair | `ui-ja/issue36-relaxed-v5-chatgpt-repair` | 30,629 rowsを既存31 audit shardsへ分割し、ChatGPT側で明確な翻訳・意味欠陥を修正/監査。V4はimmutable evidenceとして保持 | Issue #36 latest V5 checkpoint |
| `UIJA-ORCH:#46` | SUPERSEDED / CLOSED | historical independent Codex orchestration for V3.1/V4 | Issue #46 / `codex/issue46-orchestrator` | historical evidence only。Codex/Lunaをtranslation judgment / semantic auditに使う現行方式ではない | Issue #46 superseded checkpoint |
| `UIJA-PARENT:#34` | OPEN / CROSS-CUTTING | Tool UI / Japanese translation quality improvement | Issue #34 | #36 translation laneとは別に bilingual search / search-noise / remaining parent concernsを保持。Stage10前にresolveまたは明示分離が必要 | Issue #34 |
| `TEMP:#30` | ACTIVE / CORE_DEV / CALIBRATION_DESIGN | Forge Neo A/B automation | Issue #30 | infrastructure PASS。dictionary freeze satisfied。#44 exact 3-evaluator coverage satisfied。representative real-image calibration design進行 | Issue #30 current body + `CURRENT_DEV_TASK.md` |
| `PROMPT:#5` | GATED | Stage10 formal Prompt handoff | Issue #5 | #30 calibration + #42 result後にformal handoff | Issue #5 |
| `PREP:#42` | RESERVED / GATED | Stage10 pre-evaluation product-purpose improvement | Issue #42 | dictionary freeze satisfied。#30 calibration後、material UI-JA/data homework完了または明示分離後、Stage10前に実施 | Issue #42 |
| `MAINT:#24` | OPEN / SAFETY_DEBT | Local protected data backup / restore verification | Issue #24 | GitHub外protected dataのbackup/restore・manifest・非破壊restore検証。core DEVとは別枠 | Issue #24 |

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
- Issue #46 Codex orchestration architecture: historical work preserved, **superseded by #36 V5 ChatGPT-led repair lane**

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

非promotionは非破棄。#42 / #30 / Stage10 controlled tests等で必要に応じて再評価する。

## Active / Ready Work

### #36 UI-JA V5 — ChatGPT-led repair/audit

Current policy:
- GitHub remains canonical; chat history is not canonical.
- V4 artifacts remain frozen as evidence. V5 is a separate repair lane.
- current branch: `ui-ja/issue36-relaxed-v5-chatgpt-repair`
- 30,629-row table is processed through the existing 31 audit shards.
- ChatGPT performs translation/semantic repair review directly.
- Codex/Luna is **not** used for translation-quality judgment or semantic audit in the current lane.
- repair only clear defects: Chinese/non-Japanese residue, raw English debris, obvious semantic mistranslation, relation inversion, broken machine-composed labels.
- awkward but understandable Japanese may remain unchanged.
- canonical English identity/order must remain unchanged.
- shard chats are workers, not new sources of truth; durable progress/results return to GitHub/#36.
- after all shards: integration/revalidation -> separate independent production-promotion gate.

Issue #46 is historical/superseded and must not be interpreted as the current execution route.

### #44 KNOWLEDGE evaluator coverage

Final evaluator desk coverage: **SATISFIED / HANDOFF COMPLETE**。
`AUTO_CANDIDATE` は自動採点承認ではない。実画像でのsemantic correctnessは #30 representative calibrationで検証する。

### #30 Forge Neo A/B automation — CURRENT CORE DEV

- infrastructure: **PASS_PIPELINE**
- final dictionary freeze: **SATISFIED**
- #44 exact evaluator coverage: **SATISFIED**
- current phase: **representative real-image calibration design / controlled calibration prep**
- current manifest: 32 cases × 4 images = planned 128 images
- all planned images are screened by WD14 / Kagami / CL Tagger first; human review is concentrated on protected-route anchors, exceptions and stratified AUTO-likely samples
- human image-level judgment remains reference ground truth
- relation/binding, subject/object, body-site, count, spatial, insertion/contact/restraint, compound and disagreement cases remain conservative human-review candidates
- false-positive suppression / precision takes priority over maximum automation rate
- Stage10 production A/B remains prohibited until later Gates complete

### #34 UI-JA parent remaining concerns

#36 V5 translation convergenceとは別に、bilingual search / search-noise / parent-level UI/search concernsを保持する。
Stage10前の#42 activation条件を満たすため、remaining concernを完了するか、別Gateとして明示分離する。

### #24 protected-data maintenance

GitHub外local protected dataについて、backup location / freshness / manifest / restore verification / rebuildabilityを明示する。
本件はcore DEVを自動的に占有しないが、見えないsafety debtとして放置しない。

## WAITING / GATED

### #42 Stage10 pre-evaluation product-purpose improvement

Dictionary promotion/freeze prerequisite: **SATISFIED**。
#44 evaluator coverage prerequisite: **SATISFIED**。
開始条件として残るのは #30 representative calibration完了と、#36 V5 / #34 UI-JA/search等、評価対象Prompt/searchをmaterially変え得るpre-Stage10 homeworkの完了または明示分離。

### #5 PROMPT formal handoff

Formal completionは以下の後:
1. #43 final freeze handoff — SATISFIED
2. #44 evaluator coverage return — SATISFIED
3. #30 representative routing/calibration
4. #42 product-purpose improvement result

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
10. #44 final evaluator coverage — **SATISFIED / exact 3-evaluator**
11. #36 V5 ChatGPT-led 31-shard repair/audit -> final integration/revalidation -> independent promotion gate — **ACTIVE**
12. #34 remaining parent UI/search concerns — REMAINS / resolve or explicitly separate before #42
13. #30 representative routing/evaluator calibration — **ACTIVE / CURRENT CORE DEV**
14. #42 product-purpose improvement pass — REMAINS / after #30 and material UI-JA/data homework complete or separated
15. #5 formal Prompt handoff — REMAINS / after #30 + #42
16. `docs/stages/STAGE_10_PREP.md` remaining checks — REMAINS
17. Stage10 production A/B — NOT STARTED

## Canonical dependency order

Parallel now:
- Core DEV: `#30 representative calibration design -> controlled representative calibration`
- UI-JA lane: `#36 V5 31-shard ChatGPT repair/audit -> integration/revalidation -> independent promotion gate`
- KNOWLEDGE: `#44 coverage complete`; scoped follow-up only when needed
- Maintenance/cross-cutting: `#24 protected-data safety`, `#34 remaining UI/search parent concerns`

Then:
`#30 representative calibration -> #42 product-purpose improvement -> #5 formal Prompt handoff -> remaining STAGE_10_PREP checks -> Stage10 production A/B`

#42 activation additionally requires material #34/#36 UI-JA/data homework to be completed or explicitly separated。

## Next Actions

1. #30 representative calibration design/current passを完了し、controlled real-image calibrationへ進む
2. #36 V5の31 shardをChatGPT側で処理し、各成果をGitHub正本へ返す
3. #36 V5全shard完了後にintegration/revalidationし、production writeは別independent gateへ送る
4. #34 remaining parent concernsをresolveまたはStage10 Gateから明示分離
5. #42 product-purpose improvement pass
6. #5 formal Prompt handoff
7. `STAGE_10_PREP.md` remaining checksをclose
8. 全Gate完了後のみ Stage10 production A/B
9. parallel safety debt: #24 protected-data backup / restore verificationを完了させる

## Source-of-Truth Rule

- current core DEV = **Issue #30** until management explicitly switches DEV
- `CURRENT_DEV_TASK.md` Source Issue must remain **#30** while this DEV slot is active
- Issue #30 / CURRENT_STATE / CURRENT_DEV_TASK が一致しない場合、Codexは実装開始しない
- final formal concept name = **`Special Core Dictionary`**
- #32/#48/#49/#43 dictionary validation/promotion/freeze chain is completed; do not restart it
- #32 parked REVIEW / IMAGE_TEST_REQUIRED evidence is carry-forward asset and must not be discarded
- #44 exact evaluator desk coverage is completed; `AUTO_CANDIDATE` is not production auto-score approval
- **Issue #46 is superseded historical orchestration evidence; it is not the current UI-JA execution route**
- current UI-JA execution route = **Issue #36 V5 ChatGPT-led 31-shard repair/audit**
- shard chats are execution workers; GitHub/#36 remains canonical
- DEV切替時は Issue + CURRENT_STATE + CURRENT_DEV_TASK を同一管理操作で同期する
- completion reportだけで次Gateへ進まない。live GitHub stateを再確認する
