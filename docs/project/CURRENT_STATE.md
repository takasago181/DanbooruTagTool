# CURRENT STATE

最終更新: 2026-09-08

## Current Stage

Stage 9 overall Gate 完了 / Stage10 準備Gate実施中 / automated E2E動作確認 + A/B自動化準備中

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
  - 残る不確定項目はStage10実画像A/BへHOLD移管。
- 常設班: 開発 / 監査 / 知識 / Prompt の4班。

## Active Work / Issues

- #28 `[Stage10-PREP][DEV] Automated E2E functional test + machine verdict`
  - 現行DEV Issue。
  - unit/regressionだけでなく、実アプリ主要経路を自動で通して `PASS / FAIL / BLOCKED` を機械判定する。
  - mockだけでE2E PASSとはしない。
  - アプリ/session初期化、検索、Special選択、common/rare候補選択、selection persistence、Prompt preview/copy、provenance/evidence、Stage9D可逆variant復元、stale/invalid result保護まで確認する。
  - GUI実行可能環境ではTk UI headless automationも通す。環境不足で必須経路を実行不能ならBLOCKED。
- #5 `[Stage10][PROMPT] Formal handoff pending`
  - #4 KNOWLEDGE handoff受領済み。
  - Stage10正式handoff / Specialデータ / 実験仕様 /固定条件等の整理。
- #6 `[Stage10][TEMP] Forge Neo comparison environment`
  - Forge Neo比較環境の導入・動作確認。
  - existing-tool-firstでMulti Prompt Slots / Forge Neo Infinite Image Browsing / built-in X/Y/Z等を確認する。
- #30 `[Stage10-PREP][TEMP] Forge Neo A/B automation & external-tool integration`
  - Stage10本番A/Bの手作業を可能な限り減らす臨時担当。
  - 既存導入済み拡張 → Forge Neo標準機能 → Forge Neo対応拡張 → 外部CLI/API/OSS → 不足分だけ薄いglue scriptの順で検討する。
  - A/B Prompt差し替え、固定/複数seed生成、metadata/実Prompt追跡、WD14等による一次判定、`A_WIN / B_WIN / REVIEW / BLOCKED` 振り分け、結果レポートまでを対象とする。
  - 本体productionへ未検証の実験管理・自動判定を先行実装しない。

## Not Started / Do Not Start Yet

- Stage10本番画像A/B試験
- Stage10 winner/scoring logicのproduction固定
- model family別Prompt grammarの未検証共通化

## Current Gates

Stage10本番開始前に最低限必要:

1. Stage9 overall Gate — **SATISFIED**
2. #28 automated E2E functional test — **CURRENT**
3. #4 KNOWLEDGEのStage10知識整理を正式handoffへ反映 — **SATISFIED**
4. #6 Forge Neo比較環境の導入・動作確認
5. #30 Forge Neo A/B automationのexternal-tool-first構成確認 + dry run
6. #5 Prompt班へ正式Specialデータ・実験仕様・自動化運用をhandoff
7. Multi Prompt Slots等の比較手段確認
8. A/B固定条件定義
9. metadata保存方法定義
10. model family差を保持し未検証共通化していないこと
11. 実際に使ったPromptを各画像/結果へ追跡できること
12. `docs/stages/STAGE_10_PREP.md` の残チェックを満たすこと

## Next Actions

1. Issue #28で実アプリ主要経路の自動E2Eテストとmachine verdictを実装・実行する。
2. DEVがremote branch / commit / test result / machine-readable report / human-readable reportを実確認する。
3. PASS時のみStage10準備を継続する。FAIL/BLOCKEDならStage10本番へ進まず原因を解消する。
4. #6 / #30 / #5の残Gateを並列・合流で完了する。
5. #30はexternal / existing tool firstで、既存機能だけで減らせる手作業を先に実測し、実際のgapだけを自作対象にする。
6. #5は `docs/stages/STAGE_10_KNOWLEDGE_HANDOFF.md` と #6 / #30の結果を正式handoffへ反映する。
7. 全Gateが満たされた後にのみStage10本番A/Bへ移行する。

## Blocking / Unknown

- GitHub Actions workflowは現時点で存在せず、過去の275 passed等はlocal pytest証跡。起動→操作→出力までの継続的E2E Gateが未整備だったためIssue #28で補う。
- GitHubはlocal protected dataの完全backupではない。E2E必須経路がlocal protected dataを必要とする場合は、local protected environmentでの実行証跡を使用し、GitHub CI PASSとは表現しない。
- Stage10はまだ未開始。
- Issue #4のHOLD項目はStage10実画像A/Bで再評価するが、pre-Stage10 KNOWLEDGE blockerではない。
- #30の自動評価は完全自動判定を前提にせず、認識困難・信頼度不足をREVIEWへ逃がす設計とする。

## Source-of-Truth Rule

- このファイルは現在地の正本。
- 実作業の管理記録・完了条件・結果は対応Issueに残す。
- active DEV Issueが存在する場合のみ `docs/project/CURRENT_DEV_TASK.md` をそのIssue本文の同期ミラーとして使う。
- 現在のactive DEV Issueは #28。
- Codexへ新規/再開指示前にIssue #28本文/stateと最新mainのCURRENT_STATE/CURRENT_DEV_TASKをlive照合する。
- Codexはprivate Issueへ直接書き込む前提ではない。repository成果を残し、DEVが確認してIssueへ証跡化する。
- Codexの完了報告だけで次Gateへ進まない。
- 仕様変更は `DECISIONS.md` またはStage仕様へ反映する。
- 共有管理ファイルは最新mainを取得してから更新し、stale copyで上書きしない。
