# GitHub Project 最小セットアップ（任意）

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
