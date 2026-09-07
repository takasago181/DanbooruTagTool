# DanbooruTagTool 管理骨格

目的は「班を増やさず、正本・進捗・引継ぎ・Codex作業境界の所在を固定し、ユーザーの手作業を減らす」ことです。

## 最初に見るもの

作業チャットは、古いhandoffや記憶ではなく最新mainから次を確認する。

1. `docs/project/CURRENT_STATE.md` — 現在地の正本
2. `docs/project/PERMANENT_RULES.md` — Stageをまたぐ固定ルール
3. `CURRENT_STATE.md` に記載された自班/担当の現行Issue
4. 必要な `DECISIONS.md` / 現行Stage仕様 / main実装状態

Codexはさらに `AGENTS.md` と `docs/project/CURRENT_DEV_TASK.md` を読む。

## 役割分担

- 本体開発班: 唯一の司令塔。仕様決定、Stage管理、Codex実装指示。
- 監査班: 第三者監査。PASS / CONDITIONAL PASS / FAIL を返す。
- 知識班: 外部調査。仕様決定権は持たない。
- テストPrompt班: Stage10のA/B実験用Prompt作成。仕様決定権は持たない。
- Forge Neo環境準備: 臨時担当。Stage10比較環境の導入・動作確認後に終了。
- Codex: 班ではなく、本体開発班の実装担当。
- GitHub管理・調整チャット: 班ではない。正本整合・Issue/管理文書更新・班間調整だけを行う。

## 正本の置き場所

- `docs/project/CURRENT_STATE.md`
  - 「今どこにいるか」の唯一の状態表。
- `docs/project/PERMANENT_RULES.md`
  - Stageをまたいで有効な固定ルール。
- `docs/project/DECISIONS.md`
  - 重要な設計判断と理由。
- `docs/stage9/` / `docs/stages/`
  - 現行Stage・次Stageの仕様とGate。
- GitHub Issues
  - 実作業のtask contract、完了条件、結果、checkpoint履歴。
- Pull Request / branch / commit
  - 実際に変更されたコード・文書とreview対象。
- `docs/project/CURRENT_DEV_TASK.md`
  - Codexがprivate DEV Issue本文を追加認証なしで読むための同期ミラー。独立正本ではない。

チャット履歴は正本ではありません。

## CURRENT_DEV_TASKの扱い

- GitHub IssueがDEV作業の管理記録。
- `CURRENT_DEV_TASK.md` はCodex読取専用mirror。
- `CURRENT_STATE.md` の現行DEV Issue番号とmirror Sourceが違えばCodexは停止。
- DEV Issueのpurpose/scope/禁止事項/完了条件/stateを変更する管理作業ではmirrorも同期する。
- IssueコメントだけではCodexのtask contractを変更しない。
- Codexへ新規/再開指示を出す直前に、DEV/管理側がprivate Issue本文と最新mainのmirrorをlive照合する。同じIssue番号のまま本文が変わったdriftもここで検出する。

## 途中checkpoint

意味のある成果をチャットだけに保持し続けない。

次の場合は担当Issueへ短いcheckpointコメントを残す。
- 重要な実装/調査/監査/環境確認が成功した
- 後続作業の前提になる事実が確定した
- 長時間中断・話題切替・handoffに入る
- 会話が長く、直近の成功地点を失うと再開コストが高い

最低限:
- 最後に成功したこと/結果
- 未完了またはblocker
- 次作業
- branch/commit/file/evidence（ある場合）

通常のcheckpointはIssueコメントに置き、global stateが変わらない限り `CURRENT_STATE.md` は更新しない。

## 班間の受け渡し

DEV / AUDIT / KNOWLEDGE / PROMPT / 現行TEMPの依頼と返却は、原則GitHub Issue経由で行う。

- 依頼側は、受取側の現行Issueへ「何をしてほしいか・理由・期待する出力・関連Issue/File」をcheckpointとして残す。
- 受取側は、結果をチャットだけで返さず自班Issueへ「結果・根拠・判定・限界・次」を記録する。
- 依頼元の次作業に必要な結果は、依頼元Issueへ短い返却checkpointも残し、詳細結果のIssueを参照する。
- ユーザーを班間コピペの中継役にすることを標準運用にしない。
- GitHubに載せられないlocal-only / binary / protected dataやconnector障害時だけfallbackを使い、その理由と代替handoffの所在をIssueへ残す。

詳細形式は `docs/project/WORKFLOW.md` の「班間依頼・返却」を参照する。

## チャット引継ぎ

会話長大化、Stage/Pilot/監査区切り、大方針変更、正式handoffでは、ユーザー指示を待たず作業チャット側から移行を提案する。

順序:

旧チャット
→ GitHubへcheckpoint/現在地を反映
→ 必要ならIssue本文・Decision・Stage仕様・CURRENT_STATEを更新
→ shared management fileは最新mainへ差分統合
→ DEV contract変更ならCURRENT_DEV_TASKも同期
→ 更新完了確認
→ 新チャット移行を提案
→ 新チャットがGitHubから復元

長大な手書きhandoffをユーザーへ作らせることを標準にしない。

## Codex実装・review

- 本体実装は原則、最新mainからtask用feature branchを作る。
- 直接mainへ未review実装をcommitしない。
- stable checkpointをcommitし、push可能ならremoteへpushする。
- ChatGPT/DEV/AUDITがGitHub branch/commit/PRから確認できる成果物はGitHubを標準handoffにする。
- local-only/ignored data、binary evidence、push不能などGitHubだけで確認できない時だけ `docs/CHATGPT_CODEX_HANDOFF.md` のZIP fallbackを使う。

## Local protected data

GitHubは管理状態とcommit済みコード/文書の正本ですが、ローカルworkspace全体のbackupではありません。

`.gitignore` には `data/source/`、`data/derived/`、`data/runtime*`、Special2788の大容量CSV等が含まれます。
これらがGitHubに見えなくても削除・欠損とは限りません。

禁止:
- `git clean -fdx`
- `git clean -fdX`
- ignored protected dataを広範囲に消すcleanup

fresh cloneだけでfull runtime/full testsを再現できるとは仮定しない。

## 最小運用

1. 作業前に `CURRENT_STATE.md` と自班Issueを確認する。
2. 新しい確定作業はIssue化する。
3. 意味のある途中成果はIssue checkpointへ残す。
4. 班間依頼・返却はGitHub Issueで往復し、ユーザーへ手動中継を要求しない。
5. task contract変更はIssue本文へ反映する。現行DEVならmirrorも同期する。
6. 仕様変更は `DECISIONS.md` またはStage仕様へ反映する。
7. shared management docは最新mainを再取得してから統合する。
8. AUDIT PASS前にGateを越えない。
9. 承認済みStage仕様に残るsubstage/gateを暗黙に飛ばさない。

詳細は `docs/project/PERMANENT_RULES.md` / `docs/project/CHAT_START_PROTOCOL.md` / `docs/project/WORKFLOW.md` を参照する。
