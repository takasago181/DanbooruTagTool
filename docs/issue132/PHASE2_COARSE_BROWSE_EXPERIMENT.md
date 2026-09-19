# Issue #132 Phase 2 — 粗粒度 browse 入口実験

## Status

**PHASE 2 COARSE-BROWSE EXPERIMENT COMPLETE — RESEARCH ONLY**

Phase 1 の136候補をいきなり個別再分類せず、現行Unified 19 routesを7〜9個程度へ畳んだ場合に、第一階層の「どこにあるの？」問題がどれだけ自然消滅するかを評価した。

このPhase 2は設計実験のみ。

- production taxonomy変更: none
- runtime変更: none
- UI変更: none
- search ranking変更: none
- Japanese overlay変更: none
- #70 / #118 / #131 / Performance lane変更: none
- merge / production apply: none

Dedicated branch:

`research/taxonomy-usability-audit`

Phase 1 base:

`f40f28ef3808ea6f3699c16a9aa903cb56f086e6`

---

## 1. 結論

現時点では、**19 routesをそのままユーザーの第一階層に見せるより、8入口 + 横断facetへ分離する案が最も筋が良い**。

理由は単純で、Phase 1 の136候補に対して:

- **32件**: 粗粒度mergeだけで第一階層競合が消える
- **28件**: 色を第一階層categoryではなく横断facetへ移すことで、top-level secondary追加問題ではなくなる
- **14件**: 実は現行Unifiedですでに同じ第一階層へ畳まれており、Phase 1候補生成上のsource-taxonomy境界問題
- 合計 **74 / 136 = 54.41%** は、個別のtop-level reclass / secondary追加を先に行う必要がない

新8入口による純粋な新規効果だけでも:

- 32件 merge解消
- 28件 facet化
- 合計 **60 / 136 = 44.12%**

が「個別タグ分類修正」から「入口設計 / facet設計」の問題へ移る。

残り **62 / 136 = 45.59%** は、粗粒度化だけでは消えず、Phase 3で見る価値がある。

---

## 2. 提案する8入口

### 1. 人物・関係

Current routes:

- PEOPLE_COUNT
- RELATION_ROLE

初心者の最初の問いを「誰がいるか / どういう関係か」に寄せる。

### 2. 身体・見た目・状態

Current routes:

- BODY_SITE
- HAIR_FACE
- NONHUMAN_TRANSFORM
- FLUID_EXCRETION

身体部位、髪・顔、身体変化、体液・状態を同じ大入口へ寄せる。

ここではontology purityより、

> 身体について探したい

というユーザーの探索起点を優先する。

### 3. 衣装・露出

Current route:

- CLOTHING_EXPOSURE

これは現行Unifiedでも既にかなり粗くまとまっているため維持。

### 4. ポーズ・行動

Current routes:

- ACTION_CONTACT
- POSE_POSITION

今回の最重要mergeの1つ。

「これはポーズか、行為か」をタグを知らないユーザーに先に判断させない。

### 5. 表情・視線

Current route:

- EXPRESSION_GAZE

ここは意味が明確で、身体全体へ潰すメリットがPhase 1 sampleでは確認できなかったため独立維持。

### 6. 物・場所・生き物

Current routes:

- TOOL_OBJECT
- LIVING
- SCENE_BACKGROUND
- LIGHT_TIME_WEATHER

「ドアは物か背景か」「窓は物か場所か」のような境界を第一階層から追い出す。

中に入った後で:

- 物・小物
- 生き物
- 場所・背景
- 光・時間・天候

へ絞ればよい。

### 7. 構図・画面表現

Current routes:

- COMPOSITION_CAMERA
- STYLE_PROCESSING
- TEXT_SYMBOL

画角、加工、文字等を「画面そのものの見え方」としてまとめる。

### 8. 内容・メタ

Current route:

- CONTENT_RATING

内容区分やメタ情報を、視覚的対象から分離する。

---

## 3. 第一階層から外すもの

### COLOR_PATTERN_SHAPE

`COLOR_PATTERN_SHAPE` は独立した第一階層入口ではなく、**横断facet「色・柄・形」**へ移す案。

理由:

- `black_bikini` は「衣装」でもあり「黒」でもある
- `blue_eyes` は「身体・顔」でもあり「青」でもある
- 色をsemantic homeとして競わせるとsecondary pathが大量に必要になる
- Phase 1 mechanical poolでは color + target + no color secondary が **1,703件**

これを1,703件の「分類修正候補」として扱うより、

> 対象のhomeはそのまま
> 色は横断属性として絞り込む

方が自然。

ただし、色検索性を失ってよいという意味ではない。

**色facetはbrowse rootまたは各大入口から1タップで使える必要がある。**

---

## 4. 136候補への効果

Machine-readable result:

- `docs/issue132/phase2_candidate_effects.csv`

### A. 粗粒度mergeで新たに第一階層問題が消える — 32件

主な内訳:

#### ACTION vs POSE

以下のようなタグは「ポーズ・行動」へ統合すると、どちらをprimaryにするかを第一階層では争わなくてよくなる。

- `princess_carry`
- `push_down`
- `spanking_self`
- `foot_pussy`
- `presenting_own_ass`
- `holding_own_legs_back`
- `standing_doggystyle`
- `holding_own_leg_back`
- `holding_another's_legs_back`

Special `POSE_SCENE` / `pose_camera` のprojection gapも、第一階層ではACTIONとPOSEを分けないため問題化しにくくなる。

Phase 1のSpecial mechanical pool:

- `POSE_COMPOSITION + pose_camera`: **12件**

この12件すべてについて、pose/actionのexact route projectionは第一階層の必須条件ではなくなる。

#### OBJECT vs PLACE

18 sampled rowsがそのまま吸収される。

例:

- `door`
- `window`
- `open_door`
- `open_window`
- `bar_counter`
- `counter`
- `wooden_stairs`
- `stone_bridge`

Phase 1 mechanical pool全体では object/place fixture ambiguity が **64件**。

この64件を個別にOBJECTかPLACEへ決着させる必要性を大きく下げられる。

#### BODY vs HAIR

`sex_hair` はBODY_SITEかHAIR_FACEかを第一階層で争わなくてよくなる。

#### STYLE vs TEXT

`text_background` はSTYLE_PROCESSINGとTEXT_SYMBOLを同じ「構図・画面表現」へ入れることで第一階層競合が消える。

---

## 5. facet化でtop-level問題ではなくなる — 28件

Phase 1 sampleの色 + target候補28件。

例:

- `black_bikini`
- `blue_eyes`
- `gold_nails`

これらは:

- bikini → 衣装
- eyes / nails → 身体・見た目
- black / blue / gold → 色facet

として扱う。

つまり「secondary COLOR routeを30k taxonomyへ大量追加する」という解決方法を避けられる。

---

## 6. 現行Unifiedですでに第一階層では吸収済み — 14件

Phase 1の `clothing_identity_vs_state_or_placement` のうち14件。

例:

- `bandana_around_neck`
- `mask_around_neck`
- `off_shoulder`
- `shirt_on_shoulders`
- `sweater_around_waist`

General sourceではCLOTHINGとCLOTHING_STATE_EXPOSUREの境界があるが、現行Unifiedでは両方とも `CLOTHING_EXPOSURE` へ入る。

したがってこれは、少なくとも第一階層browseでは既に大部分が解消している。

例外:

- `cover_bikini_girl_(gta_vi)_(pose)`

これは「衣装かポーズか」なので新8入口でも跨る。個別review対象として残す。

---

## 7. 粗粒度化しても残る62件

### 7.1 ACTION + BODY target — 30件

例:

- `biting_breast`
- `grabbing_another's_arm`
- `finger_in_another's_mouth`

「ポーズ・行動」と「身体・見た目」は別入口なので、粗粒度化だけでは解消しない。

ただしここもsecondary categoryを増やす前に、

**横断facet: 身体部位 / 対象部位**

として扱える可能性が高い。

例:

> ポーズ・行動
> → 対象部位: 胸

で `biting_breast` を出す。

これはPhase 3で検証する。

### 7.2 STYLE / META + visual target — 14件

`text_background` 以外。

例:

- `bad_face`
- `collage_background`
- `cursor_hair_ornament`
- `dashed_eyes`
- `doodled_object`
- `pixel_eyes`

ここは一律mergeすると危険。

- 本当にprimaryがおかしいもの
- 画面表現 + 対象というmulti-axisなもの

が混ざる。

Phase 3では個別意味確認を行い、

- primary review
- target facet
- keep screen-expression home

へ分けるべき。

### 7.3 明示的primary review — 2件

- `oripathy_lesion_(arknights)`
  - 身体状態 vs ポーズ
- `cover_bikini_girl_(gta_vi)_(pose)`
  - ポーズ vs 衣装

粗粒度化しても別入口のため残る。

### 7.4 proper noun / meme / event — 15件

粗粒度化では意味を安全に決められない。

- `gigachad_(meme)`
- `distracted_boyfriend_(meme)`
- `family_guy_death_pose_(meme)`
- etc.

無理に8入口のどこかへ押し込むより、

- 固有表現・ミームfacet
- related discovery
- bounded human resolution

のどれかを別途検討する方が安全。

### 7.5 multi-axis — 1件

`cum_on_fourth_wall`

- action
- fluid/body state
- fourth-wall / screen expression

を同時に持つため、粗粒度化だけでは単一home問題にならない。

---

## 8. 7 / 8 / 9入口比較

### 9入口案

8入口案から「物・生き物」と「場所・背景」を再分離する。

Phase 1 sampleで新たに neutralize / facetize:

- **42 / 136**

問題:

- object/place sampled 18件がそのまま残る
- mechanical pool 64件の境界問題も残る

### 8入口案

新たに neutralize / facetize:

- **60 / 136**

さらに現行Unifiedですでに吸収済み14件を含めると:

- **74 / 136 = 54.41%**

が「第一階層を個別修正する問題」ではなくなる。

### 7入口案

さらに:

- 表情・視線を身体へ統合
- または内容・メタを画面表現へ統合

等を試す。

しかしPhase 1の136 sampleでは、**8入口からの追加解消は0件**。

つまり:

- ラベルが広くなりすぎる
- semantic clarityが落ちる
- 今回の観測問題は追加で減らない

ため、現時点では積極的な理由がない。

---

## 9. Phase 2 conclusion

現時点のデータでは、次の順番が最も安全。

1. **8入口をuser-facing first layerの候補として固定**
2. `COLOR_PATTERN_SHAPE` をtop-levelから外し横断facetとして試す
3. BODY targetを横断facetとして試す
4. 残る62件だけを次の人間review対象にする
5. その結果を見てからproduction taxonomy / projection変更の要否を決める

重要なのは、

> 136件を全部直してからUIを考える

ではなく、

> UI上の入口粒度を先に適正化して、それでも残る違和感だけ直す

順番へ変えること。

これにより、30,629件へsecondary pathを大量追加する方向を避けられる可能性が高い。

---

## 10. Next bounded step

Phase 3を行うなら対象は136件全部ではなく、**残った62件だけ**。

優先順:

1. ACTION + BODY 30件
   - body target facetで吸収可能か
2. STYLE/META + visual target 14件
   - 真のprimary誤りとmulti-axisを分離
3. explicit primary review 2件
4. proper meme/event 15件
5. multi-axis 1件

このPhase 3でもproduction変更は不要。

まずcandidate-onlyでfacet案を評価し、ユーザー承認後に初めて実装設計へ進む。

---

## 11. Protected boundary confirmation

変更していない:

- canonical identity
- PromptToken
- Japanese production overlay
- Special ID
- #70 data
- #118 sexual classification
- #131 UI
- Performance code
- search ranking
- UserData
- production catalog
- artifacts/current
- #64 production taxonomy / sidecar
- #76 production browse authority

No merge. No production apply.
