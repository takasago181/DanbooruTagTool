# CHAT START PROTOCOL

目的: 常設4班（DEV / AUDIT / KNOWLEDGE / PROMPT）に加え、現行Issueを持つTEMP担当やGitHub管理・調整チャットも、新しいChatGPTチャットへ移動した際に古いhandoffや旧チャットに引っ張られず、GitHub正本から同じ現在地を再構成する。

この拡張は常設班を増やすものではない。TEMPは臨時担当、GitHub管理・調整チャットは班ではない。

## 読取入口の要約

既存ルールの入口だけを要約する。権限・正本・優先順位はこの要約によって変更しない。

- 常設4班（DEV / AUDIT / KNOWLEDGE / PROMPT）とTEMP:
  `CURRENT_STATE.md` → `PERMANENT_RULES.md` → `CURRENT_STATE.md` に記載された自班の現行Issue → 必要な現行Stage仕様 / Decision / main状態
- Codex:
  `AGENTS.md` → `CURRENT_STATE.md` → `PERMANENT_RULES.md` → `CURRENT_DEV_TASK.md` → 現行Stage仕様・実装レポート
- `CURRENT_DEV_TASK.md` はDEVの現行IssueをCodexが読むための同期ミラーであり、AUDIT / KNOWLEDGE / PROMPT / TEMPの自班Issueを置き換えない。
- TEMPは常設5班目ではなく、`CURRENT_STATE.md` に記載された期間限定担当として扱う。

## 0. チャット移行を自発的に提案する条件

本プロジェクトの作業チャットは、次のいずれかに当てはまる場合、ユーザーから「引継ぎして」「新しいチャットへ移ろう」と言われるのを待たず、自発的にチャット移行を提案する。

- 会話が長大化し、現在地・最後に成功した処理・未完了項目を取り違えるリスクが高くなった。
- 過去メッセージの再探索や訂正が増え、応答品質低下の兆候が出た。
- Stage / Pilot / 監査などの大きな区切りを完了した。
- 大方針変更、担当変更、正式handoffなど、次チャットから始めた方が境界が明確になる変更が入った。
- ユーザーが明示的にチャット移行を希望した。

提案前に旧チャット側がGitHub正本を更新する。ユーザーへ長大な手書きhandoffを作らせたり、同じ情報を再入力させたりしない。

## 0.5. 途中checkpoint

チャット移行まで待つと直近の有用な作業を失う可能性があるため、次の場合は自班/担当Issueへ短いcheckpointコメントを残す。

- 意味のある実装・調査・監査・環境確認が成功した。
- 後続作業の前提になる重要な事実や判断材料が確定した。
- 長時間中断、別話題への切替、別担当への受け渡しに入る。
- 会話が長くなり、直近の成功地点を失うと再開コストが大きい。

checkpointには最低限、以下を残す。

1. 最後に成功したこと / 結果
2. 未完了またはblocker
3. 次にやること
4. 関連branch / commit / file / evidence（存在する場合）

通常の途中経過はIssueコメントで十分であり、`CURRENT_STATE.md` を毎回更新しない。Stage・Gate・担当・全体の現在地が変わった場合だけ共有正本を更新する。

checkpointコメントはtask contractを変更しない。目的・scope・禁止事項・完了条件を変更する場合はIssue本文を更新し、現行DEVなら `CURRENT_DEV_TASK.md` も同じ管理作業内で同期する。

## 1. 旧チャット側で移動前に行うこと

- `docs/project/CURRENT_STATE.md` が現在地と一致していることを確認し、全体状態に変化があれば最新化する。
- 常設班/TEMPは自班の現行Issueへ、未完了・完了・待機条件・重要な禁止事項・最後の成功地点を反映する。
- GitHub管理・調整チャットは、変更したIssue・管理文書・Decision等へ現在地と必要な記録を反映する。班ではないため専用Issueを新設する必要はない。
- Stage完了や仕様変更がある場合は、必要に応じて `DECISIONS.md` または現行Stage仕様へ反映する。
- DEVの現行Issue本文・state・完了条件を変更した場合は、`docs/project/CURRENT_DEV_TASK.md` も同じ管理作業内で同期する。
- Codexが守るべきDEVの目的・scope・禁止事項・完了条件を変更した場合、Issueコメントだけで済ませずIssue本文と `CURRENT_DEV_TASK.md` に反映する。
- 共有管理ファイルを更新する直前に最新mainを再取得し、古いチャット内コピーで上書きしない。
- チャット本文だけに新しい決定を残したまま移動しない。
- GitHub更新が完了した後に「新チャットへ移行可能」とユーザーへ伝える。

## 2. 新チャット開始時の確認順

実作業を始める前に、必ず次の順で確認する。

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. 常設班/TEMPは `CURRENT_STATE.md` に記載された自班の現行GitHub Issue、GitHub管理・調整チャットは関係する現行Issueと管理文書
4. 必要な `DECISIONS.md` / 現行Stage仕様 / mainの実装状態
5. 自班Issueの直近checkpoint / 結果コメント（必要な場合）

Issue番号は固定しない。Stageや担当変更で番号が変わるため、過去チャットや記憶から推測せず、毎回 `CURRENT_STATE.md` から特定する。

DEV / Codex連携では、Codexはさらに `docs/project/CURRENT_DEV_TASK.md` のSource Issue番号が `CURRENT_STATE.md` の現行DEV Issue番号と一致することを確認する。DEV/管理側はCodexへ新規/再開指示を出す直前に、private GitHubの現行DEV Issue本文/stateと最新mainのミラーをlive照合し、同一Issue番号内の本文driftも解消しておく。

## 3. 新チャットの認識確認 / 班ID

確認後、実作業を始める前に、まず次の固定形式で**班ID（担当ID）**を表示する。

```text
TEAM_ID: <stable team/workstream id>
TEAM: <班または担当名>
ROLE: <このチャットの役割>
ISSUE: <#number / N/A>
BRANCH: <live verified branch / main / N/A>
HEAD: <live verified 40-char commit SHA>
CHECKPOINT: <latest relevant issue comment id / contract commit / N/A>
CONTRACT: <Issue body / CURRENT_DEV_TASK / contract file@commit / N/A>
PHASE: <current phase/gate>
SOURCE_OF_TRUTH: CURRENT_STATE -> PERMANENT_RULES -> <Issue/management source> -> live branch
VERSION_LABEL: <optional human-readable label / N/A>
```

運用ルール:

- `TEAM_ID` はチャット名ではなく、現在の作業個体を識別する安定IDとする。例: `DEV:#35`, `DICT:#32:R2`, `UIJA:#36:FINAL_AUDIT`, `UIJA:#41:BLIND30_AUDIT`, `TEMP:#30`。
- `BRANCH` / `HEAD` / `CHECKPOINT` はチャット記憶から埋めず、開始時にGitHubからlive確認する。Issue-only担当で専用branchがない場合も、参照した `main` のHEADを記録する。
- `v2` / `v3` / `R3` / `FINAL` 等の版名は `VERSION_LABEL` またはPHASEの補助情報として使ってよいが、**版名だけを現在個体の識別子にしない**。
- 実際の識別は少なくとも `TEAM_ID + ISSUE + BRANCH + HEAD + CHECKPOINT/CONTRACT + PHASE` で行う。
- `CURRENT_STATE.md` の Workstreams Registry はrouting/indexであり、Issue本文、branch上の成果物、checkpoint、現行DEVの `CURRENT_DEV_TASK.md` を置き換えるtask contractではない。
- Registry / Issue / branch / checkpointの間でowner・scope・phase・HEAD系統に矛盾がある場合、勝手に一方を採用しない。`IDENTITY_CONFLICT` と明記して実作業を止め、GitHub正本を先に整合させる。
- Issue変更、branch変更、正式contract変更、大きなphase変更、チャット移行時には班IDを再取得する。通常の小checkpointごとに `CURRENT_STATE.md` の固定HEADを書き換える必要はない。

班IDの後、必要な範囲で次も自分の言葉で確認する。

1. 自分の班または担当種別と役割
2. 現在のStage
3. 現在の担当Issue番号、または管理・調整対象
4. 現在地の正本として最初に見るファイル
5. 最後に確認できた成功地点 / checkpoint（存在する場合）
6. 今の次作業
7. 今やってはいけないこと
8. Codexとの役割分担
9. 古いhandoff・旧チャット・過去Stage資料とGitHub現行状態が衝突した場合の扱い

最後に必ず以下を明記する。

`GitHub正本運用：認識済み / 未認識`

班IDをlive確認できず、または認識済みと判断できない間は実作業を開始しない。

## 4. 班・担当ごとの固定境界

### DEV

- 唯一の司令塔。
- 仕様整理・Stage管理・Codex指示・成果確認を担当する。
- CodexはDEVの実装担当であり独立班ではない。
- AUDITの正式PASSを代行しない。
- Codexへ作業を渡す直前にcurrent DEV Issueとmirrorのlive整合を確認する。
- Codexはprivate GitHub Issueへ直接書き込む前提ではない。Codexはrepository成果をcommit/pushし、DEVがGitHubから取得・確認して担当Issueへcheckpoint/完了証跡を記録する。
- Codexが「完了」と返しても、DEVがbranch/commit/report/test/protected結果を取得・確認してIssue証跡化するまでは監査渡ししない。

### AUDIT

- DEV/Codexから独立した品質ゲート。
- 実装差分・テスト・証拠を確認して PASS / CONDITIONAL PASS / FAIL を判定する。
- 開発班やCodexの自己申告だけでPASSしない。
- 監査対象が完成する前にPASSしない。

### KNOWLEDGE

- 外部知識の調査・根拠整理を担当する。
- 仕様決定権・本体実装権は持たない。
- 調査結果を勝手にproduction規則へ昇格しない。

### PROMPT

- Stage10実験用Promptの設計・作成を担当する。
- 本体仕様の決定権は持たない。
- 正式handoff前に本番Promptを固定しない。

### TEMP

- `CURRENT_STATE.md` に記載された期間限定の作業だけを担当する。
- 常設5班目にはならない。
- 自班Issueが終了したらTEMP担当も終了する。

### GitHub管理・調整チャット

- 班ではない。
- GitHub正本の整合、Issue/管理文書更新、班間の現在地調整を行う。
- DEVの仕様決定、AUDITのPASS、KNOWLEDGE/PROMPTの専門作業を代行しない。

## 5. 衝突時の扱い

- 古いhandoff・旧チャット・過去Stage資料を、現行 `CURRENT_STATE.md` / 現行Issue / mainの状態より優先して現在地を巻き戻さない。
- ただしGitHub側に明確な矛盾がある場合も、勝手に一方を採用・補完しない。
- `衝突あり` として明示し、確認後にGitHub正本を修正する。
- 複数チャットが共有管理ファイルを同時に触った場合は、最新mainを再取得してから統合し、stale copyで上書きしない。

## 6. Stage境界

- `CURRENT_STATE.md` の現在Stageを越えて勝手に進まない。
- 後続Stage用の実験知識・仮説を、前Stageのproduction規則へ先行固定しない。
- model family固有のPrompt grammarを、検証なしに全モデル共通ルールへしない。
- 承認済みStage仕様に残っている未完了substage/gateを、CURRENT_STATE側の短縮された手順だけを理由に暗黙スキップしない。矛盾があればDEVが正式に解消する。

## 7. 完了条件

新チャットが以下を満たした時点で移行完了とする。

- 班IDをGitHub live stateから取得して表示済み
- `TEAM_ID + ISSUE + BRANCH + HEAD + CHECKPOINT/CONTRACT + PHASE` が矛盾なく確認済み
- 現在Stageを正しく認識
- 現行Issueまたは管理対象を正しく特定
- 必要なら直近checkpointを把握
- 自班/担当の権限境界を正しく認識
- 次作業と禁止事項を正しく認識
- GitHubと古い資料の衝突処理を理解
- `GitHub正本運用：認識済み` を明記
