# BATCH_BE — LoRA学習パラメータ基礎 — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
目的: LoRA作成時に出てくる学習率・optimizer・scheduler・step/epoch・batch・勾配累積・rank/alpha・text encoder学習を、意味と失敗診断の観点から整理する。  
対象: 一般的なLoRA学習原理。NoobAI/Anima/Illustrious固有レシピは別Claim。

## 1. LoRAで何を学習するのか

LoRAはpretrained weightを固定したまま、低rankの追加行列を学習するparameter-efficient adaptation。

画像生成のDiffusers実装では、UNet/Transformerのattention projection等へLoRA adapterを挿入し、LoRA parameterだけをoptimizerへ渡す例がある。

rankを上げるとtrainable parameter/capacityは増えるが、品質が単調に上がるわけではない。

Source:
- https://arxiv.org/abs/2106.09685
- https://huggingface.co/docs/diffusers/main/en/training/lora

## 2. 学習率（learning rate）

学習率は1 updateでparameterをどれだけ動かすかの基本scale。

高過ぎる:
- 急速なoverfit
- identity/style以外まで強く焼き付く
- color/background/pose固定
- loss不安定
等のリスク。

低過ぎる:
- conceptが入らない
- triggerが弱い
- 同じstep数ではunderfit
になり得る。

重要:
**learning rate単独では評価しない。**
step数・batch・optimizer・scheduler・datasetと組み合わせて見る。

DiffusersのDreamBooth実験でもlearning rateとtraining stepsの組合せでoverfit/underfitが変わる。

Source:
- https://huggingface.co/blog/dreambooth
- https://huggingface.co/docs/diffusers/main/training/dreambooth

## 3. Optimizer

Optimizerはgradientからparameter updateをどう作るかを決める。

例:
- AdamW
- AdamW8bit
- Adafactor
- Lion
- Prodigy
等。

「Optimizer名だけで品質が決まる」とは扱わない。

比較時は最低限:
- learning rate
- betas等
- weight decay
- scheduler
- batch/effective batch
を揃える。

sd-scriptsでは複数optimizerとoptimizer_argsを選択可能。

Source:
- https://github.com/kohya-ss/sd-scripts/blob/main/docs/train_network_advanced.md

## 4. 学習率Scheduler

ここでいうschedulerは**推論SamplerのSchedulerと別**。

学習中のlearning rateを時間方向にどう変えるか。

例:
- constant
- linear
- cosine
- constant_with_warmup
- cosine_with_restarts

同じ初期learning rateでも、schedulerが違えば総update量・後半の学習挙動が変わる。

Source:
- https://github.com/kohya-ss/sd-scripts/blob/main/docs/train_network_advanced.md
- https://huggingface.co/docs/diffusers/main/en/training/lora

## 5. Step / Epoch / Repeat

### Step
optimizer update回数として記録するのが最も比較しやすい。

### Epoch
datasetを何周したか。
dataset size / repeat / batchが変われば、同じepochでも見た画像回数が違う。

### Repeat
dataset entryを何度サンプリング対象へ入れるか。

実践:
**epochだけで学習量を比べない。**

保存する:
- image count
- repeat/subset weight
- batch size
- gradient accumulation
- optimizer step
- epoch

## 6. Batch sizeと勾配累積

batch size:
一度のforward/backwardで扱うsample数。

勾配累積（gradient accumulation）:
複数mini-batchのgradientをためてからoptimizer updateする。

実効batchを考える時に重要だが、
- memory挙動
- optimizer update frequency
- stochasticity
は完全に同じとは限らない。

比較時は実batchとgradient accumulationを両方保存する。

Source:
- https://huggingface.co/docs/transformers/grad_accumulation
- https://huggingface.co/docs/diffusers/main/en/training/lora

## 7. Rank / Alpha

rank:
低rank行列の内側次元。大きいほどtrainable capacityが増える。

alpha:
LoRA出力のscaleに関与する設定。

ただし:
- rank = fidelity
- alpha = 強さ
という単純対応ではない。

dataset/target modules/learning rate/stepとの相互作用を見る。

既存K-LORA-011の基礎Claimを補強する。

## 8. Target Modules

LoRAをどのmoduleへ入れるかも学習identityの一部。

Diffusers例ではattentionの:
- to_q
- to_k
- to_v
- to_out
等がtargetになる。

architectureが変わればtarget可能moduleも変わる。

U-Net SDXL向けtarget設定をMMDiTへ無条件移植しない。

Source:
- https://huggingface.co/docs/diffusers/main/en/training/lora

## 9. Text Encoderを学習するか

Text encoderまで学習すると、token/Prompt conditioning側も変わる。

利点になり得る:
- 特殊trigger
- identity
- faces/subject

一方:
- VRAM増加
- overfit
- prompt semantics drift
のリスクもある。

UNet/Transformer側だけのLoRAと、text encoder込みのLoRAを同一条件として比較しない。

Source:
- https://huggingface.co/docs/diffusers/main/training/dreambooth
- https://github.com/kohya-ss/sd-scripts/blob/main/docs/train_network_advanced.md

## 10. Weight decay / dropout / regularization

Weight decay:
parameter updateへregularizationを入れるoptimizer設定の一種。

Dropout:
学習中に一部経路/条件を確率的に落とす手段。

Prior preservation / regularization images:
学習対象だけへ過度に寄り、baseの一般能力を失うのを抑える考え方。

どれも「大きくすればgeneralizationが上がる」単純dialではない。

Source:
- https://huggingface.co/docs/diffusers/main/training/dreambooth
- https://huggingface.co/docs/diffusers/training/custom_diffusion

## 11. Intermediate checkpoint

最終epochだけで判断しない。

途中checkpointを保存し、同じvalidation Prompt/seed setで:
- identity
- editability
- outfit freedom
- pose freedom
- background freedom
- style leakage
- interaction
を比較する。

最終lossが最低のcheckpointが最良画像とは限らない。

既存BATCH_ASと整合。

## 12. LoRA失敗の学習側診断

### Identityが弱い
候補:
- coverage不足
- learning rate/step不足
- captionでidentity要素を分散し過ぎ
- rank/target不足

### 同じpose/backgroundになる
候補:
- dataset bias
- captionでnuisanceを分離できていない
- overfit
- 学習率/step過多

### 服が変わらない
候補:
- outfitがidentityへ吸収
- caption factoring不足
- datasetに衣装variation不足

### 複数人物interactionだけ弱い
候補:
- trainingにjoint example不足
- role/partner bias
- solo成功をinteraction capabilityと誤認

## 13. 保存すべき学習identity

- base model exact identity/hash
- architecture / prediction type
- dataset一覧/hash
- caption
- crop/bucket
- repeat
- batch
- gradient accumulation
- optimizer + args
- learning rate
- LR scheduler
- total optimizer steps
- epoch
- rank / alpha
- target modules
- text encoder training有無
- precision
- seed
- validation suite
- intermediate checkpoint

「LoRA名 + epoch」だけでは再現情報として不足。

## 14. 昇格候補

1. 学習率とstepは組合せで評価する。
2. epoch単独は学習量の比較単位として不十分。
3. optimizer/scheduler/effective batchはtraining identity。
4. text encoder training有無は別条件。
5. rank/alphaだけでLoRA品質を推定しない。
6. intermediate checkpointを固定validationで比較する。
