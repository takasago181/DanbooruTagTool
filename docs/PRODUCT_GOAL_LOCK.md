# PRODUCT_GOAL_LOCK.md

## 目的をここで固定する

このプロジェクトの第一目的は検索でも分析でも辞書編集でもない。

> 特殊辞書の単語・組み合わせを画像生成の核として選び、
> その核だけでは固定しにくい要素をDanbooru全体と実共起から補助タグとして探し、
> 狙ったPromptを組み立てる。

以後、目的の再定義を繰り返さない。
Stage実測で前提が崩れた場合だけ、この文書を再オープンする。

## 主従

### 主役
- Special Core Dictionary の Special entry
- Special Core Dictionary の Special 組み合わせ
- Core Tag Set（生成の核）

現在のproduction snapshot/corpusは、互換上 `Special2788` として保持する。

### 補助
- 全Danbooru canonical
- true multi-tag AND
- Candidate Aggregation
- Alias
- 日本語検索
- Semantic Bridge
- Recommendation
- Prompt Builder
- LoRA

## ユーザーが本当にしたいこと

1. Special Core Dictionary から「出したいもの」を決める
2. 複数Specialを組み合わせて核を作る
3. 核だけで足りない固定要素を補助タグで埋める
4. 必要なときだけ全Danbooruへ広げる
5. 英語Promptとして生成環境へ渡す

## やらない主従逆転

- 12万タグ検索を主画面にしない
- 共起ランキング自体を目的にしない
- autocompleteの豪華さを最優先にしない
- Special Core Dictionary を単なるbadge付き候補に格下げしない

## 完成時の最小操作

Specialを探す
→ 核へ追加
→ 実共起で補助候補を見る
→ 必要な補助を追加
→ Prompt Copy
