# NoobAI / Anima 実践ガイド

Owner: Issue #44 `KNOWLEDGE:#44`  
役割: **モデル固有の設定・Prompt傾向・使い分けだけを扱う**  
一般的な生成原理: `IMAGE_GENERATION_FOUNDATIONS_JA.md`  
失敗診断: `ADULT_IMAGE_GENERATION_DECISION_TREE.md`  
現在判定: `CLAIM_REGISTRY.csv`

## 1. 最初にどれを使うか

### NoobAI XL 1.1 EPSから始める
向く状況:
- Danbooru/e621系タグで表現しやすい
- タグ中心で試したい
- SDXL/Illustrious系のLoRA・周辺資産を試したい
- Forge Neoで標準的に学習したい

現在のStage10第一レーン。

### Animaを比較する
向く状況:
- 複数人物
- 属性の持ち主が混ざる
- 関係性を短い自然文でも表したい
- Regional / Reference / Edit系も含めて試したい

ただし、**タグのみより自然文併用が普遍的に強いとは未確定（HOLD）**。
タグだけで曖昧なsceneでは、短く事実的な自然文を比較候補にする。

### WAI Illustrious v17
現在は比較・履歴用。
過去のローカル検証は捨てないが、第一レーンではない。

## 2. NoobAI XL 1.1 EPS

### 公式baseline
- サンプラー（Sampler）: `Euler a`
- ステップ数（Steps）: `25–30`
- CFG: `5–6`
- 解像度: SDXLの約1MP帯を基準

縦長の開始候補:
- `832×1216`
- `896×1152`
- `768×1344`

### Promptの基準順
`人数 -> キャラ -> 作品 -> artist -> 目標概念 -> 一般タグ -> その他`

これはNoobAIの基準であり、全モデル共通文法ではない。

### 成人向けでの注意
公式例に安全寄りNegativeが含まれていても、成人向け能力検証の中立baselineとしてそのまま使わない。

最初は:
1. 目標sceneの最小構造
2. 必要な可視性・構図
3. 必要ならキャラ
4. style/backgroundは後

難しい人数・役割・身体部位・relationの成功率はまだHOLD。

### LoRA
Illustrious系LoRAは**候補**にはなるが、互換性を保証しない。

比較:
`base -> LoRA単体 -> weight比較 -> 複数LoRA`

いきなり複数積まない。

## 3. NoobAI XL V-Pred 1.0

EPSとは別モデルprofile。

### baseline
- Sampler: `Euler`
- Steps: `28–35`
- CFG: `4–5`
- V-Pred対応runtimeが必要

### 注意
- EPSの設定をそのまま移さない
- EPSとV-Predの結果を一つのモデルとして集計しない
- 1枚の色・コントラスト差から優劣を決めない

実用差は今後の比較対象。

## 4. Animaのprofile

正確なfile/hashは `VERSION_FRESHNESS_LEDGER.csv` を正本にする。

### Base
役割:
- 柔軟性・多様性
- 制御比較
- 公式LoRA学習base

通常生成の開始目安:
- Steps `30–50`
- CFG `4–5`

### Aesthetic
役割:
- 一貫性・標準的な見栄えを優先する比較
- quality/score系の扱いがBaseと同じとは限らない

### Turbo
役割:
- 高速なPrompt/seed探索

開始目安:
- CFG `1`
- Steps `8–12`

CFG1系では通常のNegative運用をそのまま移植しない。
Base/Aestheticとは別profileとして評価する。

## 5. AnimaのPrompt

公式系統ではタグと自然文の混在が可能。

実践上は次を分けて比較する。

### タグ中心
向く:
- 既知キャラ
- 外見
- artist/style
- atomicな概念

### 短い自然文を追加
比較価値が高い:
- 誰が誰に何をしているか
- 属性の持ち主
- 相対位置
- 関係性
- 視認条件

ただし**長文にすれば強い**とは扱わない。
情報量が増えるほど構造負荷も増える。

### 複数人物
最低限:
- Aのidentity
- Bのidentity
- 区別に必要な外見
- count
- relation
- camera/visibility

タグの距離だけで「この属性はA」と保証しない。

## 6. Animaでの複数人物・LoRA

能力を段階で分ける。

1. 1人でidentityが出る
2. 2人が同時に存在できる
3. 単純なinteractionが成立する
4. 強いrelationでもidentity/roleが維持される

1が成功しても4の成功を意味しない。

複数Character LoRAでは:
`base -> A -> B -> A+B`

混ざる場合:
- weight
- source dataset
- Regional
- Reference
- localized adapter
を順に疑う。

詳細診断はDecision Treeへ。

## 7. AnimaのRegional / Reference / Edit

Anima周辺には現在:
- Regional conditioning
- Region/LLLite Control系
- IP-Adapter系
- Edit/Reference系
など複数の補助手段がある。

役割を分ける。

| 手段 | 主担当 |
|---|---|
| Regional | 情報を場所ごとに分離 |
| Reference / IP-Adapter | 見た目・identityの参照 |
| pose / line / depth | 構造・geometry |
| Edit / inpaint | 既に良い画像の局所修正 |
| Hires / detailer | 仕上げ |

**1つの道具に全部を担当させない。**

Control元画像に髪型・服・小物など不要な情報が残っている場合、その情報も移ることがある。強度を上げる前にControl元を整理する。

## 8. Negativeのモデル境界

Negativeは生成後の消しゴムではなく条件付け。

モデル・profile・sceneによって効き方が変わる。

成人向けや通常と異なる人数・身体構造を扱う時は:
- broad anatomy Negative
- safety/rating Negative
が目標自体を弱めないかA/Bする。

Anima TurboのCFG1と、NoobAI EPSの通常CFGを同じNegative運用にしない。

## 9. Hires / img2img / 仕上げ

モデルの素の成功と、仕上げ後の成功を分ける。

保存順:
1. base PNG
2. Hires/高解像度版
3. inpaint/Edit版
4. 最終版

Animaはsecond-passやlatent upscaleで崩れる報告があり、万能な数値レシピは固定しない。

「baseは正しいが仕上げで壊れた」なら、Promptを作り直す前に第二passを疑う。

## 10. 比較実験の最低ルール

モデル差を比べる時:
- scene定義を固定
- seed setを固定
- 解像度を同等条件にする
- 各モデルの公式profileを使う
- LoRA/Controlなしのbase比較を先にする
- その後に補助手段を足す

Sampler/Steps/CFGを全部同時に変えた比較から、原因を1つに断定しない。

## 11. 現在確定していないもの

- NoobAIの難しいrelation/body-site/countの安定上限
- Noob EPSとV-Predの実用的な優劣
- Animaのtag-only vs 短い自然文併用の普遍的勝敗
- Anima Base/Aesthetic/Turboの難しいsceneでの成功率差
- 複数Character LoRA + interactionの安定性
- Anima finishingの万能設定

数値を断定する前に `CLAIM_REGISTRY.csv` / HOLDを確認する。

## 12. 根拠

モデル・runtimeの現在情報:
`VERSION_FRESHNESS_LEDGER.csv`

主な研究:
- `../research/BATCH_L_NOOB_ANIMA_PRACTICAL_GENERATION_DEEP_DIVE_20260913.md`
- `../research/BATCH_N_CURRENT_MODEL_PROMPT_RUNTIME_REFRESH_20261002.md`
- `../research/BATCH_O_COMMUNITY_PRACTICE_HARVEST_20261002.md`
- `../research/BATCH_P_COMMUNITY_TAG_NEGATIVE_RUNTIME_20261002.md`
- `../research/BATCH_AG_ANIMA_RELATION_STRESS_COMMUNITY_20261002.md`
- `../research/BATCH_AY_REAL_WORLD_ADULT_WORKFLOW_ARCHETYPES_20261002.md`
