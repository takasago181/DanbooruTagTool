# CURRENT STATE

最終更新: 2026-09-08

## Current Stage

Stage 9 overall Gate 完了 / Stage10 準備Gate実施中 / automated E2E PASS

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
- Issue #38 `[UI-JA][CROSS] Translation automation R3 spec + blind pilot review`: KNOWLEDGE / PROMPT contracts返却済み、R3 test implementation specへhandoff済み。Issue #39が実装・検証の後続担当。
- 常設班: 開発 / 監査 / 知識 / Prompt の4班。
- 別働横断班: ツール本体UIおよび翻訳改善班（Issue #34）。

## Active Work / Issues

### ACTIVE NOW

- 現在activeなDEV実装Issue: **#35 `[UI][DEV] Japanese-first desktop UI pass (dictionary frozen)`**。
  - parent: #34 UI-JA cross-team。
  - branch: `ui-ja/issue35-ui-only`
  - UI/presentation-only。`data/**`、Japanese overlay内容、Special2788内容、canonical/alias/semantic/generation-profile dataを変更しない。
  - Final Prompt以外は日本語がある場合 `日本語 / canonical`、ない場合 `日本語未登録 / canonical`。
  - recommendation/search ranking semanticsとStage9 composition semanticsは変更しない。
  - 実装後real Windows Tk screenshot/manual inspection必須。
- #32 `[DICT-VALIDATION] Special2788 generation metadata full validation (quarantine)`
  - production inputs read-onlyの長期品質監査。
  - Stage10 final dictionary freezeへ向けた意味/生成メタデータ検証。
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

- #39 `[UI-JA][DEV-QUEUED] R3 translation automation test engine + unseen 100 / blind30 harness`
  - Issue #40 architecture verdictを反映したbridge32条件を維持。
  - full-suiteの52 setup errorsは全件Windows ACL / WinError 5と証跡化済み。`FULL_PYTEST = ENVIRONMENT_BLOCKED`、call-phase failure 0。
  - search-safety reworkはPASS。残HOLDは#40 controlled-bridge契約の薄いpatch 1件。
  - bridge patch PASS前にreal frozen evidence / blind30 quality auditへ進まない。
  - #35をCURRENT_DEV_TASKから置き換えない。
- #5 `[Stage10][PROMPT] Formal handoff pending`
  - #4 KNOWLEDGE handoff受領済み。
  - #37共同結論を受領。
  - Prompt構造、A/B質問、support-isolation、replacement workflowの準備は進めてよい。
  - final representative Special IDs、Tagger割当、AUTO/REVIEW最終routing、production thresholdは辞書freeze後までHOLD。
- #36 `[UI-JA][DATA] Japanese overlay coverage audit + priority expansion (quarantine)`
  - production Japanese dataはfreezeしたまま候補/検証を継続。
  - #39 R3 gateと独立監査後にpromotion可否を判断。
- #34 `[UI-JA][CROSS] Tool UI / Japanese translation quality improvement`
  - UI-JA全体parent。#35 / #36 / #39の親管理Issueとして継続。

### RESERVED NEXT DEV — production data promotion / integration

- 次のproduction data反映は**DEV班の予約作業**とする。新Issueは現時点では作らず、実際にpromotion-readyになった時点で必要なら1本だけDEV Issueを起動する。
- 対象は2 lane:
  1. #32 Special辞書検証の承認済みproduction promotion（Special2788 generation metadata / semantic-support等）
  2. #36/#39 UI-JAの承認済みproduction promotion（Japanese display/search overlay等）
- 2 laneを同時完了待ちにはしない。**先に独立promotion gateを満たしたlaneからDEVが順次反映**する。
- production書き込み・mergeは必ず直列化する。同時promotionは禁止。
- #32 laneの反映は、2,788/2,788 + frozen semantic-support全件 + revalidation解消/明示park + false-PASS gate + candidate cross-consistency + separate final promotion audit PASS後。
- UI-JA laneの反映は、R3 bridge/fresh100/blind30 gate + false READY 0 + stale/contradiction解消 + separate overlay promotion audit PASS後。
- 各promotionはDEVが実施し、protected integrity / deterministic build or overlay generation / focused + regression + full feasible suite / real Windows UI確認を行い、AUDITが反映後差分を独立確認する。
- #32 production promotion完了後に**final Special2788 dictionary freeze**とし、そのsnapshotをKNOWLEDGEのWD14 / Kagami-24k / CL Tagger v2 coverage比較へ渡す。UI-JAの完了を待ってStage10 core準備を止めない。
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
12. #32 promotion audit PASS → DEV production反映 → final Special2788 dictionary freeze
13. final Special2788 dictionary freeze後、KNOWLEDGEがWD14 / Kagami-24k / CL Tagger v2 coverageを比較しPROMPT/#30へ返却
14. `docs/stages/STAGE_10_PREP.md` の残チェックを満たすこと

## Next Actions

1. #35 UI-only改善を継続し、real Windows Tk screenshot/manual inspectionを実施。`data/**`は変更しない。
2. #32はfull validation / final promotion auditまで継続。PASS後、予約済みDEV promotionを起動し、production反映後にSpecial2788をfreezeする。
3. #36/#39はR3 bridge → fresh100 → blind30 → overlay promotion auditまで継続。PASS後、予約済みDEV promotionでproduction Japanese overlayへ反映する。
4. #30は `docs/testing/ISSUE30_SPECIAL_REPRESENTATIVE_ROUTING_DESIGN_20260908.md` に従い、test method / routing architectureのみ整理する。
5. final Special2788 freeze後、KNOWLEDGEがWD14 EVA02 v3 / Kagami-24k / CL Tagger v2 stable/fixed releaseの2,788 coverage比較を実施する。
6. coverage返却後、PROMPTがfinal representative Special/caseを確定し、#30がcapability別AUTO/REVIEW routingを校正する。
7. #5へ#30最終結果・正式Specialデータ・実験仕様・自動化運用を反映する。
8. 全Gate完了後のみStage10本番A/Bへ移行する。

## Blocking / Unknown

- Stage9 blockerなし。Issue #28 functional E2E PASS。
- E2Eはvisual-layout/manual desktop inspection、全2,788 Special総当たり、Forge同時稼働性能、画像品質を検証するものではない。
- GitHub Actions CIは未導入。#28 PASSはlocal protected-data environmentの実Tk証跡。
- #30のForge API/A/B/metadata/WD14配管blockerは解消済み。
- #30の残blockerはfinal dictionary freeze後のevaluator coverage、representative Special確定、capability別routing妥当性、REVIEW fallback校正。
- #39 full pytestは`ENVIRONMENT_BLOCKED`。call-phase failure 0の証跡あり。残HOLDはcontrolled-bridge contract patch。
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
- 実作業・完了条件・結果は対応Issueに残す。
- active DEV Issueが存在する場合のみ `docs/project/CURRENT_DEV_TASK.md` を現行DEV Issue本文の同期ミラーとして使う。
- 現在activeなDEV Issueは **#35**。#30/#32/#39および予約済みfuture promotion taskがCURRENT_DEV_TASKを上書きしない。
- 共有管理ファイルは最新mainを取得してから更新し、stale copyで上書きしない。
- Codex完了報告だけで次Gateへ進まない。
- 仕様変更は `DECISIONS.md` またはStage仕様へ反映する。
