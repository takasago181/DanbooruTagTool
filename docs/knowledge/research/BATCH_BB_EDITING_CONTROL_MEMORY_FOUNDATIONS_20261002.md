# BATCH_BB — 画像生成の基礎C: img2img / inpaint / Control / LoRA / VRAM — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Goal: local image generationで日常的に使う補助機能を「何をしているか」から説明する。

---

# 1. txt2imgとimg2img

## txt2img

主にrandom latent/noiseから開始。

`noise -> denoise conditioned by Prompt -> latent -> VAE decode`

## img2img

元画像を出発点として使う。

概念:
`input pixels -> VAE encode -> latent -> add noise according to strength -> denoise -> decode`

だからimg2imgは:
**元画像へPromptを上書きするfilter**
ではない。

noiseを追加して再生成する。

---

# 2. Denoise / strength

Diffusersのimg2img `strength`:

- high -> より多くnoiseを追加 -> 元画像から離れやすい
- low -> noiseが少ない -> 元画像を保持しやすい
- 1 -> 最大noise、ほぼfull denoising path

重要:
strengthは実際に使うdenoising stepsとも関係する。

したがって:
`denoise 0.5`
を別sampler/modelへ普遍的にコピーしない。

### 教え方

目的を先に決める:
- preservation
- restyle
- moderate redraw
- structural rewrite

その後strengthをsweepする。

---

# 3. Inpaint

Inpaint:
**maskで指定した範囲を局所的に再生成するediting workflow。**

Diffusers convention:
- white = inpaint/repaint
- black = preserve

UIによってmask inversion optionがあるので確認。

向く:
- hand/face defect
- local identity
- clothing part
- object replacement
- small relation correction
- background replacement

向かない:
global count/relation/layoutが完全に間違っているのを
小さいmaskで無理に直すこと。

---

# 4. Inpaint maskの考え方

Maskは「どこを触るか」。

重要axis:
- mask boundary
- feather/blur
- padding/crop
- full image vs masked-area processing
- denoise/strength
- prompt for edited area
- surrounding context

Diffusers `padding_mask_crop`:
mask周辺をpadding付きcropし、高解像度でinpaintして元画像へ戻す方法。

実用原則:
- maskが狭すぎる -> 必要なgeometryを直せない
- 広すぎる -> identity/composition driftが増える
- hard edge -> boundary artifact候補
- context不足 -> 周辺との接続がおかしくなる

exact mask blur/padding numeric defaultsはruntime/model-specific。

---

# 5. ControlNet

ControlNet:
**text Promptに加え、edge/depth/pose等のvisual structural conditionでdenoiserを誘導するadapter。**

base modelを置き換えるのではなく、
extra control network/residualを通じて構造情報を加える。

代表control:
- Canny/edge
- depth
- pose
- segmentation

それぞれ伝える情報が違う。

---

# 6. PreprocessorとControl model

混同しやすい。

## Preprocessor
元画像からcontrol representationを作る。

例:
- image -> canny edges
- image -> depth map
- image -> pose keypoints

## Control model
そのcontrol representationをどう生成へ効かせるか学習したmodel/adapter。

したがって:
「ControlNetが効かない」
ときはまず
**preprocessor output自体が正しいか**
を見る。

bad control mapを強くしても正しくならない。

---

# 7. Control strength / start / end

主要axis:

### conditioning scale / weight
control signalをどれだけ強く入れるか。

### start
denoisingの何%地点からcontrolを適用するか。

### end
何%地点まで適用するか。

Diffusers ControlNet APIでも
`control_guidance_start`
`control_guidance_end`
を持つ。

つまりControlは:
**ON/OFFだけではなく、どれだけ・いつ効かせるか**
という2軸以上を持つ。

---

# 8. Control source leakage

Control imageは目的以外の情報も持つことがある。

lineart:
- pose
- silhouette
- hair shape
- clothing line
- accessory
- object contour

depth:
- front/back
- body volume
- object placement

だから:
poseだけ欲しいのにhair shapeまで移る
ことがある。

既存BATCH_AY原則:
不要情報をmask/removeしてcontrol sourceをpreprocessする。

---

# 9. LoRAとは何か

LoRA = Low-Rank Adaptation。

基礎:
**base model全部を再学習する代わりに、小さい追加weightを挿入してその部分を学習するadapter technique。**

利点:
- trainable parameterが少ない
- fileが小さい
- training memory/時間を下げやすい
- base modelを残したままadapterを交換できる

Diffusers/PEFTでは:
- rank
- alpha
- target modules

等を設定する。

---

# 10. LoRAの推論時weight

LoRA weightは単なる
「似せ具合slider」
ではない。

weightを変えると:
- identity
- style
- composition
- clothing
- background
- color
- Prompt response

まで変わり得る。

だから:
base -> LoRA low -> medium -> high
をfixed seedで比較。

複数LoRA:
base -> A -> B -> A+B
の順。

---

# 11. LoRA rank / alpha

## rank
low-rank matrixの内部次元。
高いほど一般にtrainable parameter数が増える。

## alpha
LoRA updateのscale設計に関わるparameter。

注意:
rank/alphaだけでLoRA品質は決まらない。

同時に:
- dataset
- caption
- learning rate
- target modules
- training duration
- base model

を見る。

---

# 12. VRAMとは何か

VRAM = GPUがmodel weights / activations / latent / attention states等を置くmemory。

足りないと:
- OOM
- CPU offload
- slower fallback
- lower batch/resolution
などが必要。

VRAMとsystem RAMは別。

ただしoffloadを使えばCPU RAMを補助storageとして使うことはできる。

---

# 13. Precision / dtype

代表:
- float32
- float16
- bfloat16
- fp8 / lower-bit quantization

一般にbit数を下げると:
- model weight memoryを減らせる
- 対応hardwareではspeed benefitがあり得る

一方:
- numerical precision
- compatibility
- unsupported operation
- quality/stability

のtradeoffがある。

Hugging Face docsではbf16はfp16よりnumerical errorにrobustな面を持つが、hardware supportは異なる。

**lower precision = 必ず高速・無劣化**
とはしない。

---

# 14. Quantization

Quantization:
**weights/activations等をより少ないbit表現へ落としてmemoryを節約する技術群。**

目的:
- large modelをconsumer GPUへ載せる
- memory削減
- 一部hardwareでspeed改善

ただし:
- backend
- quantization type
- component
- architecture

で結果が違う。

正本では
「4bitなら画質同じ」
のような一文ルールを禁止。

---

# 15. Offload

Offload:
使用していないcomponent/weightsをCPUへ置き、
必要時にGPUへ移動する。

## model offload
text encoder / transformer / VAE等のcomponent単位。

## sequential CPU offload
より細かく移動してVRAMを削減。

代償:
CPU-GPU transferが増え、かなり遅くなり得る。

VRAM不足時の優先順位はmodel/runtimeで変わるが、
「OOMだから即解像度だけ下げる」以外の選択肢として理解する。

---

# 16. Attention backend

attentionはmodern image modelでmemory/computeの大きな要素。

例:
- PyTorch SDPA
- FlashAttention系
- xFormers
- runtime-specific optimized attention

目的:
- speed
- memory reduction

backendを変えると完全bit-identical再現を期待しない方が安全。

promotion evidenceではruntime/backendを必要に応じて保存。

---

# 17. Batch

混同:

### batch size
同時にGPUで処理する画像数。

通常増やすと:
- throughputを上げられる場合
- VRAM増加

### batch count / repeated generations
UIで単に何回繰り返すか。

同じ4枚でも:
- batch size 4 x count 1
- batch size 1 x count 4

はmemory/runtime behaviorが違う。

---

# 18. VRAM不足時の初心者診断

まず:
1. model family / required components
2. resolution
3. batch size
4. Control / multiple LoRA / detailer
5. VAE decode
6. precision
7. attention optimization
8. offload
9. quantization

を確認。

変更した項目は速度/品質/再現性への影響を分離する。

---

# 19. 基礎Cの教師用チェック

説明できるべき:

- img2imgは元画像へ何をしている?
- denoise/strengthを上げると何が変わる?
- inpaint maskのwhite/blackは?
- maskを広げるリスクは?
- preprocessorとControlNet modelの違いは?
- Control strength/start/endは何?
- LoRAとはcheckpointとどう違う?
- rankとは?
- VRAMとRAMは?
- fp16/bf16/quantization/offloadは何のため?
- batch sizeとbatch countは?

---

## Sources

- https://huggingface.co/docs/diffusers/main/api/pipelines/stable_diffusion/img2img
- https://huggingface.co/docs/diffusers/en/using-diffusers/inpaint
- https://huggingface.co/docs/diffusers/using-diffusers/controlnet
- https://huggingface.co/docs/diffusers/api/pipelines/controlnet
- https://arxiv.org/abs/2302.05543
- https://huggingface.co/docs/diffusers/main/training/lora
- https://huggingface.co/docs/diffusers/main/optimization/fp16
- https://huggingface.co/docs/diffusers/main/optimization/memory
- https://huggingface.co/docs/diffusers/main/quantization/overview
