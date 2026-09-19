# Issue #132 Phase 1 — タグ分類の納得感 / discoverability audit

## Status

**PHASE 1 AUDIT PACKAGE COMPLETE — STOP RULE REACHED**

この資料は分類の監査・レビュー用です。production taxonomy、catalog、runtime、UserData、#70、#118、#131、Performance系コードは変更していません。

- live main base: `f40f28ef3808ea6f3699c16a9aa903cb56f086e6`
- dedicated branch: `research/taxonomy-usability-audit`
- dedicated Issue: #132
- candidate review set: **136 rows**
- production merge/apply: **none**

---

## 1. Authority confirmed

### General — Issue #64

Accepted authority:

- `docs/issue64/production_candidate/general_taxonomy.json`
- `docs/issue64/production_candidate/effective_sidecar.csv`
- `docs/issue64/production_candidate/manifest.json`
- runtime importer: `AcceptedGeneralTaxonomyImporter`

Frozen accepted totals:

- population: **30,629**
- PROPOSED: **28,226**
- UNRESOLVED: **2,403**
- confidence: **25,097 HIGH / 3,129 MEDIUM / 2,403 LOW**
- taxonomy SHA-256: `7311fa1bf1523fcd83134c975b579289d7dbc8aa4cdb1313952d906fc2beb70f`
- effective sidecar SHA-256: `a118f5f904c38cee5b63f0c83b06a56f50ee8afdb623c52eb354731bc0b846d9`
- canonical sequence SHA-256: `ca5cc065c92aa38f9daa6b6c8a1f1c13db135057ebfabca076479dfa96872e2b`

#64 は ontology を厳密化するためではなく、初心者向けの浅い実用分類として17 genre / 最大2階層で作られている。primary path に加えて secondary paths を持てる。

Historical bounded review も確認した。最終accepted candidateは30,629件をLLMで全面再読しておらず、最後のsemantic gateは76件のbounded reviewだった。既知の境界修正として、例えば `standing_on_chair` / `sitting_on_creature` を行為・接触へ、`cropped_*` familyを構図へ、`*_nails`の色修飾を身体部位側へ寄せる等が既に行われている。

### Special — Issue #76

Current production Special browse v2:

- production Special identities: **3,059**
- status:
  - AutoCandidate: **2,718**
  - HumanResolved: **315**
  - DeferProductFitReview: **5**
  - OutOfScopeNoBrowse: **0**
  - ReferenceOnlyNoDirectBrowse: **21**
- kind: **9**
- body facet: **6**
- theme facet: **3**

Specialは単一棚へ押し込む設計ではなく、`kind + body + theme` を独立させる。accepted evidenceはexplicit catalog build時だけ読み、`CatalogEntry.SpecialBrowseV2` にbakeされる。normal startupはcatalog内のprecomputed mappingだけを読む。

### Unified browse — Issue #117

Current user-facing browse is neither #64 nor #76そのものではなく、両方の**projection / canonical union**。

- ordinary discovery routes: **19**
- headings: 「何を描く」「動き・状態」「画面・表現」
- General + Special overlap is canonical-deduped
- General proposed paths are mapped into Unified routes
- Special kind/body/theme is projected into Unified routes/facets
- General secondary pathもUnified routeへunionされる
- Special body/theme facetsは保持される

重要なcoarsening:

- General `EXPRESSION_EMOTION` + `GAZE_ORIENTATION` → Unified `EXPRESSION_GAZE`
- General `CLOTHING` + `CLOTHING_STATE_EXPOSURE` → Unified `CLOTHING_EXPOSURE`
- Special `BODY_STATE` → Unified `BODY_SITE`
- Special `POSE_SCENE` は `SpecialRoute()` の直接mappingを持たず、generation profileの `POSE_COMPOSITION + CompositionRoleOverride=pose/camera` または明示overrideでrouteを補う

つまり「source taxonomy上は説明可能」でも、Unifiedへ投影すると意味が潰れたり、逆にGeneral/Specialのunionで自然に補完されることがある。

---

## 2. なぜ「なんでここ？」が起きやすいか

### 2.1 Generalはmulti-path対応だが、実データはほぼsingle-path

accepted sidecarを機械集計:

- secondary 0件: **29,949**
- secondary 1件: **679**
- secondary 2件: **1**
- secondaryを1つ以上持つ行: **680 / 30,629 = 約2.22%**

したがって現状の主要リスクは、単純な「誤分類」だけではない。

**主分類は納得できるが、ユーザーが別の自然な入口から探せない**ケースが大量にあり得る。

例:

- `black_bikini`: 衣装をprimaryにするのは自然。しかし「黒」から探す経路が無い。
- `biting_breast`: 行為をprimaryにするのは自然。しかし「胸」から探す経路が無い。
- `door` / `window`: 物としても、背景・場所の構成要素としても探され得る。

### 2.2 Generalの境界ルールは正しくてもcompound tagで一軸が落ちる

#64 taxonomy自体には「色修飾より対象物identityを主とする」「他者・物との接触なら行為」等の妥当な境界がある。

しかしそれを**primaryだけで運用**すると、

- modifier + target
- action + body site
- clothing + state/placement
- pose + contact
- object + place fixture

のようなcompound identityでsecondary discoveryが不足する。

### 2.3 Unified projectionでsource taxonomyの差が潰れる

例:

- BODY_STATE → BODY_SITE
- CLOTHINGとCLOTHING_STATE_EXPOSURE → 同じCLOTHING_EXPOSURE

これはUIを浅くする目的では合理的だが、ユーザーの「髪の状態」「衣服そのもの」「着方」という感覚が同じ棚に吸収される。

### 2.4 General/Special mismatchは悪いとは限らないが、projection次第

良い補完例:

- `penis_awe`
  - General: EXPRESSION_EMOTION
  - Special: body facet MALE_GENITAL
  - Unifiedでは表情側 + 男性器facetを両方持てる。
  - 単一ontologyに揃えない方がむしろdiscoverabilityが良い。

注意例:

- `holding_own_legs_back`
  - General: ACTION_CONTACT/INTERACTION
  - promoted Special: POSE_SCENE
  - generation role: `pose_camera`
  - Unified overlayが自動route化するのはroleが厳密に `pose` / `camera` の場合だけ。
  - 結果、Special側の「pose」意図がUnified routeへ出ず、GeneralのACTIONだけが前面に残り得る。

このタイプは#76 authorityの誤りではなく、**Unified projection gap** として扱うべき。

---

## 3. Mechanical high-risk pools

以下は**confirmed error件数ではない**。regex / token / structural ruleで拾った、人間レビュー候補poolの件数。pool同士は重複し得る。

| Pattern | Mechanical pool | 意味 |
|---|---:|---|
| leading color + target、COLOR secondaryなし | **1,703** | 対象主分類は妥当でも色から探せない候補 |
| ACTION + explicit body token、BODY secondaryなし | **328** | 行為は妥当でも対象部位から探せない候補 |
| STYLE/META + visual target、secondaryなし | **31** | 画面表現と顔/目/背景/物の境界 |
| clothing identity + state/placement、secondaryなし | **15** | 衣装と着方・配置の境界 |
| POSE内にstrong action/state signal | **7** | primary自体を疑う高優先候補 |
| object/place fixture ambiguity | **64** | ドア・窓・カウンター等 |
| UNRESOLVED meme/event/project family | **397** | 安全な保留だが発見経路が無いfamily |
| Special POSE_COMPOSITION role=`pose_camera` | **12** | Unifiedのpose/camera exact mappingと不一致 |

### 重要な読み方

1,703件の色候補を「1,703件誤分類」とは扱わない。

たとえば `red_dress` を衣装primaryにするのは#64の設計意図どおり。問題は「赤」からも見つかるべきか、というsecondary discoverability。

逆に `oripathy_lesion_(arknights)` が `POSE_MOVEMENT` にいるようなものは、primary自体の再確認を優先する。

---

## 4. Phase 1 review candidates

File:

- `docs/issue132/phase1_candidates_v1.csv`

Total: **136**

Breakdown:

| Review pattern | Rows |
|---|---:|
| modifier_target_missing_secondary | 28 |
| action_body_missing_secondary | 30 |
| style_meta_vs_visual_target | 15 |
| clothing_identity_vs_state_or_placement | 15 |
| pose_vs_action_or_state | 7 |
| object_vs_place_fixture | 18 |
| proper_meme_event | 15 |
| general_special_mismatch | 1 |
| special_body_vs_hair | 1 |
| special_fluid_vs_meta | 1 |
| pose_scene_projection_gap | 5 |

### Representative rows

#### `oripathy_lesion_(arknights)`

- current: `POSE_MOVEMENT`
- candidate: `BODY_PART`
- reason: 「病変」という身体状態をポーズから探すのは初心者の直感から外れやすい。
- priority: high

#### `spanking_self`

- current: `POSE_MOVEMENT`
- candidate: `ACTION_CONTACT/INTIMATE + secondary POSE_MOVEMENT`
- reason: 自己への叩く行為がidentity中心で、ポーズだけでは行為側から見つからない。

#### `cover_bikini_girl_(gta_vi)_(pose)`

- current: `CLOTHING/EVERYDAY`
- candidate: `POSE_MOVEMENT + secondary CLOTHING/COSTUME`
- reason: canonical自体が `(pose)` を明示しているのに、衣装だけに見える。

#### `cursor_hair_ornament`

- current: `STYLE_QUALITY_META`
- candidate: `CLOTHING/ACCESSORY + secondary STYLE_QUALITY_META`
- reason: 初心者はまず「髪飾り」を衣装・アクセサリから探す可能性が高い。

#### `black_bikini`

- current: `CLOTHING/EVERYDAY`
- current secondary: none
- candidate: current primary維持 + `COLOR_APPEARANCE`
- reason: primary correctionではなくdiscoverability追加候補。

#### `biting_breast`

- current: `ACTION_CONTACT/INTIMATE`
- current secondary: none
- candidate: current primary維持 + `BODY_PART`
- reason: 「噛む」と「胸」の両方が探索軸になる。

#### `sex_hair`

- General: `BODY_PART`
- Special: `BODY_STATE`
- current Unified projection: BODY_SITE側
- candidate: `BODY_SITE + HAIR_FACE`
- reason: 実際の視覚identityは「髪の状態」なので、髪・顔側から探せないのは違和感が強い。

#### `cum_on_fourth_wall`

- General: ACTION_CONTACT/INTIMATE
- Special: FLUID_EXCRETION
- candidate Unified: ACTION + FLUID + STYLE_PROCESSING
- reason: 「fourth wall」は画面演出の意味も強い。

#### `standing_doggystyle`

- General: ACTION_CONTACT/INTIMATE
- Special: POSE_SCENE
- generation role: `pose_camera`
- candidate Unified: ACTION_CONTACT + POSE_POSITION
- reason: 「行為」と「立位体位」の両方が自然な入口。

### Existing precedent that supports secondary routing

Special Unified overlay already contains explicit secondary route overrides for:

- rape face
- ahegao
- naughty face
- torogao
- looking at penis
- looking at pussy

つまり「semantic homeを1つに固定せず、ユーザーが自然に探す別入口を追加する」という考え方自体は、現行production設計にも既に存在する。

---

## 5. Japanese display limitation

ユーザー指定のprotected boundaryに従い、production Japanese overlayは変更していない。

さらにGeneralのproduction `data/runtime/japanese_overlay.json` はprotected local inputで、live GitHub mainに内容が置かれていない。そのためこのGitHub-only Phase 1ではGeneral候補の**現在のproduction display_jaを安全に取得できない**。

したがってCSVでは:

- promoted Specialでtracked metadataに `display_ja` があるもの: その値
- それ以外: `（監査用仮訳）...` と明記したreview gloss

を使っている。

仮訳をproduction Japanese authorityとして扱ってはいけない。将来local read-only validationを行う場合は、canonicalでprotected overlayとJOINして表示文字列だけ照合し、overlay自体は変更しない。

---

## 6. 修正方針の比較

### Option 1 — 現在の単一主分類を維持し、明確な誤分類だけ直す

**Pros**

- 最小変更
- #64思想をそのまま維持
- regression範囲が狭い

**Cons**

- `black_bikini` / `biting_breast` のような「primaryは正しいが別入口がない」問題を解決しない
- compound tagの違和感が残る

**Phase 1 evidence**

`oripathy_lesion_(arknights)` や一部pose/action候補には有効。ただし136件全体の主解にはならない。

### Option 2 — primary + secondary path方式を拡張

**Pros**

- General schemaに既に存在する
- Unified browseもGeneral secondary pathをroute unionできる
- primary authorityを壊さずdiscoverabilityだけ増やせる
- color/object、action/body、object/placeのような複合identityに合う

**Cons**

- secondaryを増やしすぎるとカテゴリ件数が膨らみ、何でもどこでも出る状態になり得る
- family単位の明確な追加条件が必要

**Phase 1 evidence**

今回の最大構造問題である「secondary利用率 約2.22%」へ最も直接的に効く。Phase 2で試験するなら、まず限定familyで検証する価値が高い。

### Option 3 — Generalの一部をSpecial同様の kind + facet にする

例:

- semantic home
- body / target
- color
- state
- scene

を独立facet化する。

**Pros**

- multi-dimensional tagを最も素直に表現できる
- single-primary conflictを根本的に減らせる

**Cons**

- General 30k規模で全面導入すると大改修
- catalog schema / projection / UI / validationの範囲が大きい
- shallow beginner browseという#64の意図を複雑化する恐れ
- 今回のPhase 1から直接productionへ進めるには重すぎる

**Phase 1 evidence**

Specialでは有効性が確認できるが、General全面採用を正当化する証拠はまだない。必要なら「身体部位」「色」「場所」等の限定facet実験から始めるべき。

### Option 4 — 現行分類を維持し、検索/関連表示だけ改善

**Pros**

- taxonomy authorityをほぼ触らない
- exact search利用者には効果が出やすい

**Cons**

- browse画面での「なんでここ？」自体は残る
- search rankingは今回のprotected boundaryであり、このlaneでは変更不可
- タグ名を知らない初心者のbrowse discoverabilityという目的に対しては間接的

**Phase 1 evidence**

補助策にはなり得るが、今回の主目的だけを考えるとtaxonomy route不足の代替にはならない。

---

## 7. Phase 1 conclusion

現状は「30,629件の主分類が大量に間違っている」と判断する根拠はない。

より強く見えているのは次の3種類。

1. **少数のprimary再確認候補**
   - 例: `oripathy_lesion_(arknights)`, `spanking_self`, `cover_bikini_girl_(gta_vi)_(pose)`

2. **大量になり得るsecondary discoverability不足**
   - 色 + 対象物
   - 行為 + 身体部位
   - 物 + 場所
   - 衣装 + 状態
   - 現在secondary path使用は680/30,629件だけ

3. **General / Specialは妥当でもUnified projectionで一軸が落ちるケース**
   - 特に `POSE_SCENE` と `pose_camera` 境界
   - ただしGeneral側が補完する行もあるため、Specialだけを見て機械修正してはいけない

したがって次段階で全面再分類をする必要はない。

Phase 2へ進める場合は、この136件を人間レビューし、各行を最低でも次の4 dispositionへ分けてからfamily展開するのが安全:

- KEEP_PRIMARY_ADD_SECONDARY
- RECLASSIFY_PRIMARY
- KEEP_UNRESOLVED
- UNIFIED_PROJECTION_ONLY

その後、accepted familyだけをboundedに類似タグへ展開する。

---

## 8. Protected-boundary confirmation

Phase 1で変更していないもの:

- canonical tag identity
- PromptToken
- Japanese production overlay
- Special ID
- #70 Character / Copyright / Artist data
- #118 sexual classification
- search ranking
- UserData
- production catalog
- artifacts/current / current runtime
- #131 UI
- Performance optimization
- #64 production taxonomy / sidecar
- #76 production browse authority

No merge. No production apply. No catalog replacement.

**STOP here for user review.**
