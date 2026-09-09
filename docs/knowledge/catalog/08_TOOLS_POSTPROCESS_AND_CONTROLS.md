# 08 — Tools / Postprocess / Controls

## Forge Neo

WAI17作者推奨UI。現在のユーザー環境とも一致。

ただしWebUI/parser機能とmodel semanticsを分ける。

例:
- BREAK / AND / weighting syntax = tool/parser layer
- Special理解 = model layer

## Hires fix

高解像化だけではなくsecond generation passとして扱う。

WAI17作者はlimb correction効果を言及しているため:
- base image
- Hires result
を別 evidence として保存。

Hiresで直った = base Prompt成功、ではない。

## ADetailer

automatic detection -> mask -> inpaint の後処理。

- final appearance改善には有用
- semantic/PROMPT-only capability監査ではOFFをbaseline
- ADetailer Prompt/Negativeが別なら特にconfound

## img2img / inpaint

修正レーン。base generation能力とは分離。

`POSTPROCESS_RESCUE` ラベルで記録可能。

## LoRA

LoRAはconceptだけを追加するとは限らない。

持ち込み得るもの:
- style
- pose
- framing
- background/context
- anatomy prior
- trigger bundle

複数LoRAではinterference / identity loss / leakageの可能性。

監査時は:
- base without LoRA
- single LoRA
- multiple LoRA
を分ける。

## ControlNet / DWPose

pose/depth/edge等のspatial control。

Prompt-onlyで成立しないgeometryを補助できるが、**concept理解の証明ではない**。

## Forge Couple / regional prompting

actor/resource separationに有用。

ただしcheckpointが理解していないcompositionを魔法のように理解させるものではない。

`ASSISTED_ONLY` を別状態にする。

## Dynamic Prompts

有望用途:
- support候補のcontrolled enumeration
- A/B variant生成
- 1変数ずつの組合せ試験

避ける:
- 無制限ランダム化
- seed/variant identityを失う運用

## metadata / reproducibility

保存推奨:
- checkpoint exact name/hash
- tool/build
- sampler/scheduler
- steps/CFG/resolution
- seed
- actual positive/negative
- LoRA + weight
- Hires/img2img/ADetailer/control state
- PNG metadata

## 原本

- `research/TOSHIAKI_WIKI_PRACTICAL_FINDINGS_20260909.md`
- `research/WAI17_LOCAL_ENV_TEST_BASELINE_20260909.md`
- `GENERATION_KNOWLEDGE_CORPUS.md`
- official Forge/ADetailer/Control sources in source registry