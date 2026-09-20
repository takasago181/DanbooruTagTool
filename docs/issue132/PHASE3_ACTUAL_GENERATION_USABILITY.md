# Issue #132 Phase 3 — 実際の成人向け画像生成から逆算した discoverability redesign

## Status

**PHASE 3 ACTUAL-GENERATION USABILITY SYNTHESIS — RESEARCH ONLY**

Phase 2 の「19 routeを8前後へ畳む」発想を、実際の成人向け画像生成ワークフロー・KNOWLEDGE #44・#76 Special v2・#118 intent filter・現行General分布・現行モデル情報で再評価した。

### 結論

**flatな8/9分類を最終UXにする案は採用しない。**

代わりに、

> 強いintentから入る -> 選択を保持 -> 次に不足している意味軸を絞る -> 最後に見せ方/外見/背景を足す

という **intent-first / multi-axis scene discovery** を第一候補にする。

これはcanonical taxonomyの置換ではない。
browse/discovery projectionとして扱う。

---

## 1. KNOWLEDGE #44 の最新知見

2026-09-17の Batch N は、成人向け生成で以下5レイヤーを分離すべきと整理している。

1. canonical semantic identity
2. human scene-construction order
3. browse/discovery entry path
4. model-specific Prompt serialization
5. generation diagnosis/evaluation

重要:

**human planning order != browse taxonomy != model Prompt order**

成人向けscene planningで使う意味軸:

1. subjects / count / identity
2. core action / state
3. relation / role / ownership
4. target / body site
5. geometry / position / topology
6. implement / device / appendage
7. state / timing / count / source-destination
8. visibility / framing
9. appearance / clothing / exposure / expression
10. setting / background / lighting / style

またbrowseはontology-first固定順ではなく:

> enter from any strong intent -> preserve selection -> surface informative missing dimensions next

を候補としている。

---

## 2. 現在の実タグ分布でflat taxonomyを検証

#118 final intent authorityのordinary identity union:

- total: 31,752
- SEXUAL: 2,037
- CONTEXTUAL: 1,951
- therefore visible under `性的`: **3,988 identities**

内訳:

- General only: **1,234**
- Special only: **1,050**
- General + Special overlap: **1,704**

したがって `性的` view の **2,754 / 3,988 = 69.06%** はすでにSpecial metadataを持つ。

残りGeneral-onlyは1,234件。

### General sideで分類済みの性的view

#64 PROPOSEDかつ#118 SEXUAL/CONTEXTUAL:

**2,835件**

root distribution:

| General root | count |
|---|---:|
| ACTION_CONTACT | 1,174 |
| CLOTHING | 564 |
| CLOTHING_STATE_EXPOSURE | 516 |
| BODY_PART | 309 |
| OBJECT_PROP | 112 |
| POSE_MOVEMENT | 50 |
| STYLE_QUALITY_META | 28 |
| PERSON_COUNT | 26 |
| COLOR_APPEARANCE | 13 |
| EXPRESSION_EMOTION | 12 |
| COMPOSITION_CAMERA | 11 |
| LIVING_NATURE | 6 |
| GAZE_ORIENTATION | 6 |
| TEXT_SYMBOL | 5 |
| PLACE_BACKGROUND | 3 |

もし前Phaseのように:

- 行為 + ポーズ
- 衣装 + 露出

へflat mergeすると:

- 行為/ポーズ: **1,224 = 43.17%**
- 衣装/露出: **1,080 = 38.10%**

合計:

**2,304 / 2,835 = 81.27%**

つまり性的用途のGeneral browseをflatな大分類へ畳むと、
**2棚だけに8割以上が集中する。**

これは分類数を減らしてもbrowse usabilityを改善しない。

---

## 3. General-onlyの「未カバー部分」は実は限定的

性的view 3,988件のうちGeneral-onlyは1,234件。

そのうち#64 PROPOSEDは1,146件、UNRESOLVEDは88件。

1,146件の内訳:

- clothing-related: **689 / 60.12%**
- action-related: **312 / 27.23%**
- body: 69
- pose: 22
- object: 22
- style/meta: 12
- person: 7
- expression/gaze: 9
- color: 4

衣装系 + 行為系だけで:

**1,001 / 1,146 = 87.35%**

重要な含意:

**全31,752件を新taxonomyへ再分類する必要はない。**

Special metadataを持つ約69%は既存#76のmulti-axis browseを再利用できる。

追加設計の中心は:

- General-only sexual/contextual約1.2k
- 特に衣装/露出と行為/接触

へscene-discovery metadataを足すこと。

---

## 4. #76 Special v2はこの用途に近い

#76 accepted v0.8 reference 2,788 rows:

### kind
- 行為・接触 907
- 衣服・露出 503
- 道具・物 299
- 身体・状態 298
- 体液・排泄 275
- ポーズ・構図・場面 156
- 人物・関係 123
- 異形・変形 119
- 表現・メタ 66

### body
- 男性器 307
- 乳房・乳首 266
- 女性器 183
- 口・口内 175
- 尻・肛門 113
- 尿道 20

### theme
- 拘束・BDSM 366
- 損傷・R18G 66
- 生殖・妊娠・授乳 25

907件ある行為棚でも:

- body/theme facetあり: 534
- body/themeなし: 373

代表intersection:

- 尻・肛門 × 行為・接触 = 43
- 尻・肛門 × 道具・物 = 14
- BDSM × 道具・物 = 139
- BDSM × 口・口内 × 道具・物 = 43
- 口・口内 AND 男性器 = 22

この実績からも、
大分類をさらに細かい永久treeへ戻すより
**cross-axis intersection**の方が成人向け生成のscene selectionに合う。

---

## 5. 提案する新UX — 「分類」ではなくscene builder

### A. Scene Core — 最初に選べる強いintent

固定順wizardにはしない。
どこからでも開始可能。

#### 1. 人物・人数・役割

目的:

- 誰がいる
- 何人
- actor / receiver
- relationship / role

これは生成時のbindingに直結する。

#### 2. 行為・状態

目的:

- 何をしている
- 何が起きている

General:
- ACTION_CONTACT/INTIMATE
- ACTION_CONTACT/INTERACTION
- ACTION_CONTACT/OBJECT_USE

Special:
- kind ACTION_CONTACT
- BODY_STATE等から必要なstate route

重要:
「行為一覧を1,000件表示」ではなく、
他軸とintersectionして使う。

#### 3. 身体部位

既存Special body facetを中心に:

- 乳房・乳首
- 女性器
- 尻・肛門
- 口・口内
- 男性器
- 尿道

General-onlyにも必要な範囲で同じbody-target projectionを持たせる。

例:

`biting_breast`

- action = biting/contact
- body = breast

semantic homeをBODYへ変える必要はない。

#### 4. 体位・配置・接続

poseだけではなく生成上のgeometryを意識。

- position
- relative orientation
- topology
- contact geometry

ただしcameraはここに混ぜない。

例:

`standing_doggystyle`

は

- action/state
- position/geometry

の両方から見つかる。

#### 5. 道具・媒介物

- toy / object
- restraint implement
- device / machine
- appendage等

生成上重要なのは単なるobject presenceではなく:

`device -> target -> body-site -> functional relation`

までsceneを完成できること。

#### 6. テーマ

existing #76 themeを維持。

- BDSM / restraint
- reproduction / pregnancy / lactation
- injury / R18G

将来themeを増やす場合も、
永久deep taxonomyより横断facet優先。

---

## 6. Scene Refinement — core決定後に足す

これらは「同格の第一分類」ではなく、
多くの場合core sceneを補強するもの。

### 衣装・露出

General-only sexual viewの最大未カバー領域。

細分は既存#64をそのまま活用可能:

- everyday / underwear
- accessory
- costume
- uniform
- clothing state / exposure

`性的` filter下では衣装689件を1棚に出すのではなく、
subroute chipで絞る。

### 表情・反応・視線

- expression/emotion
- gaze/orientation

成人向けでは重要だが、scene relationより通常は後段refinement。

### 見せ方 / visibility / camera

- framing
- POV
- focus
- angle
- visibility support

重要:

cameraはbody/positionと別軸。
「見えるか」を助けるsupport layer。

### 場所・背景・光・style

scene finishing。

settingが生成意図の核の場合だけ強いentryとして開始可能にする。

---

## 7. Adaptive next-facet

固定taxonomy順より、選択内容に応じて次候補を変える。

### body-siteから入った場合

例: 乳房・乳首

次候補:

1. 行為/状態
2. 衣装/露出
3. 道具
4. 人物/role
5. visibility/camera

### BDSM themeから入った場合

次候補:

1. role
2. device
3. body-site
4. topology/pose
5. visibility

### deviceから入った場合

次候補:

1. target person
2. body-site
3. functional action/relation
4. position
5. count
6. visibility

### fluidから入った場合

次候補:

1. source
2. destination
3. timing/state
4. quantity
5. actor/target
6. visibility

これはKNOWLEDGE Batch Nのscene-completion routeと整合する。

---

## 8. Prompt出力とは分離する

Browseで選ぶ順番をそのままPrompt順にしてはいけない。

### NoobAI XL 1.1 EPS

author caption structure:

`count -> character -> series -> artist -> special -> general -> other`

Danbooru/e621 native-tag model。

したがってscene builderで:

- body-siteから先に選んだ
- deviceから先に選んだ

としても、Prompt exportではNoob profileに従って整理可能。

### Anima

tag + natural language mixed可。
multi-characterではidentity/basic appearanceを明示することが重要。

したがってhard binding sceneでは、
同じscene selectionsをAnima用に別serializeできる。

### WAI/Illustrious

Illustrious-familyではcritical composition conceptのstackやconcept overloadに注意する。

UIがfacetを大量に選ばせて、
全部を無条件Promptへ投入する設計は避ける。

---

## 9. Prompt spam防止

Scene builderでは選択タグを最低でも:

- Core
- Refinement
- Support

に役割分離する候補。

### Core

画像の成立条件。

- target action
- body site
- relation
- position
- device

### Refinement

見た目を決める。

- clothing
- expression
- appearance
- setting

### Support

coreを見える/成立しやすくする補助。

- framing
- visibility
- simple pose support

関連候補を全部自動挿入しない。

KNOWLEDGEのminimum-sufficient Prompt / anti-support原則、およびcompositional-load evidenceに合わせる。

---

## 10. Product proposal

`性的` lensでのUI候補:

### 作りたい内容

**シーンの核**
- 人物・役割
- 行為・状態
- 身体部位
- 体位・配置
- 道具
- テーマ

**見た目・仕上げ**
- 衣装・露出
- 表情・視線
- 構図・見せ方
- 場所・背景・光

これを10個のmutually-exclusive categoryにはしない。

各blockはfacet/entry path。

複数選択してintersectionする。

### 選択後

現在の条件例:

`性的 > 行為・接触 > 乳房・乳首 > BDSM`

のようにcompact chip表示。

その下に:

**次に絞る**
- 役割
- 道具
- 体位
- 見せ方

をcontext-sensitiveに出す。

---

## 11. Current taxonomyを壊さない実装方針

このUXのために#64/#76 authorityを置換しない。

推奨:

1. #118の `性的` lensを入口にする
2. Specialを持つidentityは既存#76 kind/body/themeを再利用
3. General-only 1,234件にだけboundedなscene-discovery overlayを追加
4. 最優先は1,001件を占める clothing/action families
5. BODY/POSITION/DEVICE等の追加facetは必要なidentityだけ
6. existing search ranking維持
7. PromptToken/canonical/Japanese overlay不変

つまり:

**canonical taxonomyではなくuser-discovery projectionを改善する。**

---

## 12. Phase 2 correction

Phase 2の:

> 19 routes -> flat 8入口

はtaxonomy complexityの問題を発見する実験として有効だったが、
成人向けgeneration UXの最終候補としてはsuperseded。

理由:

- sexual Generalでaction+clothingに81.27%集中
- flat shelf削減は巨大棚を作るだけ
- #44/#76 evidenceはmulti-axisを支持
- model prompt orderとhuman browse orderを分離すべき

したがってPhase 3では:

**flat coarse taxonomy -> intent-first multi-axis scene builder**

へ方針修正する。

---

## 13. Next bounded validation

production変更の前に、
actual-generation task matrixでbrowse pathを比較する。

最低でも:

1. action-first ordinary adult scene
2. body-site-first scene
3. position-first scene
4. device-first scene
5. BDSM theme-first scene
6. fluid/source-destination scene
7. clothing/exposure-first scene
8. multi-person role/binding scene

比較:

- current 19-route browse
- Phase2 flat coarse browse
- Phase3 adaptive scene browse

測る:

- target tag発見までのclick数
- backtrack数
- search fallback有無
- 意図しない大量結果
- core/refinement混同
- Promptへ不要タグを積みすぎる誘因

このtask matrixでPhase3が明確に優位なら、
初めてproduction implementation designへ進む。

---

## 14. Protected boundary

このPhaseはresearch documentationのみ。

変更しない:

- #64 production taxonomy
- #76 production taxonomy
- #118 intent authority
- canonical identity
- PromptToken
- Japanese overlay
- Special ID
- search ranking
- #70
- #131
- Performance
- catalog.db
- UserData
- artifacts/current
- main

No merge. No production apply.
