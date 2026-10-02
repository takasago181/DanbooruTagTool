# 成人向け画像生成 — 実用診断フロー（Decision Tree）

Owner: Issue #44 `KNOWLEDGE:#44`  
対象: 成人であることが明確な、合意的・成人ファンタジーの画像生成  
役割: **失敗の種類を切り分け、次の最小操作を決める**  
判定の正本: `CLAIM_REGISTRY.csv`

## 最初にやること

生成が崩れた時、最初にタグを増やさない。

`再現条件確認 -> 主失敗を1つ選ぶ -> 最小Prompt -> 固定4 seed -> 1変数A/B -> 必要なら補助機能`

同じ構造失敗が4 seed中3以上で続き、簡潔な表現を2系統試しても直らない場合は、学習効率上の目安として次の補助手段を比較する。

これは「Promptだけでは絶対不可能」という証明ではない。

## 0. 再現条件

最低限:
- モデル / checkpoint / profile
- seed
- 解像度 / 縦横比
- Sampler / Scheduler
- Steps / CFG
- Positive / Negative
- LoRA名とweight
- Regional / ControlNet / Reference
- Hires / img2img / inpaint
- runtime/version

元PNGやComfyUI workflowがあれば優先。

## 1. 主失敗を決める

| 症状 | 分類 | 最初に見るもの |
|---|---|---|
| 概念自体が出ない | 概念未生成 | tag / trigger / model exposure |
| 人数が違う | 人数失敗 | count / framing / aspect |
| AとBの特徴が混ざる | 属性混線 | A単体 / B単体 / LoRA |
| 役割が逆 | 役割交換 | subject binding |
| 身体部位の持ち主が逆 | 所有者失敗 | binding / Regional |
| 接触・関係が成立しない | relation失敗 | relation表現 / pose |
| poseが違う | geometry失敗 | pose / depth / Reference |
| 前後関係が違う | 奥行き失敗 | depth / camera |
| 画面外・隠れる | 可視性失敗 | crop / camera / overlap |
| 手足など局所だけ崩れる | 局所解剖 | inpaint / detailer |
| LoRA追加時だけ崩れる | LoRA干渉 | 1本ずつ追加 |
| Regionalで境界が出る | 分離過剰 | 分離強度 |
| Hires後だけ崩れる | 第二工程崩れ | Hires設定 |

## 2. 概念が出ない

### 単体でも出ない
確認:
- canonical tag
- 旧表記 / historical spelling
- model-specific trigger
- training cutoff

current Danbooruにタグがあることと、モデルが学習していることは別。

### 単体では出る
複数人物時だけ消えるなら、語彙不足より:
- binding
- 情報量
- 場所の分離
を疑う。

## 3. 人数が違う

style/backgroundを一度外し:
- 人数
- subject identity
- framing
だけにする。

同じ人数失敗が4 seed中3以上なら:
- 縦横比
- pose / Reference
- Regional / layout control
を比較する。

## 4. 人物特徴が混ざる

順番:
1. Aだけ
2. Bだけ
3. A+B、LoRAなし
4. LoRA Aだけ
5. LoRA Bだけ
6. A+B LoRA
7. weight比較
8. Regional / Reference / localized adapter

**どの段階から混ざったか**が診断結果。

## 5. 役割・身体部位の持ち主が逆

まずA/Bのidentityを安定させる。

次に残す:
- 役割
- target
- relation
- 可視性

Animaではタグのみと短い自然文併用を比較してよいが、普遍的な優劣はHOLD。

同じ交換が4 seed中3以上ならRegional/Referenceを比較する。

## 6. pose・接触形状が違う

語彙よりgeometry問題を疑う。

優先:
- pose
- depth
- line / edge
- Reference

identity tagやquality tagを増やすだけで解こうとしない。

## 7. 見えない

「生成されていない」と即断しない。

確認:
- camera distance
- crop
- viewpoint
- overlap
- occlusion
- depth order

**存在しているが見えていない**を別失敗として扱う。

## 8. Negativeを入れたら弱くなった

Negativeは中立な掃除ではない。

A/B:
- A: 目標を抑制し得るNegativeなし
- B: 比較したいNegativeあり

他条件は固定。

見る:
- 目標概念
- relation
- count
- visibility
- anatomy
- composition
- censor / watermark / text

成人向け能力検証では安全寄りNegativeを自動的に中立baselineとみなさない。

## 9. LoRAを入れると壊れる

`base -> A -> B -> A+B`

それでも必要なら:
- weight比較
- 時間方向の適用
- mask / localization
- Regional
- dataset監査

同じ背景・pose・styleを強制するならdataset entanglementも疑う。

## 10. Regionalで分離したがinteractionが壊れる

2軸で採点する。

**分離**
- identity leak
- attribute swap

**一体感**
- 接触
- overlap
- 境界
- relation

目標は最強設定ではなく、**必要な分離を満たす最弱設定**。

## 11. 局所anatomyだけ崩れた

人数・identity・役割・relation・可視性・大きいposeが通っているなら、全体を再生成しない。

inpaint / detailerで局所修正。

## 12. Hires後だけ崩れた

base PNGを残す。

Hiresは第二生成工程として別診断。

見る:
- denoise
- Hires側Sampler / Scheduler
- Steps / CFG
- Hires Prompt / Negative
- LoRA / Control再適用
- checkpoint

base成功とHires成功は別の証拠。

## 13. Promptだけから補助機能へ切り替える目安

Promptを続ける:
- seedごとに失敗種類が変わる
- 意味自体は通っている
- 最小Prompt未実施
- model-native表現未実施

補助機能を比較する:
- 単体概念は出る
- 主失敗が明確
- 最小Prompt済み
- 表現2系統済み
- 4 seed中3以上で同じ構造失敗

対応:
- identity / binding -> Regional / Reference
- pose -> pose control
- 前後・重なり -> depth
- 輪郭・layout -> line / edge
- 局所anatomy -> inpaint / detailer

## 14. 最短の返答型

失敗画像を診断する時は:

1. 主失敗は何か
2. 既に成功している部分は何か
3. 次に変える1変数
4. 同じseed setで比較
5. 同じ構造失敗が続けば次のControl
6. Promptだけの能力と補助後の能力を分ける

モデル固有注意は:
`PRACTICAL_GENERATION_NOOB_ANIMA.md`

根拠:
- `../research/BATCH_AW_ADULT_DIAGNOSTIC_ESCALATION_AND_MODEL_GAPS_20261002.md`
- `../research/BATCH_AQ_REGIONAL_LEARNING_AND_REPRODUCIBILITY_20261002.md`
- `../research/BATCH_AV_DATASET_STYLE_BIAS_AND_PREPROCESSING_20261002.md`
