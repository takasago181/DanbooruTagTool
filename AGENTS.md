# AGENTS.md — DanbooruTagTool v1.7

## 作業開始ゲート

Codexは独立した班ではなく、DEV（開発班）の実装担当。
新しいCodexセッションや作業再開時は、実装・テスト・commitを始める前に現在地をGitHub正本から確認する。

最初に必ず読む:
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. `docs/project/CURRENT_DEV_TASK.md`
4. 現行Stageの仕様・実装レポート

その後、必要に応じて下記の恒久仕様を読む。
Issue番号は固定値として記憶せず、毎回 `CURRENT_STATE.md` から現行DEV Issueを特定する。

作業開始前に少なくとも次を確認できる状態にする:
- 現在のStage
- 現行DEV Issue番号と作業範囲
- `CURRENT_STATE.md` の現行DEV Issue番号と `CURRENT_DEV_TASK.md` のSource Issue番号が一致していること
- 触ってよい範囲 / 触ってはいけない範囲
- 次に実装する境界
- Stage Gate

古いhandoff・旧チャット・過去Stage資料とGitHub現行状態が衝突した場合、古い資料で現在地を巻き戻さない。ただし勝手に破棄・統合・補完もせず、衝突としてDEVへ報告する。
現在地・現行DEV Issue・DEV task mirrorの整合を確認できない場合は推測で実装を開始しない。

禁止:
- 現在Stageを越えて勝手に次Stageへ進む
- 承認済みStage仕様に残る未完了substage/gateを暗黙に飛ばす
- Stage10実験用Prompt知識をStage9 production規則へ先行固定する
- NoobAI / WAI / Illustrious / Anima等のmodel family固有Prompt grammarを共通前提にする
- DEVの正式仕様決定やAUDITのPASS判定をCodexが代行する

## 現行DEV Issue本文の読取

Codexはprivate GitHub Issue APIへの追加認証を要求しない。
現行DEV Issue本文は、repository内の `docs/project/CURRENT_DEV_TASK.md` をCodex読取用ミラーとして使用する。

確認手順:
1. `docs/project/CURRENT_STATE.md` から現行DEV Issue番号を取得する。
2. `docs/project/CURRENT_DEV_TASK.md` の `Source` Issue番号と一致することを確認する。
3. 一致した場合のみ、同ファイルの目的・作業範囲・禁止事項・完了条件を現行DEV taskとして読む。
4. 不一致・欠損・明確な矛盾がある場合は実装を開始せずDEVへ報告する。

同期ルール:
- GitHub Issueが実作業の管理記録で、`CURRENT_DEV_TASK.md` はCodex読取用ミラー。
- DEV Issueの本文・state・完了条件を変更する管理作業では、ミラーも同じ管理作業内で更新する。
- Codexが守るべき目的・scope・禁止事項・完了条件はIssue本文とミラーに存在するものだけを現行指示として扱う。
- Issueコメントは結果・証跡・checkpoint・履歴の記録には使えるが、コメントだけで現行taskの条件を上書きしたものとは扱わない。
- Codex自身がIssue本文を推測してミラーを書き換えない。
- DEV/管理側はCodexへ新規実装・再開を渡す直前にprivate Issue本文/stateと最新mainのmirrorをlive照合する運用。Codexはその管理preflightを代行せず、local側では番号・mirror・scope・Gateを再確認する。

## task branch

本体実装は原則として最新mainからtask用feature branchを作る。

- 実装を直接mainへcommitしない。
- 作業開始前にlocal mainを可能な範囲で最新origin/mainへfast-forwardし、clean working treeを確認する。
- 現行taskに対応する明確なbranch名を使う。
- 意味のあるstable checkpointはcommitする。
- push可能ならremoteへpushし、branch名とcommit SHAを報告する。
- mainへのmergeやStage完了宣言はDEV/AUDIT Gateを越えてCodexが独断で行わない。

既にDEVが明示的に指定したtask branchがある場合はそれを使う。
branch/current mainに予期しない差分がある場合は、勝手にreset/force overwriteせずDEVへ報告する。

## local protected data safety

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

## 恒久仕様として読む

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

## ChatGPT受け渡し

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

## 製品目的

特殊2,788語の単語・組み合わせをCore Tag Setとして画像生成の核にし、
実Danbooru post-level dataで核に必要な補助タグを探索し、
必要なら全124,016 canonicalへ広げ、
最終的に英語Prompt + LoRAへ変換する。

主従:
Special2788 → true AND共起 → All Danbooru補完 → Prompt

autocomplete自体を製品の主役にしない。

## 絶対ルール

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

## 拡張可能な境界は5つ

1. DataSource
2. TagSearchEngine
3. CooccurrenceEngine
4. Translation / SpecialDictionary
5. PromptFormatter

## Stage 2で必ず扱う問題

AND集合を作るだけでは不十分。
AND後のCandidate Aggregationを高速に行う構造まで比較する。

例:
- tag_id -> post set
- post_id -> tag_id[]
の双方向構造を候補に含める。

base size:
1 / 100 / 10,000 / 100,000
程度でcandidate aggregation性能を測る。

## ユーザー環境

- Windows 11
- Ryzen 7 9800X3D
- RTX 5070 12GB
- RAM 32GB
- Samsung 990 PRO 2TB
- Forge Neo / Illustrious XL
- ComfyUI 日本語UI
- Forgeと同時常駐して邪魔にならないRAM設計を重視

## 報告

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

## Core Tag Set

- Special2788の単語・組み合わせを第一級オブジェクトにする。
- `docs/CORE_TAG_SET_SCHEMA.md` のv1 minimumを超えて高機能化しない。
- CoreとAuxiliaryを内部的に混ぜない。
- ユーザーの核がRecommendationに埋もれるUIを作らない。

## 2本の最重要課題

目的/UX:
- Core Tag Set

技術/性能:
- Candidate Aggregation

どちらか片方だけを「最重要」としてもう片方を後回しにしない。
