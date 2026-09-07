# GitHub Project 最小セットアップ

GitHub上でProjectを1個だけ作る。

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

- Stage 9B
  - Stage = 9B

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

## 最初に作るIssue

1. `[Stage9B][DEV] Stage9B完了`
2. `[Stage9B][AUDIT] Stage9B完了監査`
3. `[Stage10][TEMP] Forge Neo比較環境 動作確認`
4. `[Stage10][KNOWLEDGE] Stage10 Prompt知識整理`
5. `[Stage10][PROMPT] Stage10正式handoff待ち`

最初から細かいIssueを大量に作らない。
作業が確定した時点で増やす。
