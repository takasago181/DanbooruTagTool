# DECISIONS

重要な設計判断だけを残す。
日々の進捗は `CURRENT_STATE.md` / 各Issueへ書く。

---

## D-001 常設4班制

Status: ADOPTED

常設:
- 本体開発班
- 監査班
- 知識班
- テストPrompt班

理由:
- 仕様決定・第三者監査・外部調査・実験Prompt作成を分離できる。
- これ以上の常設分割は個人開発では管理コストが増えやすい。

---

## D-002 Codexは独立班にしない

Status: ADOPTED

Codexは開発班の実装担当。
独立した仕様決定権を持たせない。

---

## D-003 Forge Neo環境準備は臨時担当

Status: ADOPTED

Stage10比較環境の導入・動作確認まで。
完了後は常設しない。

---

## D-004 Stage10実験実行・記録班は保留

Status: HOLD

Stage10で数試験を実行後、
Prompt作成より metadata保存・A/B評価・集計が重いと判明した場合のみ独立させる。

---

## D-005 Stage10実験知識をStage9へ先行固定しない

Status: ADOPTED

NoobAI / WAI / Illustrious / Anima のPrompt grammarはモデル差を保つ。
Stage10用framing、caption順、hybrid形式などを全モデル共通ルールへ昇格させない。

---

## D-006 CURRENT_DEV_TASKはCodex読取用同期ミラー

Status: ADOPTED

GitHub IssueをDEV作業の管理記録として維持し、`docs/project/CURRENT_DEV_TASK.md` はprivate Issue APIへ追加認証できないCodexが現行DEV taskを読むための同期ミラーとする。

理由:
- ユーザーへGitHub CLI導入・browser認証・Issue本文の手動copy/pasteを要求しないため。
- Issueとmirrorの二重正本化を避けるため。

規則:
- `CURRENT_STATE.md` の現行DEV Issue番号とmirror Sourceが不一致ならCodexは停止。
- purpose/scope/禁止/完了条件の変更はIssue本文 + mirrorへ同期する。
- IssueコメントだけではCodexの現行task contractを変更しない。
- DEV/管理側はCodexへ指示する直前にprivate Issueとmirrorをlive照合し、同一Issue番号内のdriftも検出する。

---

## D-007 GitHub-first proactive handoff + intermediate checkpoint

Status: ADOPTED

長いチャットを記憶装置として使わない。
本プロジェクトの作業チャットは、会話長大化・Stage/Pilot/監査区切り・大方針変更・正式handoff時に、ユーザー指示を待たずGitHubを先に更新して新チャット移行を提案する。

さらに、移行まで待つと失うと困る意味のある途中成果は担当Issueへcheckpointコメントとして残す。

理由:
- 突然のチャット終了や会話上限でも再開地点を失いにくくする。
- 長大な手書きhandoffをユーザーへ作らせない。

---

## D-008 Stage9C / Stage9DをStage10前に暗黙スキップしない

Status: ADOPTED

`docs/stage9/STAGE9_PROMPT_COMPOSER_SPEC_v1.md` はStage9A〜9Dを定義し、9A〜9Dのgate通過後にStage9完了としている。
したがってStage9B監査PASSだけを理由にStage10本番A/Bへ進まない。

将来DEV Issue #17でStage9C/9Dを処理する。
もし不要・延期へ変更するなら、DEVが根拠付きでStage9仕様そのものを正式改訂し、CURRENT_STATE / Stage10 Prepも同期する。

---

## D-009 GitHub管理正本とlocal protected dataを分離

Status: ADOPTED

GitHubを現在地・Issue・commit済みコード/文書の正本として使うが、ローカルworkspace全体のbackupとは扱わない。
`.gitignore` 対象のraw/derived/runtime/Special大容量データはlocal protected dataであり、GitHubに存在しないことを削除と解釈しない。

`git clean -fdx` / `git clean -fdX` 等、ignored protected dataを消し得る操作は禁止する。

---

## D-010 Codex実装はfeature branch、ChatGPT reviewはGitHub優先

Status: ADOPTED

Codexの本体実装は原則task用feature branchで行い、直接mainへ実装commitしない。
review対象がGitHub branch/commit/PRから取得できる場合は、それを標準handoffとする。

ZIP handoffはlocal-only/ignored data、binary evidence、push不能などGitHubだけでreviewできない場合のfallbackとする。

理由:
- mainを未監査実装から守る。
- ユーザーのmanual upload作業を減らす。
- DEV/AUDITが同一commitを確認できるようにする。

---

## D-011 Shared management docsはlatest-main merge必須

Status: ADOPTED

複数チャットが並行して動くため、`CURRENT_STATE.md` 等の共有管理文書を古い会話内コピーから丸ごと上書きしない。
変更直前に最新mainを取得し、最新内容へ差分を統合する。競合時は停止して明示的に解消する。

理由:
- 他班/管理チャットの最新更新をstale writeで消す事故を防ぐ。
