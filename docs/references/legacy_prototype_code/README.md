# Danbooru 共起タグ推薦 Prototype

## 何をするもの？

複数のDanbooruタグを入力すると、**入力した全タグと共起しやすい候補タグ**を上位に出すローカル試作です。

例:

```text
twintails, school uniform
```

を入れると、各候補タグについて

- twintails とどれくらい共起するか
- school_uniform とどれくらい共起するか
- 片方だけでなく「両方と」安定して共起するか

を計算してランキングします。

## 今回独自に追加したもの

公開のDanbooru共起検索の考え方を参考にしつつ、以下を追加しています。

- 複数タグの**共通重視（調和平均）**
- バランス（幾何平均）
- 最弱一致（入力タグのうち一番弱い共起率）
- 件数重視
- 2026-09-02版のalias辞書で入力をcanonicalへ正規化
- 特殊2,788語からcanonicalへ解決
- 特殊2,788語に日本語がある候補は日本語も表示
- 共起元の2026-05件数と、手元の2026-09辞書件数を並べて表示
- General / Character / Copyrightの候補切り替え
- 1girl / solo等の巨大汎用タグを任意で除外

## データ

共起部分は u-haru/danbooru_tagsearch が公開している以下を初回に取得します。

- `available_tags.csv`
- `cooccurrence_all_normalized.npz`

その共起データは `u-haru/danbooru-tags-20260518` に基づいており、
公開Dataset READMEでは post ID 1 ～ 11,403,815 を収集したと説明されています。

共起行列ファイル:
- 公開サイズ: 455,719,557 bytes
- SHA-256:
  `dc1749f1d00f8b7063015176b81b603b49552c341074993c50c4390d8c8b6ca6`

このZIPには上記455MBファイル自体は入れていません。
`DOWNLOAD_DATA.bat` があなたのPCで直接取得し、SHA-256を検証します。

## 起動

### 1. Python

WindowsでPython 3が使える状態にします。

### 2. 初回だけ

`DOWNLOAD_DATA.bat`

を実行します。

約456MBの共起行列等を取得します。

### 3. 起動

`START.bat`

を実行します。

初回だけ `.venv` を作り `numpy` を入れます。

## おすすめの最初のテスト

```text
twintails, school uniform
```

次に:

```text
twintails, school uniform, sitting
```

のように1個追加して、順位がどう変化するか確認してください。

他にも:

```text
aqua hair, twintails
long hair, blue eyes, school uniform
cowboy shot, looking at viewer
```

などで違いが見やすいです。

## スコア方式

### 共通重視
入力タグごとの共起率の**調和平均**。

どれか1タグとの関係が弱い候補を強く下げます。
今回の「いろんなタグを入れて、全部に共通する候補を上げる」に一番近い方式です。

### バランス
幾何平均。

共通重視より少し寛容です。

### 最弱一致
入力タグの中で最も低い共起率そのもの。

かなり厳格なANDに近い見方です。

### 件数重視
幾何平均にタグの出現件数を軽く加味。

珍しすぎるタグより、実用上よく使われるタグを上げたい場合向けです。

## 重要な注意

共起は「一緒にタグ付けされる傾向」であって、
「画像生成モデルで必ず相性が良い」という保証ではありません。

また、共起元は2026-05-18系、あなたの辞書は2026-09-02なので、
その間に新設されたタグは共起データ側に存在しない場合があります。

## 参考

- u-haru/danbooru_tagsearch
  https://huggingface.co/spaces/u-haru/danbooru_tagsearch
- u-haru/danbooru-tags-20260518
  https://huggingface.co/datasets/u-haru/danbooru-tags-20260518

この試作は既存Spaceのソースをコピーしたものではなく、
公開されている共起行列の仕様とタグ索引ルールを参照して独自実装しています。
