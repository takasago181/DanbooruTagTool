# CURRENT DEV TASK

最終同期: 2026-09-08

## Mirror Metadata

- Source: GitHub Issue #17
- Title: `[Stage9][DEV] Stage9C/9D completion gate before Stage10`
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
- Stage9B: 実装完了 / Issue #3 independent audit PASS
- Issue #2: completed / closed
- 現行DEV: Issue #17
- Stage10: 未開始

## 前提

- Stage9B監査済み成果は latest-main integration branch `codex/stage9b-main-integration` に安全に統合済み。
- Integration report: `docs/stage9/STAGE9B_LATEST_MAIN_INTEGRATION_REPORT.md`
- Stage9B focused/regressionはPASS。
- latest main側のStage0 protected testに既存不整合が1件あり、Issue #26へ別追跡した。Stage9B実装欠陥ではない。

## 今やること

1. latest mainとStage9B integration成果を基点にStage9Cを承認済みStage9仕様に沿って実施・検証する。
2. Stage9Dを承認済みStage9仕様に沿って実施・検証する。
3. Issue #26のprotected-test不整合を、protected hash検証を弱めず最小修正するか、9C/9D回帰の前提として解消する。
4. 9C/9Dに必要なfocused tests / regression / implementation reportを残す。
5. review可能なbranch/commitとしてremoteへpushする。
6. そこで停止し、Issue #22へ独立監査handoffできる状態にする。

## 禁止

- Stage9C/9Dを暗黙に省略しない
- #22監査PASS前にStage9全体PASSと宣言しない
- Stage10画像A/Bを開始しない
- Stage10実験知識をStage9 production規則へ先行固定しない
- model family別Prompt grammarを未検証で共通化しない
- protected hash検証を弱体化してIssue #26を解消しない

## 参照

- `docs/stage9/STAGE9_PROMPT_COMPOSER_SPEC_v1.md`
- `docs/stage9/STAGE9A_IMPLEMENTATION_REPORT.md`
- `docs/stage9/STAGE9B_IMPLEMENTATION_REPORT.md`
- `docs/stage9/STAGE9B_LATEST_MAIN_INTEGRATION_REPORT.md`
- `docs/project/CURRENT_STATE.md`
- `docs/project/PERMANENT_RULES.md`
- Issue #22 Stage9C/9D audit
- Issue #26 Stage0 protected integrity test mismatch

## 完了条件

A. Stage9C / Stage9Dを実施・検証し、実装差分・tests・report・branch/commitを揃える。Issue #26もprotected検証を弱めず解消または監査可能な形で処理する。

または

B. DEVが根拠付きでStage9仕様を正式改訂し、9C/9Dの扱いを変更したうえで、関連するDecision / Stage仕様 / CURRENT_STATE / STAGE_10_PREPを同期し、その変更を#22で監査可能にする。

Stage9全体Gateの最終PASSはIssue #22 AUDITが判定する。
