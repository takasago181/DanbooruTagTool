# CURRENT STATE

最終更新: 2026-09-10

## Current Stage

Stage 9 overall Gate 完了 / Stage10 準備Gate実施中 / automated E2E PASS / Special Core Dictionary freeze 完了

本ファイルは現在地のrouting正本。task contract / completion criteria / result evidenceは対応Issueを正本とし、更新競合時はlive Issue / branch / checkpointを優先して同期する。

## Current Core DEV

**NONE / management handoff state**

Issue #43 は completed / closed。次の core DEV はまだ正式選択していない。
#46/#36 UI-JA と #44 KNOWLEDGE はそれぞれ独立レーンとして進行可能だが、CURRENT_DEV_TASK を勝手に引き継がない。
新しい core DEV を選ぶ場合は Issue + CURRENT_STATE + CURRENT_DEV_TASK を同一管理操作で同期する。

## Workstreams Registry

| TEAM_ID | Status | Issue / scope | Branch / locator | Current phase | Restore anchor |
| --- | --- | --- | --- | --- | --- |
| `DICT:#32:R2` | COMPLETED / PROMOTED / CARRY_FORWARD_ONLY | #32 Special Core Dictionary historical `Special2788` validation | `dict-validation/quarantine` | 2,788/2,788 validation complete。approved effective subsetは#49でproduction反映済み。REVIEW/ITRはparked evidenceとして保持 | Issue #32 + #48 + #49 + #43 freeze |
| `KNOWLEDGE:#44` | ACTIVE / ONGOING / COVERAGE_READY | persistent generation knowledge corpus | `knowledge/generation-corpus` | final dictionary freeze済み。次はWD14 / Kagami-24k / CL Tagger v2 evaluator coverage return | Issue #44 latest checkpoint |
| `UIJA:#36:V3.1` | ACTIVE / REEXECUTION_PENDING | Japanese overlay final convergence | `ui-ja/issue36-final-agent-convergence` | #46 orchestratorによる30,629 full execution + V3.1 revalidation待ち | Issue #36 / #46 |
| `UIJA-ORCH:#46` | ACTIVE / FULL_EXECUTION_AUTHORIZED | independent Codex orchestration | `codex/issue46-orchestrator` | full execution authorized / production promotion not authorized | Issue #46 latest checkpoint |
| `UIJA-PARENT:#34` | OPEN / CROSS-CUTTING | Tool UI / Japanese translation quality improvement | Issue #34 | #36 translation laneとは別に bilingual search / search-noise / remaining parent concernsを保持。Stage10前にresolveまたは明示分離が必要 | Issue #34 |
| `TEMP:#30` | ACTIVE / GATED_ON_COVERAGE | Forge Neo A/B automation | Issue #30 | infrastructure PASS。dictionary freeze satisfied。#44 evaluator coverage後にrepresentative routing/calibration | Issue #30 |
| `PROMPT:#5` | GATED | Stage10 formal Prompt handoff | Issue #5 | #44 coverage + #30 calibration + #42 result後にformal handoff | Issue #5 |
| `PREP:#42` | RESERVED / GATED | Stage10 pre-evaluation product-purpose improvement | Issue #42 | dictionary freeze satisfied。UI-JA/data homework完了または明示分離後、Stage10前に実施 | Issue #42 |
| `MAINT:#24` | OPEN / SAFETY_DEBT | Local protected data backup / restore verification | Issue #24 | GitHub外protected dataのbackup/restore・manifest・非破壊restore検証。core DEVとは別枠 | Issue #24 |

## Completed

- Stage9 overall Gate: **PASS / completed**
- Issue #28 automated E2E: **PASS / completed**
- Issue #6 Forge Neo comparison environment: **PASS_WITH_NOTE / completed**
- Issue #35 Japanese-first desktop UI: **ISSUE35_FINAL_COMPLETION_PASS / completed / closed**
- Issue #32 dictionary validation: **completed**
- Issue #48 independent final promotion audit: **APPROVE_WITH_REQUIRED_PROMOTION_CONTRACT**
- Issue #49 production promotion:
  - post-write audit: **APPROVE_ISSUE49_POST_WRITE**
  - audited branch: `codex/issue49-dict-promotion-latest-main`
  - audited HEAD / merged production-dictionary HEAD: `490f5653460804c8a40cb48d093b91d5d8dd5d9c`
  - active candidate rows 228 / effective assignments 246 / affected Specials 171
  - changed production cells: 246 across 171 rows
  - exact row count / identity / order: 2,788 maintained
  - scope leak: 0
  - excluded leakage: 0
  - #49-specific new failures/errors: 0
  - **completed / closed**
- Issue #43 Special Core Dictionary naming/freeze:
  - verdict: **PASS_ISSUE43_FREEZE**
  - Issue #43 caused blockers: 0
  - branch final HEAD: `19e2650b14eed73d82cf09912fb6fbf3c2b1237c`
  - merged to `main` by fast-forward
  - production profile SHA unchanged: `55490940378e15d8e41454e701d0c202abbab307a08fb6e56841171e0edec1fd`
  - exact row count / identity / order: 2,788 maintained
  - **completed / closed**

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

### #46 -> #36 UI-JA final convergence

- #46: **FULL_EXECUTION_AUTHORIZED / PRODUCTION_PROMOTION_NOT_AUTHORIZED**
- run/resume authorized 30,629 orchestration
- durable artifacts -> #36
- #36 V3.1 revalidation
- eligibleでもproduction writeは別のindependent promotion gate

### #44 KNOWLEDGE evaluator coverage

Dictionary freeze prerequisiteは **SATISFIED**。
次のcurrent priority:
- finalized 2,788-entry Special Core Dictionary against WD14 / `wd-eva02-large-tagger-v3`
- Kagami-24k
- CL Tagger v2 stable/fixed release

最低限、raw vocabulary / Core-Extended-Alias-Semantic / post-count-band / Alias-vs-canonical-target coverageを返し、#30 / #5へhandoffする。

### #30 Forge Neo A/B automation

- infrastructure: **PASS_PIPELINE**
- final dictionary freeze: **SATISFIED**
- remaining gate: #44 evaluator coverage + representative Special case selection
- then capability-aware `AUTO / REVIEW / BLOCKED` calibration and evidence-supported candidate `A_WIN / B_WIN` behavior

### #34 UI-JA parent remaining concerns

#36 translation convergenceとは別に、bilingual search / search-noise / parent-level UI/search concernsを保持する。
Stage10前の#42 activation条件を満たすため、remaining concernを完了するか、別Gateとして明示分離する。

### #24 protected-data maintenance

今回のprotected-data incidentを踏まえ、GitHub外local protected dataについて、backup location / freshness / manifest / restore verification / rebuildabilityを明示する。
本件はcore DEVを自動的に占有しないが、見えないsafety debtとして放置しない。

## WAITING / GATED

### #42 Stage10 pre-evaluation product-purpose improvement

Dictionary promotion/freeze prerequisiteは **SATISFIED**。
開始条件として残るのは、UI-JA dictionary/display/search work等、評価対象Prompt/searchをmaterially変え得るpre-Stage10 homeworkの完了または明示分離。
対象: 日本語意図揺れ、support競合、model-family差、failure diagnosis、Prompt bloat、minimum sufficient set、parked evidence再評価。

### #5 PROMPT formal handoff

Formal completionは以下の後:
1. #43 final freeze handoff — SATISFIED
2. #44 evaluator coverage return
3. #30 representative routing/calibration
4. #42 product-purpose improvement result

#42からPrompt設計へ返る変更/IMAGE_TEST_REQUIREDを統合してからformal handoffを完了する。

## Current Gates

1. Stage9 overall Gate — SATISFIED
2. #28 automated E2E — SATISFIED
3. Stage10 KNOWLEDGE handoff base — SATISFIED
4. #6 Forge Neo comparison environment — SATISFIED / PASS_WITH_NOTE
5. #30 infrastructure plumbing — SATISFIED / PASS_PIPELINE
6. #35 completion — SATISFIED
7. #32 validation + independent promotion audit — SATISFIED
8. #49 production FIX implementation + post-write audit + production merge — SATISFIED / completed
9. #43 naming/final dictionary freeze gate — SATISFIED / completed
10. #44 final evaluator coverage return — REMAINS / READY NOW
11. #46 full UI-JA orchestration -> #36 revalidation -> independent promotion gate — REMAINS / READY NOW
12. #34 remaining parent UI/search concerns — REMAINS / resolve or explicitly separate before #42
13. #30 final representative routing/evaluator calibration — REMAINS / waits #44 coverage
14. #42 product-purpose improvement pass — REMAINS / after material UI-JA/data homework is complete or separated
15. #5 formal Prompt handoff — REMAINS / after #44 + #30 + #42
16. `docs/stages/STAGE_10_PREP.md` remaining checks — REMAINS
17. Stage10 production A/B — NOT STARTED

## Canonical dependency order

Parallel now:

- Lane A: `#46 full execution -> #36 revalidation -> independent UI-JA promotion gate`
- Lane B: `#44 evaluator coverage`
- Maintenance/cross-cutting: `#24 protected-data safety`, `#34 remaining UI/search parent concerns`

Then:

`#44 coverage -> #30 representative calibration -> #42 product-purpose improvement -> #5 formal Prompt handoff -> remaining STAGE_10_PREP checks -> Stage10 production A/B`

#42 activation additionally requires material #34/#36 UI-JA/data homework to be completed or explicitly separated.

## Next Actions

1. #46 authorized 30,629 full execution -> #36 V3.1 revalidation -> separate independent promotion gate
2. parallel: #44 finalized Special Core Dictionary evaluator coverage return
3. #34 remaining parent concernsをresolveまたはStage10 Gateから明示分離
4. #30 final representative routing/evaluator calibration
5. #42 product-purpose improvement pass
6. #5 formal Prompt handoff
7. `STAGE_10_PREP.md` remaining checksをclose
8. 全Gate完了後のみ Stage10 production A/B
9. parallel safety debt: #24 protected-data backup / restore verificationを完了させる

## Source-of-Truth Rule

- current core DEV = **NONE** until a management action explicitly selects the next DEV Issue
- `CURRENT_DEV_TASK.md` must also say no current DEV during this handoff state
- final formal concept name = **`Special Core Dictionary`**
- Issue #43 is completed/closed and its final branch HEAD is on main
- #49 production dictionary promotion is completed/closed;再実装対象ではない
- #32 validation is completed; parked REVIEW / IMAGE_TEST_REQUIRED evidence is carry-forward asset and must not be discarded
- #46 full execution authorization is not production-promotion authority and does not itself become core DEV
- #44 is long-lived KNOWLEDGE, not core DEV
- DEV切替時は Issue + CURRENT_STATE + CURRENT_DEV_TASK を同一管理操作で同期する
- Codex completion reportだけで次Gateへ進まない。live GitHub stateを再確認する
