# CURRENT DEV TASK

最終同期: 2026-09-08

## Mirror Metadata

- Source: GitHub Issue #2
- Title: `[Stage9B][DEV] Runtime Composer Stage9B`
- State: open
- Source issue body synced from: 2026-09-08
- Purpose: Codexがprivate GitHub Issue APIへ追加認証せず、現行DEV作業内容をrepository内から読めるようにするための同期ミラー。

## Sync Contract

- GitHub Issueが実作業の管理記録であり、このファイルはCodex読取用ミラー。
- `docs/project/CURRENT_STATE.md` に記載された現行DEV Issue番号と、このファイルの `Source` が一致しない場合は実装を開始しない。
- 現行DEV Issueの本文・state・完了条件を変更する管理作業では、このファイルも同じ管理作業内で更新する。
- Codexはprivate GitHub Issue APIやIssueコメントへ直接書き込むことを前提にしない。Issueへのcheckpoint/完了証跡は、Codexがrepositoryへ残した成果をDEV/管理側が確認して記録する。
- Issueとこのミラーに矛盾が見つかった場合、Codexは推測で補完せずDEVへ報告して停止する。

## 現在地

- Stage9A: PASS
- Stage9B implementation: 完了
- Stage9B independent audit: Issue #3 PASS
- 監査済みbranch: `codex/stage9b-runtime-composer`
- 監査済みcommit: `eb4048f68f28ea53c3fc1c47a8b3671065be8dbf`
- 現在のDEV残作業は、監査済みStage9B成果を最新mainへ安全に統合し、Issue #2を終了できる状態にすること。

## 今やること

1. 最新mainを取得する。
2. 監査済みcommit `eb4048f68f28ea53c3fc1c47a8b3671065be8dbf` のStage9B実装差分を最新main上へ安全に統合する。
3. 管理文書・Stage10 prompt-reference等、監査後にmainへ追加された無関係な後続変更を巻き戻さない。
4. Stage9B production変更面に競合があれば推測で解消せずDEVへ報告する。
5. 統合後にStage9A/9B focused regression、必要なprotected/regression確認、`git diff --check` を再確認する。
6. 統合成果をreview可能なbranch/commitとしてremoteへpushする。
7. そこで停止し、Stage9C/9Dへ進まない。

## 禁止

- 監査済みStage9Bロジックを理由なく変更しない
- source laneを1つのscoreへ潰さない
- Stage9C/9Dをこの#2終了処理へ混ぜない
- Stage10画像A/B試験を開始しない
- Stage10実験用Prompt知識をproduction規則として先行固定しない
- NoobAI / WAI / Illustrious / AnimaのPrompt grammarを共通前提にしない
- 最新mainのmanagement/docs/Stage10 reference変更を巻き戻さない

## 参照

- `docs/stage9/STAGE9_PROMPT_COMPOSER_SPEC_v1.md`
- `docs/stage9/STAGE9A_IMPLEMENTATION_REPORT.md`
- `docs/stage9/STAGE9B_IMPLEMENTATION_REPORT.md`（監査済みbranch上）
- `docs/project/CURRENT_STATE.md`
- `docs/project/PERMANENT_RULES.md`
- Issue #3 audit result comment `5575251865`

## 完了条件

- 監査済みStage9B成果が最新main系列へ安全に統合可能なreview branch/commitとしてremoteに存在する
- 統合後のfocused/regression/protected確認で受入済み挙動を壊していない
- Codexがbranch/commit・再検証結果・競合有無・停止地点をrepository側へ残す
- DEVがremote成果を確認後、Issue #2へ終了証跡を記録してcloseする
- #2 close後にのみ#17を現行DEVへ昇格する
- #22監査PASS前にStage10へ進まない
