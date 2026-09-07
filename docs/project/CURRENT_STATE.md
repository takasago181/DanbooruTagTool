# CURRENT STATE

最終更新: 2026-09-08

## Current Stage

Stage 9B 準備 / 実装中

## Completed

- Stage 9A: PASS。実装・テスト・実装レポートは main に存在。
- Stage10用Prompt作成班: 役割・基本原則を分離済み。
- Stage10用Prompt知識調査: 本体実装知識とは分離して扱う方針を確定。
- 常設班: 開発 / 監査 / 知識 / Prompt の4班に固定。
- GitHub管理骨格と初期Issue群を作成済み。
- Codex用の現行DEV task mirrorを `docs/project/CURRENT_DEV_TASK.md` に導入。
- GitHub-first chat handoff、途中checkpoint、shared-doc stale write防止、DEV Issue/mirror preflight、local protected data保護、feature-branch review方針を管理ルールへ統合済み（management #18）。
- DEV/Codex完了証跡Gateを管理ルールへ追加。Codexはrepository成果をcommit/pushし、DEV/管理側がそれを確認してIssueへ完了証跡を記録する。Codex自身のprivate Issue書込みは要求しない。

## Active Work / Issues

- #2 `[Stage9B][DEV] Runtime Composer Stage9B`
  - 本体開発班の現行作業。Stage9Aの `PromptComposer.compose()` 境界から再開。
  - Codex読取用ミラー: `docs/project/CURRENT_DEV_TASK.md`
  - Codex側の完了報告は受領済みだが、DEVがremote/fallback成果物をまだ取得・確認できていないため現時点では未完了扱い。
- #3 `[Stage9B][AUDIT] Stage9B completion audit`
  - 監査班。#2完了後に正式監査。完成前にPASSしない。
- #4 `[Stage10][KNOWLEDGE] Test Prompt knowledge`
  - 知識班。Stage10実験用知識を整理。仕様決定権なし。
- #5 `[Stage10][PROMPT] Formal handoff pending`
  - テストPrompt班。正式handoff / Specialデータ / 実験仕様待ち。
- #6 `[Stage10][TEMP] Forge Neo comparison environment`
  - 臨時担当。導入・動作確認後に終了し、常設班にはしない。

## Queued Gates

- #17 `[Stage9][DEV] Stage9C/9D completion gate before Stage10`
  - #2完了 + #3監査PASS後の将来DEV作業。
  - 現行DEV Issue #2を置き換えない。`CURRENT_DEV_TASK.md` Sourceも現在は#2のまま。
  - 承認済みStage9仕様のStage9C（Local UI integration）/ Stage9D（Stage10 experiment hooks）を処理し、Stage9BからStage10へ暗黙に飛ばさないためのDEV Gate。
- #22 `[Stage9][AUDIT] Stage9C/9D completion audit`
  - #17完成後の将来AUDIT Gate。
  - #17の自己完了だけでStage9全体PASSにせず、独立監査でPASS / CONDITIONAL PASS / FAILを判定する。

## Not Started / Do Not Start Yet

- Stage9C / Stage9D（#17開始条件を満たすまで着手しない）
- Stage9C / Stage9D完了監査（#17完成前に#22 PASS判定しない）
- Stage10本番A/B試験
- Stage10実験管理機能の本体実装
- model family別Prompt grammarの全モデル共通化
- Stage10実験実行・記録担当の常設化

## Current Gates

Stage10開始前に最低限必要:

1. #2 Stage9B完了
   - Codexのrepository成果をDEVが取得・確認し、DEVがIssueへ完了証跡を記録することを含む
2. #3 Stage9B監査PASS
3. #17でStage9C / Stage9Dを処理
   - 9C/9Dを変更・延期する場合は、DEVがStage9仕様そのものを正式改訂し、Decision / CURRENT_STATE / STAGE_10_PREPも同期する
4. #22 Stage9C/9D完了監査PASS → Stage9全体Gate完了
5. Stage10正式handoff
6. #6 Forge Neo比較環境の導入・動作確認
7. #5へ正式Specialデータ・実験仕様を渡す
8. Stage10固定条件・metadata保存方法等、`docs/stages/STAGE_10_PREP.md` の開始前チェックを満たす

## Next Actions

1. Codexが作成したStage9Bのremote branch/commit/reportを取得できるか確認する。
2. 取得できたらDEVが実装レポート、focused/full test結果、protected確認、未解決事項、停止地点を確認する。
3. DEVがIssue #2へ完了証跡を記録し、監査渡し可能と判断する。
4. #3 監査班へStage9B監査を渡す。
5. #3 PASS後に #17 を現行DEVへ昇格させ、Stage9C / Stage9Dを処理する。
6. #17完了後に #22 へ独立監査を渡し、Stage9全体Gateを判定する。
7. #4の知識整理をStage10正式handoffへ反映する。
8. #6 Forge Neo比較環境の動作確認を終える。
9. #5へ正式handoffし、全Stage10開始Gate確認後に本番試験へ移行する。

## Blocking / Unknown

- Stage9B: Codex画面上では完了報告あり。ただしDEVがremote/fallback成果物をまだ確認できていないため、#2は未完了扱い。
- GitHub Project本体は未設定だが、CURRENT_STATE + Issuesで現行作業は管理できるためStage9B blockerではない。
- Stage10実験実行・記録担当は未作成。実際の試験で結果整理がボトルネックになった場合だけ分離を再検討する。
- GitHubはlocal protected dataの完全backupではない。`data/source/` / `data/derived/` / `data/runtime*` / Special大容量CSV等は.gitignore対象を含むため、fresh cloneだけでfull runtime/full testsを再構成できるとは仮定しない。

## Source-of-Truth Rule

- このファイルは「現在地」の正本。
- 実作業の管理記録・完了条件・結果は対応するGitHub Issueに残す。
- 意味のある途中成果は担当Issueへcheckpointコメントとして残す。通常checkpointだけでこのファイルを更新しない。
- Codexは現行DEV Issue本文を `docs/project/CURRENT_DEV_TASK.md` の同期ミラーから読む。
- DEV Issueの本文・state・完了条件を変更する管理作業では、`CURRENT_DEV_TASK.md` も同じ管理作業内で更新する。
- Codexへ新規/再開指示を出す直前に、DEV/管理側がprivate Issue本文/stateと最新mainのmirrorをlive照合し、同一Issue番号内のdriftも解消する。
- `CURRENT_STATE.md` の現行DEV Issue番号と `CURRENT_DEV_TASK.md` のSource Issue番号が一致しない場合、Codexは実装を開始しない。
- Codexはprivate Issueへ直接書き込む前提ではない。Codexはrepository成果をcommit/pushし、DEV/管理側がGitHubから確認して担当Issueへ証跡を記録する。
- DEV/Codexの完了はチャット報告だけで確定しない。DEVがremote branch/commitまたはfallback成果物、要求された実装レポート、テスト/protected結果を確認し、担当Issueへ完了証跡を残してから次Gateへ進む。
- 仕様変更は `DECISIONS.md` またはStage仕様へ反映する。
- 共有管理ファイルは変更直前に最新mainを取得してから統合し、stale copyで上書きしない。
- 古いhandoff / 旧監査 / 過去Stage資料を、現行Issueやmainの実装状態より優先しない。
- 情報が衝突した場合は自動採用せず、衝突として確認する。
- GitHubに存在しない.gitignore対象local protected dataを削除済みと解釈しない。
