# BATCH_BF — 色管理・画像出力基礎 — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
目的: 「生成は同じなのにビューア/SNS/編集ソフトで色が違う」を、モデル生成失敗と混同しないための出力基礎を整理する。

## 1. 画素値と見た目は同じ概念ではない

画像ファイルにはRGB数値だけでなく、**その数値をどの色空間として解釈するか**の情報を持てる。

同じRGB値でも:
- color profile
- gamma/transfer function
- viewerのcolor management
- display
により見え方が変わり得る。

したがって「PNGを開いたら暗い」は、生成modelだけの問題とは限らない。

## 2. PNGの色空間情報

PNG 3rd Editionでは、色空間を少なくとも:
1. cICP
2. ICC profile（iCCP）
3. sRGB chunk
4. gAMA + cHRM
で示せる。

対応viewerは優先順位に従って解釈する。

Source:
- https://www.w3.org/TR/png-3/

## 3. sRGB

sRGBはWeb/一般表示で広く使われる標準的なRGB色空間。

PNGではsRGB chunkにより、pixel sampleがsRGBであることを明示できる。

**「RGB画像だから自動的にsRGB」とは限らない。**
untagged imageはviewer側の推測に依存する場合がある。

## 4. ICC profile

ICC profileは、画像sampleが属する色空間を記述する。

PNGではiCCP chunkへ埋め込める。

実践:
- 編集ソフトへ渡す
- 色を厳密に揃える
- wide-gamut環境で扱う
場合にprofile有無を確認する。

## 5. Gamma

gAMA chunkは画像sampleと表示輝度の関係を示す情報。

gammaを「画像の明るさslider」とだけ覚えない。
color management pipelineの一部。

alpha channelには通常のgamma補正をかけない。

Source:
- https://www.w3.org/TR/png-3/

## 6. PNG / JPEG / WebPの使い分け

### PNG
向く:
- 生成原本
- metadata保持
- lossless保存
- 再編集

### JPEG
向く:
- 最終配布
- 容量優先
- 写真系

注意:
lossy compressionなので、再編集原本には不利。

### WebP
lossy/lossless両modeを持つ。
対応環境・metadata保持方針を確認する。

知識班の標準:
**生成比較の原本はlosslessを優先**。

## 7. 生成metadataと色metadataを分ける

生成metadata:
- Prompt
- seed
- model hash
- Sampler
等。

色metadata:
- ICC
- sRGB
- gamma
等。

片方が残っていても、もう片方が残るとは限らない。

画像編集・変換・SNS投稿でmetadataが削除される可能性を前提にする。

## 8. SNS/画像ホストへ出した後は別artifact

Upload後:
- recompression
- resize
- metadata strip
- color conversion
が起き得る。

したがって:
`local master PNG`
と
`uploaded/displayed image`
を同一evidenceにしない。

厳密比較ではローカル原本を使う。

## 9. 成人向け画像生成への実践影響

例えば:
- skin toneが変わった
- saturationが落ちた
- shadowが潰れた
- Hires後だけ色が違う

場合、Prompt/LoRAだけでなく:
1. base PNGとfinal PNGのpixel/metadata
2. color profile
3. edit/export設定
4. viewer
5. upload後の変換
を切り分ける。

## 10. 保存方針

学習・比較用:
- base masterをlosslessで保持
- generation metadata保持
- 可能ならcolor profile明示
- edit前/後を別fileにする
- upload版をmasterへ上書きしない

## 11. 昇格候補

1. output appearanceはmodel生成だけでなくcolor-management chainの影響を受ける。
2. PNGはsRGB/ICC/gamma等の色空間情報を持てる。
3. untagged imageはviewer間差の原因になり得る。
4. generation metadataとcolor metadataは別管理。
5. SNS/変換後画像を再現性のmaster evidenceにしない。

Source:
- https://www.w3.org/TR/png-3/
