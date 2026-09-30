# スマートフォン向け画像生成教科書 v1

成果物: `IMAGE_GENERATION_TEXTBOOK_JA.pdf`。A5縦、1カラム、本文13.5pt/行間19.6pt。
第0〜13章の14章、59テーマ。知識索引にはRegistry全90件を保持する。
本文の直接Claim参照は83件。未使用7件も索引に原文・判定・scope・validationを残す。

## 内容

意味の理解、モデル別入力、Special/Support、Promptの役割、weight/runtime、Negative、
構図、複数人物、臨床的な成人用語と構造監査、LoRA/後処理、失敗分類、実践、ツール利用。
成人向け章に具体的な露骨な性行為画像の生成レシピ・最適化は収録しない。
この点では元依頼の全詳細要件を満たさない。`KNOWLEDGE_GAPS.md`に明示する。

## 正本と固定版

- 知識基準SHA: `9142071e6b10a456a89cb8594ae62d95a07a50b2`
- main/product基準SHA: `4e85099737e0f01adbd2dea9640abded9af20638`
- 編集日: 2026-10-01 JST。外部source確認日は元の2026-09-09〜17を保持。
- `references/`のCSV/registerは固定版build入力で、独立した知識正本ではない。
- inventoryは全corpusファイルのpath/hashと教科書用途分類を記録する。
- Claim判定、canonical、production code/catalog/taxonomy、runtime、UserDataを変更しない。
- merged旧PROMPT知識も#44のBatch A–Nとcatalogを通じて扱う。

## 閲覧

PDFの目次と各章のテーマ目次はタップ可能。各ページに「目次へ戻る」を配置。
本文Claim IDは知識索引へ、原資料は固定GitHub SHAへリンクする。
用語集と日本語/英語/canonical表面の索引から各章へ移動できる。

## 再生成と更新

`BUILD.md`に1コマンドの生成とQAを記載。フォントをrepositoryへ追加しない。
新しい#44知識を反映する場合、別のdocs専用branchでcold startを行い、基準SHA、
snapshot入力、chapter map、原稿、gapsを照合してからbuild/QAする。
buildだけでは最新版へ自動更新しない。既存Claimの判定を教科書の都合で修正しない。

## 判定とstop point

構造QAは `references/PDF_QA.json`、目視QAは `QA.md`。
Android/iPhone実機確認は未実施。ローカル1080×2400 phone-fitレンダリングを
実機viewerの動作保証とは呼ばない。次Gateはユーザー/DEVによる読書用v1レビュー。
main merge・production apply・knowledge acceptanceをこの作業で実施しない。
