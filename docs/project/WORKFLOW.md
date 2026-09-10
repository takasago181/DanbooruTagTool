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
目的・scope・禁止事項・完了条件を変える場合はlive Issue本文を更新する。`CURRENT_STATE.md` のcurrent DEV routingと整合させ、`CURRENT_DEV_TASK.md` は必要な移行参考情報としてのみ更新する。

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

GitHubへ依頼を登録した後、チャット側でもユーザーへ依頼内容を見せる。
ユーザーに再投稿・転記は求めないが、少なくとも「依頼先 / 依頼内容 / 理由 / 欲しい結果」が分かる形で本文または要約を提示する。

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

ユーザーの判断や次作業に影響する重要な返却結果は、GitHubへ記録した上でチャット側でも要約して知らせる。
GitHubを正本としつつ、ユーザーから依頼・返却内容が見えない運用にはしない。

標準の流れ:

班A Issue
→ 班B Issueへ依頼checkpoint
→ ユーザーへ依頼内容を可視化
→ 班Bが作業
→ 班B Issueへ詳細結果checkpoint
→ 班A Issueへ短い返却checkpoint + 班B Issue参照
→ 必要な結果をユーザーへ要約
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

Codexは新規実装・再開時に、自身でlive Issueを直接取得して確認する。

1. 最新mainの `CURRENT_STATE.md` からcurrent DEV Issue番号を取得する。
2. `gh issue view <ISSUE_NUMBER> --comments` でIssue title / state / body / 最新コメント / 最新checkpointを取得する。
3. continuation contract / completion condition / blocker・gateを確認し、`PERMANENT_RULES.md` と照合する。
4. `CURRENT_STATE.md` のIssue番号と取得結果が一致し、Issueが想定外にclosed / supersededでないことを確認する。
5. `gh` 不在、認証失敗、取得失敗、本文とcheckpointの関係不明、または明確な矛盾があればfail-closedで停止する。
6. `CURRENT_DEV_TASK.md` は参考資料 / fallback diagnostic artifactとしてdrift診断にのみ使い、古い内容を根拠に続行しない。

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
- task contractが変わる場合はDEV Issue本文を更新し、`CURRENT_STATE.md` のroutingと整合させる。`CURRENT_DEV_TASK.md` の更新は移行参考情報として任意とする。
- 条件を満たす前に無条件PASSとして扱わない。

### FAIL
- Stageを進めない。
- 指摘と根拠をAUDIT Issueへ残す。
- DEVは現行DEV Issueを再開するか、必要ならrepair Issueを明示的に作る。
- scope/禁止/完了条件が変わる場合はIssue本文を更新し、`CURRENT_STATE.md` と整合させる。
- live Issue preflight後にCodexへ修正を渡す。
- 再監査でPASSするまで次Stageを正式開始しない。

## GitHubとlocal protected data

GitHubはmanagement stateとcommit済みコード/文書の正本だが、local workspace全体のbackupではない。
`.gitignore` 対象のraw/derived/runtime/Special大容量データ等はlocal protected dataとして別に存在する。

- GitHub上に見えないことを削除と解釈しない。
- `git clean -fdx` / `git clean -fdX` 等のignored file一括削除は禁止。
- fresh cloneだけでfull runtime/full testsが成立するとは仮定しない。

## GitHub Project

**現在は未採用。**

Issue #47で検討したGitHub Project管理ボードは、`CURRENT_STATE.md` + 各Issue + `CURRENT_DEV_TASK.md` の3層で十分と判断し、2026-09-10に `NOT PLANNED` でcloseした。

したがって現在は:
- Projectのfield/viewを作成・同期しない
- Projectをtask contractやGate authorityとして扱わない
- 管理正本を増やさない

将来、現行3層で実際に管理不能・高頻度の見落としが発生した場合のみ、別Issueで再検討する。

過去のProject field/view案はGit履歴と `CONTROL_BOARD_MIGRATION_DESIGN.md` に履歴として残す。
