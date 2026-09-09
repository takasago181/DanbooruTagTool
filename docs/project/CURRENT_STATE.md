# CURRENT STATE

最終更新: 2026-09-09

## Current Stage

Stage 9 overall Gate 完了 / Stage10 準備Gate実施中 / automated E2E PASS

## Active Teams Registry

この表は、作業チャットが「自分はどの班・どのIssue・どの版の作業個体か」をGitHubから復元するための**routing/index**。task contractそのものではない。実作業の目的・scope・完了条件は対応Issue、現行DEVはさらに `CURRENT_DEV_TASK.md`、成果物の固定点はbranch/checkpoint/contractを正本として読む。

`HEAD` は動くためこの表へ固定しない。各チャットは開始時に `CHAT_START_PROTOCOL.md` に従いbranchのlive HEADと最新checkpoint/contractを取得し、班IDを表示する。表とIssue/branch/checkpointが矛盾する場合は `IDENTITY_CONFLICT` として作業開始前に管理整合を行う。

| TEAM_ID | Status | Issue / scope | Branch / locator | Current phase | Restore anchor |
| --- | --- | --- | --- | --- | --- |
| `DEV:#35` | ACTIVE | #35 UI-only Codex slot | `ui-ja/issue35-ui-only` | implementation exists; test/manual completion gate | Issue #35 + `CURRENT_DEV_TASK.md` |
| `DICT:#32:R2` | ACTIVE | #32 Special2788 validation | `dict-validation/quarantine` | R2 long-running audit; Batch23 PASS; next safe restart sequence 2301 | Issue #32 latest checkpoint + `validation_quarantine/handoff.md` |
| `KNOWLEDGE:#44` | ACTIVE / ONGOING | #44 persistent generation knowledge corpus | `knowledge/generation-corpus` | organized corpus finalized; ongoing evidence maintenance for #32 / Stage10 / future #42 | Issue #44 latest checkpoint + `docs/knowledge/KNOWLEDGE_CATALOG.md` |
| `UIJA:#36:V3` | ACTIVE / EXECUTION_AUTHORIZED | #36 Japanese overlay quarantine / FINAL CONVERGENCE V3.1 | `ui-ja/issue36-final-agent-convergence` | V3.1 spec frozen; #45 independent audit PASS; Codex execution authorized | Issue #36 checkpoint `5601218088` + V3.1 contract commit `86bf72246b3f1f42b52f562f45d4027f0d1a71ea` |
| `TEMP:#30` | ACTIVE / GATED | #30 Forge Neo A/B automation | Issue #30 + `docs/testing/ISSUE30_SPECIAL_REPRESENTATIVE_ROUTING_DESIGN_20260908.md` | plumbing PASS; final evaluator/routing calibration waits for dictionary freeze | Issue #30 latest checkpoint / routing design |
| `PROMPT:#5` | GATED | #5 Stage10 formal Prompt handoff | Issue #5 + Stage10 prep docs | final representative Special/evaluator inputs wait for dictionary freeze | Issue #5 + `docs/stages/STAGE_10_PREP.md` |

Reserved-only #42/#43 and backlog #24 are not active team identities until their activation conditions are met.

## Completed

- Stage9A: PASS。
- Stage9B: 実装完了 / Issue #3 independent audit PASS。
- Stage9C / Stage9D: Issue #17 DEV完了 / Issue #22 independent audit PASS。
- Stage9C/9D監査済みPR #27をcurrent mainへ統合済み。
  - audited head: `94c6789fc6f921b7362c0e890d3fee7f3db893a3`
  - merge commit: `0f17d65e1e3c737dfacd9cfee0c9d4062b683ade`
- Issue #26 protected integrity修正: audit PASS / main反映 / completed。
- Stage9 overall Gate: **PASS / completed**。
- Issue #4 `[Stage10][KNOWLEDGE] Test Prompt knowledge`: Stage10開始前外部調査完了 / Prompt班へhandoff済み。
  - knowledge handoff: `docs/stages/STAGE_10_KNOWLEDGE_HANDOFF.md`
  - handoff commit: `e1f676f28fcf963b6b2e0942c2381458065a1a5e`
  - 残る不確定項目はStage10実画像A/Bまたは明示HOLDへ移管。
- Issue #28 `[Stage10-PREP][DEV] Automated E2E functional test + machine verdict`: **PASS / completed**。
  - branch: `codex/issue28-e2e-verdict`
  - tested source: `fcf7b217d4270f43747cb7259aa80153e90ae45d`
  - evidence head: `04629908b38c29e3896eeca3c1fb64cf164c7142`
  - PR #33 merged to main / merge commit `9504fd64ce6b4acc762f589a734d67eac6b79e93`
  - real Windows local protected-data environment / real Tk 8.6.15 / no mocked rendering
  - full suite 285 passed / exit 0 / machine verdict PASS / required real-Tk scenarios 3/3 PASS
  - invalid recommendation resultのstate破壊バグを検出し、validation完了前に候補状態を置換しない修正をmainへ反映。
  - Stage0 protected hash/size/path-set checks維持・PASS。
- Issue #6 `[Stage10][TEMP] Forge Neo comparison environment`: **PASS_WITH_NOTE / completed**。
  - Multi Prompt Slots fixed SHA: `b3f45b17e5a24a20b4fa04edac74e6a4fec23dfe`。
  - Forge Neo Infinite Image Browsing fixed SHA: `ced039479c2e1463c9bdb136d355e01b3dfc9279`。
  - fixed-seed A/B (Seed 5072) PASS / PNG metadata・actual Prompt traceability PASS / baseline regular-generation regression PASS。
  - completion checkpoint: `docs/testing/ISSUE6_COMPLETION_CHECKPOINT_20260908.md`
  - verification: `docs/testing/ISSUE6_EXTENSION_INSTALL_AND_VERIFICATION_20260908.md`
  - audit: `docs/testing/ISSUE6_EXTENSION_AUDIT_20260908.md` / commit `472a219058771fe117b87d62c9d53d5402b8cff9`
- Issue #37 `[Stage10-PREP][CROSS] Validate golden-set representativeness against DanbooruTagTool purpose`: KNOWLEDGE / PROMPT representativeness reviewの共通結論を受領。
  - joint decision: **`REPLACE_OR_AUGMENT_WITH_SPECIAL_REPRESENTATIVE_SET`**
  - existing `standing / sitting / long_hair / smile` setはplumbing/evaluator fixtureとしてのみ保持。
  - Stage10代表評価としては不十分。
  - Special2788-centered代表性、rare/niche、relation / actor-target / body-site binding、multiple-Special、support-dependent visibilityをテスト方式へ反映。
  - routing思想: unsupported/low-confidence=`REVIEW`、traceability/infrastructure欠損=`BLOCKED`、simple/relational/composite/rare/model-familyを1つのglobal confidence/margin thresholdへ統合しない。
  - design authority: `docs/testing/ISSUE30_SPECIAL_REPRESENTATIVE_ROUTING_DESIGN_20260908.md`
- Issue #38 `[UI-JA][CROSS] Translation automation R3 spec + blind pilot review`: KNOWLEDGE / PROMPT contracts返却済み、R3 test implementation specへhandoff済み。
- Issue #39 `[UI-JA][DEV] R3 translation automation test engine + unseen 100 / blind30 harness`: **audit PASS / completed**。
  - audited implementation head: `53f02d9b3419db8fd9099b38204c29eed289ee8e`
  - actual quality pilot was follow-up Issue #41。
- Issue #41 `[UI-JA][PILOT] R3 fresh100 semantic evidence + real #32 bridge + blind30 quality gate`: **PASS_PILOT / completed / closed**。
  - final blind scoring checkpoint: `5589825869`。
  - production promotion、remaining P0 925、main merge、Stage10 production A/BはこのPASSでは未許可。
- Issue #45 `[UI-JA][AUDIT] Issue #36 FINAL CONVERGENCE V3 specification pre-review`: **APPROVE_V3_SPEC_FOR_EXECUTION / completed / closed**。
  - initial verdict: `APPROVE_WITH_REQUIRED_SPEC_CHANGES`（comment `5601089974`）。
  - replacement V3.1 contract: `86bf72246b3f1f42b52f562f45d4027f0d1a71ea`。
  - final delta re-review verdict: `APPROVE_V3_SPEC_FOR_EXECUTION`（comment `5601202000`）。
  - #36 execution authorization checkpoint: `5601218088`。
  - production promotionはこのspec PASSだけでは未許可。
- 常設班: 開発 / 監査 / 知識 / Prompt の4班。
- 別働横断班: ツール本体UIおよび翻訳改善班（Issue #34）。

## Active Work / Issues

### ACTIVE NOW

- 現在activeなDEV実装Issue: **#35 `[UI][DEV] Japanese-first desktop UI pass (dictionary frozen)`**。
  - parent: #34 UI-JA cross-team。
  - branch: `ui-ja/issue35-ui-only`
  - remote implementation checkpoint: `13b2a5ba3396e1d569cf9442b18b19eb7c815b1a`。
  - UI/presentation-only。`data/**`、Japanese overlay内容、Special2788内容、canonical/alias/semantic/generation-profile dataを変更しない。
  - recommendation/search ranking semanticsとStage9 composition semanticsは変更しない。
  - automated/remote implementationだけでfinished扱いせず、required test evidence + real Windows Tk screenshot/manual inspectionを完了する。
- #32 `[DICT-VALIDATION] Special2788 generation metadata full validation (quarantine)`
  - branch: `dict-validation/quarantine`。
  - production inputs read-onlyの長期品質監査。
  - Batch23（2201-2300）R2 gateはPASS。normal first-passの安全な再開地点はsequence 2301（Batch24）。
  - cumulative: PASS 1846 / FIX 174 / REVIEW 263 / IMAGE_TEST_REQUIRED 17。semantic support coverage 55/58。
  - #41用bridge fast-path/snapshotはnormal 2,788-row順序を進めた扱いにしない。
  - 現在の2,788件は**この監査の固定母数**として維持するが、最終freeze時の件数を2,788へ固定しない。
  - 2,788件本体監査完了後、final promotion audit前にpre-freeze completeness reconciliation（漏れ監査）を1回実施する。
  - genuine missing Specialが見つかった場合は既存2,788監査をやり直さず、追加deltaだけ同じ#32基準で監査してからpromotionへ進む。
- #44 `[KNOWLEDGE][ONGOING] Persistent generation knowledge corpus for dictionary audit and Stage10`
  - 現行の長期KNOWLEDGE lane。旧#4はcompleted historical handoffであり、ongoing ownerではない。
  - branch: `knowledge/generation-corpus`。
  - verified organized-corpus HEAD: `120a3d4a2f13d650d0cb22c2bc9a146aa7183ff3`。
  - canonical reading layer: `docs/knowledge/KNOWLEDGE_CATALOG.md` + `docs/knowledge/catalog/00-10`。
  - current reorganization status: **REORGANIZATION_COMPLETE / CATALOG_CANONICAL / INDEPENDENCE_PRESERVED**。
  - evidence/referenceを蓄積し、#32 / Stage10 / future #42へ根拠を返す。production仕様・#32 verdictを勝手に変更しない。
  - latest organization checkpoint: `5600440007`。
- #36 `[UI-JA][DATA] Japanese overlay coverage audit + priority expansion (quarantine)`
  - current V3 branch: `ui-ja/issue36-final-agent-convergence`。
  - V2 machine-convergence result was rejected as final convergence because accepted Japanese coverage collapsed while fallback expanded excessively。
  - V3.1 frozen authoritative contract commit: `86bf72246b3f1f42b52f562f45d4027f0d1a71ea`。
  - contract: `translation_quarantine/r3/ISSUE36_FINAL_CONVERGENCE_V3_AGENT_REVIEW.md`。
  - Issue #45 final spec verdict: **`APPROVE_V3_SPEC_FOR_EXECUTION`**（comment `5601202000`）。
  - current phase: **SPEC FROZEN / CODEX EXECUTION AUTHORIZED**（Issue #36 checkpoint `5601218088`）。
  - V3.1 agent execution may proceed under the frozen contract; semantic/scope rules may not be weakened。
  - production Japanese overlayは未変更のまま。production promotionはNOT_AUTHORIZEDで、V3.1 execution結果とseparate promotion audit/gateが必要。
- #30 `[Stage10-PREP][TEMP] Forge Neo A/B automation & external-tool integration`
  - Stage10本番A/Bの手作業を可能な限り減らす臨時担当。
  - external / existing tool first。
  - **Infrastructure pipeline: PASS_PIPELINE**。evidence commit `f2fc7acb15f996630c9f008284d80cf3261fb32f`。
  - Forge Neo API → fixed-seed A/B → `/sdapi/v1/png-info` actual metadata → WD14 raw confidenceまでuser manual operations 0で通過。
  - generic golden-set evidence `33215269cfeb33b3afab0c36a6a8bd52cb55952e` はlow-level fixtureとして保持。
  - generic contact-sheet taskは次のproduct-representative stepとして**PAUSED / SUPERSEDED**。
  - 次に進めてよいのはSpecial-representative test method / capability-routed routing設計まで。
  - final test data / evaluator allocationは辞書freeze + KNOWLEDGE coverage返却待ち。

### WAITING / GATED

- #5 `[Stage10][PROMPT] Formal handoff pending`
  - #4 KNOWLEDGE handoff受領済み。
  - #37共同結論を受領。
  - Prompt構造、A/B質問、support-isolation、replacement workflowの準備は進めてよい。
  - final representative Special IDs、Tagger割当、AUTO/REVIEW最終routing、production thresholdは辞書freeze後までHOLD。
- #34 `[UI-JA][CROSS] Tool UI / Japanese translation quality improvement`
  - UI-JA全体parent。#35 / #36の親・調整Issueとして継続。#41 pilotと#45 V3.1 spec auditはcompleted。
- #42 `[Stage10-PREP][RESERVED] Product-purpose improvement pass before production A/B`
  - **RESERVED ONLY**。辞書/data homeworkの完了・promotion/freeze前にactivateしない。
- #43 `[NAMING][RESERVED] Replace Special2788 as product concept name before final Stage10 freeze handoff`
  - **RESERVED ONLY**。#32 approved production promotion完了後の指定Gateまでactivateしない。

### RESERVED NEXT DEV — production data promotion / integration

- 次のproduction data反映は**DEV班の予約作業**とする。新Issueは現時点では作らず、実際にpromotion-readyになった時点で必要なら1本だけDEV Issueを起動する。
- 対象は2 lane:
  1. #32 Special辞書検証の承認済みproduction promotion（Special2788 generation metadata / semantic-support等）
  2. #36 UI-JAの承認済みproduction promotion（Japanese display/search overlay等。#39 engine基盤と#41 PASS_PILOTはcompleted evidence）
- 2 laneを同時完了待ちにはしない。**先に独立promotion gateを満たしたlaneからDEVが順次反映**する。
- production書き込み・mergeは必ず直列化する。同時promotionは禁止。
- #32 laneの反映は、current 2,788/2,788 + frozen semantic-support全件 + revalidation解消/明示park + false-PASS gate + candidate cross-consistency + **pre-freeze completeness reconciliation** + genuine missing-Special deltaがあればその追加監査 + separate final promotion audit PASS後。
- UI-JA laneの反映は、#41 PASS_PILOT evidence + #36 final artifact quality gate + false READY 0 + stale/contradiction解消 + separate overlay promotion audit PASS後。
- 各promotionはDEVが実施し、protected integrity / deterministic build or overlay generation / focused + regression + full feasible suite / real Windows UI確認を行い、AUDITが反映後差分を独立確認する。
- #32 production promotion完了後に**final Special dictionary freeze**とし、最終件数はcompleteness reconciliation結果に従う。そのsnapshotをKNOWLEDGEのWD14 / Kagami-24k / CL Tagger v2 coverage比較へ渡す。UI-JAの完了を待ってStage10 core準備を止めない。
- UI-JA promotionはStage10 core Gateと独立して進めてよいが、他のproduction変更と衝突する場合は後ろへ直列化する。
- この予約は#35の現行task contract / `CURRENT_DEV_TASK.md`を変更しない。#35完了前にpromotion DEVへ切り替えない。

### BACKLOG / MAINTENANCE

- #24 `[Maintenance][DEV] Local protected data backup / restore verification`
  - Stage10 blockerではない保守タスク。

## Not Started / Do Not Start Yet

- Stage10本番画像A/B試験
- Stage10 winner/scoring logicのproduction固定
- model family別Prompt grammarの未検証共通化
- final representative Special ID / exact case listの固定
- WD14 / Kagami-24k / CL Tagger v2最終担当範囲の固定
- SpecialごとのAUTO/REVIEW最終routing
- production confidence / margin threshold固定

## Current Gates

Stage10本番開始前に最低限必要:

1. Stage9 overall Gate — **SATISFIED**
2. #28 automated E2E functional test — **SATISFIED**
3. #4 KNOWLEDGEのStage10知識整理を正式handoffへ反映 — **SATISFIED**
4. #6 Forge Neo比較環境の導入・動作確認 — **SATISFIED / PASS_WITH_NOTE**
5. #30 Forge Neo A/B automation external-tool-first
   - infrastructure plumbing (`Forge API -> A/B -> metadata -> WD14 raw`) — **SATISFIED / PASS_PIPELINE**
   - generic golden fixture — **SATISFIED as plumbing fixture only**
   - Special-representative routing/test design — **DIRECTION ADOPTED via #37**
   - final representative data / evaluator coverage / routing calibration — **REMAINS / HOLD until dictionary freeze**
6. #5 Prompt班へ正式Specialデータ・実験仕様・自動化運用をhandoff
7. Multi Prompt Slots等の比較手段確認 — **SATISFIED**
8. A/B固定条件定義
9. metadata保存方法定義 — **SATISFIED for Issue #6 baseline / handoff**
10. model family差を保持し未検証共通化していないこと
11. 実際に使ったPromptを各画像/結果へ追跡できること — **SATISFIED for Issue #6 baseline / handoff**
12. #32 current 2,788 validation完了 → pre-freeze completeness reconciliation → missing-Special deltaがあれば追加監査 → promotion audit PASS → DEV production反映 → final Special dictionary freeze
13. final Special dictionary freeze後、KNOWLEDGEがWD14 / Kagami-24k / CL Tagger v2 coverageを比較しPROMPT/#30へ返却
14. #42 reserved pre-Stage10 product-purpose improvement passをactivation条件成立後に完了
15. `docs/stages/STAGE_10_PREP.md` の残チェックを満たすこと

## Next Actions

1. #35はremaining test evidence + real Windows Tk screenshot/manual inspectionを完了する。`data/**`は変更しない。
2. #32はnormal sequence 2301からcurrent 2,788 full validationを継続。完了後にpre-freeze completeness reconciliationを実施し、genuine missing Specialがあれば追加deltaのみ同じ基準で監査する。その後にfinal promotion audit → 予約済みDEV promotion → #43 naming gate → final Special dictionary freezeへ進む。
3. #44 KNOWLEDGEはcanonical `docs/knowledge/catalog/00-10`体系を維持しつつpersistent corpusを継続し、#32のfalse-PASS防止・model-family別Prompt support・Stage10 evaluator設計に必要な根拠をGitHub corpusへ蓄積する。旧#4へ現在地を戻さない。
4. #36はIssue #45で承認されたfrozen V3.1 contract `86bf72246b3f1f42b52f562f45d4027f0d1a71ea`に従ってCodex agent executionを進める。quarantine境界を維持し、production `data/**` / Japanese overlayへ直接書き込まない。
5. #36 V3.1 execution完了後はfinal artifact quality gateとseparate promotion auditを通し、production promotionはそのPASS後のみDEVへhandoffする。
6. #30は `docs/testing/ISSUE30_SPECIAL_REPRESENTATIVE_ROUTING_DESIGN_20260908.md` に従い、test method / routing architectureのみ整理する。
7. final Special dictionary freeze後、#44 KNOWLEDGEがWD14 EVA02 v3 / Kagami-24k / CL Tagger v2 stable/fixed releaseの**final frozen Special count** coverage比較を実施する。
8. coverage返却後、PROMPTがfinal representative Special/caseを確定し、#30がcapability別AUTO/REVIEW routingを校正する。
9. #5へ#30最終結果・正式Specialデータ・実験仕様・自動化運用を反映する。
10. 辞書/data前提が完了・freezeした後に#42をactivateし、product-purpose improvement passを完了する。
11. 全Gate完了後のみStage10本番A/Bへ移行する。

## Blocking / Unknown

- Stage9 blockerなし。Issue #28 functional E2E PASS。
- E2Eはvisual-layout/manual desktop inspection、全2,788 Special総当たり、Forge同時稼働性能、画像品質を検証するものではない。
- GitHub Actions CIは本体production Gateとして未導入。#28 PASSはlocal protected-data environmentの実Tk証跡。
- #30のForge API/A/B/metadata/WD14配管blockerは解消済み。
- #30の残blockerはfinal dictionary freeze後のevaluator coverage、representative Special確定、capability別routing妥当性、REVIEW fallback校正。
- #39 engine実装はaudit PASS / completed。full pytestの既知Windows ACL limitationは#41のisolated pilot evidenceと区別して扱う。
- #41は**PASS_PILOT / completed / closed**。active blockerではない。
- #45は**APPROVE_V3_SPEC_FOR_EXECUTION / completed / closed**。active blockerではない。
- #36 V3.1 executionはauthorized。production promotionは未許可で、execution結果・final artifact quality gate・separate promotion auditが残る。
- 現2,788件はrunning auditの固定母数だが、**final frozen Special countの完全性はpre-freeze completeness reconciliation完了まで未確定**。
- WD14をSpecial2788全体のground truthにしない。
- unusual anatomy系Specialへ `bad anatomy / extra limbs / extra arms` 等を無条件適用しない。別A/B項目。
- #34/#35はStage10開始Gateそのものではないが、現行UIを完成UIとして扱わない。

## Issue Hygiene

- Issue番号は履歴・参照のため振り直さない。
- 新規Issueは、owner / scope / lifecycle / Gateのいずれかが既存Issueから独立して管理する必要がある場合に限る。
- 単なる途中経過、再監査、結果返却、同一task内の次ステップは原則として既存Issueのcheckpointコメントで継続し、不要にIssue番号を増やさない。
- 完了条件を満たし、後続Issueまたは正本へ結果がhandoff済みのIssueはcloseして履歴として保持する。
- `CURRENT_STATE.md` では `ACTIVE NOW / WAITING / BACKLOG` を分け、通常作業者が全履歴Issueを追わなくて済む状態を維持する。

## Source-of-Truth Rule

- このファイルは現在地の正本。
- `Active Teams Registry` は現在地を見失わないためのrouting/indexであり、新しい独立正本ではない。
- 実作業・完了条件・結果は対応Issueに残す。
- active DEV Issueが存在する場合のみ `docs/project/CURRENT_DEV_TASK.md` を現行DEV Issue本文の同期ミラーとして使う。
- 現在activeなDEV Issueは **#35**。#30/#32/#36/#44および予約済みfuture promotion taskがCURRENT_DEV_TASKを上書きしない。#41/#45はcompleted historical evidenceでありactive identityではない。
- 各作業チャットは開始時に `CHAT_START_PROTOCOL.md` の班ID形式でlive `BRANCH / HEAD / CHECKPOINT / CONTRACT / PHASE` を再取得する。`v2/v3/R3/FINAL`等の人間向け版名だけで現在個体を判断しない。
- 共有管理ファイルは最新mainを取得してから更新し、stale copyで上書きしない。
- Codex完了報告だけで次Gateへ進まない。
- 仕様変更は `DECISIONS.md` またはStage仕様へ反映する。