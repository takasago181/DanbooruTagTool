# CURRENT STATE

最終更新: 2026-09-10

## Current Stage

Stage 9 overall Gate 完了 / Stage10 準備Gate実施中 / automated E2E PASS

本ファイルは現在地のrouting正本。task contract / completion criteria / result evidenceは対応Issueを正本とし、更新競合時はlive Issue / branch / checkpointを優先して同期する。

## Active Teams Registry

| TEAM_ID | Status | Issue / scope | Branch / locator | Current phase | Restore anchor |
| --- | --- | --- | --- | --- | --- |
| `DEV:#49` | ACTIVE | #49 audited #32 fixes production promotion | Issue #49 / dedicated feature branch from latest `main` | management sync complete; implementation may start under #49 contract | Issue #49 latest checkpoint + `CURRENT_DEV_TASK.md` |
| `DICT:#32:R2` | VALIDATION_COMPLETE / PROMOTION_READY | #32 Special2788 full validation | `dict-validation/quarantine` | 2,788/2,788 first-pass完了、semantic support 58/58、completeness PASS、#48 independent final promotion audit PASS_WITH_CONTRACT | Issue #32 checkpoint `5605952933` + Issue #48 comment `5605993533` |
| `KNOWLEDGE:#44` | ACTIVE / ONGOING | persistent generation knowledge corpus | `knowledge/generation-corpus` | catalog整理済み。Stage10 / #42 / evaluator設計向けの継続知識owner | Issue #44 latest checkpoint + `docs/knowledge/KNOWLEDGE_CATALOG.md` |
| `UIJA:#36:V3.1` | ACTIVE / REEXECUTION_PENDING | Japanese overlay final convergence | `ui-ja/issue36-final-agent-convergence` | failed execution `cafcd41d...` は独立性欠陥でreject。semantic contract自体は維持 | Issue #36 checkpoint `5601610579` |
| `UIJA-ORCH:#46` | ACTIVE / FULL_EXECUTION_AUTHORIZED | one-command independent Codex orchestration | `codex/issue46-orchestrator` | pilot・bounded fixes・delta audit完了。30,629 full execution authorized。production promotionは未許可 | Issue #46 comment `5603074340` |
| `TEMP:#30` | ACTIVE / GATED | Forge Neo A/B automation | Issue #30 | infrastructure PASS。final evaluator/routing calibrationはfinal Special dictionary freeze待ち | Issue #30 latest checkpoint |
| `PROMPT:#5` | GATED | Stage10 formal Prompt handoff | Issue #5 | final representative Special/evaluator inputsはdictionary freeze待ち | Issue #5 + `docs/stages/STAGE_10_PREP.md` |

Reserved-only #42/#43、backlog #24、管理基盤 #47 は現行DEV task contractを置き換えない。

## Completed

- Stage9 overall Gate: **PASS / completed**。
- Issue #28 automated E2E: **PASS / completed**。
- Issue #6 Forge Neo comparison environment: **PASS_WITH_NOTE / completed**。
- Issue #35 Japanese-first desktop UI: **ISSUE35_FINAL_COMPLETION_PASS / completed / closed**。
- Issue #37 representative-set review: **REPLACE_OR_AUGMENT_WITH_SPECIAL_REPRESENTATIVE_SET**。
- Issue #39 UI-JA R3 engine: audit PASS / completed。
- Issue #41 UI-JA pilot: **PASS_PILOT / completed / closed**。
- Issue #45 V3.1 spec audit: **APPROVE_V3_SPEC_FOR_EXECUTION / completed**。

### Issue #32 dictionary validation closure

- Special first-pass: **2,788 / 2,788**
- Special verdict totals: PASS 2,292 / FIX 174 / REVIEW 305 / IMAGE_TEST_REQUIRED 17
- semantic support: **58 / 58 audited**
- semantic-support IMAGE_TEST_REQUIRED: **33 rows parked**
- active revalidation pending: 0
- candidate FIX cross-consistency: completed
- completeness reconciliation: PASS / `GENUINE_MISSING_SPECIAL = 0`
- final evidence-derived Special count: **2,788**
- #32 final recommendation: **READY_FOR_FINAL_PROMOTION_AUDIT**
- #48 independent final promotion audit: **APPROVE_WITH_REQUIRED_PROMOTION_CONTRACT**

### Quarantine carry-forward rule — DO NOT DISCARD

#32でproduction promotion対象にならなかった項目は、失敗・不要・削除対象を意味しない。特に以下は**将来の検証資産として保存し、捨てない**。

- Special `REVIEW`: **305件**
- Special `IMAGE_TEST_REQUIRED`: **17件**
- semantic-support `IMAGE_TEST_REQUIRED`: **33行**
- そのほか証拠不足・model-family依存・controlled image evidence待ちで明示parkされた候補

これらは `dict-validation/quarantine` / `validation_quarantine/**` の監査証跡・候補データを保持する。

運用ルール:
1. #49 production promotionから除外することと、候補を破棄することを混同しない。
2. quarantineのrow identity、verdict、evidence、reason、model/version scope、関連Special/support identityを保持する。
3. #42 product-purpose improvement pass、#30/Stage10 representative controlled image tests、必要なmodel-family別検証の入力候補として再利用する。
4. 実画像または新しい独立証拠で有効性が確認されたものは、既存監査証跡を残したまま別Gateで再判定し、必要なら将来のproduction correction candidateへ昇格できる。
5. 有効性が否定されたものも履歴を削除せず、REJECT/HOLD等の根拠付き結果として残す。
6. Stage10開始のために未解決候補を一括削除・一括PASS・一括REJECTしてはいけない。

このcarry-forward ruleは「全部productionへ入れる」という意味ではない。**証拠が足りない有望候補を失わず、後の実画像検証で再評価できる状態を維持する**ためのルールである。

## Active Work / Issues

### #49 dictionary production promotion — current DEV

- current DEV Issue: **#49 `[DICT-PROMOTION][DEV] Apply audited Issue #32 fixes to production`**。
- latest mainからdedicated feature branchで実装する。
- 174 Special-level FIX verdictからeffective manifestを機械的に作る。
- REVIEW 305 / IMAGE_TEST_REQUIRED 17 / semantic-support parked 33は**今回promotionしないが、quarantineから削除・破棄もしない**。
- implementation/test/push後は **READY_FOR_POST_WRITE_AUDIT** または **HOLD_PROMOTION_IMPLEMENTATION** でSTOP。
- main merge / Stage10 start / #36 production promotionは禁止。別post-write independent auditが必須。

### #36 / #46 UI-JA final convergence

- #36 frozen V3.1 semantic contract: `86bf72246b3f1f42b52f562f45d4027f0d1a71ea`。
- failed execution `cafcd41d...` は構造欠陥でreject済み。
- #46 latest verdict: **PASS_DELTA / FULL_EXECUTION_AUTHORIZED / PRODUCTION_PROMOTION_NOT_AUTHORIZED**。
- 次は#46 orchestratorで30,629 full executionを行い、#36をre-run/revalidateする。

### #44 KNOWLEDGE

- ongoing persistent knowledge owner。
- canonical reading layer: `docs/knowledge/KNOWLEDGE_CATALOG.md` + `docs/knowledge/catalog/00-10`。

### #30 Forge Neo A/B automation

- infrastructure pipeline: **PASS_PIPELINE**。
- final representative data / evaluator coverage / routing calibrationはfinal Special dictionary freeze後までHOLD。
- #32のparked REVIEW / IMAGE_TEST_REQUIREDは、Stage10 representative controlled-test候補として利用可能。ただし無差別全件画像化はせず、#42/#30でrisk/value/model scopeを基に優先順位付けする。

## WAITING / GATED

### #5 PROMPT
- final representative Special IDs / Tagger allocation / AUTO-REVIEW routing / production thresholdはfinal dictionary freeze後までHOLD。

### #42 Stage10 pre-evaluation product-purpose improvement
- **RESERVED ONLY**。dictionary/data homework・promotion・freeze後にactivate。
- 日本語意図揺れ、support競合、model-family ineffective/harmful guidance、failure diagnosis、Prompt bloat、minimum sufficient set、local success/failure historyを評価する。
- #32のREVIEW 305 / IMAGE_TEST_REQUIRED 17 / semantic-support parked 33を**discardせずcarry-forward inputとして受け取り、実画像・新規独立証拠が必要な候補を再評価する**。

### #43 naming gate
- **RESERVED ONLY**。#49 approved production promotion完了後にactivate。
- preferred formal concept name: `Special Core Dictionary`。

## Not Started / Do Not Start Yet

- Stage10 production image A/B
- Stage10 winner/scoring production fixation
- unvalidated universal model-family Prompt grammar
- final representative Special exact case list
- final evaluator allocation / AUTO-REVIEW routing
- production confidence/margin threshold

## Current Gates

1. Stage9 overall Gate — **SATISFIED**
2. #28 automated E2E — **SATISFIED**
3. Stage10 KNOWLEDGE handoff — **SATISFIED**
4. #6 Forge Neo comparison environment — **SATISFIED / PASS_WITH_NOTE**
5. #30 infrastructure plumbing — **SATISFIED / PASS_PIPELINE**
6. #35 completion — **SATISFIED / completed**
7. #32 validation + completeness + final independent promotion audit — **SATISFIED**
8. #49 approved production FIX implementation + post-write independent audit + merge — **ACTIVE / REMAINS**
9. #43 naming/final dictionary freeze gate — **REMAINS after #49**
10. final dictionary freeze後のKNOWLEDGE evaluator coverage return — **REMAINS**
11. #36/#46 full UI-JA execution + independent final artifact/promotion gate — **REMAINS**
12. #30 final representative routing/evaluator calibration — **REMAINS after dictionary freeze**
13. #5 formal Prompt handoff — **REMAINS**
14. #42 product-purpose improvement pass — **REMAINS after prerequisites**
15. `docs/stages/STAGE_10_PREP.md` remaining checks — **REMAINS**

## Next Actions

1. #49 approved effective FIX subsetをproduction feature branchへ適用し、post-write auditへ渡す。
2. #49 audit PASS後のみmain統合。
3. #43 naming gate → final Special Core Dictionary snapshot freeze。
4. #46 authorized full execution → #36 revalidation → separate promotion audit。
5. final dictionary freeze後、#44 KNOWLEDGEがevaluator coverageを返す。
6. #30がrepresentative routing/evaluator calibrationを行う。この際#32 parked資産を必要に応じて候補化する。
7. #5 formal handoff。
8. prerequisites完了後#42をactivateし、#32 parked資産を含む未確定事項をproduct-purpose観点で再評価する。
9. 全Gate完了後のみStage10 production A/Bへ進む。

## Source-of-Truth Rule

- このファイルは現在地のrouting正本。
- task contract / completion criteria / result evidenceは対応Issueが正本。
- active DEV Issueがある場合だけ `docs/project/CURRENT_DEV_TASK.md` を同期ミラーとして使う。
- 現在active DEVは **#49**。
- #32はvalidation complete / promotion evidence laneであり、first-pass再実行対象ではない。
- #32のREVIEW / IMAGE_TEST_REQUIRED / parked evidenceは**非promotion = 非破棄**。quarantine carry-forward assetとして保持する。
- #46はfull execution authorizedだが、production promotion authorityではない。
- 共有管理ファイルは最新mainを確認してから更新し、stale copyで上書きしない。
- Codex完了報告だけで次Gateへ進まない。
- 仕様変更は`DECISIONS.md`または該当Stage/Issue contractへ反映する。
