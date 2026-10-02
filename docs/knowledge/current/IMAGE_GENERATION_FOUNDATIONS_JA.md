# 画像生成 基礎教科書 — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Status: `CURRENT_FOUNDATION_GUIDE / CLAIM_REGISTRY_WINS`

この文書は、NoobAI / Anima / Illustrious等の具体的レシピより前に理解する共通知識。

## この教科書の表記ルール

**説明は日本語を主にする。**
英語は、実際のUI名・モデル名・技術用語を照合できるように括弧で補助する。

例:
- 潜在表現（latent）
- 条件付け（conditioning）
- ノイズ除去（denoising）
- 文章エンコーダー（Text Encoder）
- サンプラー（Sampler）
- スケジューラ（Scheduler）

英語の名称を並べるだけで説明を終えない。

---

# 1. まず1本の図

`プロンプト（Prompt）`
→ `文字をトークンへ分ける（Tokenizer）`
→ `文章を数値表現へ変える（Text Encoder）`
→ `生成条件（Conditioning）`

同時に:

`シード（Seed）`
→ `初期ノイズ / 潜在表現（Random Noise / Latent）`

そして:

`生成条件 + ノイズを含む潜在表現`
→ `UNet / DiT が各ステップで修正方向を予測`
→ `サンプラー / スケジューラが次の状態を計算`
→ `繰り返す`
→ `完成した潜在表現`
→ `VAEで画像へ復号`
→ `画像`

この図を基準にすると設定の意味が整理しやすい。

---

# 2. 用語を一言で

| 用語 | 一言 |
|---|---|
| プロンプト（Prompt） | 作りたい内容をモデルへ伝える条件 |
| トークナイザー（Tokenizer） | 文字列をモデルが扱う単位へ分ける |
| 文章エンコーダー（Text Encoder） | トークンを生成モデルが使える数値表現へ変える |
| 条件付け（Conditioning） | ノイズ除去の方向を誘導する条件情報 |
| シード（Seed） | 擬似乱数生成器の初期値 |
| ノイズ（Noise） | 生成開始点などで使うランダムな数値配列 |
| 潜在表現（Latent） | 画像を圧縮して扱う内部表現 |
| UNet / DiT | 各ステップで修正方向を予測する中心モデル |
| サンプラー（Sampler） | モデルの予測から次の状態へ進む計算方法 |
| スケジューラ（Scheduler） | ノイズ量や時間刻みをどう進めるか決める仕組み。ライブラリによってはサンプラー相当も含む |
| ステップ数（Steps） | ノイズ除去・更新を何回繰り返すか |
| CFG | プロンプト条件へどれだけ強く寄せるかを調整する値 |
| ネガティブプロンプト（Negative） | 避けたい方向を生成条件として与える。生成後の消しゴムではない |
| VAE | 画像と潜在表現を相互変換する |
| LoRA | 基本モデルへ追加して特徴を学習させる小型アダプター |
| ControlNet | ポーズ・奥行き・輪郭などの構造情報を追加して誘導する |
| 画像から画像生成（img2img） | 元画像の潜在表現へノイズを加えて描き直す |
| 部分修正（inpaint） | マスクした範囲を中心に再生成する |
| 高解像度化（Hires） | 基本生成後の高解像度化・再生成工程。単純な拡大とは限らない |
| VRAM | GPU上でモデルや計算途中のデータを保持するメモリ |

---

# 3. Seedを「構図番号」と覚えない

Seedはrandom generatorの初期値。

同じ:
- model
- Prompt
- sampler/scheduler
- resolution
- LoRA/Control
- runtime

なら比較用に強い。

しかしmodelを変えれば同じseedでも同じ構図を保証しない。

使い方:
- 1変数A/B -> seed固定
- reliability -> 固定seedを複数使う

---

# 4. Stepsを「画質」と覚えない

Steps = denoising反復回数。

多いほど時間は増える。
品質向上はmodel/samplerごとに頭打ちがある。

Turbo/distilled modelは少数step前提のこともある。

まずauthor baseline。

---

# 5. SamplerとScheduler

Forge系で:

Sampler:
`Euler a / Euler / DPM++ ...`

Scheduler:
`Normal / Karras / Exponential / Beta ...`

と分かれていても、
Diffusersでは両方まとめてScheduler classとして実装されることがある。

だから用語より:

- **更新方法**
- **noise levelをどう配置するか**

の2点を見る。

---

# 6. CFG

CFGはPromptへの「従わせる圧力」。

高くすれば何でも理解するわけではない。

高すぎると:
- quality低下
- 色/コントラスト変化
- diversity低下
- composition変化

があり得る。

モデル公式値をbaselineにする。

---

# 7. Negative

Negativeは消しゴムではない。

denoising conditioningの一部。

だから:
「extra armsを消したい」
と入れたNegativeが、
意図的に通常と違う手足/人数を要求するsceneまで弱める可能性がある。

成人向けでもrating/safety Negativeは実験変数。

---

# 8. Resolution

解像度は:
- detail
- composition
- visible body range
- VRAM
- generation time

に関係。

幅×高さが増えるほど負荷は増える。

モデル推奨のpixel area / aspect bucketから開始。

---

# 9. img2img

元画像:
→ VAE encode
→ noise追加
→ denoise
→ decode

Denoise/strength:

低:
元画像を強く保持。

高:
より自由に描き直す。

目的:
- preserve
- restyle
- redraw

を先に決める。

---

# 10. Inpaint

Maskの中を再生成。

基本:
- white = edit
- black = keep
  ※UI inversion設定に注意。

局所異常なら強い。
global relation/countが間違っているならbaseへ戻る。

---

# 11. ControlNet

Prompt:
「何を描くか」

Control:
「どんな構造にするか」

例:
- pose -> skeleton
- depth -> front/back/depth
- canny/line -> contour/layout

Controlには:
- strength
- start
- end

がある。

強くすれば必ず良くなるわけではない。

---

# 12. LoRA

Base checkpointを丸ごと交換せず、
追加weightでcharacter/style/conceptを学習・適用する。

初心者の順:
1. base
2. LoRA 1個
3. weight sweep
4. 2個目
5. A+B比較

最初からLoRA5個積まない。

---

# 13. VRAM

VRAM不足でまず確認:

1. resolution
2. batch size
3. model size
4. Control/adapter数
5. precision
6. attention optimization
7. VAE tiling
8. offload
9. quantization

CPU offloadはVRAMを減らせるが遅くなり得る。

---

# 14. 初心者が最初に保存するもの

- checkpoint/hash
- VAE
- Prompt
- Negative
- seed
- width/height
- sampler
- scheduler
- steps
- CFG
- LoRA + weight
- Control
- img2img/inpaint/Hires state
- runtime/version

これがないと
「昨日の画像がなぜ出ない」
を診断できない。

---

# 15. 最初の学習順

### Level 1
txt2img:
seed / resolution / steps / CFG

### Level 2
Prompt:
tag / Negative / weight

### Level 3
LoRA:
1 adapter + weight

### Level 4
img2img / inpaint

### Level 5
pose/depth/line Control

### Level 6
Regional / reference

### Level 7
multi-character / relation-heavy

### Level 8
training / dataset

順番を飛ばすと
何が効いたか分からなくなる。

---

# 16. 基礎を理解した判定

次を自分の言葉で説明できれば最低基礎PASS:

- latent
- seed
- VAE
- tokenizer/text encoder
- sampler/scheduler
- steps
- CFG
- Negative
- resolution
- img2img denoise
- inpaint mask
- Control strength
- LoRA
- VRAM/precision/offload

詳細根拠:
- `../research/BATCH_AZ_GENERATION_FOUNDATIONS_PIPELINE_20261002.md`
- `../research/BATCH_BA_SAMPLING_GUIDANCE_FOUNDATIONS_20261002.md`
- `../research/BATCH_BB_EDITING_CONTROL_MEMORY_FOUNDATIONS_20261002.md`


---

# 17. Metadata / Hash / safetensors

生成画像だけでなく設定も保存する。

特に:
- PNG Info / workflow
- model hash
- exact LoRA
- seed/settings

を残す。

`.safetensors` は安全なtensor保存形式で、model family名ではない。
同じ拡張子にcheckpoint/LoRA/VAE等があり得る。

# 18. Clip Skip

CLIP text encoderのどのlayer出力をPrompt embeddingに使うか変える設定。

CFGやPrompt weightとは別。
CLIP構成が違うmodelへ古いClip Skip recipeをそのまま移さない。

# 19. Textual Inversion

少数画像から新しいtoken embeddingを学習するpersonalization。

- embedding = text encoder側のlearned token
- LoRA = model layer側へ追加するlow-rank update

別物として扱う。

詳細:
`../research/BATCH_BC_OUTPUT_METADATA_AUXILIARY_FOUNDATIONS_20261002.md`
