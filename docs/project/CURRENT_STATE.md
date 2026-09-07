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

## Active Work / Issues

- #2 `[Stage9B][DEV] Runtime Composer Stage9B`
  - 本体開発班の現行作業。Stage9Aの `PromptComposer.compose()` 境界から再開。
  - Codex読取用ミラー: `docs/project/CURRENT_DEV_TASK.md`
- #3 `[Stage9B][AUDIT] Stage9B completion audit`
  - 監査班。#2完了後に正式監査。完成前にPASSしない。
- #4 `[Stage10][KNOWLEDGE] Test Prompt knowledge`
  - 知識班。Stage10実験用知識を整理。仕様決定権なし。
- #5 `[Stage10][PROMPT] Formal handoff pending`
  - テストPrompt班。正式handoff / Specialデータ / 実験仕様待ち。
- #6 `[Stage10][TEMP] Forge Neo comparison environment`
  - 臨時担当。導入・動作確認後に終了し、常設班にはしない。

## Not Started / Do Not Start Yet

- Stage10本番A/B試験
- Stage10実験管理機能の本体実装
- model family別Prompt grammarの全モデル共通化
- Stage10実験実行・記録担当の常設化

## Current Gates

Stage10開始前に最低限必要:

1. #2 Stage9B完了
2. #3 Stage9B監査PASS
3. Stage10正式handoff
4. #6 Forge Neo比較環境の導入・動作確認
5. #5へ正式Specialデータ・実験仕様を渡す

## Next Actions

1. #2 Stage9Bを完了させる。
2. #3 監査班へStage9B監査を渡す。
3. #4の知識整理をStage10正式handoffへ反映する。
4. #6 Forge Neo比較環境の動作確認を終える。
5. #5へ正式handoffし、Stage10本番試験へ移行する。

## Blocking / Unknown

- GitHub Project本体はまだ未設定。
- Stage10実験実行・記録担当は未作成。実際の試験で結果整理がボトルネックになった場合だけ分離を再検討する。

## Source-of-Truth Rule

- このファイルは「現在地」の正本。
- 実作業の管理記録・完了条件・結果は対応するGitHub Issueに残す。
- Codexは現行DEV Issue本文を `docs/project/CURRENT_DEV_TASK.md` の同期ミラーから読む。
- DEV Issueの本文・state・完了条件を変更する管理作業では、`CURRENT_DEV_TASK.md` も同じ管理作業内で更新する。
- `CURRENT_STATE.md` の現行DEV Issue番号と `CURRENT_DEV_TASK.md` のSource Issue番号が一致しない場合、Codexは実装を開始しない。
- 仕様変更は `DECISIONS.md` またはStage仕様へ反映する。
- 古いhandoff / 旧監査 / 過去Stage資料を、現行Issueやmainの実装状態より優先しない。
- 情報が衝突した場合は自動採用せず、衝突として確認する。
