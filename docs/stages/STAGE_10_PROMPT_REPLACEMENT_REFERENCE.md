# Stage10 Prompt Replacement Candidate Reference

最終更新: 2026-09-08

## 位置づけ

Stage10のテストPrompt作成時に、ChatGPTが具体的に記述できない核心部分だけを置換札にする場合のPROMPT班向け参照ルール。

- 現在StageはStage 9B。Stage10本番開始を意味しない。
- Stage10正式handoff前の準備ルールであり、本体production仕様ではない。
- 本体仕様・Special意味正本を変更しない。
- 正式handoff / 正式Specialデータ / 正式実験仕様が渡された後は、それらを優先する。

## 基本ルール

1. ChatGPTが具体的に書ける成人向け内容は、予防的に置換札へ逃がさず具体的にPromptへ書く。
2. ChatGPTが具体的に書けない核心部分だけ、日本語の非Prompt置換札にする。
3. 置換札だけを提示してユーザーへタグ探索を丸投げしない。
4. 置換が必要な場合、Special2788参照辞書を使い、実在候補を併記する。
5. 候補は可能な限り以下を示す。
   - 第一候補（canonicalを優先）
   - Alias候補 + canonical_target
   - broad / specific候補
   - Semantic候補（Semanticであることを明示）
   - Special ID
   - post_count（ある場合）
6. canonical / Alias / Semanticを混同しない。
7. 複数の置換箇所がある場合は、A / B / Cのように部位・行為・状態を分ける。
8. Stage10の成人向けPromptでは未成年対象語を使用しない。

## 出力形式

例:

```text
【差し替えA：対象内容を日本語で説明】

第一候補:
ID xxx — canonical tag
canonical / Core or Extended / post_count

Alias候補:
ID xxx — alias tag
→ canonical_target: canonical_tag

Broad候補:
ID xxx — broad tag

Semantic候補:
ID xxx — semantic phrase
※ Danbooru canonical tagではない

推奨:
通常は第一候補。Alias挙動・broad+specific・Semantic反応そのものを測る場合のみ対応候補へ差し替える。
```

## 参照辞書

PROMPT班向け人間可読・GitHub検索可能な派生辞書:

- `data/special2788/prompt_reference/README.md`
- `data/special2788/prompt_reference/MANIFEST.txt`
- `data/special2788/prompt_reference/`
  - 01〜12はカテゴリ別ファイル
  - 13「その他・文脈」は1404件を8ファイルへ分割
  - 合計2788件

元のSpecial2788データを置き換える正本ではない。タグ探索・差し替え候補提示のための補助資料としてのみ使う。
