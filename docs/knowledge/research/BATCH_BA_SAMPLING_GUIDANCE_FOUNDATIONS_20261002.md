# BATCH_BA — 画像生成の基礎B: Sampler / Scheduler / Steps / CFG / Negative — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Goal: 「数値レシピ」ではなくdenoising loop内の役割として理解する。

---

# 0. 先に重要な注意

**SamplerとSchedulerという用語はUI/libraryで完全に統一されていない。**

Forge/A1111系UI:
- Sampler: Euler / Euler a / DPM++ 2M SDE ...
- Scheduler: Normal / Karras / Exponential / Beta ...

Diffusers:
- `EulerDiscreteScheduler`
- `DPMSolverMultistepScheduler`

のように、solver/sampling methodとnoise/timestep scheduleを一つのScheduler classが抱える場合がある。

したがって#44では:

- **sampling algorithm / solver**
- **noise/timestep schedule**

を概念として分ける。
UIラベルはruntime-specificとして記録する。

---

# 1. Denoising step

生成はhigh-noise stateからlow-noise stateへ進む。

各stepの概念:

1. current latent + timestep/noise level + conditioningをmodelへ渡す
2. modelがpredictionを返す
3. sampling algorithm/schedulerがpredictionからnext latentを計算
4. 次のnoise levelへ進む
5. 最終latentをVAE decode

Steps = この反復を何回に分けるか、というinference設定の一つ。

---

# 2. Sampler / solver

実用的には:

**model predictionを使って「次のlatentへどう進むか」を決める数値的更新方法。**

例:
- Euler
- Euler ancestral
- Heun
- DPM++
- UniPC

違い得る:
- 必要step数
- stochasticity
- stability
- sharpness/texture tendencies
- model compatibility
- speed

ただし「Sampler名だけで絵柄が決まる」とは扱わない。
checkpoint/profile/steps/schedule/CFGとの組み合わせで評価する。

---

# 3. Scheduler / noise schedule

実用的には:

**各stepをどのnoise level / timestepへ配置するか。**

Diffusers docs:
- schedulerはdenoising processに「そのstepでどれくらいnoiseを除くか」を指示する。
- sigmasは各stepのnoise levelを表す。
- Karras / exponential / beta 等でstep placementが変わる。

したがって:

`Euler + Karras`

のようなUI表現は概念的に:
- Euler系sampling update
- Karras系sigma schedule

の組み合わせ。

---

# 4. Steps

Stepsを増やすと:
- denoising update回数が増える
- 通常は時間も増える

しかし:

**stepsを2倍 = qualityが2倍**
ではない。

理由:
- scheduler/solverにより少数step性能が違う
- distilled/turbo系は少数step前提
- model authorが想定するrangeがある
- ある程度以降は改善が小さい/変化中心になることがある
- 過剰stepが常に良いという保証はない

実験:
1. exact model + sampler/schedule + seed固定
2. 例: low / author baseline / highの3点
3. detailだけでなくstructure/Prompt adherenceも見る

---

# 5. Sigma / timestep

Sigma:
**その時点でsampleがどの程度noisyかを示す量として使われる。**

概念:

`high sigma -> ... -> low sigma -> final`

step数が同じでも、
どのsigmaへstepを置くかで生成経路は変わる。

だから:
- Samplerだけ記録してSchedulerを落とす
- Stepsだけ記録してsigma/timestep schemeを落とす

のは再現性不足になり得る。

---

# 6. EulerとEuler a

Euler:
Euler-type denoising update。

Euler a:
Euler Ancestral。

「a」は単なるquality版ではなく、
ancestral sampling variant。

重要:
- same seed / same stepsでもEulerとEuler aは別sampling path。
- authorがEuler aを推奨しているmodelで、別sampler結果をそのmodelの標準能力として混ぜない。

NoobAI EPS / WAI17でEuler a author baselineを保持している理由。

---

# 7. CFGとは何か

CFG = Classifier-Free Guidance。

元論文の考え方:
- conditional prediction
- unconditional prediction

を組み合わせ、conditioning方向へどれだけ強く寄せるかを調整する。

初心者向け:
**Prompt条件へ従わせる圧力を強めるguidance。**

ただし:

**CFGを上げる = Prompt理解力そのものが増える**

ではない。

高すぎるguidanceは:
- image quality低下
- overexposure/saturation
- composition変化
- diversity低下

などを起こし得る。

Diffusers docsも、guidance scaleを上げるとPromptへ近づく一方でqualityを犠牲にし得ると説明する。

---

# 8. CFG 1 / guidanceなし系

guidance implementationはmodel/pipeline依存。

一部pipelineでは:
- guidance_scale <= 1でCFGを使わない
- Negative conditioningが無視される/通常経路で効かない

場合がある。

これがAnima Turbo CFG1で
「普通のNegative Prompt運用をそのまま移植しない」
理由。

**Negative欄に文字が入っていること**と
**そのpipelineがNegative conditioningを実際に使っていること**
は別。

---

# 9. Negative Prompt

Negative Promptは:
**「悪いもの一覧を生成後に消すフィルタ」ではない。**

CFG系pipelineではnegative textもembedding/conditioningとしてdenoising guidanceへ参加する。

そのため:
- intended conceptと意味が重なるNegative
- anatomy/countを変えるtargetに対するbroad anatomy Negative
- rating/safety condition

はtarget自体を弱める可能性がある。

#44の既存原則:
Negativeはactive semantic intervention。

---

# 10. Positive / NegativeのA/B

原因診断:

固定:
- checkpoint
- seed
- resolution
- sampler/scheduler
- steps
- CFG
- LoRA
- Control

変える:
- Negativeだけ

採点:
- target presence
- count
- relation
- composition
- anatomy
- style/artifact

これで
「Negativeが効いた」
と
「modelが元々苦手」
を分ける。

---

# 11. Prompt Weightとの違い

Prompt weight:
特定conditioningの相対的な強調。

CFG:
conditioning全体へのguidance強度。

同じ「強くする」でも別軸。

例:
- `(tag:1.2)` を変更
- CFG 5 -> 7

は同じ実験ではない。

Prompt weightを上げても:
- concept ignorance
- wrong binding
- wrong geometry

が自動解決するわけではない。

---

# 12. Sampler比較の正しい順

1. exact model author baseline
2. seed固定
3. steps固定またはauthor-valid range
4. schedulerも固定
5. samplerだけ変更
6. 複数seedへ広げる

SamplerとSchedulerとStepsを同時に変えて
「Aの方が良い」
と結論しない。

---

# 13. 基礎Bの教師用チェック

説明できるべき:

- SamplerとSchedulerの違いは?
- なぜUIによって名称が違う?
- Stepsは何回の何?
- Sigmaとは?
- CFGは何を強める?
- CFGを上げればPrompt理解が増えるわけではないのはなぜ?
- Negativeはどこへ作用する?
- CFG1でNegativeが効かないpipelineがあるのはなぜ?
- weightとCFGは何が違う?

---

## Sources

- https://huggingface.co/docs/diffusers/using-diffusers/schedulers
- https://huggingface.co/docs/diffusers/main/api/schedulers/overview
- https://huggingface.co/docs/diffusers/api/schedulers/euler
- https://huggingface.co/docs/diffusers/v0.40.0/api/schedulers/euler_ancestral
- https://huggingface.co/docs/diffusers/main/api/modular_diffusers/guiders
- https://huggingface.co/docs/diffusers/api/pipelines/stable_diffusion/stable_diffusion_3
- https://arxiv.org/abs/2207.12598
