DanbooruTagTool Codex Pack FINAL v1.3
================================

目的:
特殊2,788語の単語・組み合わせをCore Tag Setとして生成の核にし、
実Danbooru post-level dataで true multi-tag AND 共起を確認し、
必要なときだけ全Danbooruへ広げ、
最後に英語Prompt + LoRAへ変換するツールを作る。

このパックは「完成アプリ」ではなく、
CodexにStage 0/1から安全に開発を始めさせる正式な設計・データパック。

■ 最初にCodexへ送る文
`FIRST_CODEX_REQUEST.txt`
の内容をそのまま送る。

■ 正本
- data/source/
- data/special2788/

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

■ 未同梱
4GB級のpost-level metadata本体。
Stage 1でSource Datasetを選定した後に取得する。

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

この版を目的レビューの終点とする。
