# CURRENT DEV TASK

最終同期: 2026-09-08

## Mirror Metadata

- Source: GitHub Issue #2
- Title: `[Stage9B][DEV] Runtime Composer Stage9B`
- State: open
- Source issue body synced from: 2026-09-08
- Last live body comparison: 2026-09-08 — completion-evidence responsibilities corrected: Codex writes repository evidence; DEV/management writes Issue evidence.
- Purpose: Codexがprivate GitHub Issue APIへ追加認証せず、現行DEV作業内容をrepository内から読めるようにするための同期ミラー。

`updated_at` はIssueコメント追加でも変化し得るため、時刻の不一致だけでbody driftとは判定しない。DEV/管理側はCodexへ新規/再開指示を出す直前にprivate Issue本文/stateをlive取得し、このmirrorのtask contractと照合する。

## Sync Contract

- GitHub Issueが実作業の管理記録であり、このファイルはCodex読取用ミラー。
- `docs/project/CURRENT_STATE.md` に記載された現行DEV Issue番号と、このファイルの `Source` が一致しない場合は実装を開始しない。
- 現行DEV Issueの本文・state・完了条件を変更する管理作業では、このファイルも同じ管理作業内で更新する。
- Codexが守るべき目的・scope・禁止事項・完了条件を変更する場合、Issueコメントだけで済ませずIssue本文とこのミラーへ反映する。
- Issueコメントは結果・証跡・checkpoint・履歴の記録には使用できるが、コメントだけでこのミラーの現行task条件を上書きしない。
- Issueとこのミラーに矛盾が見つかった場合、Codexは推測で補完せずDEVへ報告して停止する。
- Issue番号を過去セッションから固定値として記憶しない。必ず `CURRENT_STATE.md` から現行DEV Issueを特定する。
- Issue番号が同じでも本文だけ変更される可能性があるため、番号一致だけを完全な同期証明とは扱わない。Codex handoff直前のDEV/管理live比較を追加Gateとする。
- Codexはprivate GitHub Issue APIやIssueコメントへ直接書き込むことを前提にしない。Issueへのcheckpoint/完了証跡は、Codexがrepositoryへ残した成果をDEV/管理側が確認して記録する。

## 目的

Stage9Aで実装済みの純粋 `PromptComposer.compose()` 境界からStage9Bを開始し、既存の補助候補をComposerへ接続する。

## 現在地

- Stage9A: PASS
- Stage9B: 未完了
- `prompt_composer.py` / `tests/test_stage9a_prompt_composer.py` / Stage9A実装レポートはmainに存在
- Codex画面上の「完了」報告だけではStage9B完了としない。DEVがrepository成果を取得・確認してIssue証跡化するまで監査渡ししない。

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
- `docs/project/CHAT_START_PROTOCOL.md`

## 関連Issue

- #3 Stage9B completion audit
- #4 Stage10 Test Prompt knowledge
- #5 Stage10 Formal handoff pending
- #6 Forge Neo comparison environment
- #17 Stage9C/9D completion gate before Stage10（将来task。現行DEVではない）

## 完了条件

- Stage9B対象の実装と回帰テストが完了
- 既存Stage0-9Aの受入済み挙動を壊していない
- 監査班へ正式なStage9B完了監査を渡せる状態になる
- Codexはレビュー可能なbranch/commit、変更内容、focused/full test結果、protected surface/hash確認、未解決事項、次Gateへの停止地点をrepository内の実装レポート等へ残す
- `docs/stage9/STAGE9B_IMPLEMENTATION_REPORT.md` をcommitする
- 可能ならfeature branchをremoteへpushする
- Codex自身がIssue #2へ直接書き込むことは要求しない
- push失敗時は完了と名乗らず、branch/commit SHA・失敗理由を報告し、ZIP fallback等でDEVが成果を回収できる状態にする
- DEV/管理側がremoteまたはfallback成果物を確認後、Issue #2へ完了証跡を記録する
- DEV側のIssue証跡記録と一次確認が完了するまで、Issue #3へ監査渡し可能とは扱わない

## Current task boundary note

Stage9C/9Dは#2へ混ぜず、#2 + #3完了後の将来DEV Gate #17として扱う。
