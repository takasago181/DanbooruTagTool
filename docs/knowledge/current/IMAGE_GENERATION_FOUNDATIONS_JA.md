# 画像生成 基礎教科書 — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Status: `CURRENT_FOUNDATION_GUIDE / CLAIM_REGISTRY_WINS`

この文書は、NoobAI / Anima / Illustrious等の具体的レシピより前に理解する共通知識。

---

# 1. まず1本の図

`Prompt`
→ `Tokenizer`
→ `Text Encoder`
→ `Conditioning`

同時に:

`Seed`
→ `Random Noise / Latent`

そして:

`Conditioning + Noisy Latent`
→ `UNet / DiT が各stepで予測`
→ `Sampler/Schedulerが次のlatentを計算`
→ `繰り返す`
→ `Clean Latent`
→ `VAE Decode`
→ `画像`

この図を基準にすると設定の意味が整理しやすい。

---

# 2. 用語を一言で

| 用語 | 一言 |
|---|---|
| Prompt | 作りたい内容の条件 |
| Tokenizer | 文字列をmodelのtokenへ分ける |
| Text Encoder | tokenを生成modelが使うvectorへ変える |
| Conditioning | denoisingを誘導する条件情報 |
| Seed | 擬似乱数generatorの初期値 |
| Noise | 生成開始点などで使うrandom tensor |
| Latent | pixel画像を圧縮した内部表現 |
| UNet / DiT | 各stepで更新方向を予測する中心model |
| Sampler | predictionから次状態へ進む数値的方法というUI上の呼び方 |
| Scheduler | noise/timestepの進み方。libraryによってSampler込みでこう呼ぶ場合もある |
| Steps | denoising更新の回数 |
| CFG | Prompt conditioning方向へ寄せるguidance強度 |
| Negative | 避けたい方向のconditioning。後処理filterではない |
| VAE | pixel ↔ latent変換 |
| LoRA | base modelへ追加する小型学習adapter |
| ControlNet | pose/depth/edge等で構造を追加誘導 |
| img2img | 元画像latentへnoiseを足して再生成 |
| inpaint | mask範囲だけを中心に再生成 |
| Hires | base後の高解像度/再生成工程。単純拡大とは限らない |
| VRAM | GPU上でmodel/計算途中を保持するmemory |

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
