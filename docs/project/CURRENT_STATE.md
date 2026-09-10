# CURRENT STATE

最終更新: 2026-09-10

## Current Stage

Stage 9 overall Gate 完了 / Stage10 準備Gate実施中 / automated E2E PASS / Special Core Dictionary freeze 完了

本ファイルは現在地のrouting正本。task contract / completion criteria / result evidenceは対応Issueを正本とし、更新競合時はlive Issue / branch / checkpointを優先して同期する。

## Current Core DEV

**Issue #30 / Stage10 representative evaluator calibration design**

Issue #44の3-evaluator desk coverageは完了し、#30へのhandoffも同期済み。次のcore DEVとして #30 を正式選択した。
`CURRENT_DEV_TASK.md` は Source Issue #30 に同期済み。Codexはlatest mainを取得し、Issue #30 / CURRENT_STATE / CURRENT_DEV_TASKの一致を確認してから作業開始する。

#46/#36 UI-JA と #44 KNOWLEDGE は独立レーンとして並行可能だが、#30のcore DEV contractを勝手に引き継がない。

## Workstreams Registry

| TEAM_ID | Status | Issue / scope | Branch / locator | Current phase | Restore anchor |
| --- | --- | --- | --- | --- | --- |
| `DICT:#32:R2` | COMPLETED / PROMOTED / CARRY_FORWARD_ONLY | #32 Special Core Dictionary historical `Special2788` validation | `dict-validation/quarantine` | 2,788/2,788 validation complete。approved effective subsetは#49でproduction反映済み。REVIEW/ITRはparked evidenceとして保持 | Issue #32 + #48 + #49 + #43 freeze |
| `KNOWLEDGE:#44` | ACTIVE / ONGOING / COVERAGE_COMPLETE | persistent generation knowledge corpus | `knowledge/generation-corpus` | 2,788 × WD14 / Kagami-24k / CL Tagger v2.00 desk coverage完了。#30 handoff済み。今後は必要な追加知識/校正返却を担当 | Issue #44 correction checkpoint `5614819866` + commit `557aa4c` |
| `UIJA:#36:V3.1` | ACTIVE / REEXECUTION_PENDING | Japanese overlay final convergence | `ui-ja/issue36-final-agent-convergence` | #46 orchestratorによる30,629 full execution + V3.1 revalidation待ち | Issue #36 / #46 |
| `UIJA-ORCH:#46` | ACTIVE / FULL_EXECUTION_AUTHORIZED | independent Codex orchestration | `codex/issue46-orchestrator` | full execution authorized / production promotion not authorized | Issue #46 latest checkpoint |
| `UIJA-PARENT:#34` | OPEN / CROSS-CUTTING | Tool UI / Japanese translation quality improvement | Issue #34 | #36 translation laneとは別に bilingual search / search-noise / remaining parent concernsを保持。Stage10前にresolveまたは明示分離が必要 | Issue #34 |
| `TEMP:#30` | ACTIVE / CORE_DEV / CALIBRATION_DESIGN | Forge Neo A/B automation | Issue #30 | infrastructure PASS。dictionary freeze satisfied。#44 exact 3-evaluator coverage satisfied。representative real-image calibration design開始 | Issue #30 current body + `CURRENT_DEV_TASK.md` |
| `PROMPT:#5` | GATED | Stage10 formal Prompt handoff | Issue #5 | #30 calibration + #42 result後にformal handoff | Issue #5 |
| `PREP:#42` | RESERVED / GATED | Stage10 pre-evaluation product-purpose improvement | Issue #42 | dictionary freeze satisfied。#30 calibration後、UI-JA/data homework完了または明示分離後、Stage10前に実施 | Issue #42 |
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
- Issue #44 finalized evaluator desk coverage:
  - correction checkpoint: `5614819866`
  - machine-generated coverage commit: `557aa4c`
  - #30 handoff sync: `dba23df`
  - WD14 direct: 658 / 2,788 (23.60%)
  - Kagami direct: 1,412 / 2,788 (50.65%)
  - CL Tagger v2.00 direct: 1,704 / 2,788 (61.12%)
  - 3-evaluator direct union: 1,725 / 2,788 (61.87%)
  - observable including components: 1,957 / 2,788 (70.19%)
  - exact 3-evaluator: true
  - AUTO_CANDIDATE 939 / REVIEW_REQUIRED 1,018 / BLOCKED 831
  - relation/binding structural risk: 918
  - production `data/**`, #32, canonical unchanged

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

Final evaluator desk coverage: **SATISFIED / HANDOFF COMPLETE**。

Confirmed current result:
- WD14 direct 658 (23.60%)
- Kagami direct 1,412 (50.65%)
- CL Tagger v2.00 direct 1,704 (61.12%)
- direct union 1,725 (61.87%)
- observable including components 1,957 (70.19%)
- AUTO_CANDIDATE 939 / REVIEW_REQUIRED 1,018 / BLOCKED 831

`AUTO_CANDIDATE` は自動採点承認ではない。実画像でのsemantic correctnessは #30 representative calibrationで検証する。

### #30 Forge Neo A/B automation — CURRENT CORE DEV

- infrastructure: **PASS_PIPELINE**
- final dictionary freeze: **SATISFIED**
- #44 exact evaluator coverage: **SATISFIED**
- current phase: **representative real-image calibration design**
- first pass target: about 30 representative cases, not 2,788 sweep
- human image-level judgment remains reference ground truth
- compare WD14 / Kagami / CL v2.00 raw outputs and routing strategies
- relation/binding, subject/object, body-site, count, spatial, insertion/contact/restraint, compound and disagreement cases remain conservative human-review candidates
- false-positive suppression / precision takes priority over maximum automation rate
- Stage10 production A/B remains prohibited until later Gates complete

### #34 UI-JA parent remaining concerns

#36 translation convergenceとは別に、bilingual search / search-noise / parent-level UI/search concernsを保持する。
Stage10前の#42 activation条件を満たすため、remaining concernを完了するか、別Gateとして明示分離する。

### #24 protected-data maintenance

今回のprotected-data incidentを踏まえ、GitHub外local protected dataについて、backup location / freshness / manifest / restore verification / rebuildabilityを明示する。
本件はcore DEVを自動的に占有しないが、見えないsafety debtとして放置しない。

## WAITING / GATED

### #42 Stage10 pre-evaluation product-purpose improvement

Dictionary promotion/freeze prerequisiteは **SATISFIED**。
#44 evaluator coverage prerequisiteも **SATISFIED**。
開始条件として残るのは #30 representative calibration完了と、UI-JA dictionary/display/search work等、評価対象Prompt/searchをmaterially変え得るpre-Stage10 homeworkの完了または明示分離。
対象: 日本語意図揺れ、support競合、model-family差、failure diagnosis、Prompt bloat、minimum sufficient set、parked evidence再評価。

### #5 PROMPT formal handoff

Formal completionは以下の後:
1. #43 final freeze handoff — SATISFIED
2. #44 evaluator coverage return — SATISFIED
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
10. #44 final evaluator coverage return — **SATISFIED / exact 3-evaluator**
11. #46 full UI-JA orchestration -> #36 revalidation -> independent promotion gate — REMAINS / READY NOW
12. #34 remaining parent UI/search concerns — REMAINS / resolve or explicitly separate before #42
13. #30 final representative routing/evaluator calibration — **ACTIVE / CURRENT CORE DEV**
14. #42 product-purpose improvement pass — REMAINS / after #30 and material UI-JA/data homework is complete or separated
15. #5 formal Prompt handoff — REMAINS / after #30 + #42
16. `docs/stages/STAGE_10_PREP.md` remaining checks — REMAINS
17. Stage10 production A/B — NOT STARTED

## Canonical dependency order

Parallel now:

- Core DEV: `#30 representative calibration design -> controlled representative calibration`
- Lane A: `#46 full execution -> #36 revalidation -> independent UI-JA promotion gate`
- KNOWLEDGE: `#44 coverage complete`; remains available for scoped calibration/knowledge follow-up
- Maintenance/cross-cutting: `#24 protected-data safety`, `#34 remaining UI/search parent concerns`

Then:

`#30 representative calibration -> #42 product-purpose improvement -> #5 formal Prompt handoff -> remaining STAGE_10_PREP checks -> Stage10 production A/B`

#42 activation additionally requires material #34/#36 UI-JA/data homework to be completed or explicitly separated。

## Next Actions

1. #30: latest mainから現行DEV contractを確認し、about-30 representative calibration設計を完成する
2. #30: schema / case rationale / execution procedure / evaluator comparison / routing Gateをreviewable branch/commitへ残す
3. #46 authorized 30,629 full execution -> #36 V3.1 revalidation -> separate independent promotion gate
4. #34 remaining parent concernsをresolveまたはStage10 Gateから明示分離
5. #30の代表実画像calibrationをcontrolledに実施し、AUTO/HUMAN REVIEW/BLOCKED境界を証拠で更新
6. #42 product-purpose improvement pass
7. #5 formal Prompt handoff
8. `STAGE_10_PREP.md` remaining checksをclose
9. 全Gate完了後のみ Stage10 production A/B
10. parallel safety debt: #24 protected-data backup / restore verificationを完了させる

## Source-of-Truth Rule

- current core DEV = **Issue #30** until its current calibration-design pass is completed or management explicitly switches DEV
- `CURRENT_DEV_TASK.md` Source Issue must remain **#30** while this DEV slot is active
- Issue #30 / CURRENT_STATE / CURRENT_DEV_TASK の目的・scope・禁止事項が一致しない場合、Codexは実装開始しない
- final formal concept name = **`Special Core Dictionary`**
- Issue #43 is completed/closed and its final branch HEAD is on main
- #49 production dictionary promotion is completed/closed;再実装対象ではない
- #32 validation is completed; parked REVIEW / IMAGE_TEST_REQUIRED evidence is carry-forward asset and must not be discarded
- #44 exact evaluator desk coverage is completed; `AUTO_CANDIDATE` is not production auto-score approval
- #46 full execution authorization is not production-promotion authority and does not itself become core DEV
- DEV切替時は Issue + CURRENT_STATE + CURRENT_DEV_TASK を同一管理操作で同期する
- Codex completion reportだけで次Gateへ進まない。live GitHub stateを再確認する
