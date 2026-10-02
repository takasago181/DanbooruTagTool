# BATCH_BD — 予測方式とAttention基礎 — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
目的: epsilon / v-prediction / flow matching と、self-attention / cross-attention / joint attentionを、画像生成の実践診断へつながる形で整理する。  
方針: 数式用語を目的化せず、「モデルが何を予測し、runtimeは何を合わせる必要があるか」「attentionが何を結び付け、何を保証しないか」を重視する。

## 1. 予測方式は「Sampler名」と別

DiffusersのEuler/DDPM系schedulerでは、`prediction_type` として少なくとも:
- `epsilon`
- `sample`
- `v_prediction`

を区別する。

`epsilon` はノイズ予測。
`sample` はクリーンなsample側を直接予測する形式。
`v_prediction` は、noisy sample・signal・noiseを別の基底で表したv-parameterization。

重要なのは、**同じSampler名でもcheckpointが想定するprediction typeが違えば、正しい推論条件は同じではない**こと。

Source:
- https://huggingface.co/docs/diffusers/api/schedulers/euler
- https://huggingface.co/docs/diffusers/api/schedulers/ddpm
- https://arxiv.org/abs/2202.00512
- https://arxiv.org/abs/2210.02303

## 2. epsilon prediction

直感:
- noisy latentに混ざった「ノイズ成分」をモデルが予測する。

実践上:
- SD1.x/多くのSDXL系などで一般的だった方式。
- scheduler側もcheckpointのprediction typeを正しく解釈する必要がある。
- 「epsilonだから高品質」「v-predだから高品質」のような品質tierではない。

## 3. v-prediction

v-predictionは単純に「画像の移動速度」を意味するものではない。

VP diffusion文脈では、signal/noiseを組み合わせた別parameterizationとして扱う。
Progressive Distillationでは、few-stepでの安定性改善を狙うparameterizationとして議論され、Imagen VideoやStable Diffusion v2系でも採用例がある。

実践上:
- EPS checkpointとV-Pred checkpointを同じものとして扱わない。
- sampler / scheduler / runtime metadataの対応を確認する。
- 同じseed・PromptでもEPSとV-Predの結果を同一分布の比較として扱わない。
- 「V-Predは暗部が強い」等の見た目差はcheckpoint固有の実測事項で、v-pred一般原理にしない。

Source:
- https://arxiv.org/abs/2202.00512
- https://arxiv.org/abs/2210.02303
- https://huggingface.co/docs/diffusers/using-diffusers/schedulers

## 4. Flow Matching

Flow Matchingはepsilon/v-predの単純な別名ではない。

元論文では、Continuous Normalizing Flowのvector fieldを直接regressionする学習枠組みとして定義され、noiseからdataへ連続的に運ぶ確率pathを扱う。

現在のDiffusersでは、SD3やFlux/Qwen-Image等のflow-matching family向けにFlowMatch系schedulerを別系統として持つ。

実践上:
- FlowMatchモデルへ従来diffusion checkpoint用schedulerを安易に差し替えない。
- checkpointが採用するtraining objective / scheduler familyを実行identityの一部にする。
- `v_prediction` の「v」とFlow Matchingのvector field/velocityを同一概念として教えない。

Source:
- https://arxiv.org/abs/2210.02747
- https://huggingface.co/docs/diffusers/api/schedulers/flow_match_euler_discrete
- https://huggingface.co/docs/diffusers/main/using-diffusers/schedulers

## 5. 実践向け予測方式チェック

生成が明らかに崩れる場合:
1. checkpoint family確認
2. EPS / V-Pred / FlowMatch等のtraining objective確認
3. scheduler config / runtime metadata確認
4. sampler/scheduler互換性確認
5. merged checkpointならmetadata欠落を疑う

**Samplerだけ変えて直そうとする前に、prediction type mismatchを除外する。**

---

# Attention

## 6. Attentionを一言で

Attentionは、ある表現が「他のどの情報をどの程度参照するか」を計算する仕組み。

画像生成ではarchitectureによって使い方が違うため、`attention = Promptの単語を画像の場所へ貼る機能` とだけ覚えない。

## 7. Self-Attention

自己注意（self-attention）は、基本的には**同じ表現集合の中**で要素同士を参照する。

画像latent/patch側なら:
- 離れた位置の関係
- 全体構造
- 一貫性
等を扱う助けになる。

ただし、どのlayerで何を表すかはarchitecture依存。

Diffusersのattention processorもself-attentionとcross-attentionでprojectionの扱いを区別している。

Source:
- https://huggingface.co/docs/diffusers/main/api/attnprocessor

## 8. Cross-Attention

交差注意（cross-attention）は、**異なる情報源**を結び付けるattention。

Latent Diffusionではcross-attentionを導入し、textやbounding box等のconditioningを画像生成へ入れられるようにした。

典型的なtext-conditioned U-Netでは:
- query: 画像latent側
- key/value: text encoder等のconditioning側

として理解するとよい。

Source:
- https://arxiv.org/abs/2112.10752

## 9. Cross-AttentionとPrompt binding

Prompt-to-Promptは、cross-attention mapがPrompt中の語と画像の空間layoutの関係に強く関与することを利用した。
Attend-and-Exciteは、cross-attentionの弱いsubject tokenを強めることで、subject omissionやattribute binding問題を改善する。

ここから実践上わかること:
- Prompt中に単語が存在するだけで、そのsubjectが必ず生成されるわけではない。
- 複数subjectでは、attribute bindingが崩れ得る。
- cross-attentionを調整する手法はbinding改善の手段になり得る。

ただし:
**cross-attention mapは完全なsemantic ground truthではなく、厳密な所有者保証でもない。**

Source:
- https://arxiv.org/abs/2208.01626
- https://arxiv.org/abs/2301.13826
- https://arxiv.org/abs/2306.05427

## 10. Regionalとの関係

Regional prompting / regional attentionは、Prompt conditioningを空間的に分離する発想と親和性が高い。

実践では:
- Aの条件をA領域へ
- Bの条件をB領域へ
と分けることでidentity/attribute contaminationを下げられることがある。

一方:
- 接触
- overlap
- interaction
のような**領域を跨ぐ関係**では、強い分離がcoherenceを落とし得る。

このため:
`最大分離`ではなく`必要な分離を満たす最小強度`
を選ぶ。

これは既存K-PRACTICAL-035等と整合。

## 11. 新しいDiT/MMDiTでは注意

すべての新モデルが「U-Net + text cross-attention」と同じ構造ではない。

Stable Diffusion 3のMMDiTはtext/imageを別weightで処理しつつjoint attentionを使い、text-image間の双方向情報流を持つ。

したがって:
- SD1.x/SDXL向けcross-attention hack
- old Regional technique
- LoRA target assumptions

をMMDiT/FlowMatch familyへ無検証で移植しない。

Source:
- https://huggingface.co/docs/diffusers/api/models/sd3_transformer2d
- https://huggingface.co/docs/diffusers/api/pipelines/stable_diffusion/stable_diffusion_3

## 12. #44へ昇格したい原則

1. prediction typeはcheckpoint/runtime identityの一部。
2. epsilon / v-pred / flow matchingは別概念。
3. prediction type mismatchは生成破綻原因になり得る。
4. self-attentionとcross-attentionは役割を分けて教える。
5. cross-attentionはtext-image bindingへ関与するが、所有関係を保証しない。
6. modern MMDiT/joint-attention architectureへ旧U-Net前提を無検証転用しない。

## 13. 実践への接続

成人向け複数人物で:
- 「Aの属性がBへ移る」
- 「subjectが消える」
- 「relationは書いたがbindingが崩れる」

時に、単なるtag不足だけでなく**conditioning/binding/locality問題**として考えられる。

ただしattention内部を直接操作する前に:
1. A-only / B-only
2. minimal Prompt
3. fixed seed
4. Regional/reference
の順で、より観測可能な層から診断する。
