# BATCH_BG — LoRA学習の損失・timestep・dataset前処理基礎 — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
目的: LoRA/画像生成学習で見かけるMin-SNR、timestep bias、bucket、caption dropout/tag dropoutを、設定名ではなく学習上の役割で理解する。

## 1. Diffusion学習は全timestepが同じ難しさではない

Diffusion学習では、異なるnoise level/timestepをまたいでlossを学習する。

Min-SNR論文は、timestep間でoptimization directionが競合し得ることを指摘し、SNRに基づいてloss weightを調整する。

重要:
- inference Stepsを変える話ではない
- inference Schedulerを変える話でもない
- **training lossの重み付け**の話

Source:
- https://arxiv.org/abs/2303.09556
- https://huggingface.co/docs/diffusers/training/text2image

## 2. Min-SNR

Min-SNR weightingは、SNRに応じて各timestepのloss contributionを再配分する。

Diffusersではepsilon prediction / v_predictionの両方に対応する実装例がある。

実践上:
- `snr_gamma`を変えたrunは別training condition
- 「5が万能」と一般化しない
- 小規模datasetでは効果が目立ちにくい場合もある
- final image評価を省略しない

## 3. Timestep bias / sampling

training時にどのtimestepを多く見るか、どのtimestepのlossを重くするかを変えると、学習で重視されるnoise regimeが変わる。

Diffusers SDXL trainingにはtimestep bias strategy等がある。

これは:
- high-noise側
- low-noise側
の学習比重を変え得る。

ただし「high-noise = composition」「low-noise = detail」を万能な固定対応として扱わない。
実際の効果はarchitecture/training recipe依存。

Source:
- https://huggingface.co/docs/diffusers/v0.35.0/training/sdxl

## 4. Resolution bucket

縦横比が違う画像を単純に同じsizeへ潰す代わりに、複数の解像度bucketへ振り分ける手法がある。

sd-scriptsでは:
- enable_bucket
- min/max bucket resolution
- bucket resolution steps
- bucket_no_upscale
等をtraining configurationとして持つ。

実践上:
- crop
- resize
- aspect distribution
- bucket
はdatasetそのものと同じくtraining identity。

Character LoRAで:
- 顔アップばかり
- 全身が少ない
- 横長sceneがない
等のcoverage問題を、bucket設定だけで解決できるわけではない。

Source:
- https://github.com/kohya-ss/sd-scripts/blob/main/docs/config_README-ja.md

## 5. Caption dropout

Caption dropoutはtraining時にcaption全体を確率的に空にする等の操作。

狙いとしてはconditioningへの依存の仕方を変えるregularizationの一種として使われる。

重要:
- inferenceでPromptを空にすることと同じ実験ではない
- rateを変えたら別training condition
- trigger学習や属性の分離へ影響し得るので、Character LoRAでは無思考に入れない

sd-scriptsには:
- caption_dropout_rate
- caption_dropout_every_n_epochs
等がある。

## 6. Tag dropout

tag形式captionでは、一部tagだけ落とす設定もある。

目的の一つ:
特定tagの同時出現へ過度に固定されるのを弱める。

一方:
- identity core tag
- outfit tag
- mutable attribute
をどうdropするかで学習意味が変わる。

「dropoutを入れればgeneralizationが上がる」とは固定しない。

Source:
- https://github.com/kohya-ss/sd-scripts/blob/main/docs/config_README-ja.md
- https://github.com/kohya-ss/sd-scripts/blob/main/library/dataset.py

## 7. Caption shuffle / keep tokens

tag順序をshuffleする設定では、triggerやidentity tokenまで無秩序に動かしたくない場合がある。

keep_tokens等で先頭側を固定する設計が使われる。

つまりcaption trainingでは:
- 何を書くか
だけでなく
- 何を固定するか
- 何をshuffleするか
- 何をdropするか
も学習条件。

## 8. Dataset preprocessingを「準備作業」と軽視しない

学習結果を変え得る:
- resize
- crop
- bucket
- flip
- color augmentation
- caption shuffle
- caption dropout
- tag dropout
- repeats

これらをtraining runのmetadataへ含める。

## 9. 成人向け・複数人物LoRAでの意味

relation-heavy datasetでは特に:
- actor/target tokenがdropされる
- partner identityがdropされる
- role tagがshuffleされる
と、意図したbinding学習を弱め得る。

逆に常に全captionを固定すると、scene/contextまでidentityへ絡む可能性もある。

したがってcaption augmentationは:
**identity / mutable attributes / scene contextを何に吸収させたいか**
を先に定義して設計する。

## 10. 昇格候補

1. Min-SNRはtraining loss weightingでありinference scheduler設定ではない。
2. timestep bias/samplingはtrainingで重視するnoise regimeを変える。
3. bucket/crop/resizeはtraining identity。
4. caption/tag dropoutはtraining-time conditioning regularizationで、無条件にgeneralizationを改善するとは限らない。
5. dataset preprocessing設定を再現metadataへ保存する。
