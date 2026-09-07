# AGENTS.md — DanbooruTagTool v1.4

## 作業開始ゲート

Codexは独立した班ではなく、DEV（開発班）の実装担当。
新しいCodexセッションや作業再開時は、実装・テスト・commitを始める前に現在地をGitHub正本から確認する。

最初に必ず読む:
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. `CURRENT_STATE.md` に記載されたDEVの現行GitHub Issue
4. 現行Stageの仕様・実装レポート

その後、必要に応じて下記の恒久仕様を読む。
Issue番号は固定値として記憶せず、毎回 `CURRENT_STATE.md` から現行DEV Issueを特定する。

作業開始前に少なくとも次を確認できる状態にする:
- 現在のStage
- 現行DEV Issue番号と作業範囲
- 触ってよい範囲 / 触ってはいけない範囲
- 次に実装する境界
- Stage Gate

古いhandoff・旧チャット・過去Stage資料とGitHub現行状態が衝突した場合、古い資料で現在地を巻き戻さない。ただし勝手に破棄・統合・補完もせず、衝突としてDEVへ報告する。
現在地または担当Issueを確認できない場合は推測で実装を開始しない。

禁止:
- 現在Stageを越えて勝手に次Stageへ進む
- Stage10実験用Prompt知識をStage9 production規則へ先行固定する
- NoobAI / WAI / Illustrious / Anima等のmodel family固有Prompt grammarを共通前提にする
- DEVの正式仕様決定やAUDITのPASS判定をCodexが代行する

## GitHub Issue読取

private repository の現行Issue本文は、未認証のGitHub RESTへ直接アクセスせず、ローカルの GitHub CLI (`gh`) を優先して読む。

推奨手順:
1. `gh auth status --hostname github.com` で認証状態を確認する。
2. 未認証なら `gh auth login --hostname github.com --git-protocol https --web` で一度だけ対話認証する。
3. 認証後、`gh issue view <Issue番号> --repo takasago181/DanbooruTagTool --json number,title,state,body,url` で現行Issue本文を読む。
4. Issue番号は `CURRENT_STATE.md` から取得し、過去セッションの番号を固定値として使わない。

セキュリティ:
- tokenを標準出力・ログ・報告へ表示しない。
- `gh auth status --show-token` や `gh auth token` を確認目的で使わない。
- Windows Credential Manager等に保存された資格情報を直接抜き出さない。
- PATをソース、設定ファイル、handoff、Issue、commitへ保存しない。

Issue本文を取得できない場合:
- 推測でIssue本文を再構成しない。
- `Issue本文取得失敗` としてDEVへ報告し、実装開始を止める。
- `CURRENT_STATE.md` とStage仕様だけを根拠に、Issueの詳細を読んだことにしない。

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

- ChatGPTのレビュー・監査・判断が予定される作業では、`docs/CHATGPT_CODEX_HANDOFF.md` の固定受け渡し運用を自動適用する。
- `C:\\Codex\\DanbooruTagTool\\_handoff\\CHATGPT_HANDOFF\\` には今回の監査に必要なコピーだけを置き、完了後に `C:\\Codex\\DanbooruTagTool\\_handoff\\CHATGPT_HANDOFF.zip` を作成・検証する。元ファイルの移動・削除・改変、巨大原本・秘密情報・cache/build成果物の混入は禁止。

## 製品目的

特殊2,788語の単語・組み合わせをCore Tag Setとして画像生成の核にし、
実Danbooru post-level dataで核に必要な補助タグを探索し、
必要なら全124,016 canonicalへ広げ、
最終的に英語Prompt + LoRAへ変換する。

主従:
Special2788 → true AND共起 → All Danbooru補完 → Prompt

autocomplete自体を製品の主役にしない。

## 絶対ルール

- `data/source/` と `data/special2788/` は正本。上書き禁止。
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
