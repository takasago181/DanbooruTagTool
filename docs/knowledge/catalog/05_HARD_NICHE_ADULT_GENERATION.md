# 05 — Hard / Niche Adult Generation

## 範囲

成人・合意下のBDSM/sexual activity、または明確な成人ファンタジーの生成監査知識。

ここでは「性癖ジャンル名」でなく、**生成上必要な能力**へ分解する。

## Structural classes

- `UNARY_OBJECT_OR_STATE`
- `BODY_SITE_STATE`
- `SIMPLE_RELATION`
- `BINDING_RELATION`
- `RESTRAINT_TOPOLOGY`
- `DEVICE_RELATION`
- `MULTI_PENETRATION_OR_COUNT`
- `NONHUMAN_APPENDAGE_RELATION`
- `ANATOMY_CHANGING`
- `COMPOSITE_HARD`

## Risk dimensions

- exposure / rarity
- binding
- visibility
- geometry
- count
- Negative collision
- style/context leak
- evaluator blindness
- LoRA confound
- postprocess rescue

## 領域別の現在知識

### 挿入・body-site系
成功条件を分離:
`site / action / implement / count / ownership`

object存在だけで成功判定しない。

原本: `research/HARD_FETISH_ANAL_INSERTION_20260909.md`

### BDSM / restraint
拘束はrope/cuff存在ではなく、必要に応じて**接続topology**を見る。

`device / body-site / topology / pose / role`

原本: `research/HARD_FETISH_BDSM_RESTRAINT_20260909.md`

### machine / device
machineが画面にあるだけでは不足。

`device type / target / body-site / functional contact`

原本: `research/HARD_FETISH_MACHINE_DEVICE_20260909.md`

### tentacle / nonhuman appendage
`source / ownership / appendage role / target / relation / count`

hair/tail/clothing/external actor/machine appendageとの混線を疑う。

原本: `research/HARD_FETISH_TENTACLE_FANTASY_20260909.md`

### fluid / excretion
`material / source / destination / state / quantity`

fluid存在だけでrelation成功としない。

原本: `research/HARD_FETISH_FLUID_EXCRETION_20260909.md`

### rare / anatomy-changing
- one-seed failureでモデル未学習と断定しない
- common priorへのcollapseを疑う
- broad/frequent constituentはA/B候補
- generic anatomy/count Negativeは高リスク

原本: `research/HARD_FETISH_RARE_EXTREME_20260909.md`

## 複合hard case

必ずA_ONLY/B_ONLYを先に確認し、ABで初めて崩れるならcomposition/binding問題を優先。

原本: `research/HARD_FETISH_COMPOSITE_FAILURE_MATRIX_20260909.md`

## モデル差

WAI17 / NoobAI / Animaを同一扱いしない。

原本: `research/HARD_FETISH_MODEL_FAMILY_MATRIX_20260909.md`

## 重要な評価原則

- presence != relation
- exact body-site/countはfirst-class predicate
- rare tagがTagger vocabulary外ならmachine failure扱いしない
- LoRA-assisted / Control-assisted / postprocess-rescuedは別レーン
- anatomy-changing caseはNegative ON/OFFを分離

## 出典原本

`research/HARD_FETISH_SOURCES_20260909.md`