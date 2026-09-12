# Batch F — Prompt Semantic Role Decomposition for Explanation

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-13

Backlog item: `K-RB-02 Prompt semantic-role decomposition for explanation`

Status: `RESEARCH_PASS_V1 / NO_PRODUCT_PROMOTION`

## Purpose

Batch E classified **what kind of surface** appears in an existing Prompt. This batch answers the next question:

> Once a surface has been classified safely, what does its semantic content describe?

The goal is a beginner-facing explanation vocabulary that can say things like:

- `1girl` = 人数・主体
- `blue_hair` = 外見
- `smile` = 表情
- `sitting` = 姿勢
- `from_above` = 視点
- `bedroom` = 場所

without automatically rewriting, deleting, ranking or optimizing the Prompt.

This is an **explanation role model**, not a canonical ontology and not the General 30,629 browse taxonomy owned by Issue #64.

---

## 1. Evidence basis

Danbooru's current tagging checklist naturally separates several kinds of visible information:

- artist / copyright / character identification
- character count/grouping
- body parts and appearance
- hair / eye / skin features
- wear/costume/accessories
- viewpoint and framing
- action/posture and gestures
- face/facial expression
- objects
- relationships and interactions
- composition
- background/scenery/location
- time/weather
- technical/meta/source information

Current Danbooru tag groups further show that body parts, posture, gestures, groups, locations, image composition, face tags, colors and related families are distinct practical semantic clusters.

Primary sources:
- https://safebooru.donmai.us/wiki_pages/howto%3Atag_checklist
- https://safebooru.donmai.us/wiki_pages/help%3Atags
- https://safebooru.donmai.us/wiki_pages/tag_group%3Abody_parts
- https://safebooru.donmai.us/wiki_pages/tag_group%3Agestures
- https://safebooru.donmai.us/wiki_pages/tag_group%3Agroups
- https://safebooru.donmai.us/wiki_pages/tag_group%3Alocations
- existing project semantic audit: `DANBOORU_WIKI_SEMANTIC_AUDIT_20260909.md`

Important boundary:
Danbooru's organization is evidence that these semantic dimensions are useful and distinct. It does **not** force the project to copy Danbooru's checklist headings or build a complete ontology.

---

## 2. Separate three axes

Existing Prompt explanation should not use one overloaded category field.

Keep separate:

1. **surface/runtime class** — Batch E: canonical tag, Alias, runtime syntax, LoRA, free phrase, etc.
2. **semantic role** — this batch: what the content describes.
3. **Danbooru category / authority** — General, Character, Copyright, Artist, Meta, or non-Danbooru.

Example:

`(smile:1.2)`

- surface class = runtime attention wrapper
- inner semantic role = expression
- canonical identity = `smile` if exact lookup succeeds
- Danbooru category = general

Example:

`hatsune_miku`

- surface class = canonical tag
- semantic role = character identity
- Danbooru category = character

Example:

`<lora:Rella_Style:0.7>`

- surface class = extra-network reference
- semantic role = runtime/model asset, not image-semantic role
- Danbooru category = none

---

## 3. Proposed semantic explanation roles

These roles are deliberately broad enough for beginner explanation and narrow enough to avoid a giant ontology.

### R1 — `SUBJECT_COUNT_GROUP`

What/ how many primary subjects or participants are present.

Examples:
- `1girl`
- `2girls`
- `solo`
- group/count surfaces

Explain as:
`人数・主体構成`

Keep separate from identity: `1girl` does not tell us which character.

### R2 — `CHARACTER_IDENTITY`

Who the depicted named character is.

Typically Danbooru Character category.

Explain as:
`キャラクター指定`

Do not collapse source series/copyright into this role.

### R3 — `SOURCE_SERIES_CONTEXT`

Which work/series/source context the character/image belongs to.

Typically Danbooru Copyright category.

Explain as:
`作品・シリーズ指定`

This is contextual identity, not visible appearance by itself.

### R4 — `ARTIST_CREATOR_SURFACE`

Artist/creator identity surface.

Typically Danbooru Artist category when canonical.

Explain as:
`作者・絵師名`

Important:
Do **not** automatically explain this as `画風` or `style`. Artist identity and model-learned style effect are separate claims.

### R5 — `BODY_APPEARANCE`

Stable or visible physical appearance/body traits.

Includes broad families such as:
- body part/state
- hair color/length/style
- eye/skin color
- body build
- visible anatomy
- species/creature traits where applicable

Explain as:
`外見・身体特徴`

Body-site-specific semantics should retain the exact site when important rather than reducing everything to generic appearance.

### R6 — `CLOTHING_ACCESSORY_EQUIPMENT`

What the subject wears/carries/equips, when the concept is primarily an item/state rather than an action.

Includes:
- clothing
- costume
- footwear
- jewelry/accessories
- worn equipment

Explain as:
`服装・装飾・装備`

If the same object participates in an action (`holding sword`) the object and relation may need separate roles.

### R7 — `EXPRESSION_GAZE_FACE_STATE`

Facial expression, eye state, gaze and related face-level communicative state.

Includes:
- smile/frown
- open/closed eyes
- blush where used as visible face/body state
- looking at viewer / looking away where gaze is the primary semantic axis

Explain as:
`表情・視線`

Do not merge camera viewpoint with gaze direction.

### R8 — `POSE_POSTURE_GESTURE`

Subject's own posture/pose/gesture when it does not inherently require another actor/object relation.

Includes:
- standing/sitting/kneeling/lying
- leg/arm pose
- hand gestures

Explain as:
`姿勢・ポーズ・ジェスチャー`

Relation-heavy concepts belong in R9 even if they also constrain pose.

### R9 — `ACTION_RELATION_INTERACTION`

Action or relation involving actor, target, object, ownership, contact, source/destination or topology.

Examples:
- holding an object
- hugging another
- actor-target contact
- body-site interaction
- restraint topology
- source/destination fluid relation

Explain as:
`行為・接触・関係`

Important:
This is where current KNOWLEDGE's `presence != relation success` principle matters. Object presence is not the same as a correct relation.

### R10 — `OBJECT_PROP`

Object/prop present in the scene when its main role is object identity rather than relation.

Examples:
- chair
- sword
- cup
- vehicle

Explain as:
`物・小道具`

If relation matters, pair with R9 instead of pretending object presence describes the whole concept.

### R11 — `CAMERA_FRAME_VIEWPOINT_ORIENTATION`

How the scene is framed or observed.

Subdimensions should remain available:
- frame/crop: close-up, upper body, full body, wide shot
- viewpoint: from above, from below, from side, POV
- orientation: subject/body direction when distinct
- focus/visibility: what is emphasized or visible

Explain as:
`構図・画角・視点`

Do not flatten these into one meaning internally. Current knowledge already treats frame/viewpoint/orientation/visibility as distinct roles for conflict analysis.

### R12 — `ENVIRONMENT_LOCATION_BACKGROUND`

Where the scene occurs and what surrounds it.

Includes:
- bedroom / classroom / beach / city
- indoors / outdoors
- background type
- scenery

Explain as:
`場所・背景・環境`

Danbooru's location/background groups support this as a distinct semantic family.

### R13 — `TIME_WEATHER_ATMOSPHERE`

Environmental time/weather/atmospheric state.

Includes:
- day / night / twilight
- rain / snow / fog / cloudy sky

Explain as:
`時間・天候・空気感`

Keep actual style/lighting separate when possible.

### R14 — `LIGHT_COLOR_VISUAL_TREATMENT`

Visible lighting/color/compositional treatment that is not simply subject appearance.

Includes:
- backlighting / sidelighting
- monochrome / global color treatment
- some composition-level visual treatments

Explain as:
`光・色・見せ方`

Exact style/model quality conventions remain separate in R15.

### R15 — `STYLE_QUALITY_MODEL_CONVENTION`

Prompt surfaces intended to influence style, quality, aesthetic level, model-specific score/rating conventions or learned Prompt recipes.

Explain as:
`画風・品質・モデル向け指定`

Important:
This role may contain non-Danbooru surfaces. Exact membership/effectiveness is model/version scoped and is a separate research item (`K-RB-07`, `K-RB-08`).

Do not tell the user a quality token is canonical merely because it is common in generation Prompt examples.

### R16 — `META_TECHNICAL_SOURCE`

Metadata/technical/source information rather than ordinary depicted content.

Typical Danbooru Meta examples can include technical/source/context tags.

Explain as:
`メタ情報・技術情報`

Meta category is not synonymous with generation-quality instruction.

### R17 — `NEGATIVE_TARGET_ROLE`

Not a standalone semantic family. This is an overlay on any role when the content appears in Negative conditioning.

Example:
- `bad_hands` may concern anatomy/error content
- a target concept in Negative may conflict with desired semantics

Store:
- semantic role
- negative channel

separately.

### R18 — `UNKNOWN_OR_MULTIROLE`

Use when:
- meaning is unclear
- one concept genuinely spans multiple roles
- classification would require unsupported inference

Multi-role is preferable to forcing a false single category.

---

## 4. Role hierarchy should stay shallow

For beginner comprehension, avoid building a deep taxonomy inside KNOWLEDGE.

Recommended structure:

```text
role
  + optional subrole
  + exact semantic detail from canonical/wiki data
```

Example:

```text
role: CAMERA_FRAME_VIEWPOINT_ORIENTATION
subrole: VIEWPOINT
canonical: from_above
Japanese explanation: 上から見下ろす視点
```

Example:

```text
role: ACTION_RELATION_INTERACTION
subrole: ACTOR_TARGET_CONTACT
canonical: holding_another's_legs
Japanese explanation: 相手の両脚を持つ行為
```

This keeps the explanation system lightweight while exact semantics stay in the dictionary/wiki layer.

---

## 5. Multi-role cases are normal

Some tags carry more than one explanatory dimension.

Examples:

### `cowboy_shot`
Primary role: frame/crop.
It indirectly affects visible body area, but should not be reclassified as anatomy.

### `bound_wrists`
Primary role: action/relation/topology.
Also references body site (wrists).
Store body-site detail as semantic predicates, not a second unrelated tag meaning.

### `sitting_split`
Pose/posture plus leg configuration.
Implication to broader `split`/`sitting` does not mean the role should be duplicated into multiple UI tags automatically.

### character + copyright
A character Prompt often includes both character and series tags. They remain two different semantic roles even if used together.

---

## 6. Role assignment must not claim generation effect

The role answers:

> What does this content describe?

It does **not** answer:

> How strongly does this checkpoint respond to it?

Examples:
- Artist tag can be `ARTIST_CREATOR_SURFACE` even if exact style effect is unknown.
- `from_above` can be `CAMERA.../VIEWPOINT` even if generation reliability varies.
- `bound_wrists` can be `ACTION_RELATION_INTERACTION` regardless of whether WAI17 draws it correctly.

This separation lets the tool explain Prompt meaning without pretending to be a model-success oracle.

---

## 7. Suggested beginner explanation pattern

For a safely identified surface:

```text
日本語名
canonical English
役割
短い説明
必要なら注意
```

Example:

```text
上からの視点
from_above
役割: 構図・画角・視点
カメラが被写体を上から見下ろす構図です。
```

Example:

```text
初音ミク
hatsune_miku
役割: キャラクター指定
描くキャラクターの指定です。
```

Example:

```text
<lora:Rella_Style:0.7>
役割: 実行時アセット指定
LoRAを読み込むための構文で、Danbooruタグではありません。
```

The last example uses Batch E's surface class rather than forcing a semantic-image role.

---

## 8. Boundaries with Issue #64

This research does **not** own General 30,629 browse taxonomy.

Difference:

- #64 taxonomy = user discovery navigation for the exact General population
- Batch F roles = explanation of what an already-present Prompt surface means/does semantically

They may share labels such as `表情`, `構図`, `衣装`, but one must not silently become the other's source of truth.

If future implementation wants to reuse one mapping for both, DEV must validate that the roles actually align instead of assuming equivalence.

---

## 9. Durable conclusions proposed for later Claim review

Candidate durable statements:

1. Surface/runtime classification and semantic-role classification are separate axes.
2. Prompt explanation benefits from preserving identity, appearance, clothing, expression/gaze, posture, interaction/relation, object, camera, environment, time/weather, visual treatment, style/quality convention and meta/technical roles separately.
3. Character, Copyright and Artist identity should not be collapsed into General image attributes.
4. Camera viewpoint, subject gaze and subject orientation are distinct semantic dimensions.
5. Object presence and actor-target relation are distinct; relation concepts require a relation role rather than only an object role.
6. Multi-role/unknown is a valid state and is preferable to false precision.
7. Semantic role says what content describes, not how reliably a model generates it.

No Claim Registry promotion in this batch. Review together with K-RB-03 before adding beginner-explanation Claims.

---

## 10. Next research dependency

Next backlog item:

`K-RB-03 Beginner-safe Japanese explanation rules`

K-RB-03 should define how the roles and exact canonical meanings become concise Japanese text while preserving:
- identity
- actor/target
- body-site
- count
- hierarchy/Alias distinction
- uncertainty
- canonical English traceability
