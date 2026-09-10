# DanbooruTagTool 管理ボード運用方針

Status: **NOT PLANNED / SUPERSEDED BY CURRENT_STATE + ISSUE MODEL**

初回採用検討: 2026-09-09  
見送り決定: 2026-09-10  
Decision owner: Issue #47

## Final decision

GitHub Project「DanbooruTagTool 管理ボード」の本体導入は行わない。

理由:
- `docs/project/CURRENT_STATE.md` が全体routing/current stage/dependency/workstream stateを担う。
- 各GitHub Issueがtask contract / completion criteria / checkpoint / evidenceを担う。
- Codexは `CURRENT_STATE.md` が示すcurrent core DEV IssueをGitHubから直接取得する。`CURRENT_DEV_TASK.md` は移行期間中の参考資料 / fallback diagnostic artifactとして保持する。
- これに加えてGitHub Projectを常時同期対象にすると、管理情報の重複・drift・更新負担が増える。

## Current management model

正規管理は次の2層を中心とし、移行参考資料を別扱いで保持する。

1. `CURRENT_STATE.md` — 全体routing/current stateとcurrent DEV Issue番号
2. 各live Issue — task contract / evidence / checkpoint

`CURRENT_DEV_TASK.md` は移行期間中の参考資料 / fallback diagnostic artifactであり、Issueの代替・同期義務の対象ではない。

GitHub Projectはtask contractやGate authorityとして使用しない。

## Preserved historical material

以下は導入検討の履歴として保持する。
- 本ファイルのGit履歴
- `docs/project/CONTROL_BOARD_MIGRATION_DESIGN.md`
- Issue #47
- 過去に各Issueへ行った導入通知
- Issue template側に残る一般的なGitHub-first管理参照

これらは現在のProject導入義務を意味しない。

## Reconsideration condition

将来、Issue数・並列レーン・依存関係が増え、現在の3層では実際に運用不能または高頻度の見落としが発生した場合のみ、別Issueで再検討する。

現時点では新しい管理正本を増やさない。
