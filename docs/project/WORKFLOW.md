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

## 途中checkpoint

意味のある成果が出た時、長時間中断・話題切替・handoff前、または直近成果を失うと再開コストが高い時は、担当Issueへ短いcheckpointコメントを残す。

最低限:
- 最後に成功したこと / 結果
- 未完了またはblocker
- 次作業
- branch / commit / file / evidence（ある場合）

通常のcheckpointはIssueコメントに置く。コメントは履歴・証跡であり、task contractを変更しない。
目的・scope・禁止事項・完了条件を変える場合はIssue本文を更新する。現行DEV Issueなら `docs/project/CURRENT_DEV_TASK.md` も同じ管理作業内で同期する。

## 班間依頼・返却

班間の情報受け渡しはGitHub Issueを標準経路とする。ユーザーを手動コピペの中継役にしない。

### 依頼側

班Aが班Bへ依頼する時は、班Bの現行Issueへ依頼checkpointを残す。

最低限:
- `FROM`: 依頼元班 / Issue
- `REQUEST`: 何をしてほしいか
- `WHY`: なぜ必要か
- `EXPECTED OUTPUT`: 返してほしい形式・判定
- `RELATED`: 関連Issue / file / commit / evidence

### 受取側

班Bは作業結果をチャットだけで終わらせず、自班Issueへ結果checkpointを残す。

最低限:
- `RESULT`
- `EVIDENCE / SOURCE`
- `DECISION`: FACT / ADOPT候補 / HOLD / REJECT / PASS / FAIL 等、班に応じた判定
- `LIMITATION / BLOCKER`
- `NEXT`

### 返却

結果が依頼元班の次作業に必要なら、班Bまたは管理側が班Aの現行Issueにも短い返却checkpointを残す。
詳細は班BのIssueを参照させ、同じ長文を複製しない。

標準の流れ:

班A Issue
→ 班B Issueへ依頼checkpoint
→ 班Bが作業
→ 班B Issueへ詳細結果checkpoint
→ 班A Issueへ短い返却checkpoint + 班B Issue参照
→ 班AがGitHubから再開

対象:
- DEV
- AUDIT
- KNOWLEDGE
- PROMPT
- 現行Issueを持つTEMP

例外:
- local-only / binary / protected data
- GitHub connector障害
- push不能などGitHubに成果物を置けない合理的理由

例外時も、理由・代替handoffの所在・次に誰が回収するかをIssueへ記録する。

## DEV → Codex preflight

Codexへ新規実装・再開指示を出す直前にDEV/管理側が行う。

1. private GitHubの現行DEV Issue本文/stateをlive取得する。
2. 最新mainの `CURRENT_STATE.md` と `CURRENT_DEV_TASK.md` を取得する。
3. 現行DEV Issue番号 = mirror Source を確認する。
4. Issue本文とmirrorの目的・scope・禁止事項・完了条件を照合する。
5. 同一Issue番号でも差分があればmirrorを先に同期する。
6. 整合確認後だけCodexへ実装/再開指示を出す。

Codex側はさらにAGENTS.mdに従ってlocalのcurrent state/mirrorを確認する。

## Shared management docsの更新

`CURRENT_STATE.md` / `PERMANENT_RULES.md` / `DECISIONS.md` / `CURRENT_DEV_TASK.md` / Stage Gate文書を変更する前に、必ず最新mainを再取得する。

- staleなチャット内コピーで全体上書きしない。
- 競合があれば勝手に一方を採用しない。
- 通常の班内進捗は自班Issueに置き、global stateが変わった時だけ `CURRENT_STATE.md` を更新する。

## Codex implementation branch

本体実装は原則、最新mainからtask用feature branchを作る。

- 直接mainへ実装commitしない。
- stable checkpointをcommitする。
- push可能ならremoteへpushしてDEV/ChatGPT/AUDITがGitHubから確認できるようにする。
- GitHubから確認できる成果物について、ユーザーへ手動ZIP uploadを要求しない。
- local-only/ignored dataやbinary evidenceが監査に必要な時だけZIP handoffを使う。

## Audit結果の戻り方

### PASS
- 完了条件を満たした証拠をIssueへ残す。
- CURRENT_STATE / 次Stage Gateを必要に応じて更新する。
- 次のStage/Issueへ進める。

### CONDITIONAL PASS
- 条件・未解決事項をAUDIT Issueへ明記する。
- 条件が次Stage開始を妨げるかDEVが確認する。
- 修正が必要なら現行DEV Issueへ戻すか、明示的なrepair Issueを作る。
- task contractが変わる場合はDEV Issue本文 + CURRENT_DEV_TASKを同期する。
- 条件を満たす前に無条件PASSとして扱わない。

### FAIL
- Stageを進めない。
- 指摘と根拠をAUDIT Issueへ残す。
- DEVは現行DEV Issueを再開するか、必要ならrepair Issueを明示的に作る。
- scope/禁止/完了条件が変わる場合はIssue本文とmirrorを同期する。
- mirror preflight後にCodexへ修正を渡す。
- 再監査でPASSするまで次Stageを正式開始しない。

## GitHubとlocal protected data

GitHubはmanagement stateとcommit済みコード/文書の正本だが、local workspace全体のbackupではない。
`.gitignore` 対象のraw/derived/runtime/Special大容量データ等はlocal protected dataとして別に存在する。

- GitHub上に見えないことを削除と解釈しない。
- `git clean -fdx` / `git clean -fdX` 等のignored file一括削除は禁止。
- fresh cloneだけでfull runtime/full testsが成立するとは仮定しない。

## GitHub Project 推奨Fields

| Field | 値 |
|---|---|
| Status | Backlog / Ready / Working / Audit / Blocked / Hold / Done |
| Team | DEV / AUDIT / KNOWLEDGE / PROMPT / TEMP |
| Stage | 9B / 9C / 9D / 10 / 11 / Maintenance |
| Type | Spec / Implementation / Research / Experiment / Bug / Audit |
| Priority | P0 / P1 / P2 |

## 推奨Views

### NOW
Status = Ready, Working, Audit, Blocked

### Stage 9
Stage = 9B, 9C, 9D

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
