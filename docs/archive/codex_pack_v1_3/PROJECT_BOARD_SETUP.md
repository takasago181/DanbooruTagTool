# GitHub Project 最小セットアップ（HISTORICAL / NOT PLANNED）

> **現在は使用しません。**
>
> GitHub Project管理ボードの導入は Issue #47 で **NOT PLANNED / CLOSED** と決定済みです。
> 現行管理は次の3層です。
>
> 1. `docs/project/CURRENT_STATE.md` — 全体routing/current state
> 2. 各GitHub Issue — task contract / checkpoint / evidence
> 3. `docs/project/CURRENT_DEV_TASK.md` — current core DEVのCodex読取ミラー
>
> このファイルは過去の導入案を歴史資料として保存しているだけです。新しい作業チャットやCodexは、この文書を現行セットアップ指示として使わないでください。
> 2026-09-11 cleanup auditで現行用途なしを明示しました。削除はしていません。

---

## Historical proposal below

GitHub Project本体は補助UIです。
`docs/project/CURRENT_STATE.md` + GitHub Issuesだけで現行作業を管理できるため、Project未設定はStage blockerではありません。

必要になった場合だけProjectを1個作る。

名前:
`DanbooruTagTool Development`

## Fields

1. Status
   - Backlog
   - Ready
   - Working
   - Audit
   - Blocked
   - Hold
   - Done

2. Team
   - DEV
   - AUDIT
   - KNOWLEDGE
   - PROMPT
   - TEMP

3. Stage
   - 9B
   - 9C
   - 9D
   - 10
   - 11
   - Maintenance

4. Type
   - Spec
   - Implementation
   - Research
   - Experiment
   - Bug
   - Audit

5. Priority
   - P0
   - P1
   - P2

## Views

- NOW
  - Status: Ready / Working / Audit / Blocked

- Stage 9
  - Stage = 9B / 9C / 9D

- Stage 10
  - Stage = 10

- Audit Queue
  - Team = AUDIT
  - Status != Done

- Knowledge Queue
  - Team = KNOWLEDGE
  - Status != Done

- Prompt Queue
  - Team = PROMPT
  - Status != Done

## 現行Issueの扱い

Projectを後から作る場合も、Issue番号・Stage・現在地は `CURRENT_STATE.md` から取得する。
このファイルに書かれた例や古いIssue番号を正本として使わない。

最初から細かいIssueを大量に作らない。
作業が確定した時点で増やす。

現在の管理では、Stage9B後に承認済みStage9仕様の9C/9D Gateを暗黙スキップしないことが重要。詳細は `CURRENT_STATE.md` と将来DEV Issue #17を参照する。
