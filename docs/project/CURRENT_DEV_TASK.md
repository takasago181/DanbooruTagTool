# CURRENT DEV TASK

最終同期: 2026-09-08

## Mirror Metadata

- Source: GitHub Issue #2
- Title: `[Stage9B][DEV] Runtime Composer Stage9B`
- State: open
- Source issue updated at: 2026-09-07T17:46:20Z
- Purpose: Codexがprivate GitHub Issue APIへ追加認証せず、現行DEV作業内容をrepository内から読めるようにするための同期ミラー。

## Sync Contract

- GitHub Issueが実作業の管理記録であり、このファイルはCodex読取用ミラー。
- `docs/project/CURRENT_STATE.md` に記載された現行DEV Issue番号と、このファイルの `Source` が一致しない場合は実装を開始しない。
- 現行DEV Issueの本文・state・完了条件を変更する管理作業では、このファイルも同じ管理作業内で更新する。
- Issueとこのミラーに矛盾が見つかった場合、Codexは推測で補完せずDEVへ報告して停止する。
- Issue番号を過去セッションから固定値として記憶しない。必ず `CURRENT_STATE.md` から現行DEV Issueを特定する。

## 目的

Stage9Aで実装済みの純粋 `PromptComposer.compose()` 境界からStage9Bを開始し、既存の補助候補をComposerへ接続する。

## 現在地

- Stage9A: PASS
- Stage9B: 未完了
- `prompt_composer.py` / `tests/test_stage9a_prompt_composer.py` / Stage9A実装レポートはmainに存在

## Stage9Bでやること

- semantic/search補助候補を独立laneとしてComposerへ接続
- true-AND共起候補を独立laneとしてComposerへ接続
- 各laneのevidence / provenance / selection stateを保持
- user include/exclude状態を保持できる形にする
- 最小限の理由表示を追加

## 境界・禁止

- source laneを1つのscoreへ潰さない
- Stage9AへUI作業を後付けしない
- Stage10画像A/B試験を開始しない
- Stage10実験用Prompt知識をproduction規則として先行固定しない
- NoobAI / WAI / Illustrious / AnimaのPrompt grammarを共通前提にしない

## 正本・参照

- `docs/stage9/STAGE9A_IMPLEMENTATION_REPORT.md`
- `docs/stage9/STAGE9_PROMPT_COMPOSER_SPEC_v1.md`
- `docs/project/CURRENT_STATE.md`
- `docs/project/PERMANENT_RULES.md`

## 関連Issue

- #3 Stage9B completion audit
- #4 Stage10 Test Prompt knowledge
- #5 Stage10 Formal handoff pending
- #6 Forge Neo comparison environment

## 完了条件

- Stage9B対象の実装と回帰テストが完了
- 既存Stage0-9Aの受入済み挙動を壊していない
- 監査班へ正式なStage9B完了監査を渡せる状態になる
