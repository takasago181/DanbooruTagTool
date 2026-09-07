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
- 全体監査pre-gate: Stage9C/9D **FAIL / RETURN TO DEV**
- 監査対象: `codex/stage9c9d-completion` / `99b4f4a80c12f15dfcc3e62f608af6a2c1cccf88`
- Stage10: 未開始
- DEV実確認が終わるまで #17は未完了、#22へhandoffしない。

## 今やること

1. Stage9Cのcommon / rare候補集合上書き問題を修正する。
   - visibleな全recommendation候補集合をatomicに登録する、または全bucketを保持する。
   - lane / evidence identityを維持する。
   - common + rare同時表示後、それぞれから選択できる回帰テストを追加する。
2. Stage9Dの可逆A/B variant contractをStage9 spec §10に合わせる。
   - Special position
   - broad generic support 0 / 1 / 2
   - role-density variants
   - weight variants
   - LoRA Prompt contraction variants
   - comparison metadata
   - Stage9ではwinner/scoring logicを入れない。
3. 必要なfocused / regression testsを追加・再実行する。
   - Stage9A/9B
   - Stage8C / Ruleset2
   - Stage7 UI関連
   - protected/hash
   - full suite可能範囲
   - `git diff --check`
4. `docs/stages/STAGE_10_PREP.md` を現状へ同期する。
   - Stage9C/9Dを未着手扱いにしない。
   - #22 PASS前にStage9全体完了やStage10開始可能と読める状態にしない。
5. Issue #26のprotected-test修正方針を維持する。
   - `data/special2788/prompt_reference/` を許容しても、既存protected source filesのhash/size検証は弱めない。
6. implementation reportを更新し、review可能なremote branch / commitを作る。
7. そこで停止する。#22へはDEVがremote成果を実確認してIssue #17へ完了証跡を記録するまで渡さない。

## 禁止

- Codexの完了報告だけで#17を完了扱いにしない
- DEV確認前に#22へhandoffしない
- #22 PASS前にStage9全体PASSと宣言しない
- Stage10画像A/Bを開始しない
- Stage10 winner/scoring logicをStage9へ入れない
- Stage10実験知識をStage9 production規則へ先行固定しない
- model family別Prompt grammarを未検証で共通化しない
- protected hash検証を弱体化してIssue #26を解消しない

## 完了条件

- Stage9C common / rare候補集合上書き問題を解消し、回帰テストで固定する。
- Stage9D §10の必要な可逆A/Bノブを実装・検証する、または正式な仕様改訂を行う。
- `STAGE_10_PREP.md` を現状へ同期する。
- Issue #26のprotected hash検証を弱めない修正を維持・検証する。
- focused / regression / protected / full suite可能範囲 / `git diff --check` の結果を残す。
- implementation reportを更新する。
- review可能なremote branch / commitを作る。
- DEVがremote branch、commit SHA、変更ファイル、tests、implementation reportを実確認し、Issue #17へ完了証跡を記録する。
- その後にのみIssue #22へ独立監査handoffする。

Stage9全体Gateの最終PASSはIssue #22 AUDITが判定する。
