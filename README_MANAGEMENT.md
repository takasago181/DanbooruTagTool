# DanbooruTagTool 管理骨格

目的は「班を増やさず、正本・進捗・引継ぎ・Codex作業境界の所在を固定し、ユーザーの手作業を減らす」ことです。

## 最初に見るもの

作業チャットは、古いhandoffや記憶ではなく最新mainから次を確認する。

1. `docs/project/CURRENT_STATE.md` — 現在地の正本
2. `docs/project/PERMANENT_RULES.md` — Stageをまたぐ固定ルール
3. `CURRENT_STATE.md` に記載された自班/担当の現行Issue
4. 必要な `DECISIONS.md` / 現行Stage仕様 / main実装状態

Codexはさらに `AGENTS.md` を読み、current DEV IssueをGitHubから直接取得する。

## 役割分担

- 本体開発班: 唯一の司令塔。仕様決定、Stage管理、Codex実装指示。
- 知識班: 外部調査・知識コーパス維持。仕様決定権は持たない。
- Prompt班: Stage10のA/B実験用Prompt設計・正式handoff。仕様決定権は持たない。
- AUDIT: 常設班ではない。独立監査が必要な品質Gateごとに新しく起動し、PASS / HOLD / FAIL等を返した後は常時待機しない。
- Forge Neo環境準備/TEMP: 必要な期間だけ動く臨時担当。
- Codex: 班ではなく、本体開発班の実装担当。
- GitHub管理・調整チャット: 班ではない。正本整合・Issue/管理文書更新・班間調整だけを行う。

常設は **DEV / KNOWLEDGE / PROMPT の3班**。AUDITは独立性を維持したまま、必要時だけ起動するGateロールです。

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
チャット履歴は正本ではありません。

## DEV Issueの扱い

- GitHub IssueがDEV作業のtask contract、完了条件、checkpoint、evidenceを担う。
- `CURRENT_STATE.md` はcurrent DEV Issue番号とroutingを担う。
- IssueコメントだけではCodexのtask contractを変更しない。
- Codexは新規/再開時にlive Issueを取得し、本文と最新checkpointの関係を確認する。

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

DEV / KNOWLEDGE / PROMPT / 必要時のAUDIT / 現行TEMPの依頼と返却は、原則GitHub Issue経由で行う。

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
→ DEV contract変更ならlive Issue本文とCURRENT_STATEのroutingを整合
→ 更新完了確認
→ 新チャット移行を提案
→ 新チャットがGitHubから復元

長大な手書きhandoffをユーザーへ作らせることを標準にしない。

## Codex実装・review

- 本体実装は原則、最新mainからtask用feature branchを作る。
- 直接mainへ未review実装をcommitしない。
- stable checkpointをcommitし、push可能ならremoteへpushする。
- ChatGPT/DEV/必要時AUDITがGitHub branch/commit/PRから確認できる成果物はGitHubを標準handoffにする。
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
5. task contract変更はIssue本文へ反映し、CURRENT_STATEのroutingと整合させる。
6. 仕様変更は `DECISIONS.md` またはStage仕様へ反映する。
7. shared management docは最新mainを再取得してから統合する。
8. 独立監査が必要なGateでは、必要時にAUDITを起動し、PASS前にGateを越えない。
9. 承認済みStage仕様に残るsubstage/gateを暗黙に飛ばさない。

詳細は `docs/project/PERMANENT_RULES.md` / `docs/project/CHAT_START_PROTOCOL.md` / `docs/project/WORKFLOW.md` を参照する。
