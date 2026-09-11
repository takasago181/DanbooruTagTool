# AGENTS.md — DanbooruTagTool v1.8

## 1. 役割と作業開始ゲート

Codexは独立した班ではなく、DEV（開発班）の実装担当。
新しいCodexセッションや作業再開時は、実装・テスト・commitを始める前に現在地をGitHub正本から確認する。

### 最初に行うremote-current-state確認

現在どのlocal branchにいるかに関係なく、**branch-localの管理ファイルを現在地として読む前に**、まずremoteの最新管理状態を確認する。

1. `git status --short --branch`
2. `git fetch origin --prune`
3. `origin/main` のHEADを確認
4. 以下を `git show origin/main:<path>` 等のread-only操作で直接読む
   - `AGENTS.md`
   - `docs/project/CURRENT_STATE.md`
   - `docs/project/PERMANENT_RULES.md`
5. `origin/main` 上のcurrent core DEV / Stage Gateを先に確定し、`CURRENT_STATE.md` からcurrent DEV Issue番号を取得する
6. そのIssue番号のlive GitHub Issueを `gh issue view <ISSUE_NUMBER> --comments` で直接取得する
7. Issue title / state / body / 最新コメント / 最新checkpoint / continuation contract / completion condition / blocker・gateを確認する
8. `PERMANENT_RULES.md` と照合し、整合している場合だけ作業を開始する
9. その後でのみ、現在branch上の管理ファイルとの差分を確認する

**古いtask branch上の `CURRENT_STATE.md` / `AGENTS.md` を、fetch後の `origin/main` より優先して現在地判定に使ってはいけない。**
現在branchの管理ファイルが `origin/main` と異なる場合、branch-local stateはそのbranch作成時点の履歴として扱い、現在地は `origin/main` を優先する。

この規則はrepository rootにも適用する。`C:\Codex\DanbooruTagTool` がfeature branch上にあること自体は許容するが、rootにあるlocal `CURRENT_STATE.md`を「rootだから最新」と判断してはならない。rootのbranch / HEAD / `origin/main`との差を確認し、現在地は次の順で確定する。

1. GitHub live `main` のHEAD
2. live `main` の `docs/project/CURRENT_STATE.md`
3. 対応するlive GitHub Issue本文
4. Issue最新checkpoint/comment
5. live `docs/project/PERMANENT_RULES.md`
6. 必要なfeature branch / local worktree

local worktreeの `CURRENT_STATE.md`、handoff、branch-local management documentはhistorical snapshotの可能性がある。local資料とlive `main` / live Issue / checkpointが衝突した場合、古いlocal資料を根拠にcompleted Issueを再開、superseded taskを再実行、old Waveやold Gateを再開してはならない。矛盾が解消されるまでfail-closedで停止する。

remote-current-state確認後、通常のCodex DEV読取順は:
1. `origin/main:docs/project/CURRENT_STATE.md`
2. `origin/main:docs/project/PERMANENT_RULES.md`
3. `gh issue view <CURRENT_DEV_ISSUE> --comments`
4. 現行Stageの仕様・実装レポート

その後、必要に応じて下記の恒久仕様を読む。
Issue番号は固定値として記憶せず、毎回 `origin/main` の `CURRENT_STATE.md` から現行DEV Issueを特定する。

作業開始前に少なくとも次を確認できる状態にする:
- 現在のStage
- 現行DEV Issue番号と作業範囲、または `NO_CURRENT_DEV / MANAGEMENT_HANDOFF`
- `CURRENT_STATE.md` のcurrent DEV Issue番号と、取得したlive GitHub Issueが一致していること
- 現在branchが最新mainに対して古い / ahead / divergedのどれか
- 触ってよい範囲 / 触ってはいけない範囲
- 次に実装する境界
- Stage Gate

### NO_CURRENT_DEV の扱い

`origin/main` の `CURRENT_STATE.md` が current core DEV = `NONE` / `NO_CURRENT_DEV / MANAGEMENT_HANDOFF` の場合、これは**正常な管理停止状態**であり不整合ではない。

この状態では:
- Codexは新しいcore DEV Issueを推測・自動選択しない。
- open Issueを見つけても勝手にcurrent DEVへ昇格しない。
- KNOWLEDGE / PROMPT / UI-JA / TEMP / 必要時AUDIT等の独立レーンは、それぞれ `CURRENT_STATE.md` と明示されたIssue/branch/contractに従う場合だけ進める。
- 新しいcore DEV実装は、管理側が live Issue と `CURRENT_STATE.md` を選択・整合させた後に開始する。

古いhandoff・旧チャット・過去Stage資料とGitHub現行状態が衝突した場合、古い資料で現在地を巻き戻さない。ただし勝手に破棄・統合・補完もせず、衝突としてDEVへ報告する。
現在地・現行DEV Issue・最新checkpointの整合を確認できない場合は推測で実装を開始しない。

## 2. 作業開始時の禁止・停止条件

禁止:
- 現在Stageを越えて勝手に次Stageへ進む
- 承認済みStage仕様に残る未完了substage/gateを暗黙に飛ばす
- Stage10実験用Prompt知識をStage9 production規則へ先行固定する
- NoobAI / WAI / Illustrious / Anima等のmodel family固有Prompt grammarを共通前提にする
- DEVの正式仕様決定やAUDITのPASS判定をCodexが代行する

## 3. 現行DEV task contract

現行DEVの目的・scope・禁止事項・完了条件は、Section 1で取得したlive GitHub Issue本文から読む。`CURRENT_STATE.md` はcurrent DEV Issue番号とroutingを担い、GitHub IssueがDEV作業の正本である。

Issueコメントは最新checkpoint・結果・証跡・履歴の確認に使う。コメントだけでIssue本文のtask contractを黙って上書きしたものとは扱わない。

## 4. task branch / 起動時Git同期

本体実装は原則として最新mainからtask用feature branchを作る。

Codexは**新しいセッション開始時・作業再開時・新しいtask branchを作る直前**に、ユーザーへ手動 `git pull` を求める前に自分で次のpreflightを実行する。

1. `git status --short --branch` で現在branchとworking treeを確認する。
2. `git fetch origin --prune` でremote refsを更新する。
3. **現在branchをswitchする前に** `origin/main` の管理ファイルをread-onlyで直接読み、現在地を確定する。
4. local `main` と `origin/main` の関係を確認する。
5. local `main` がcleanかつ `origin/main` へfast-forward可能で、未追跡path collisionやworktree制約がないことを確認できた場合のみ、`git switch main` → `git merge --ff-only origin/main` で自動同期する。
6. 同期後の `main` HEADを記録し、そのmain上の `CURRENT_STATE.md` / `PERMANENT_RULES.md` を再確認する。実Issueの場合は、current DEV Issueを `gh issue view <ISSUE_NUMBER> --comments` で再取得する。
7. current DEVが実Issueの場合のみ、明示されたtask branchへ移るか、最新mainからtask branchを作る。
8. 既存task branchを再開する場合は、そのbranchと最新mainの差分を確認し、勝手にrebase/reset/force-updateせず、task contractに従って継続可否を判断する。

自動同期を止める条件:
- tracked working treeに未commit変更がある
- local mainとorigin/mainがdivergeしている
- fast-forward-onlyで更新できない
- 未追跡file/directoryがswitch/fast-forward先とpath collisionする
- worktree制約により安全なswitchができない
- merge/rebase/reset/checkoutによりユーザー作業を失う可能性がある
- remote fetchに失敗した
- 現在のbranch/HEADがtask contractと矛盾する

停止条件に当たった場合は、**stash・reset・rebase・force checkout・force pushを自動実行しない**。現状、失敗した操作、必要な判断だけを報告する。

追加ルール:
- 実装を直接mainへcommitしない。
- main同期のための `fetch` / `ff-only` はCodex自身が行う。通常はユーザーへ毎回 `git pull` を依頼しない。
- 現行taskに対応する明確なbranch名を使う。
- 意味のあるstable checkpointはcommitする。
- push可能ならremoteへpushし、branch名とcommit SHAを報告する。
- mainへのmergeやStage完了宣言はDEV/AUDIT Gateを越えてCodexが独断で行わない。

既にDEVが明示的に指定したtask branchがある場合はそれを使う。
branch/current mainに予期しない差分がある場合は、勝手にreset/force overwriteせずDEVへ報告する。

## 5. local protected data safety

GitHubはmanagement stateとcommit済みcode/docsの正本だが、local workspace全体のbackupではない。

`.gitignore` には、環境によって以下のlocal protected dataが含まれる。
- `data/source/`
- `data/derived/`
- `data/runtime/`, `data/runtime_index/`, `data/runtime_source/`
- `data/special2788/*.csv`, `*.xlsx`
- 大容量serialized/index data
- `_handoff/`, backups等

GitHub treeにこれらが見えないことを「削除された」「不要」と解釈しない。

絶対禁止:
- `git clean -fdx`
- `git clean -fdX`
- ignored fileを広範囲に消すcleanup
- local protected dataを復元可能性確認なしで削除/上書き

fresh cloneだけでfull runtime/full pytest環境が揃うとは仮定しない。
必要なlocal dataが見つからない場合は、勝手に再取得・別snapshotへ差し替えずDEVへ報告する。

詳細な恒久ルールは `docs/project/PERMANENT_RULES.md` の「Local protected data」も参照する。

## 6. 恒久仕様として読む

1. `docs/PRODUCT_GOAL_LOCK.md`
2. `docs/CODEX_IMPLEMENTATION_SPEC_JA_v1.3.md`
3. `docs/CORE_TAG_SET_SCHEMA.md`
4. `docs/FLOWCHARTS.md`
5. `docs/RAW_SOURCE_SCHEMA.md`
6. `docs/DATASET_CANDIDATES.md`
7. `docs/STATISTICS_POLICY.md`
8. `docs/SEMANTIC_BRIDGE_SCHEMA.md`
9. `docs/AUXILIARY_TAG_ROLE_POLICY.md`
10. `docs/FEATURE_PRIORITY.md`
11. `docs/TESTING_POLICY.md`
12. `docs/ARCHITECTURE_POLICY.md`
13. `docs/CHATGPT_CODEX_HANDOFF.md`

効率実行の詳細が必要な場合は `docs/project/EFFICIENT_EXECUTION_RULES.md` を読む。これは使用量・往復削減の運用正本であり、品質・安全・Stage Gateを弱めるための規則ではない。

## 7. ChatGPT受け渡し

ChatGPT/DEV/AUDITがreviewする成果物はGitHub-firstで受け渡す。

標準:
- task branchへcommit
- push可能ならremoteへpush
- branch名 / commit SHA / changed files / tests / unresolvedを報告
- GitHubから取得できる成果物についてユーザーへ手動ZIP uploadを要求しない

fallback:
- reviewにlocal-only/ignored dataが必要
- binary evidence等がGitHubにない
- pushできない
- DEV/ユーザーが明示的にZIPを要求

fallback時だけ `docs/CHATGPT_CODEX_HANDOFF.md` のZIP手順を適用する。
元ファイルの移動・削除・改変、巨大原本・秘密情報・cache/build成果物の混入は禁止。

恒久的なbranch・成果物・監査handoffルールは `docs/project/PERMANENT_RULES.md` の「Codex branch・成果物・監査handoff」を正本とする。

## 8. 製品目的・実装不変条件

### 製品目的

特殊2,788語の単語・組み合わせをCore Tag Setとして画像生成の核にし、
実Danbooru post-level dataで核に必要な補助タグを探索し、
必要なら全124,016 canonicalへ広げ、
最終的に英語Prompt + LoRAへ変換する。

主従:
Special2788 → true AND共起 → All Danbooru補完 → Prompt

autocomplete自体を製品の主役にしない。

### 絶対ルール

- `data/source/` と `data/special2788/` はlocal正本。上書き禁止。
- `data/derived/` は監査済み派生物。
- `archive/provenance/` は由来資料。通常実装の入力にしない。
- 特殊辞書の統計値を水増ししない。「データは公平、UIでは優遇」。
- 日本語/英語は同格入力。言語モードを作らない。
- canonical完全一致をaliasやsemanticより優先。
- 空白でtag tokenを分割しない。Promptレベルの区切りはcomma/newline。
- 内部canonicalはunderscore形式。space化はPromptFormatterだけ。
- ambiguous aliasをsilent resolveしない。
- Semantic 336にfake canonical / fake post_count / fake co-occurrenceを付けない。
- statistics runtimeのglobal_countは採用post datasetから計算する。
- 2026-09 tag dictionary post_countは「現在使用数」専用。
- different snapshotsを混ぜてLift相当を計算しない。
- pair共起をtrue multi-tag ANDと表示しない。
- pytestはStage 0から追加・維持。最後だけ書かない。
- speculative plugin architectureは禁止。

### 拡張可能な境界は5つ

1. DataSource
2. TagSearchEngine
3. CooccurrenceEngine
4. Translation / SpecialDictionary
5. PromptFormatter

### Stage 2で必ず扱う問題

AND集合を作るだけでは不十分。
AND後のCandidate Aggregationを高速に行う構造まで比較する。

例:
- tag_id -> post set
- post_id -> tag_id[]
の双方向構造を候補に含める。

base size:
1 / 100 / 10,000 / 100,000
程度でcandidate aggregation性能を測る。

### Core Tag Set

- Special2788の単語・組み合わせを第一級オブジェクトにする。
- `docs/CORE_TAG_SET_SCHEMA.md` のv1 minimumを超えて高機能化しない。
- CoreとAuxiliaryを内部的に混ぜない。
- ユーザーの核がRecommendationに埋もれるUIを作らない。

### 2本の最重要課題

目的/UX:
- Core Tag Set

技術/性能:
- Candidate Aggregation

どちらか片方だけを「最重要」としてもう片方を後回しにしない。

## 9. ユーザー環境

- Windows 11
- Ryzen 7 9800X3D
- RTX 5070 12GB
- RAM 32GB
- Samsung 990 PRO 2TB
- Forge Neo / Illustrious XL
- ComfyUI 日本語UI
- Forgeと同時常駐して邪魔にならないRAM設計を重視

## 10. 報告

毎回:
1. 変更した項目
2. 変更しなかった項目
3. 新規作成ファイル
4. バックアップ先
5. 実施したテスト
6. テスト結果
7. 未解決事項
8. 次にChatGPTへ渡す情報

加えて実装branchがある場合:
- branch名
- commit SHA
- push状況

## 11. 効率実行と品質保護

- 独立・非競合・読み取り専用で同一の限定調査段階にあるツール呼び出しは、Code Modeで可能ならまとめて実行する。失敗を許容できる補助証拠と、失敗時に判定を止める必須証拠を先に分ける。
- 単純確認の1経路・2サイクル予算は、HEAD、branch、Issue state等の単一値確認だけに使う。「完了」「PASS」「正常」「次Gateへ進める」等の複合判定には使わない。
- 低リスク小規模修正ではPlanを省略できるが、着手前に原因も局所的か確認し、対象・最小差分・触らない範囲・検証を固定する。
- N=3は過剰抽象化防止の判断材料であり、安全性・整合性・validation・protected data・transaction・external boundary等へ機械適用しない。
- GUIは決定的テストを先に使う。ただしuser-visible layout、DPI、focus、OS/native UIを変更した場合は必要な最終実機受入を省略しない。
- **使用量節約を理由に、現行task contract、完了条件、Stage Gate、protected integrity、必要な回帰テスト、AUDIT証拠を削らない。**

詳細は `docs/project/EFFICIENT_EXECUTION_RULES.md` を正本とする。
