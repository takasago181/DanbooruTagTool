# Test Prompt Replacement Reference — Special2788

PROMPT班がテストPrompt作成時の差し替え候補を探すための、人間向け・GitHub検索可能な派生辞書です。

## 状態

- 全2788件を収録済み。
- 元Special IDを保持。
- 日本語 / 英語Tag / ID / Layer / post_count / Aliasのcanonical_targetをコンパクトに併記。
- 元のSpecial2788正本を置き換えない。
- Stage10本番開始を意味しない。現在Stageは `docs/project/CURRENT_STATE.md` に従う。
- PROMPT班の置換候補提示ルールは `docs/stages/STAGE_10_PROMPT_REPLACEMENT_REFERENCE.md` を参照。
- 件数・ハッシュ・ファイル構成は `MANIFEST.txt` を参照。

## Prompt作成時の使い方

ChatGPTが具体的に書けない核心部分だけ置換札にし、置換札の横へこの辞書から候補を付ける。

優先して示すもの:

1. 第一候補のcanonical
2. Alias候補 + canonical_target
3. broad / specific候補
4. Semantic候補（Semanticであることを明示）
5. Special ID
6. post_count（ある場合）

複数の置換対象がある場合はA / B / Cのように分ける。置換札だけを出してユーザーへタグ探索を丸投げしない。

## Layer略号

- C = Core
- E = Extended
- A = Alias
- S = Semantic
- post_countが `-` の場合、0件ではなく数値件数を持たない。
- Alias行の `->` はcanonical_target。

## ジャンル

01. 身体・解剖 — 147件
02. 裸体・衣服・露出 — 229件
03. ポーズ・体位・構図 — 65件
04. 性行為・性的刺激 — 252件
05. 挿入・性具・機械 — 149件
06. 拘束・BDSM・支配 — 161件
07. 体液・排泄・汚損 — 150件
08. 異形・触手・非人間 — 70件
09. 生殖・妊娠・授乳 — 14件
10. R18G・損傷・グロ — 80件
11. 年齢・関係性・役割 — 38件
12. メタ・レーティング — 29件
13. その他・文脈 — 1404件

合計: 2788件。

## ファイル分割

- 01〜12: 各ジャンル1ファイル
- 13: `part01`〜`part08` に分割

分割はGitHub上での検索・確認をしやすくするためで、データ削減ではありません。

## 成人限定

Stage10のPrompt作成対象人物は成人のみです。辞書網羅性・検出参照のため年齢関連語や未成年関連語も元辞書どおり収録されていますが、未成年対象語をStage10の成人向けPrompt候補には使用しません。
