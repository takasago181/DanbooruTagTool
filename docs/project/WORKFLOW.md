# WORKFLOW

## Issueの流れ

Backlog
→ Ready
→ Working
→ Audit
→ Done

必要時:
- Blocked
- Hold

## 役割

### DEV
実装・仕様整理・Stage管理。

### AUDIT
完了条件、回帰、正本整合性を確認。

### KNOWLEDGE
外部調査と根拠整理。
出力は FACT / ADOPT候補 / HOLD / REJECT を基本とする。

### PROMPT
Stage10の実験Promptを作る。
原則1実験1疑問。
A/B間で比較対象以外を固定。

## GitHub Project 推奨Fields

| Field | 値 |
|---|---|
| Status | Backlog / Ready / Working / Audit / Blocked / Hold / Done |
| Team | DEV / AUDIT / KNOWLEDGE / PROMPT / TEMP |
| Stage | 9B / 10 / 11 / Maintenance |
| Type | Spec / Implementation / Research / Experiment / Bug / Audit |
| Priority | P0 / P1 / P2 |

## 推奨Views

### NOW
Status = Ready, Working, Audit, Blocked

### Stage 9B
Stage = 9B

### Stage 10
Stage = 10

### Audit Queue
Team = AUDIT and Status != Done

### Research Queue
Team = KNOWLEDGE and Status != Done

### Prompt Queue
Team = PROMPT and Status != Done

個人開発なので担当者フィールドは不要。
「Team」は人ではなく作業モードを表す。
