# BATCH_BC — 画像生成の基礎D: output metadata / hash / safetensors / Clip Skip / Textual Inversion — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`

## 1. 生成画像そのものと再現情報は別

完成画像だけ残しても、再生成できるとは限らない。

最低限残す:
- model/checkpoint identity
- hash when available
- Prompt / Negative
- seed
- width / height
- sampler / scheduler
- steps
- CFG
- VAE
- LoRA + weight
- Control
- img2img/inpaint/Hires
- runtime/version

AUTOMATIC1111系ではPNG text chunkへgeneration parametersを書き込むPNG Info機能がある。
JPEG/WebPでは実装によりEXIFへparametersを保存する経路もある。

重要:
metadata保存は「画像品質」の機能ではなく**再現性/evidence**の機能。

---

## 2. PNG / JPEG / WebP

### PNG
一般的な生成作業では、lossless保存とtext metadataを扱いやすいことから証拠画像に向く。

### JPEG
lossy compression。
閲覧・共有では軽いが、pixel-level比較や再編集のmasterには不向き。

### WebP
lossy/lossless双方の設定があり得る。
runtimeの保存設定を確認する。

Evidence用:
**元の生成PNGを保存し、SNS/共有用変換とは分ける。**

---

## 3. Model hash

filenameは変更できる。
同名fileでも中身が違うことがある。

hash:
file contentから計算するidentity signal。

実用:
- exact checkpoint確認
- LoRA版違い確認
- runtime再現
- source/evidence照合

ただし:
- UIのshort hash
- SHA256 full hash
- Hub revision/commit

を混同しない。

可能ならfull SHA256 + model source/revision。

---

## 4. safetensors

safetensors:
tensorを保存するためのformat。

Hugging Face documentation:
- pickleと違い安全性を重視したsimple tensor format
- fast/zero-copy design
- header metadataからdtype/shape等を確認可能

重要:
**safetensors = model architecture**
ではない。

同じ.safetensors拡張子でも:
- SDXL checkpoint
- LoRA
- VAE
- embedding-compatible weight
など中身の役割が違い得る。

file extensionだけでmodel familyを判定しない。

---

## 5. ckptとの実用差

.ckptはPyTorch pickle-based checkpointとして流通してきた。

safetensorsが好まれる大きな理由:
- arbitrary pickle code executionを避ける安全なtensor storage
- metadata parsingしやすい
- local model配布で広く普及

ただし:
safetensors化しただけで生成品質は上がらない。

---

## 6. Clip Skip

Clip Skip:
CLIP text encoderの最終層側を一部skipし、どのhidden stateをPrompt embeddingに使うか変更するruntime/model option。

Diffusers API example:
`clip_skip=1` = pre-final layer outputを使う。

重要:
- Prompt weightとは違う
- CFGとは違う
- 全model familyに意味がある設定ではない
- CLIPをその形で使わないmodelへ古いSD1.5 recipeをコピーしない

Noob/Anima等ではexact model author/runtime guidanceがない限り万能defaultにしない。

---

## 7. Textual Inversion / embedding

Textual Inversion:
text encoder embedding spaceへ新しいlearned token/“word”を追加し、少数画像のconceptをPromptから呼び出すpersonalization technique。

LoRAとの違い:

### Textual Inversion
主にlearned text embedding。

### LoRA
model/text-encoder等の対象layerへlow-rank weight updateを追加。

したがって:
embeddingとLoRAを同じ「追加モデル」という一分類で扱わない。

現代anime workflowではLoRAの方が中心でも、
古いNegative embeddingやconcept embeddingを読むための基礎知識として残す。

---

## 8. Negative embedding

Textual Inversion embeddingはPositiveだけでなく、
communityではNegative fieldから呼ぶembeddingとしても使われる。

しかし:
- embedding自体が何を学習したか
- target model familyとの互換性
- adult/unusual anatomy targetとのsemantic collision

を確認する。

「negative embeddingを入れれば品質が上がる」
を普遍則にしない。

---

## 9. Metadata hygiene

Evidence画像は:
1. original untouched PNG
2. runtime infotext/workflow
3. exact model hashes
4. sidecar experiment note if needed

を保持。

Discord/SNS/image editor/optimizerを通した画像はmetadataが失われる可能性があるため、
original evidenceを置換しない。

---

## Sources

- https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Features
- https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/master/modules/shared_options.py
- https://huggingface.co/docs/safetensors/index
- https://huggingface.co/docs/safetensors/en/metadata_parsing
- https://huggingface.co/docs/diffusers/api/pipelines/stable_diffusion/stable_diffusion_3
- https://huggingface.co/docs/diffusers/v0.17.0/en/training/text_inversion
