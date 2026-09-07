# CURRENT DEV TASK

最終同期: 2026-09-08

## Mirror Metadata

- Source: GitHub Issue #28
- Title: `[Stage10-PREP][DEV] Automated E2E functional test + machine verdict`
- State: open
- Purpose: Codexがprivate GitHub Issue APIへ追加認証せず、現行DEV作業内容をrepository内から読めるようにする同期ミラー。

## Sync Contract

- GitHub Issueが実作業の管理記録であり、このファイルはCodex読取用ミラー。
- `docs/project/CURRENT_STATE.md` の現行DEV Issue番号と、このファイルの `Source` が一致しない場合は実装を開始しない。
- Issue本文・state・完了条件変更時はこのファイルも同じ管理作業内で同期する。
- Codexはprivate Issueへ直接書き込む必要はない。repository成果を残し、DEVが確認してIssueへ証跡化する。

## 現在地

- Stage9 overall Gate: **PASS / completed**
- Stage10本番A/B: **未開始**
- 現行DEV: Issue #28
- 背景: 既存の275 passed等はlocal pytest証跡で、GitHub Actions workflowは存在しない。実アプリの起動→操作→Prompt出力までを継続的に自動判定するE2E Gateが不足している。

## 今やること

1. 実アプリ主要経路を自動で通すE2E / functional smoke testを追加する。
2. 可能な限り実production class/pathを使用し、mockだけで成立する偽E2Eにしない。
3. 最低限以下を通す。
   - アプリ/session初期化
   - 日本語または英語検索
   - Special候補選択 / Core反映
   - semantic / co-occurrence候補登録
   - common / rareそれぞれから選択
   - INCLUDE / EXCLUDE / DEFAULT persistence
   - manual auxiliary追加 / 削除
   - Prompt preview生成
   - copy相当出力一致
   - provenance / evidence追跡
   - Stage9D reversible variant切替→baseline完全復元
   - invalid / stale resultが現在stateを壊さない
4. GUI実行可能環境ではTk UIをheadless automationで通す。
5. Tk実行不能なら、純unitだけでE2E PASSとはせず、必須GUI経路が未実施ならBLOCKEDまたは明示的に別Gate化する。
6. machine-readable result（JSON等）とhuman-readable report（Markdown）を作る。
7. verdictを `PASS / FAIL / BLOCKED` のいずれかで自動判定する。
8. focused / regression / full suite可能範囲 / protected/hash / `git diff --check` を再確認する。
9. review可能なfeature branch/commitへまとめremote pushする。
10. repository reportへ実行環境、コマンド、結果、未実施、制約、stop pointを残して停止する。

## PASS条件

- 必須シナリオが実production pathで成功。
- common/rare両bucketを実際に通す。
- Prompt output / state / provenance / selection persistence / reversible restorationが期待値一致。
- machine-readable verdict = PASS。
- focused/regression/full suite可能範囲がPASS。
- 実行環境・未実施項目・限界が明記されている。

## FAIL条件

- 起動不能、主要ユーザー経路例外、Prompt/state不整合、selection喪失、baseline復元失敗、provenance欠落、common/rare片側のみ等。
- FAIL時はStage10本番へ進まない。

## BLOCKED条件

- local-only protected data / GUI display等の環境不足で必須経路を実行不能。
- BLOCKEDをPASS扱いしない。

## 禁止

- mockだけのテストをE2E PASSと呼ばない。
- 既存protected/hash検証を弱めない。
- テストを通すためproduction仕様を都合よく弱体化しない。
- Stage10本番画像A/Bを開始しない。
- #4/#5/#6の作業を勝手に置き換えない。

## 証跡

Codexはreview可能なbranch/commit、テストコード、実行コマンド、machine-readable result、人間可読report、focused/regression/full suite結果、未解決事項、stop pointをrepositoryへ残してremote pushする。

DEVはCodex完了後にremote成果を実確認し、Issue #28へ完了証跡を記録する。Codex自身のprivate Issue書込みは不要。
