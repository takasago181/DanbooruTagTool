# CURRENT DEV TASK

最終同期: 2026-09-08

## Mirror Metadata

- Source: GitHub Issue #17
- Title: `[Stage9][DEV] Stage9C/9D completion gate before Stage10`
- State: closed
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
- Issue #17 DEV作業: 完了 / DEV実確認済み
- correction branch: `codex/stage9c9d-completion`
- correction commit: `94c6789fc6f921b7362c0e890d3fee7f3db893a3`
- audit target: PR #27 against current main / mergeable=true
- Issue #17 completion evidence: comment `5575794250`
- Stage10: 未開始
- 現在はIssue #22 independent audit待ち。Codex実装は停止。

## DEVで確認済み

- Stage9C common / rare候補集合上書き問題を修正し、両bucketから選択できる回帰テストを追加。
- Stage9D §10の可逆A/B variant contractを実装。
  - Special position
  - broad generic support 0 / 1 / 2
  - role-density variants
  - model-family scoped explicit weight variants
  - LoRA Prompt contraction variants
  - comparison metadata
- `docs/stages/STAGE_10_PREP.md` を現状へ同期。
- Issue #26の修正はprotected source fileのmanifest/hash/size検証を維持し、既知の`prompt_reference/` directoryだけを許容。
- focused 67 passed。
- Stage7 UI + Stage8 + Ruleset2 regression 99 passed。
- full suite可能範囲 275 passed / exit 0。
- `git diff --check`: PASS。
- current mainよりbranchが2 commits遅れているが、その2件はStage10 Prompt-reference guidanceと`PERMANENT_RULES.md`のみ。PR #27はcurrent mainをbaseにしmergeable=trueで、governance変更を失わない。

## 今やること

DEV実装作業はしない。Issue #22 AUDITの判定を待つ。

## 禁止

- #22 PASS前にStage9全体PASSと宣言しない
- PR #27を監査前にmergeしない
- Stage10画像A/Bを開始しない
- Stage10 winner/scoring logicをStage9へ追加しない
- Stage10実験知識をStage9 production規則へ先行固定しない
- model family別Prompt grammarを未検証で共通化しない

## 次Gate

- Issue #22 PASS → Stage9全体Gate完了処理・PR #27のmain反映確認へ進む。
- Issue #22 FAIL / CONDITIONAL PASS → #17を必要に応じてreopenし、指摘事項をCURRENT_DEV_TASKへ同期してDEVへ戻す。
- Stage10は#22 PASSだけでは開始しない。#4 / #5 / #6 / `STAGE_10_PREP.md` の残Gateを満たす必要がある。
