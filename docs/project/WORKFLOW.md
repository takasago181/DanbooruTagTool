# WORKFLOW

## Issueの流れ

Backlog
→ Ready
→ Working
→ Audit（必要なGateのみ）
→ Done

必要時:
- Blocked
- Hold

## 役割

### DEV
実装・仕様整理・routing・Gate管理。

### AUDIT
常設ではない。必要な品質Gateで、完了条件・回帰・正本整合性を独立確認する。

### KNOWLEDGE
外部調査とgeneration knowledge corpus維持。
出力は FACT / ADOPT候補 / HOLD / REJECT を基本とし、v1へ機能を自動昇格しない。

### PROMPT
将来、採用済みgeneration-effectiveness機能が画像依存の検証を必要とする場合に、controlled Prompt / A-B実験設計を担当する。
原則1実験1疑問、比較対象以外を固定する。
**v1の必須laneではない。**

### Codex
DEVの実装担当。独立した仕様決定権・Gate PASS権限は持たない。

## 途中checkpoint

意味のある成果が出た時、長時間中断・話題切替・handoff前、または直近成果を失うと再開コストが高い時は、担当Issueへ短いcheckpointを残す。

最低限:
- 最後に成功したこと / 結果
- 未完了またはblocker
- 次作業
- branch / commit / file / evidence

通常checkpointはIssueコメントに置く。
コメントは履歴・証跡でありtask contractを変更しない。
目的・scope・禁止事項・完了条件を変える場合はlive Issue本文を更新し、`CURRENT_STATE.md` routingと整合させる。

## 班間依頼・返却

GitHub Issueを標準経路とし、ユーザーを手動コピペ中継役にしない。

### 依頼
最低限:
- `FROM`
- `REQUEST`
- `WHY`
- `EXPECTED OUTPUT`
- `RELATED`

登録後はユーザーにも依頼内容を要約して見せる。

### 結果
最低限:
- `RESULT`
- `EVIDENCE / SOURCE`
- `DECISION`
- `LIMITATION / BLOCKER`
- `NEXT`

依頼元の次作業に必要なら依頼元Issueにも短い返却checkpointを残す。

対象:
- DEV
- KNOWLEDGE
- PROMPT
- 必要時AUDIT
- current TEMP

例外:
- local-only / binary / protected data
- connector障害
- push不能等

例外時も理由・代替handoff所在・回収担当をIssueへ残す。

## DEV → Codex preflight

Codexは新規実装・再開時に `AGENTS.md` startup gateを実行する。
current DEV Issueのlive取得とfail-closed条件は `AGENTS.md` / `PERMANENT_RULES.md` に従う。

## Shared management docs

`CURRENT_STATE.md` / `PERMANENT_RULES.md` / `DECISIONS.md` / product scope / Stage Gate文書を変更する前にlatest mainを再取得する。

- stale chat copyで全上書きしない
- conflict時は停止
- 通常進捗はIssue checkpointへ
- global routing/大方針が変わった時だけshared docsを更新

大方針変更では `PRODUCT_GOAL_LOCK.md`、#42等product-scope Issue、`AGENTS.md`、`FEATURE_PRIORITY.md`、`FLOWCHARTS.md`、影響lane Issueを照合する。

## Codex implementation branch

- latest mainからtask feature branch
- direct main implementation commit禁止
- stable checkpointをcommit
- push可能ならremoteへpush
- GitHubから確認できる成果物でmanual ZIPを要求しない
- local-only/binary/push failure時だけfallback

## Audit結果

### PASS
証拠をIssueへ残し、必要ならroutingを更新して次へ。

### CONDITIONAL PASS
条件・未解決事項を明記し、DEVが次Gate開始可否を判断する。無条件PASSとして扱わない。

### FAIL
次へ進めない。指摘と根拠を残し、DEV/repair Issueへ戻す。再監査PASSまでGateを越えない。

## GitHubとlocal protected data

GitHubはmanagement stateとcommit済みcode/docsの正本だが、local workspace全体のbackupではない。

- ignored raw/derived/runtime/Special large dataを保護
- GitHubに見えないことを削除と解釈しない
- `git clean -fdx` / `git clean -fdX` 禁止
- fresh cloneだけでfull runtime/full tests成立と仮定しない

## GitHub Project

現在は未採用。
Issue #47で管理ボードはNOT PLANNEDとなった。
`CURRENT_STATE.md` + live Issuesを管理正本とし、Projectをtask contract/Gate authorityにしない。
