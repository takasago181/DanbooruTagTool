# CURRENT STATE

最終更新: 2026-09-08

## Current Stage

Stage 9C / 9D DEV実施中

## Completed

- Stage 9A: PASS。実装・テスト・実装レポートは main に存在。
- Stage 9B: 実装完了。DEVがremote成果を確認し、Issue #2へ完了証跡を記録済み。
- Stage 9B independent audit: Issue #3 PASS / completed。
- Stage9B監査済み成果は latest-main integration branch `codex/stage9b-main-integration` に競合なしで統合済み。Stage9A/9B focused 36 passed、Ruleset2+Stage8C 34 passed、`git diff --check` PASS。
- Issue #2: completed / closed。
- Stage10用Prompt作成班: 役割・基本原則を分離済み。
- Stage10用Prompt知識調査: 本体実装知識とは分離して扱う方針を確定。
- 常設班: 開発 / 監査 / 知識 / Prompt の4班に固定。
- GitHub管理骨格とCodex用 `CURRENT_DEV_TASK.md` mirror導入済み。

## Active Work / Issues

- #17 `[Stage9][DEV] Stage9C/9D completion gate before Stage10`
  - 現行DEV Issue。
  - Stage9C（Local UI integration）/ Stage9D（Stage10 experiment hooks）を承認済みStage9仕様に沿って実施・検証する。
  - `docs/project/CURRENT_DEV_TASK.md` Sourceは #17 に同期済み。
  - 完了後は #22 independent auditへ渡す。
- #26 `[TEST][Stage0] protected integrity test assumes all Special2788 children are files`
  - latest main側の既存テスト不整合。
  - `data/special2788/prompt_reference/` directory追加に対して旧Stage0 testが直下childを全てfileと仮定している。
  - Stage9B実装欠陥ではない。protected hash検証を弱めず最小修正する。
- #4 `[Stage10][KNOWLEDGE] Test Prompt knowledge`
  - 知識班。Stage10実験用知識を整理。仕様決定権なし。
- #5 `[Stage10][PROMPT] Formal handoff pending`
  - Prompt班。正式handoff / Specialデータ / 実験仕様待ち。
- #6 `[Stage10][TEMP] Forge Neo comparison environment`
  - 臨時担当。導入・動作確認後に終了。

## Queued Gates

- #22 `[Stage9][AUDIT] Stage9C/9D completion audit`
  - #17完成後の独立監査Gate。
  - #17の自己完了だけでStage9全体PASSにしない。

## Not Started / Do Not Start Yet

- Stage9C/9D completion audit PASS前のStage9全体PASS宣言
- Stage10本番A/B試験
- Stage10実験管理機能の本体実装
- model family別Prompt grammarの全モデル共通化
- Stage10実験実行・記録担当の常設化

## Current Gates

Stage10開始前に最低限必要:

1. Stage9B実装完了 + #3 Stage9B監査PASS — **SATISFIED**
2. #17 Stage9C / Stage9D実施・検証 — **CURRENT**
3. #22 Stage9C/9D完了監査PASS → Stage9全体Gate完了
4. Stage10正式handoff
5. #6 Forge Neo比較環境の導入・動作確認
6. #5へ正式Specialデータ・実験仕様を渡す
7. `docs/stages/STAGE_10_PREP.md` の開始前チェックを満たす

## Next Actions

1. #17でStage9C / Stage9Dを実施・検証する。
2. #26のStage0 protected-test不整合をprotected検証を弱めず解消する。
3. focused tests / regression / implementation report / remote branch/commitを揃える。
4. #17完了後に #22へ独立監査handoffする。
5. #22 PASS後にのみStage9全体Gateを完了扱いとする。
6. #4 / #6 / #5のStage10準備Gateを完了し、すべて満たした後にStage10本番へ進む。

## Blocking / Unknown

- Stage9B blockerはなし。
- Issue #26はlatest mainのテスト前提不整合であり、Stage9C/9D回帰確認までに解消が必要。
- GitHub CIだけでは.gitignore対象local protected dataを含むfull suiteを完全再現できない。
- GitHub Project本体は未設定だが、CURRENT_STATE + Issuesで現行作業管理は可能。
- GitHubはlocal protected dataの完全backupではない。

## Source-of-Truth Rule

- このファイルは「現在地」の正本。
- 実作業の管理記録・完了条件・結果は対応するGitHub Issueに残す。
- Codexは現行DEV Issue本文を `docs/project/CURRENT_DEV_TASK.md` の同期ミラーから読む。
- DEV Issueの本文・state・完了条件を変更する管理作業では、`CURRENT_DEV_TASK.md` も同じ管理作業内で更新する。
- Codexへ新規/再開指示を出す直前に、DEV/管理側がprivate Issue本文/stateと最新mainのmirrorをlive照合する。
- `CURRENT_STATE.md` の現行DEV Issue番号と `CURRENT_DEV_TASK.md` のSource Issue番号が一致しない場合、Codexは実装を開始しない。
- Codexはprivate Issueへ直接書き込む前提ではない。Codexはrepository成果をcommit/pushし、DEV/管理側がGitHubから確認してIssueへ証跡を記録する。
- DEV/Codexの完了はチャット報告だけで確定しない。
- 仕様変更は `DECISIONS.md` またはStage仕様へ反映する。
- 共有管理ファイルは変更直前に最新mainを取得してから統合し、stale copyで上書きしない。
- 古いhandoff / 旧監査 / 過去Stage資料を、現行Issueやmainより優先しない。
- 情報衝突時は自動採用せず、衝突として確認する。
