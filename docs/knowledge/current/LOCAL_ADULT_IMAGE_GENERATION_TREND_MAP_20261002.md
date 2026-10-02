# 2026年秋 — ローカル成人向け画像生成 動向メモ

Owner: Issue #44 `KNOWLEDGE:#44`  
基準日: 2026-10-02  
対象: 成人であることが明確な成人向けローカル画像生成。主に二次元。  
役割: **現在のecosystem動向だけを記録する**。実際の操作手順は別currentガイドへ置く。

## 結論

2026年秋は、既存資産が厚いSDXL/Illustrious系と、急成長したAnima系が並行している。

「Anima一強」「Illustrious終了」のような単純な置き換えではない。

大きな変化は、**Prompt一発で全部解くより、identity・geometry・Regional・Reference・Edit・仕上げを分担する工程型生成が増えていること**。

## 1. 成熟したSDXL / Illustrious系

現在も重要:
- Illustrious
- WAI
- NoobAI
- Pony
- 既存Character / Style LoRA
- Forge / ComfyUIの成熟した周辺機能

強みはモデル単体より、**既存資産と運用ノウハウの厚さ**。

NoobAIはタグ中心の指定と知識面で引き続き重要。
WAIは比較・履歴レーンとして残る。

## 2. Animaは大規模ecosystemへ成長

2026-10-02時点のCivitai snapshotでは:
- Anima: 32K+ LoRA
- Anima generated images: 283M+
- Illustrious: 199K+ LoRA
- Pony: 101K+ LoRA
- NoobAI: 8K+ LoRA

これは**品質ランキングではなく、プラットフォーム内の資産量・利用規模の指標**。

Animaでは:
- Base / Aesthetic / Turbo
- Character / Style LoRA
- Regional
- Reference
- Edit
- Control
など周辺資産が増えている。

## 3. 複数人物が主要な研究対象

現在の難所:
- identity bleed
- attribute swap
- role swap
- 身体部位の所有者
- 接触
- overlap
- occlusion
- 複数Character LoRA干渉

1人を綺麗に出す能力と、複数人物を関係させる能力が別として扱われるようになっている。

## 4. Regionalは一般的な上級手段へ

Forge Neo / ComfyUI双方で、人物ごとの条件分離を行う手段が増えている。

重要な知見:
- 分離を強くすれば常に良いわけではない
- 強過ぎる分離はinteractionや一体感を壊し得る
- 「必要な分離を満たす最弱設定」という考え方が重要

具体的操作はPlaybook / Decision Treeへ。

## 5. Reference / Edit系が伸びている

目立つ流れ:
- IP-Adapter系
- Reference conditioning
- Edit LoRA / masked edit
- accepted baseからの局所修正

つまり「全部をTextから毎回再生成」せず、良い構造を残してidentityや局所だけ直す方向。

## 6. LoRA評価が厳しくなっている

以前:
「キャラに似れば成功」

現在:
- 未学習pose
- 別衣装
- 別背景
- 別style
- 複数人物共存
- interaction
- 他LoRAとの干渉

まで見る傾向が強い。

dataset作成も、画像枚数より**何が変化して何が固定されているか**を重視する方向。

## 7. Dataset自動化が進行

公開例では:
`動画・画像収集 -> shot分割 -> キャラ抽出 -> 重複除去 -> 自動tag/caption -> 人間監査 -> LoRA学習`

のようなpipelineが増えている。

ただし自動処理だけでidentity/nuisanceの正しさを保証しない。

## 8. ローカルLLM / VLMによるPrompt前処理

Anima周辺では:
- ローカルLLM
- VLM
- Prompt helper
を使い、人間の意図を構造化してから画像モデルへ渡す例が増えている。

現時点では**流行・workflow候補**であり、「LLMが書いたPromptの方が常に強い」という結論ではない。

## 9. UIはForge NeoとComfyUIの役割分担

傾向:
- Forge Neo: 日常的な対話型生成
- ComfyUI: Reference / Edit / Regional / 複雑な制御と再現可能なgraph

どちらか一方が常に優れるとは扱わない。

## 10. 仕上げは別工程化

現在の高度workflowでは:
- base生成
- 局所修正
- detailer
- 高解像度化
- upscale
を分離することが一般的。

base能力と最終仕上がりを同じ指標にしない。

## 11. 写実成人向けは別研究lane

Chroma / Z-Image / FLUX系など、写実側は別ecosystem。

二次元の:
- Prompt
- LoRA互換
- Control
- anatomy prior
をそのまま転用しない。

DanbooruTagToolの知識班では二次元を主軸とし、写実は別laneで扱う。

## 12. 追跡優先度

### 継続追跡
- Anima公式family
- NoobAI / Illustrious
- Character / Style LoRA
- Regional
- Reference / Edit
- 複数人物
- LoRA dataset設計

### 実験扱いを維持
- 万能Regional数値
- IP-Adapter万能論
- community派生モデルを標準化
- 一つの「最強モデル」論
- 高解像度化の万能設定

根拠:
`../research/BATCH_AX_LOCAL_ADULT_IMAGE_GENERATION_TRENDS_20261002.md`
