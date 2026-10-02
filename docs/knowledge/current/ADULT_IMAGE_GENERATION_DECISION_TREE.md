# 成人向け画像生成 — 実用診断 Decision Tree

Owner: Issue #44 `KNOWLEDGE:#44`  
対象: 成人であることが明確な、合意的・成人ファンタジーの画像生成  
目的: 「タグを足す」ではなく、失敗原因を切り分けて最小の修正へ進む  
Evidence authority: `CLAIM_REGISTRY.csv` と各 research batch

---

## まず結論

生成が崩れたら、最初にやることは **Prompt追加ではない**。

次の順で見る。

`再現条件確認 -> 失敗分類 -> 最小Prompt -> 4 seed確認 -> 1変数A/B -> 必要ならControlへ`

Prompt-onlyを延々と続ける目安は設けない。
#44の標準教材では、同じ構造失敗が**4 seed中3以上**で続き、簡潔な表現を2系統試しても直らない場合、次のcontrol mechanismへ上げる。

これは「Promptでは絶対不可能」という判定ではなく、**学習効率上の打ち切り線**。

---

## 0. 再現条件が揃っているか

最低限確認する。

- model/checkpoint/profile
- seed
- resolution / aspect ratio
- sampler / scheduler
- steps / CFG
- positive / negative
- LoRA名とweight
- Regional / ControlNet / reference
- Hires / img2img / inpaint
- runtime/version

PNG metadata / ComfyUI workflowがあるなら最優先。

---

## 1. 何が壊れているか

最初に主症状を1個決める。

| 症状 | 主ラベル | 最初に見るもの |
|---|---|---|
| そもそも概念が出ない | CONCEPT_MISSING | trigger / model exposure |
| 人数が違う | COUNT_WRONG | count / framing / aspect |
| AとBの特徴が混ざる | ATTRIBUTE_LEAK | A-only / B-only / LoRA |
| 役割が逆 | ROLE_SWAP | subject binding |
| body-siteの所有者が逆 | BODY_SITE_OWNER_WRONG | binding / region |
| 接触・関係が成立しない | RELATION_MISSING | relation representation / pose |
| poseが違う | GEOMETRY_WRONG | pose/depth/reference |
| 前後関係が違う | WRONG_DEPTH_ORDER | depth / camera |
| 画面外・隠れる | TARGET_OCCLUDED | crop / camera / overlap |
| 手足など局所だけ崩れる | LOCAL_ANATOMY | inpaint/detailer |
| LoRAを入れた時だけ崩れる | LORA_INTERFERENCE | incremental stack |
| Regionalで境界が出る | REGIONAL_BOUNDARY | isolation strength |
| Hires後だけ崩れる | HIRES_DRIFT | second-pass settings |

---

## 2. 「出ない」

### 単体でも出ない
- canonical tag
- old/historical spelling
- model-specific trigger
- training cutoff
を確認。

NoobAIではcurrent Danbooru tagが存在していても、学習時点に露出していたとは限らない。

### 単体では出る
概念知識はある可能性が高い。

複数人物時だけ消えるなら、
vocabularyより **binding / workload / locality** を疑う。

---

## 3. 「人数が違う」

まずstyle/backgroundを外して、

- count
- subject identities
- framing

だけにする。

4 seed中3以上で同じcount failureなら、
Prompt語の言い換えを続けるより、

- aspect ratio
- pose/reference
- regional/layout control

へ進む。

---

## 4. 「人物の特徴が混ざる」

順番:

1. A-only
2. B-only
3. A+B、LoRAなし
4. LoRA Aだけ
5. LoRA Bだけ
6. A+B LoRA
7. weight matrix
8. Regional/reference/localized adapter

**どの段階から混ざったか**が診断結果。

A-only/B-onlyが既に壊れているなら、Regionalの前にidentity側を直す。

---

## 5. 「role / body-site が逆」

まず subject A / subject B を安定させる。

次に、

- role
- target
- relation
- visibility

以外を減らす。

tag-onlyと短い自然言語/Hybridを比較する。

同じswapが4 seed中3以上なら、
Promptだけの再作文よりRegional/referenceへ。

ただしRegionalを強くし過ぎると、相互作用が切れて「別々の絵」のようになることがある。

---

## 6. 「pose / 接触形状が違う」

これはPromptの語彙問題ではなく、geometry問題の可能性が高い。

優先:

- pose
- depth
- line/edge
- reference

identity tagやquality tagを増やさない。

---

## 7. 「見えない」

概念未生成と決めつけない。

確認:

- camera distance
- crop
- viewpoint
- overlap
- occlusion
- depth order

「存在しているが画面に見えていない」を別failureとして扱う。

---

## 8. 「Negativeを入れたら出なくなった」

Negativeは中立な掃除ではない。

### A/B
A: 目標概念を抑制し得るNegativeなし  
B: 比較したいNegativeあり

それ以外は同じ。

採点:

- target presence
- relation
- count
- visibility
- anatomy
- composition
- censor/watermark/text

NoobAI XL 1.1 EPSの公式推奨例は `safe` positive / `nsfw` negative を含む。
成人向け能力試験では、この安全寄りbaselineをそのまま「中立」と扱わない。

---

## 9. 「LoRAを入れると壊れる」

順番:

`base -> A -> B -> A+B`

その後だけ、

- weight matrix
- late scheduling
- mask/localization
- Regional
- dataset audit

へ進む。

LoRAが同じ背景・役割・poseを強制するなら、
推論設定ではなくdataset entanglementの可能性がある。

---

## 10. 「Regionalで人物は分かれたがinteractionが変」

成功を2軸で見る。

### separation
- identity leakが減ったか
- attribute swapが減ったか

### coherence
- 接触が自然か
- overlapが壊れていないか
- region境界が出ていないか

最も強いRegional設定を選ばない。
**必要な分離を満たす最弱設定**を選ぶ。

---

## 11. 「anatomyだけ崩れた」

次が通っているなら、

- count
- identity
- role
- relation
- visibility
- global pose

Prompt全体を作り直さない。

inpaint/detailerで局所修正。

---

## 12. 「Hiresで壊れた」

baseを捨てない。

Hiresはsecond generation passとして別診断。

見る:

- denoise
- Hires sampler/scheduler
- steps/CFG
- Hires prompt/negative
- LoRA/control再適用
- checkpoint

base成功とHires成功は別evidence。

---

## 13. Prompt-onlyからControlへ上げる標準gate

### Promptを続ける
- failureがseedごとに変わる
- semantic自体は通っている
- まだminimal promptを試していない
- model-native表現を試していない

### Controlへ上げる
- conceptは単体で通る
- failure classが明確
- minimal prompt済み
- 表現2系統済み
- 4 seed中3以上で同じstructural failure

### どのControlか
- identity/binding -> Regional/reference/localized adapter
- pose -> pose control
- front/back/overlap -> depth
- contour/layout -> line/edge
- 局所anatomy -> inpaint/detailer

---

## 14. NoobAI EPS — 現在の先生用注意

公式baseline:
- Euler a
- CFG 5–6
- 25–30 steps
- around 1MP

ただしadult relationについて、
公式model cardは成功率benchmarkを出していない。

未実証:
- exact count ceiling
- role/body-site binding
- hard interaction reliability
- adult Negative OFF/ON
- Character LoRA × interaction

ここは「答えを知っているふり」をせず、controlled testを教える。

---

## 15. Anima — 現在の先生用注意

公式:
- tags + natural language + mixed
- multiple charactersでは名前だけよりbasic appearanceも推奨
- safety tagsもprompt surfaceに含む

community:
- individual identityは出るがpairでattribute swap
- interactionで不安定
- regionalでseparation改善の報告
- overlap anatomy/coherence悪化の報告

したがって、
Animaは「複数人物に強い/弱い」の一言で教えない。

`identity -> coexistence -> interaction -> regional`
の順で実測する。

---

## 16. 先生役の最短返答型

ユーザーが失敗画像を持ってきたら、

1. 「主失敗は○○」
2. 「ここは既に成功している」
3. 「次はこの1変数だけ変える」
4. 「同じ4 seedで比較する」
5. 「3/4続くなら次のControlへ」
6. 「成功してもplain-model能力とassisted能力は別」

の順で教える。

完成Promptを最初に投げない。

---

## 根拠

Detailed research:
`../research/BATCH_AW_ADULT_DIAGNOSTIC_ESCALATION_AND_MODEL_GAPS_20261002.md`

Related:
- `ADULT_IMAGE_GENERATION_TEACHING_CURRICULUM.md`
- `ADULT_IMAGE_GENERATION_TEACHER_REFERENCE.md`
- `PRACTICAL_GENERATION_NOOB_ANIMA.md`
- `../research/BATCH_AQ_REGIONAL_LEARNING_AND_REPRODUCIBILITY_20261002.md`
- `../research/BATCH_AV_DATASET_STYLE_BIAS_AND_PREPROCESSING_20261002.md`
