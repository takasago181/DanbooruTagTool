# ローカル成人向け画像生成 — 実ワークフロー型集 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
役割: **公開実例から抽出した「組み方の型」だけを残す**。  
一般診断は `ADULT_IMAGE_GENERATION_DECISION_TREE.md`、モデル設定は `PRACTICAL_GENERATION_NOOB_ANIMA.md` を参照。

## 基本原則

上級生成は巨大Prompt一本で解くより、
**意味・identity・geometry・分離・修正・仕上げを担当分けする**方が診断しやすい。

## 型1 — Native-first

構成:
`model native knowledge + 最小Prompt`

向く:
- modelがキャラ/概念を知っている
- 1人
- 単純scene

目的:
補助機能を足す前のbase能力確認。

## 型2 — Character LoRA

構成:
`base -> Character LoRA -> scene`

2人:
`base -> A -> B -> A+B`

使う時:
model nativeだけではidentity不足。

確認:
- identity
- outfit
- pose response
- background freedom
- relation response

## 型3 — Regional分離

構成:
`共通scene + region A + region B`

担当:
**誰の情報をどの領域へ入れるか**。

担当しない:
精密なpose/contact geometryそのもの。

目標:
最強分離ではなく、**混線を止められる最小強度**。
強過ぎる分離はinteractionを壊し得る。

## 型4 — Reference + Geometry Control

構成:
`Reference -> identity`
+
`pose/depth/line -> geometry`

重要:
Control元画像にはpose以外の髪・服・小物も残り得る。

不要情報が移る時は、他のweightを上げる前にControl元をmask/簡略化する。

## 型5 — Accepted baseからEdit

構成:
`良いbase -> mask -> inpaint/Edit -> 再監査`

向く:
- 表情
- 顔
- 一部衣装
- 局所anatomy
- 背景拡張

全体構造が既に正しいなら、txt2imgを最初からやり直さない。

## 型6 — 学習側へ戻る

推論で何度やっても:
- 同じpose
- 同じ背景
- 同じpartner
- 服を変えられない
- interactionだけ崩れる

ならdatasetを監査。

見る:
- soloしかないか
- joint exampleがあるか
- viewpointが偏っていないか
- partner/roleが固定されていないか
- background/styleがidentityへ絡んでいないか

## 型7 — 仕上げを別工程にする

`accepted base -> local repair -> high-resolution -> final audit`

base PNGを必ず残す。

Hires/upscale後だけ崩れた場合は第二工程の失敗として扱う。

## relation-heavy sceneの標準工程

1. **意味構造** — count / A-B / role / relation / camera / visibility
2. **base確認** — 小さな固定seed set
3. **identity** — native / LoRA / Reference
4. **geometry** — pose / depth / line
5. **分離** — 必要な時だけRegional
6. **relation再監査** — role / owner / contact / overlap / visibility
7. **局所修正** — inpaint / Edit / detailer
8. **仕上げ**
9. **最終再監査**

## Controlは1つの仕事から始める

| 手段 | 最初に任せる仕事 |
|---|---|
| Prompt | 意味 |
| Character LoRA | identity |
| Regional | 場所ごとの分離 |
| Reference | 見た目 |
| pose | 骨格 |
| depth | 前後関係 |
| line/edge | 輪郭・layout |
| inpaint/Edit | 局所再構築 |
| Hires/detailer | 仕上げ |

複数の軸が同時に変わったら、副作用として記録する。

## 根拠

詳細実例:
`../research/BATCH_AY_REAL_WORLD_ADULT_WORKFLOW_ARCHETYPES_20261002.md`

現在判定:
`CLAIM_REGISTRY.csv`
