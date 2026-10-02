# ローカル成人向け画像生成 — 実ワークフロー Playbook 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Purpose: 実際に公開されている2026年のworkflowを、成人向け二次元生成で再利用できる型に変換する。  
Evidence authority: Claim Registry + BATCH_AY

## 結論

今の上級workflowは、

**Promptを上手く書く競技**
ではなく、

**identity / geometry / locality / repair / finishingを何に担当させるか決める設計**
に近い。

---

# 1. 一番簡単: Native-first

使う:
- model native character/concept
- tags
- concise NL

流れ:
`model -> prompt -> sampler`

向く:
- モデルがキャラを知っている
- 1人
- simple interaction

先にこれを試す理由:
LoRAやControlを追加すると、失敗原因が増える。

---

# 2. Character LoRAを使う

流れ:

`base -> Character LoRA A -> test`

2人なら:

`base -> A-only -> B-only -> A+B`

ここで混ざったら、
Prompt追加の前に「LoRA同士が競合した」と切り分ける。

評価:
- identity A
- identity B
- outfit
- style
- pose response
- relation response

---

# 3. 複数人物が混ざる: Regional

使う:
- Forge Couple
- Regional Prompter
- Anima Regional Conditioning
- Regional ControlNet
- regional mask nodes

担当:
**誰の情報をどの領域へ入れるか**

担当しない:
**精密poseやbody-site geometryそのもの**

典型構造:

`common scene`
+ `region A identity`
+ `region B identity`

注意:
分離を強くすると、
interactionも切れる。

目標:
**混線が止まる最小の分離**。

---

# 4. 顔・キャラを参照画像で維持: IP-Adapter / Reference

向く:
- OC
- 10〜20枚程度の短期シリーズ
- LoRA学習をしたくない
- reference imageがある

最近のAnima実測では、
顔・髪・目・大きな服特徴は比較的運べても、
小物やほくろ等は落ちる例がある。

つまり:

`IDENTITY = feature vector`

として採点する。

## 2人で使う注意

参照していない相手の情報が薄いと、
reference側の特徴で空欄を埋めることがある。

対策順:
1. 相手のhair/eyes/outfitを明記
2. reference strength比較
3. Regional/localization
4. 必要なら別reference/edit

---

# 5. 顔はReference、poseはControl

現在かなり重要な型。

`reference image -> identity`
`lineart/OpenPose/depth -> geometry`

ただしControl画像にはpose以外の情報も入っている。

例:
lineartに
- 髪型
- リボン
- バッグ
- 衣装線
が残っていれば、それも生成へ運ばれることがある。

### 原則

**Controlに不要な情報を消す。**

顔をreference側へ任せるなら、
pose lineartの頭部を消す/弱める等を比較する。

---

# 6. 構図がもう正しい: Edit / Inpaintへ

global sceneが合っているなら、
毎回T2Iをやり直さない。

流れ:

`accepted base`
-> `mask`
-> `Edit LoRA / inpaint`
-> `relation re-audit`

向く:
- 表情だけ
- 顔identityだけ
- 一部衣装
- 背景拡張
- 局所anatomy

重要:
Edit後もrelation/contactを再確認する。

---

# 7. 2人LoRAが何度やっても駄目: 学習側へ戻る

inferenceだけで解決しない場合:

datasetを確認。

見る:
- solo画像しかない?
- interaction画像がある?
- 同じpartnerばかり?
- 同じroleばかり?
- stitched side-by-sideばかり?
- 背景固定?
- pose固定?

最近のAnima communityでは、
**joint examplesをtrainingへ入れる**
研究がかなり増えている。

ただし「何枚で十分」はまだ正本にしない。

---

# 8. LoRA作成自体も自動化され始めた

現在の公開例:

`video`
-> `shot split`
-> `YOLO + CCIPでcharacter抽出`
-> `duplicate除去`
-> `WD tag + local VLM caption`
-> `human audit`
-> `LoRA train`

つまり今後は
training parameterだけでなく、
**dataset extraction pipeline**も先生役が理解する必要がある。

---

# 9. Hires / upscale

Animaでは2026年も、
second-pass/latent upscaleでartifact報告がある。

だから:

### A
accepted base PNGを保存

### B
pixel upscale

### C
latent/img2img second pass

### D
tiled / multidiffusion

を分けて比べる。

Hires後に壊れたら、
Prompt能力の失敗に戻さない。

---

# 10. 成人向けrelation-heavy sceneの実用工程

### Stage 1 — semantic skeleton
- count
- A/B identity
- role
- relation
- camera
- visibility

### Stage 2 — base check
4 seed程度。

### Stage 3 — identity
native / Character LoRA / reference。

### Stage 4 — geometry
pose / depth / line。

### Stage 5 — separation
必要ならRegional。

### Stage 6 — relation audit
- role
- body-site owner
- contact
- overlap
- visibility

### Stage 7 — local repair
inpaint/Edit/detailer。

### Stage 8 — finishing
Hires/upscale。

### Stage 9 — final audit
HiresやEditでrelationが変わっていないか確認。

---

# 11. 失敗 → 次の道具

| 失敗 | 次に見る |
|---|---|
| conceptがない | tag/trigger/model exposure |
| characterが違う | native/LoRA/reference |
| 2人が混ざる | A/B isolate -> Regional |
| roleが逆 | Prompt simplification -> Regional/reference |
| pose違い | pose/line/depth |
| hidden/off-frame | camera/depth/aspect |
| referenceで双子化 | other subject description -> localization |
| Controlの髪型まで移る | control source preprocessing |
| anatomyだけ | inpaint/detailer |
| Hires後だけ崩れる | second pass |
| LoRAが同じ構図を強制 | dataset audit |
| interactionだけ崩れる | coexistence vs interaction training/control |

---

# 12. 覚えるべき考え方

### 画像生成能力
「一発で完成するか」ではない。

### 実用能力
「失敗した時に、どの軸をどの道具で直すか分かるか」。

現在の上級workflowはこの方向へ進んでいる。

Full case study:
`../research/BATCH_AY_REAL_WORLD_ADULT_WORKFLOW_ARCHETYPES_20261002.md`
