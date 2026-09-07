# CHATGPT_CODEX_HANDOFF.md

## 固定受け渡し運用

ChatGPTのレビュー・監査・判断が必要な成果物がある作業では、ユーザーに個別ファイルを探させない。
作業完了前に、受け渡し用コピーだけを次のフォルダへまとめる。

`C:\\Codex\\DanbooruTagTool\\_handoff\\CHATGPT_HANDOFF\\`

毎回必須:

```text
CHATGPT_HANDOFF/
  HANDOFF_MANIFEST.md
  <今回ChatGPTに確認してほしいファイルのコピー>
```

受け渡しフォルダの作成・更新が完了したら、必ずフォルダ外側の次のZIPを更新する。

`C:\\Codex\\DanbooruTagTool\\_handoff\\CHATGPT_HANDOFF.zip`

- ZIPは `_handoff/CHATGPT_HANDOFF` フォルダ全体をトップレベルに含める。ZIP自身をZIP内へ含めない。
- ユーザーがこのZIP一つだけをChatGPTへアップロードして監査できる状態にする。
- 前回の `_handoff/CHATGPT_HANDOFF.zip` は今回分で置き換えてよい。元プロジェクトファイルは移動・削除・改変しない。
- 作成後、`HANDOFF_MANIFEST.md` が列挙する全監査対象がZIP内にあることを検証する。ZIP作成または照合に失敗した場合は成功扱いにせず、失敗を明示する。

- 元ファイルは移動・削除・改変しない。`_handoff/CHATGPT_HANDOFF` はコピー専用。
- 監査に必要な実装報告書、schema/仕様書、主要コード、テスト、fixture、必要時のdiff/変更概要だけを入れる。
- 変更していない巨大原本、元Special2788全体、cache、`__pycache__`、`.venv`、`dist`/`build`、一時ファイル、秘密情報、無関係なファイルは入れない。
- handoff作成時に既存ファイルがある場合、前回分を今回分へ混在させない。必要なら既存の**受け渡しコピーだけ**を `_handoff/CHATGPT_HANDOFF/archiveYYYYMMDD_HHMM_<task>/` へ退避し、ルートは今回分だけにする。元ファイルの移動・削除・改変はしない。
- `HANDOFF_MANIFEST.md` は最低限、タスク名、実施内容、ChatGPTに確認してほしい事項、コピーしたファイル一覧、各ファイルの元の絶対パス、各ファイルの NEW/MODIFIED/REFERENCE 区分、実行したテスト、最終結果、未解決事項、次にChatGPTが判断すべきことを記載する。
- 完了報告の最後には必ず次の一文を表示する。

`ChatGPTへ渡すファイル: C:\\Codex\\DanbooruTagTool\\_handoff\\CHATGPT_HANDOFF.zip`

## 既存の完了報告

作業終了時に必ず:

## 1. 変更した項目
## 2. 変更しなかった項目
## 3. 新規作成ファイル
## 4. バックアップ先
## 5. 実施したテスト
## 6. テスト結果
## 7. 未解決事項
## 8. 次にChatGPTへ渡す情報

ChatGPTへ戻す際、Decision documentがあるStageでは必ず添付:
- docs/decisions/DATA_SOURCE_DECISION.md
- docs/architecture/INDEX_ARCHITECTURE_DECISION.md
- docs/decisions/RECOMMENDATION_RANKING_DECISION.md

ChatGPT監査:
- Special2788の主従が逆転していないか
- 正本変更なし
- pair共起をAND扱いしていないか
- Candidate Aggregationを無視していないか
- current_post_countをruntime統計へ混ぜていないか
- Semantic fake mappingなし
- ExactよりSpecial曖昧一致を上げていないか
- pytestを後回しにしていないか
- 過剰抽象化なし
- RAMがForge同時使用を無視していないか

- Core Tag Setが単なるselected_tagsへ潰されていないか
- CoreとAuxiliaryが内部的に区別されているか
- All Danbooruが主画面の主役へ逆転していないか
- 低共起を「相性が悪い」と断定していないか
- 全124,016タグrole分類を先に始めていないか
