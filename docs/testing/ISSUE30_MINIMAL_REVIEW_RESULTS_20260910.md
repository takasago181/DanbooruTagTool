# Issue #30 minimal review result — 2026-09-10

既存の19枚だけをユーザーが確認した。回答範囲は「指定したSpecialの対象が画像にあるか」であり、未回答の観点は推測していない。

## 結果

- 対象あり: 16枚
- 対象なし: 1枚（5番の対照）
- 判断できない: 2枚（11番、18番）
- 対照不成立: 5番（`exposed genitals` だがTシャツ姿で性器が露出していない）
- 部位・関係性の問題: 14番（対象はあるが膣にも入っている）
- 暫定的なAUTO補助候補: 8枚（1〜4、6、9〜10）
- HUMAN_REVIEW_ONLY: 8枚（7〜8、12〜17、19）
- BLOCKED: 2枚（5、11）
- UNRESOLVED: 1枚（18）

## 重要な解釈

1〜4、6、9〜10は、今回の「対象があるか」という観点では良好だった。ただし、これは8枚の小規模サンプルによるAUTO補助候補であり、production AUTO昇格や閾値確定ではない。

5番はTaggerのfalse positiveではなく、対照Promptが画像に実現されていない生成失敗である。11番は画像内容を観察できないため、BLOCKEDとする。

14番は対象概念の存在だけなら肯定だが、指定部位と異なる解釈が同時に現れている。したがって関係・部位・bindingの安全性を否定する例として、HUMAN_REVIEW_ONLYに固定する。18番は拘束状態を判断できず、UNRESOLVEDとしてAUTO評価から除外する。

## early-stopへの影響

レビュー順1〜4で、対象がないのに機械screeningが通ったというfalse positiveは確認されなかった。そのため、AUTO補助候補の検証を直ちに打ち切る条件は発生していない。ただし、関係・部位・複合SpecialのAUTO化は支持しない。

## 制限

- 全128枚のground truth化ではない。
- evaluatorのscore/voteを人間判定へ提示していない。
- 未レビュー画像はNOT_REVIEWEDのままであり、負例・正解には数えない。
- 新規画像生成、evaluator再実行、production `data/**`、#32、canonical、Stage10本番A/Bの変更・開始はない。

Machine-readable record: `ISSUE30_MINIMAL_REVIEW_RESULTS_20260910.json`
