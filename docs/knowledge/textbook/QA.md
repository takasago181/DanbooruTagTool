# PDF QA — smartphone-first v1

## 内容と追跡

- live main `4e85099737e0f01adbd2dea9640abded9af20638` とlive Issue #44 body/latest commentsを確認。
- corpus `9142071e6b10a456a89cb8594ae62d95a07a50b2` を固定。
- chapter mapを原稿より先に作成。全corpusファイルをinventoryで分類・hash記録。
- 本文14章 / 59テーマ / 8図。全90Claimを知識索引に保持、83Claimを本文で直接参照。
- 66 ACCEPTED / 8 HOLD / 4 CANDIDATE / 2 HISTORICAL / 10 REJECTED。CONFLICT 0。
- 全source IDが固定版source registryへ解決。S-RESEARCH-004は原registerのURL未登録backlogとして保持。
- Claim参照切れ、成人用語の欠落、正本CSVとの改変なしを確認。
- 生殖器・性行為・体液用語は臨床的な語義として記載。具体的な露骨な生成レシピは範囲外。

## レイアウト

A5 148×210mm / 1カラム。本文13.5pt、行間19.6pt（1.45）、図12pt、
注釈/Claim参照11.5pt、footer戻りリンク11pt、ページ番号11.5pt。
章番号28pt、節見出し20pt、小見出し16pt。成人向け章も同じstylesを使用。
横長tableはなく、モデル・Claim・versionを縦カードに分割。Promptは役割ごとに改行。

全ページを解析し、A5寸法、glyph bounds、文字サイズ、replacement文字、blank page、
目次・outline・link destination、Claim本文・用語の存在を検査。
判定と件数は `references/PDF_QA.json`。再build後にはこのreportも再生成する。

全ページを幅1080pxのPNGにrenderし、1080×2400pxのphone canvasへ配置。
全ページのcontact sheetsでlayoutを確認し、代表本文・図・用語・Claim・versionカードは
phone画像で確認。初回画像の孤立した根拠参照を修正し、図とClaim参照をKeepTogetherにした。
最終版で文字化け、行/図のはみ出し、巨大table、横へ伸びるPrompt、成人章だけの縮小なし。

## 限界と次Gate

Android/iPhone実機viewerでのタップ/閲覧は未実施。解析上のリンク先解決と
phone-fit画像による可読性確認を、実機PASSや生成モデルの実験PASSへ読み替えない。
知識不足・metadata差・収録範囲は `KNOWLEDGE_GAPS.md`。
次Gateは読書用v1のレビュー。main merge、production apply、knowledge HOLD closureは行わない。
