# BATCH_AW — 成人向け生成の診断・Prompt打ち切り基準・モデル別未実証領域 — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Branch: `knowledge/generation-corpus`  
Scope: clearly adult, consensual/adult-fantasy image generation; NoobAI XL 1.1 EPS / Anima / ComfyUI / Forge Neo  
Mode: pedagogy + controlled-test design + current-source refresh

## 0. 今回の目的

「Promptを足し続ければいつか直る」という教え方をやめる。

先生役は次を区別する。

1. 単語・triggerが通っていない
2. 単体では通るが複数人物でbindingが壊れる
3. 人数・位置・poseなどgeometryが壊れる
4. relationは合っているが局所anatomyだけ壊れる
5. LoRAを追加した時だけ壊れる
6. Regionalで分離した結果、interaction/coherenceが壊れる
7. Hires/detailerで後段だけ壊れる
8. Negative Promptが目標概念まで抑制している

そして「どこまでPrompt-onlyを試し、どこからControl/Regional/inpaintへ上げるか」を再現可能なルールにする。

---

## 1. NoobAI EPSの成人向け検証で最初に外して考えるもの

Official source:
https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md

NoobAI XL 1.1 EPS の公式推奨例は、

- positive側に `safe`
- Negative側に `nsfw`

を含む。

これは一般生成の作者推奨baselineとしては有効だが、成人向け能力を測る**中立baselineではない**。

成人向けcontrolled testでこの状態を固定したまま失敗すると、

- checkpointがrelationを理解できない
- safety/rating conditioningが目標を抑制した

のどちらかを切り分けられない。

### 実験ルール

成人向け検証では同じseed/settingsで少なくとも次を分ける。

A. safety/rating suppressionを目標に掛けないbaseline  
B. 比較したいNegativeだけを追加したcondition

「Negativeを全部OFFにするのが常に正しい」という主張ではない。
**Negative状態を実験変数として記録する**という意味である。

Promoted:
- K-MODEL-NOOB-009
- K-PRACTICAL-034

---

## 2. Animaの公式prompt surfaceと、そこから言えないこと

Official source:
https://huggingface.co/circlestone-labs/Anima

Animaは公式に、

- Danbooru-style tags
- natural language
- mixed prompting
- safety tags: safe / sensitive / nsfw / explicit

をprompt surfaceとして説明している。

また複数キャラクターでは、名前だけでなく基本外見も書くことを作者が推奨している。

ただしこれは、

- actor/target
- body-site ownership
- exact relation
- interaction-heavy adult topology

が高信頼で解けるというbenchmarkではない。

### 結論

Animaの公式説明から言えるのは、
「表現経路を持っている」ことまで。

relation-heavy adult reliabilityはcontrolled image testが必要。

Promoted:
- K-MODEL-ANIMA-018

---

## 3. 現在のcommunity evidence

Recent sources:

- https://www.reddit.com/r/comfyui/comments/1ws23ur/multiple_characters_in_one_single_generated_image/
- https://www.reddit.com/r/StableDiffusion/comments/1wr9r66/anima_two_characters_work_fine_individually_but/
- https://www.reddit.com/r/StableDiffusion/comments/1tcf5y6/multiple_characters_using_loras_with_anima_model/
- https://huggingface.co/circlestone-labs/Anima/discussions/202
- https://huggingface.co/circlestone-labs/Anima/discussions/93

共通して観測される症状は、

- A/B単体では出る
- 同時にすると髪色・目・衣装などが交換される
- 一方のidentityが他方を上書きする
- interaction時に悪化する
- area/regionalで分離するとidentityは改善してもoverlap部の顔・手・接触が壊れることがある

というもの。

これは「Animaは複数人物が駄目」という意味ではない。
逆に「natural languageだけで必ず解ける」という意味でもない。

**presenceとbindingを別採点する必要がある**というevidenceとして扱う。

Promoted:
- K-COMM-ANIMA-030 (CANDIDATE)

---

## 4. 評価軸を“総合的に良い/悪い”から分解する根拠

Research:

- T2I-CompBench: https://arxiv.org/abs/2307.06350
- GenEval: https://arxiv.org/abs/2310.11513

これらのcompositional T2I benchmarkは、
一枚のholistic scoreだけでなく、

- attribute binding
- object relationship
- spatial relation
- count
- color/attribute association

を分離して評価する。

成人向けrelation-heavy sceneでも同じ考え方を使う。

最低限のpredicate vector:

- COUNT
- IDENTITY_A
- IDENTITY_B
- ROLE_OWNER
- BODY_SITE_OWNER
- RELATION
- VISIBILITY
- GEOMETRY
- LOCAL_ANATOMY
- STYLE/CONTEXT_LEAK

Promoted:
- K-EVAL-021

---

## 5. Prompt-onlyを諦めるための“運用上の閾値”

これは科学的な普遍法則ではなく、#44で使う**project teaching heuristic**。

### 5.1 まず4-seed diagnostic set

同じcheckpoint/profile/settingsで固定seedを4個用意する。

1枚だけでは、
- 偶然の成功
- 偶然の失敗
- 構図差
を区別しにくい。

### 5.2 Prompt representationは最大2系統まで

例:

- model-native tag/minimal form
- concise natural-language/hybrid form

一度に10種類のPromptを書き換えない。

### 5.3 Escalation gate

以下を満たしたら、通常はPrompt-onlyの言い換えを延々と続けない。

- target conceptは単体では出る
- count/identityの基本情報は正しい
- 2種類の簡潔な表現を試した
- 同じprimary structural failureが4 seed中3以上で再発

この時点で、

- role/body-site binding -> regional/reference
- pose/contact geometry -> pose/depth/line
- visibility -> camera/aspect/depth
- localized anatomy -> inpaint/detailer

へ上げる。

重要:
このgateは「Prompt-onlyでは不可能」の証明ではない。
**学習効率上、次のmechanismを試す時点**である。

Promoted:
- K-PRACTICAL-033

---

## 6. 症状別decision tree

### A. そもそも出ない

1. 単体concept test
2. canonical / historical / model-specific trigger確認
3. model training-era exposure確認
4. minimal prompt
5. それでも出ない -> vocabulary/model-knowledge問題としてHOLD

ControlNetを先に足さない。

### B. 人数が違う

1. sceneをcount中心まで削る
2. aspect ratio / framing確認
3. 4-seedでcountのみ採点
4. 3/4以上で失敗 -> pose/reference/regionなど構図controlへ

style tagを増やして解決しない。

### C. 人物が混線する

1. A-only
2. B-only
3. A+B without LoRA if native
4. LoRA A only
5. LoRA B only
6. A+B global
7. regional/reference/localized adapter

混線が始まった段階を特定する。

### D. role / body-siteがswapする

1. stable subject description
2. relation以外を削る
3. concise NL/hybridを比較
4. 4-seed判定
5. persistentならregional/reference
6. interactionが壊れたらisolationを弱める

### E. pose/contactが違う

relation語を増やす前に、
pose/depth/line/referenceの対象。

### F. “見えない”

1. crop
2. camera distance
3. viewpoint
4. overlap/occlusion
5. depth order

を先に見る。

概念が生成されていないとは限らない。

### G. LoRAを入れると壊れる

1. base
2. LoRA A
3. LoRA B
4. A+B
5. weight matrix
6. schedule/mask/localization
7. dataset entanglement audit

trainer parameterよりdataset原因の可能性も見る。

### H. Hiresでだけ壊れる

base画像は合格として保存。

Hiresは別passとして、

- denoise
- sampler/scheduler
- Hires prompt/negative
- LoRA/control再適用
- checkpoint

を切り分ける。

### I. anatomyだけ壊れる

count/identity/relation/visibilityが正しいなら、
global Promptを作り直さずlocal repair。

---

## 7. adult Negative OFF/ON教材

目的:
Negativeが

- ノイズを消した
- 目標semanticまで消した
- 構図を変えた
- anatomyだけ変えた

を分離する。

### Test

固定:
- checkpoint
- seed
- resolution
- sampler/scheduler
- steps/CFG
- positive prompt
- LoRA/control

変更:
- Negative conditionのみ

Score:
- target presence
- relation
- count
- visibility
- anatomy
- censor/watermark/text
- composition drift

Negativeは“掃除箱”として扱わない。

---

## 8. Character LoRA × adult interaction教材

### Phase 1 — identity gate
A-only / B-only を通す。

### Phase 2 — coexistence
A+B、interactionなし。

### Phase 3 — relation
同じ2人でsimple interaction。

### Phase 4 — relation-heavy
body-site/role/visibilityを増やす。

### Phase 5 — localization
必要な場合だけRegional/reference/mask。

各段階で同じ4-seed setを使う。

「最終sceneだけ」でLoRA品質を判定しない。

---

## 9. Style LoRA × Character LoRA × relation scene

比較matrix:

- base
- Character LoRA
- Style LoRA
- Character + Style

同じseedで、

- identity
- relation
- composition freedom
- style fidelity
- context leak

を採点する。

Style LoRA追加時だけrelationが落ちる場合、
Promptを増やす前に、

- style weight
- schedule
- late-only style
- dataset composition bias

を疑う。

---

## 10. Regional isolationの最適化

最適解は「最強分離」ではない。

評価軸:

- contamination reduction
- interaction preservation
- boundary artifact
- pose/contact preservation
- identity

No Regional -> weak -> medium -> strong
を比較し、
identity separationとinteraction coherenceの両方が許容される最小強度を採る。

既存:
- Forge Neo Regional Prompter Anima: Latent/Attention yes, Region LoRA no
- ComfyUI hooks/mask/timestep: experimental primitives
- Impact-Pack RegionalSampler: latent-level regional generation

---

## 11. 先生役の返答テンプレート

ユーザーが「出ない」と言ったら、まず完成Promptを渡さない。

1. 失敗ラベルを1個決める
2. 既に成功している軸を固定する
3. 4-seed baselineを作る
4. 1変数だけ変える
5. 3/4 persistentなら次mechanismへ
6. before/afterを保存
7. 「何が証明されたか」を説明する

### 言ってはいけないこと

- このモデルなら絶対できる
- CFGを上げれば直る
- LoRA weightを上げれば直る
- Negativeを増やせば直る
- Regionalを強くすれば直る

どれも failure class を無視した万能処方になる。

---

## 12. NoobAI EPSで今後必要なcontrolled test

まだ不足:

1. adult Negative OFF / ON
2. safety/rating tag state
3. solo concept
4. 2-subject no interaction
5. simple interaction
6. role/body-site binding
7. Character LoRA single
8. Character LoRA pair
9. Style + Character LoRA
10. Hires before/after

NoobAI official model cardだけではこの成功率は分からない。

K-MODEL-NOOB-004 / K-NEG-002はHOLD維持。

---

## 13. Animaで今後必要なcontrolled test

1. tags only
2. concise NL
3. hybrid
4. no Regional
5. weak Regional
6. stronger Regional
7. native identities
8. LoRA identities
9. non-interaction
10. interaction

主評価:
- identity
- role
- relation
- body-site ownership
- overlap anatomy
- coherence

community evidenceは強い仮説源だが、数値的reliabilityはlocal fixed-seed試験が必要。

---

## 14. 教材で使う最小Prompt例の方針

長い露骨な完成Promptを正本にしない。

教材では、
- subject A
- subject B
- count
- relative position
- relation
- target site
- camera
- visibility

のslotとして示す。

利点:
- scene固有の文面に依存しない
- failure labelと対応できる
- DanbooruTagToolのbrowse/facetにも接続しやすい
- Prompt-only / Regional / Controlで同じscene modelを再利用できる

---

## Promotion result

New ACCEPTED:
- K-MODEL-NOOB-009
- K-MODEL-ANIMA-018
- K-PRACTICAL-033
- K-PRACTICAL-034
- K-EVAL-021

New CANDIDATE:
- K-COMM-ANIMA-030

Existing HOLD retained:
- K-MODEL-NOOB-004
- K-NEG-002
