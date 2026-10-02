# BATCH_AZ — 画像生成の基礎A: pipeline / latent / VAE / text encoder / seed — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Scope: modern local diffusion / flow-based image generation fundamentals  
Goal: 応用設定を暗記する前に、画像が生成される経路を説明できるようにする。

---

# 0. 最短の全体像

典型的なlatent image-generation pipelineは、概念的には次の流れ。

`Prompt`
-> `tokenizer`
-> `text encoder`
-> `text conditioning / embeddings`
-> `random latent/noise`
-> `UNet or diffusion transformer`
-> `iterative denoising / flow update`
-> `clean latent`
-> `VAE decode`
-> `pixels`

ただし全モデルが完全に同じ部品構成ではない。

- SD/SDXL/Illustrious/NoobAI系ではUNet系の理解が重要。
- newer model familiesではDiT/transformer系denoiserが増えている。
- text encoderの数・種類、prediction type、scheduler/flow formulationなどもfamilyごとに違う。
- UIの「checkpoint」一個が、内部では複数componentをまとめている場合がある。

Source:
- Hugging Face Diffusers Quickstart
- Latent Diffusion Models paper
- Diffusers model format docs

---

# 1. Diffusion / denoisingとは何か

初心者向けには:

**ランダムなノイズ状態から、モデルが何度も「次にどちらへ直すか」を予測し、画像として整合する方向へ更新していく。**

重要:
- 一回のforward passで完成画像を直接描いているわけではない。
- inference stepsはこの反復更新回数に関係する。
- denoiserの予測の意味はmodel/prediction typeによって異なり、noise predictionだけとは限らない。
- modern flow-matching系を古典的DDPMと完全に同一視しない。

Hugging FaceはUNet/DiTを、各stepでdenoising predictionを行うpipelineのworkhorseとして説明している。

---

# 2. Latentとは何か

Latent = **pixelsそのものではなく、画像を圧縮して表現した内部空間**。

Latent Diffusionの重要点:
- pixel-spaceで毎step巨大画像を処理するより計算を軽くできる。
- pretrained autoencoderでpixel imageをlatentへ圧縮し、生成モデルは主にlatent上で仕事をする。
- 最後にlatentをpixelへ戻す。

したがって:

`1024x1024のRGB画像そのものを毎step直接描き直す`

という理解は多くのlatent diffusion modelでは誤り。

Source:
Rombach et al., High-Resolution Image Synthesis with Latent Diffusion Models.

---

# 3. VAEの役割

VAE = Variational Autoencoder。

実用上は:

- **encode**: pixel image -> latent
- **decode**: latent -> pixel image

を担当するcomponent。

txt2img:
- 最終clean latentをVAE decoderがpixel画像へ戻す。

img2img/inpaint:
- 元画像をVAE encoderでlatentへ入れる経路もある。

初心者の誤解:
- VAEは「最後に色だけ直すフィルタ」ではない。
- VAEはpixel/latent境界そのもの。

だからVAEの差や不整合は、再構成される外観へ影響し得る。

### VAE tiling

大きい画像を一度にencode/decodeせず、overlapするtileに分けることでpeak memoryを下げる。

代償:
- tileごとに処理するためtone variationなどが起こり得る。
- tiledとnon-tiledは完全に同一の処理ではない。

### VAE slicing

主にbatchを分割して順番にdecodeするmemory-saving technique。
複数画像batchで効果が大きい。

Source:
Hugging Face AutoencoderKL / memory optimization docs.

---

# 4. TokenizerとText Encoder

Prompt文字列はそのままdenoiserへ渡らない。

概念:

`文字列 -> tokenizer -> token IDs -> text encoder -> embeddings/hidden states -> denoiser conditioning`

## Tokenizer

文字列をmodelが扱う単位へ分解する。

重要:
- 見た目の単語数 != token数。
- model familyによってtokenizerが異なる。
- underscore/space、記号、長い固有名などのtokenizationはmodelごとに違い得る。

## Text Encoder

tokensを、画像生成モデルが使えるvector表現へ変換する。

例:
- CLIP-family
- T5-family
- model-specific language adapters/encoders

一部pipelineはtext encoderを複数持つ。

したがって:
**同じPrompt文字列でも、model familyが違えば同じconditioningにはならない。**

Prompt grammarをmodel familyごとに分ける必要がある理由の一つ。

---

# 5. Prompt length / context

Runtimeには:
- tokenizer context limit
- chunking
- truncation
- multiple encoders
- UI preprocessing

があり得る。

A1111/Forge系の`BREAK`やemphasis syntaxはruntime layer。
Danbooru semantic identityではない。

重要:
「Promptが長い = 後ろが全部無視される」という一文ルールにしない。
実際にどう処理されるかはruntime/model implementationを確認する。

---

# 6. Seedとは何か

Seedは**擬似乱数generatorの初期状態を指定する値**。

Diffusion pipelinesではrandom operationが:
- initial Gaussian noise
- sampler/scheduler内の追加randomness
- pipeline固有のstochastic operation

などに関与し得る。

したがって、

**seed = 構図番号**

ではない。

同じseedで似た構図が出るのは、
同一pipeline identityの中で同じrandom streamを再利用して比較している結果。

### same seedで同じ画像にならない条件

以下が変われば結果は変わり得る:
- checkpoint
- VAE
- text encoder
- prompt
- scheduler/sampler
- steps
- CFG
- resolution
- LoRA
- Control
- software/runtime version
- CPU/GPU random generator
- deterministic backend behavior

Hugging Faceも、同一seedでもplatform/releaseをまたいだ完全一致を保証していない。

### 実験上の正しい使い方

A/B比較では:
- seedを固定
- 他設定を固定
- 1変数だけ変更

さらにrobustnessを見るときは:
- 複数の固定seed setへ広げる。

---

# 7. Checkpointとは何か

「checkpoint」はUIでは一つのmodel fileに見えるが、
pipeline conceptとしては複数componentから成ることがある。

例:
- UNet or transformer
- text encoder(s)
- VAE
- scheduler config
- tokenizer/config
- model metadata

Diffusers format:
componentをsubfolderごとに分離できる。

single-file:
UNet/transformer/text encoder/VAE等のweightsを一つのsafetensors/ckptへまとめる形式がある。

重要:
**checkpoint filenameだけで完全なexecution identityとは限らない。**

別VAE、外部text encoder、scheduler、runtime metadataなども記録する。

---

# 8. UNetとDiT

## UNet

Stable Diffusion系で長く使われてきたdenoising backbone。

Diffusersのconditional UNetは:
- noisy sample
- timestep
- conditioning state

を入力に、次の更新へ使うpredictionを返す。

## DiT / diffusion transformer

denoising backboneをTransformerへ置き換える系統。

DiT paperはlatent patches上でTransformerを使う構成を示した。

重要:
UNetとDiTは「画質tier」ではない。
architectureの違い。

そのため:
- VRAM optimization
- attention backend
- Control adapter
- LoRA target
- scheduler compatibility

などの実装条件をfamilyごとに確認する。

---

# 9. 解像度の基礎

Width/Heightは単なる出力キャンバス指定ではない。

変わるもの:
- latent spatial size
- attention/computation workload
- composition prior
- visible body range
- object spacing
- VRAM usage

総pixel数が増えるほど、一般に計算・memory負荷は増える。
ただし正確な増え方はarchitecture/attention implementation/batch等に依存する。

### Aspect Ratio

同じpixel数でも:
- portrait
- square
- landscape

は構図条件が異なる。

「推奨1MP」は「必ず1024x1024」という意味ではない。
model-specific recommended bucket/aspect candidatesを使う。

---

# 10. 基礎Aの教師用チェック

説明できるべき質問:

1. Promptはどうやって画像モデルへ伝わる?
2. latentはpixelと何が違う?
3. VAEはどこで使う?
4. seedは何を固定する?
5. same seedが別modelで同じ構図にならないのはなぜ?
6. checkpointとpipeline componentの違いは?
7. UNetとDiTは何が違う?
8. resolutionを変えると何が変わり得る?

これを説明できなければ、Sampler/LoRAへ進む前の基礎が不足。

---

## Sources

- https://huggingface.co/docs/diffusers/en/quicktour
- https://huggingface.co/docs/diffusers/api/models/autoencoderkl
- https://huggingface.co/docs/diffusers/using-diffusers/reusing_seeds
- https://huggingface.co/docs/diffusers/using-diffusers/other-formats
- https://huggingface.co/docs/diffusers/en/api/models/unet2d-cond
- https://huggingface.co/docs/diffusers/main/api/models/transformer2d
- https://arxiv.org/abs/2112.10752
- https://arxiv.org/abs/2212.09748
