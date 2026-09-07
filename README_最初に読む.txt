【重要 / CURRENT OPERATION】
このファイルは初期 Codex Pack v1.3 の説明を保存した歴史資料です。
現在のCodex開始手順として使用しないでください。

現在の作業開始は必ず最新mainの以下を基準にします。
1. AGENTS.md
2. docs/project/CURRENT_STATE.md
3. docs/project/PERMANENT_RULES.md
4. docs/project/CURRENT_DEV_TASK.md
5. 現行Stage仕様・実装レポート

`FIRST_CODEX_REQUEST.txt` を現在のCodexへ「そのまま送る」運用は終了しています。
同ファイルはStage0/1開始時の歴史資料です。
現在Stageは `CURRENT_STATE.md` から確認し、古いStageへ巻き戻さないでください。

以下は当時のv1.3 pack説明として保存します。

DanbooruTagTool Codex Pack FINAL v1.3
================================

目的:
特殊2,788語の単語・組み合わせをCore Tag Setとして生成の核にし、
実Danbooru post-level dataで true multi-tag AND 共起を確認し、
必要なときだけ全Danbooruへ広げ、
最後に英語Prompt + LoRAへ変換するツールを作る。

このパックは「完成アプリ」ではなく、
CodexにStage 0/1から安全に開発を始めさせる正式な設計・データパックだった。

■ 当時の最初のCodex依頼
`FIRST_CODEX_REQUEST.txt`
現在は使用禁止。歴史参照のみ。

■ 正本（local protected dataを含む）
- data/source/
- data/special2788/

これらの一部は `.gitignore` 対象で、GitHub自体はlocal dataの完全backupではない。

■ 監査済み派生物
- data/derived/

■ Semantic bridge
- data/semantic/

■ 過去資料
- archive/provenance/
通常実装では読まなくてよい。
特殊2,788の由来を再監査するときだけ参照。

■ 参考コード
- references/trial_v0.2_code/
- references/legacy_prototype_code/

参考コードには巨大CSVを重複同梱していない。
データの正本はルートdata/だけ。

■ 当時未同梱だったもの
4GB級のpost-level metadata本体。
Stage 1でSource Datasetを選定した後に取得する前提だった。

■ 最重要
これは「12万タグのTagCompleteクローン」を作る計画ではない。

主従は:
特殊2,788
→ 実共起で補強
→ 必要なら全Danbooru
→ Prompt化

■ Stage 7A UI 起動
`START_DANBOORU_TAG_TOOL.bat`

日本語・英語の1検索欄からSpecialを選び、必要なら通常Danbooruタグを
補助タグとして追加し、画面下部のread-only Promptをコピーする。
通常起動にネット接続、API key、LLMは不要。
Windows版Python 3の標準Tcl/Tkコンポーネントを使用する。追加UI frameworkは不要。

■ v1.3 FINALで追加固定
- PRODUCT_GOAL_LOCK.md
- Core Tag Setを第一級オブジェクト化
- Candidate Aggregationを実装性能上の最重要課題として明記
- Core / Auxiliary / LoRAを内部分離
- Auxiliary role分類は段階導入
- 低共起を「相性が悪い」と断定しない
- Must / Should / Laterを固定

この版は目的レビューの歴史的終点として保持する。
