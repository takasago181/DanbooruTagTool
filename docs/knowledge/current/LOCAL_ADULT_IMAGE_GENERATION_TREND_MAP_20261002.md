# 2026年秋 — ローカル成人向け画像生成 トレンド地図

Owner: Issue #44 `KNOWLEDGE:#44`  
Snapshot date: 2026-10-02  
Scope: 成人であることが明確な成人向けローカル画像生成。主対象は二次元/anime。  
注意: 「人気」と「性能の証明」は別。

## まず結論

2026年秋は**Anima一強でも、Illustrious終了でもない**。

二次元成人向けは現在、

### 1. 資産が強いSDXL陣営
- Illustrious
- WAI
- NoobAI
- Pony
- 大量の既存LoRA
- Forge / ComfyUIの成熟機能

### 2. 急成長中のAnima陣営
- Base / Aesthetic / Turbo
- tags + 自然言語
- 新しいanime知識
- Anima LoRA
- Regional
- reference
- Edit
- ローカルLLM/VLM

の二本立て。

一番大きな変化はcheckpoint名ではなく、
**「Prompt一発」から「Prompt + LoRA + reference + Regional + local repair」の工程型生成へ進んでいること**。

---

## 現在の勢力図

### 成熟している

**WAI / Illustrious**

今でも成人向け二次元の日常生成で強い。

理由:
- 既存LoRAが非常に多い
- SDXL系ツールが成熟
- Hires / Detailer / inpaintが使いやすい
- WAIは初手から見栄えが出やすい

既に大量のIllustrious LoRAを持っているなら、
Animaへ全移行する理由はまだない。

---

**NoobAI**

今でも「タグを理解して細かく指定する」方向で重要。

向く:
- Danbooru/e621を理解している
- キャラ/概念知識を使いたい
- Promptを細かく制御したい

弱点:
- 初心者にはWAIより面倒
- dedicated LoRA数はIllustrious/Ponyほど多くない

---

**Pony**

最新技術の中心ではなくなっても、
LoRA資産が非常に大きいので消えていない。

特に既存の特殊concept・stylized系資産を持つ人には現役。

---

## 一番伸びている: Anima

2026-10-02時点のCivitai ecosystem表示では:

- 32K+ Anima LoRA
- 283M+ generated images

比較表:
- Illustrious 199K+ LoRA
- Pony 101K+
- Anima 32K+
- NoobAI 8K+

数だけで品質は決められないが、
**Animaは既に「試験的な新モデル」の段階を抜けて大規模ecosystemになっている**。

### Animaで流行っている使い方

- Turboで高速試行
- Base/Aestheticで本番確認
- tags + 短い自然言語
- Character LoRA
- Style LoRA
- Regional
- reference image
- Edit LoRA
- Highres / Detailer
- ローカルLLMによるPrompt整理

---

## 今一番重要な流行: Promptを全部手で書かない

昔:
`Danbooruタグを大量に手入力`

今:
`意図 -> タグ/自然文の構造化 -> 生成 -> 失敗診断 -> Control`

特にAnimaで、

- LM Studio
- ローカルLLM
- VLM
- TIPO / DanTagGen
- Anima用Prompt helper

を前処理に使う流れが出ている。

成人向けではクラウドLLMの制限を避けるため、
**Prompt整理役までローカル化する**人もいる。

ただしLLMに全部任せるのではなく、
人数・役割・位置・relation・camera等を構造化させる使い方が実用的。

---

## 複数人物が今の主戦場

成人向けで現在かなり研究されているのは:

- 2人以上
- Character LoRA複数
- identity bleed
- role swap
- body-site ownership
- 接触
- overlap
- occlusion

単体の綺麗な一人絵より、
**「誰が誰なのかを保ったまま相互作用させる」方が難しい**。

そのためRegionalやreference系が伸びている。

---

## Regionalの流行

### Forge Neo
Regional PrompterがAnimaに対応。

現状:
- Latent: 対応
- Attention: 対応
- Region LoRA: 非対応

### ComfyUI
Anima専用Regional Conditioningが登場。

できる:
- regionごとにtext conditioning
- cross-attention分離
- self-attention分離

問題:
分離を強くし過ぎると、
人物同士が関係しなくなったり境界が硬くなる。

つまり流行は
**最大分離ではなく、必要最小限の分離**。

---

## Reference / Editが伸びている

2026年夏から目立つ。

### Anima IP-Adapter
参照画像からcharacter/styleを引く。

### Anima Edit LoRA
生成済み画像を基準に変更する。

### ReferenceLatent / Native reference系
「全部をTextから再生成」しない。

これは成人向け複数人物とも相性が良い考え方。

最初に:
- 人数
- 大きいpose
- interaction
- camera

が良い画像を作り、

後から:
- character
- style
- 局所detail

を合わせる。

---

## LoRAの流行も変わった

以前:
「キャラLoRAが似ていれば成功」

現在:
- unseen pose
- alternate outfit
- alternate background
- interaction
- pair coexistence
- style変更
- LoRA同士の干渉

まで評価する方向。

特にAnima communityでは
**multi-character用のjoint imageをdatasetに入れる**
という研究が増えている。

具体的な必要枚数はまだcommunity recipe扱い。

---

## 仕上げは一発生成から分離

現在のAIO workflowでは普通に:

1. T2I
2. I2I
3. inpaint
4. Highres
5. Face/Eye detailer
6. upscale

まで一つのworkflowに入る。

成人向けでは特に、

**relation成功**
と
**局所anatomy成功**

を別工程にした方が合理的。

---

## UIは二強

### Forge Neo
向く:
- 普段遣い
- WebUI形式
- 生成しながら調整
- Anima
- Regional
- 日本語情報が増えている

### ComfyUI
向く:
- 最新技術
- Reference
- Edit
- Regional
- 複雑なLoRA制御
- workflow再現
- 実験

今の流れは
**Forge Neoで日常生成、ComfyUIで高度な工程**
という住み分け。

---

## 中国圏でもAnimaが一般化

2026年6〜8月のBilibiliでは:

- Anima初心者教程
- LoRA導入
- Prompt plugin
- 自動反推
- all-in-one workflow
- LoRA管理

まで「初心者向けパッケージ」として出ている。

つまりAnimaは研究者だけのモデルではなくなった。

---

## 写実成人向けは別世界

二次元と混ぜない。

最近の写実ローカルでは:
- Chroma
- Z-Image
- FLUX.2 Klein系
- SDXL realism finetune

が話題。

ただし:
- Prompt方式
- LoRA互換性
- anatomy prior
- VRAM
- Control系

が二次元と違う。

DanbooruTagToolでは当面anime側を主軸で正しい。

---

## 今追う価値が高い順

### A — 今すぐ知識に入れる
- Anima
- WAI / Illustrious
- NoobAI
- Character/Style LoRA
- Regional
- Hires/inpaint/detailer
- hybrid tags + NL
- multi-character diagnosis

### B — 重点追跡
- local LLM/VLM Prompt structuring
- Anima IP-Adapter
- Anima Edit
- reference-driven character consistency
- multi-character LoRA training

### C — まだ実験扱い
- exact Regional recipes
- IP-Adapterを万能扱い
- community独自Anima派生を標準扱い
- very-high-resolution native generation
- “この一個が最強モデル”論

### D — 別研究lane
- Chroma
- Z-Image
- FLUX2
- photoreal adult

---

## #44での今後の研究優先

次に価値が高いのは:

1. Anima成人向け hybrid tag/NL controlled comparison
2. local LLM/VLMが作った構造Promptの精度
3. Character LoRA 2本のglobal vs Regional vs reference比較
4. Anima IP-Adapterのidentity preservation
5. Edit LoRAでrelationを壊さずidentityを置換できるか
6. WAI/Noob/Anima同一scene比較
7. Regional strengthとinteraction coherence
8. multi-character LoRA datasetのjoint-example効果
9. failure -> tool routingの実測
10. final Hires/detailerでrelationがどの程度維持されるか

Evidence:
`../research/BATCH_AX_LOCAL_ADULT_IMAGE_GENERATION_TRENDS_20261002.md`
