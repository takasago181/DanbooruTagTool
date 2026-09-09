# 04 Hard target genres

Owner: PROMPT / Issue #5
Status: genre map for difficult adult-target prompt construction. Not production specification.

## 目的

hard-targetを「成人向けだから難しい」と一括りにせず、**何が生成上の難しさを作っているか**でジャンル分けする。

hard = 内容強度だけではなく、rare/niche、multi-Special、actor-target relation、body-site binding、object integration、unusual geometry、visibility、long-tail recognition等を含む。

内部では露骨な完成Promptではなく、`ACT / SITE / OBJECT / ACTOR / RELATION / POSE / VISIBILITY`として監査する。

---

## A. Body-site-specific lane

特徴:
- actだけでなくexact siteが重要
- broad conceptは出てもsiteがdriftしやすい
- visibilityを上げるとpose/compositionへ副作用が出る

主要failure:
- `SITE_WRONG`
- `VISIBILITY_LOST`
- `GEOMETRY_BREAK`
- `MODEL_TRIGGER_MISMATCH`

基本診断:
1. ACT recognition
2. SITE specificity
3. competing site concepts
4. minimum pose
5. minimum visibility
6. family-specific finish

WAI17ではlean tag-first、NoobAIではspecial-first、Animaでは必要時short relation/site support候補。

---

## B. Restraint / BDSM / control lane

重要分解:
- broad theme
- physical restraint point
- restraint method/object
- role/relation
- pose/geometry
- act
- visibility

原則:
- broad themeとphysical evidenceを分ける
- mood/roleと物理拘束を混同しない
- restraint pointを一気に増やさず段階化

主要failure:
- `OBJECT_DEGRADES`
- `GEOMETRY_BREAK`
- `BINDING_LOST`
- `VISIBILITY_LOST`

監査:
- restraint evidenceが画像上にあるか
- act evidenceと同じframeで観測できるか
- multi-actorなら役割が逆転していないか

---

## C. Machine / mechanical-device lane

重要分解:
- machine identity
- active part
- target site
- human/object pose
- contact relation
- visibility

典型failure:
- machineが背景物になる
- active partが意味不明物体になる
- contact relationが失われる
- 接続方向/poseが破綻
- machine bodyとtarget evidenceを同時に見せられない

主要failure code:
- `OBJECT_DEGRADES`
- `BINDING_LOST`
- `GEOMETRY_BREAK`
- `VISIBILITY_LOST`

Prompt-only ceilingを比較的早めに疑うジャンル。

---

## D. Tentacle / non-human appendage lane

重要分解:
- appendage identity
- source identity
- count/distribution
- function split
- target site
- pose
- visibility

原則:
- まず1 functionから
- restraint/touch/contact等の複数roleを最初から詰め込まない
- sourceが必要なら明示的に扱う
- multi-siteは段階化

主要failure:
- `COUNT_FAILURE`
- `OBJECT_DEGRADES`
- `BINDING_LOST`
- `SITE_WRONG`
- `OVERPROMPTED_CONFLICT`

NoobAIのe621 exposureは調査理由にはなるが優位性の証明ではない。

---

## E. Ultra-niche / extreme specificity lane

特徴:
- body-site/object/action specificityが極端に高い
- broad sexual conceptへ吸われやすい
- rare vocabularyでmodel recognition自体が不明な場合がある

主要failure:
- `MODEL_TRIGGER_MISMATCH`
- `SITE_WRONG`
- `OBJECT_DEGRADES`
- `VISIBILITY_LOST`

基本sequence:
1. canonical Special baseline
2. one site/meaning support
3. one visibility support
4. canonical/Alias/alternate surface A/B if evidence exists
5. repeated same failureならPrompt-only ceiling review

---

## F. Multiple-Special lane

特徴:
- individual Specialは出ても同時保持で片方が落ちる
- competing acts/objects/sitesがbindingを壊す

必須test sequence:
`A_ONLY -> B_ONLY -> AB minimal -> AB + one targeted support`

主要failure:
- `MULTI_SPECIAL_DROP`
- `BINDING_LOST`
- `BODY_SITE_BINDING_ERROR`
- `OVERPROMPTED_CONFLICT`

一つのglobal scoreで平均しない。`T_A / T_B / ...`を別記録。

---

## G. Multi-actor / actor-target relation lane

特徴:
- 人物は出ても誰が何をしているかが崩れる
- attribute/identityがactor間で漏れる
- count自体も不安定になり得る

主要failure:
- `ACTOR_TARGET_SWAP`
- `ATTRIBUTE_LEAKAGE`
- `IDENTITY_MIXING`
- `COUNT_FAILURE`
- `RELATION_FAILURE`

Prompt候補:
- count/identityを先に固定
- relationをshort targeted support
- Animaはappearance anchor優先候補

Repeated failure:
- Forge Couple / Regional等をassisted-control laneとして検討

---

## H. Difficult pose / geometry / visibility lane

内容がrareでなくてもhardになり得る。

難しさ:
- unusual orientation
- contact geometry
- crop/occlusion
- subject scale
- viewpoint conflict

主要failure:
- `GEOMETRY_FAILURE`
- `VISIBILITY_FAILURE`
- `CROP_OCCLUSION_FAILURE`
- `COMPOSITION_CONFLICT`

原則:
- Frame / Viewpoint / Orientationを同roleで過積載しない
- visibility supportの副作用を独立評価
- geometryがsemantic correctなのに繰り返し壊れるならControlNet候補

---

## I. Context / aftermath / mood / state lane

これらはしばしばcore actではなくcontextual layer。

リスク:
- broad moodがcore targetより強くなる
- state/effect語を盛りすぎてcomposition/styleがdrift
- quality/aestheticと役割が混ざる

原則:
- core成立後に追加
- target realizationとcontext qualityを別評価

---

## Cross-genre principle

hard targetを失敗した時、直ちに「モデルが知らない」と決めない。

順番:
1. recognition
2. specificity/site
3. binding/relation
4. object integration
5. geometry
6. visibility
7. density/conflict
8. family grammar
9. Prompt-only ceiling

詳細:
- `docs/stages/STAGE_10_PROMPT_HARD_TARGET_CATEGORY_FAMILY_FAILURE_MATRIX_20260909.md`
- `docs/stages/STAGE_10_PROMPT_HARD_TARGET_FAMILY_MATRIX_20260909.md`
- `docs/stages/STAGE_10_PROMPT_HARD_TARGET_TEST_BACKLOG_20260909.md`
