# Issue #132 — Luna discovery-route semantic contract

Date: 2026-09-23 JST
Status: **RESEARCH CONTRACT / PASS-A ROUTE VOCABULARY**

## 1. Product purpose

This contract is for one purpose:

> A Japanese image-generation user should be able to find a useful Danbooru tag from the visual result they want, even when they do not know the exact English tag name.

This is **not** an ontology-cleanup exercise.

A route is a user-facing discovery shelf, not a statement that the tag belongs exclusively to one semantic class.

Runtime simplicity remains a hard constraint. The full semantic ledger stays research-only.

---

## 2. Pass-A question

For each identity, Luna should ask:

> If I wanted to generate this visible concept but did not know its Danbooru tag, which existing shelf would I naturally open?

Not:

> What words occur in the tag?

Not:

> What other concepts are logically related?

Not:

> Which current taxonomy entry should I confirm?

Pass A does not see current Unified route assignment.

---

## 3. Route strength

For each selected route:

### CORE

The route expresses a central, user-intent-level way to find the visual.

A user could reasonably begin from this shelf before knowing the tag.

### SUPPORTING

The route is a real secondary lookup intent, but not one of the most obvious ways to find the concept.

### Do not select

Do not select a route merely because:
- one word in the canonical tag matches it;
- it is technically implicated;
- it is a generic modifier;
- it is true of many examples but not the concept being named.

Normally use one or two routes.

A third route is allowed only when it represents an independently strong image-generation intent.

---

## 4. Existing Unified route vocabulary

### PEOPLE_COUNT — 人物・人数

Use for:
- number of people;
- group-count/composition concepts;
- explicit solo/multiple-person count structure.

Do not use for:
- relationships between people;
- actions merely involving multiple people.

---

### RELATION_ROLE — 関係・役割

Use for:
- interpersonal role/relationship;
- dominance/submission role when role is the visual concept;
- relational composition not reducible to one action.

Do not use for:
- ordinary contact/action;
- person count alone.

---

### BODY_SITE — 身体・部位

Use for:
- anatomical body part as a central visual target;
- body-site-focused state where the user would naturally search by body area.

Examples of natural intent:
- breast-focused target;
- anal/buttock target;
- mouth/oral target;
- genital target;
- arm/leg/hand target when the body location is central.

Do not use merely because a body word occurs incidentally in an action phrase.

Hair/face appearance belongs to HAIR_FACE when that is the actual visible feature.

---

### HAIR_FACE — 髪・顔

Use for:
- hairstyle/hair state;
- facial feature/appearance;
- hair/face as the primary visible control.

Do not use for:
- facial emotion or gaze: EXPRESSION_GAZE;
- generic anatomical body targeting when hair/face appearance is not the concept.

---

### CLOTHING_EXPOSURE — 衣装・露出

Use for:
- garment identity;
- accessories when worn as apparel;
- clothing state;
- nudity/exposure;
- displaced/open/removed clothing when that state is image-defining.

Do not use for:
- a random object merely because it can be worn;
- a pose/action where clothing is incidental.

---

### TOOL_OBJECT — 道具・小物

Use for:
- a distinct prop, tool, toy, weapon, vehicle, food item, device, or foreground object;
- an object that the user would intentionally add to the generated scene.

Do not use for:
- location/background structure when the environmental context is the main intent;
- body part or apparel.

---

### LIVING — 生物・植物

Use for:
- non-character animals/plants/living organisms as scene/subject elements.

Do not use for:
- transformed humanoid state: NONHUMAN_TRANSFORM;
- named characters.

---

### NONHUMAN_TRANSFORM — 異形・変形

Use for:
- transformation or clearly nonhuman/anatomically altered state;
- monsterization/inhuman visual transformation.

Do not use for:
- ordinary animal/plant objects;
- generic fantasy role without a transformation/state component.

---

### ACTION_CONTACT — 行為・接触

Use for:
- actions;
- interactions;
- touching/contact;
- sex acts;
- manipulation of another person/body/object when the action is central.

Do not use for:
- a static body arrangement whose main user intent is posture/position: POSE_POSITION;
- relationship without a specific action.

An identity may naturally be both ACTION_CONTACT and POSE_POSITION when the action and positional geometry are independently useful ways to find it.

---

### POSE_POSITION — ポーズ・体位

Use for:
- posture;
- body position;
- limb arrangement;
- movement/locomotion concepts currently represented by the Unified pose route;
- sexual position;
- stable positional geometry of one or more people.

Important: the current UI label is "ポーズ・体位", while accepted #64 POSE_MOVEMENT also covers "動き". Pass A should judge the actual user discovery intent, not assume the existing label is already optimal.

Do not use just because an action produces a pose.

The position itself must be a meaningful visual lookup intent.

Danbooru itself distinguishes sexual actions and sexual positions as separate tag-group concepts, which supports keeping these discovery intents separable.

---

### EXPRESSION_GAZE — 表情・視線

Use for:
- facial expression/emotion;
- gaze direction;
- eye orientation as expression/viewing behavior.

Do not use for:
- eye color/shape as appearance;
- face identity/hairstyle.

---

### FLUID_EXCRETION — 体液・排泄

Use for:
- bodily fluid;
- ejaculation/fluids;
- urination/excretion/soiling where fluid/excretion is a central visual.

Do not use for:
- action-only concepts where fluid is not intrinsic.

---

### COMPOSITION_CAMERA — 構図・画角

Use for:
- viewpoint;
- crop/framing;
- camera angle;
- shot type;
- POV/compositional presentation.

Do not use for:
- physical place/background;
- body pose alone.

---

### SCENE_BACKGROUND — 場所・背景・場面

Use for:
- location;
- environment;
- background setting;
- scene context that a user intentionally chooses.

Object-vs-scene fixtures are not automatically dual-routed.

A door/window/counter should gain this route only when "environment/setting" is genuinely a natural lookup intent for that identity.

---

### LIGHT_TIME_WEATHER — 光・時間・天候

Use for:
- lighting condition;
- time of day;
- weather/atmospheric condition.

Do not use for:
- generic color;
- art style.

---

### COLOR_PATTERN_SHAPE — 色・柄・形

Use for:
- color/pattern/shape when this is itself a meaningful image-generation control;
- abstract appearance properties whose lookup intent is color/pattern/shape.

Important caution:

A color token inside a target identity does **not** automatically make this route CORE.

Examples such as color + garment / color + eyes can be semantically true but combinatorial. Pass A may mark SUPPORTING if a user would genuinely browse by color, but product adoption is decided later after full-population route-load analysis.

---

### STYLE_PROCESSING — 画風・加工

Use for:
- art style;
- rendering/processing;
- medium-like presentation;
- visual production technique.

Do not use for:
- scene content;
- content rating;
- color alone.

---

### TEXT_SYMBOL — 文字・記号

Use for:
- visible text;
- symbols;
- textual/layout elements that are intentionally generated.

Do not use for:
- names/titles merely because the canonical contains words.

---

### CONTENT_RATING — 内容区分・レーティング

Use for:
- true meta/content presentation categories;
- rating/content-state concepts that are themselves useful to browse.

Do not use as a catch-all for sexual content.

Sexual/general filtering is handled by #118 content intent, not by routing every sexual tag here.

---

## 5. Separate Special facets

The following remain separate filter axes and are **not substitutes for top-level routes**:

### Body-site facets
- BREAST_NIPPLE
- FEMALE_GENITAL
- MALE_GENITAL
- MOUTH_ORAL
- BUTTOCK_ANAL
- URETHRA

### Theme facets
- BDSM_RESTRAINT
- INJURY_R18G
- REPRO_PREGNANCY_LACTATION

A tag may have:
- ACTION_CONTACT route;
- POSE_POSITION route;
- BODY facet;
- THEME facet

at the same time.

This is desirable when each axis corresponds to a different user lookup intent.

---

## 5.5. Pass-A body/theme facet judgment

Because adult/sexual image generation is a core target workflow, Pass A should also independently record the existing fixed Special-style refinement concepts.

This is an **audit capture**, not permission to extend runtime facets to General.

### Body-site IDs

Select only when the site is explicit and central to the visual concept:

- `MALE_GENITAL`
- `BREAST_NIPPLE`
- `FEMALE_GENITAL`
- `MOUTH_ORAL`
- `BUTTOCK_ANAL`
- `URETHRA`

Examples:
- biting_breast -> BREAST_NIPPLE
- finger_in_another's_mouth -> MOUTH_ORAL
- standing_doggystyle -> no body-site facet merely from the act name unless a specific site is intrinsic/explicit.

Do not infer a body site from a broad sexual act when the exact site is not part of the tag meaning.

### Theme IDs

Select only when the theme is intrinsic to the concept:

- `BDSM_RESTRAINT`
- `INJURY_R18G`
- `REPRO_PREGNANCY_LACTATION`

Do not use theme facets as generic sexual-content labels.

### Why capture these in Pass A

Current Unified body/theme refinement is primarily populated from accepted Special metadata.

A full independent census can reveal:
- whether important General-only image-generation concepts naturally need the same refinement;
- whether current Special facet coverage is already sufficient;
- whether extending the facet model would improve usability enough to justify an architecture change.

Any General facet expansion requires a separate full-population product/performance gate.

---

## 6. Search-oriented identities

Use SEARCH_ORIENTED when the tag is mainly discoverable by its name/known reference rather than by a stable visual shelf, for example:
- named meme;
- event;
- franchise-specific reference;
- highly idiosyncratic proper phrase.

Do not confuse SEARCH_ORIENTED with SEMANTIC_UNRESOLVED.

A tag can be perfectly understood and still be better served by Japanese/alias search than browse.

---

## 7. Image-generation utility rules

A natural route should usually correspond to something a user intentionally controls in the generated image:

- who/what is present;
- body area;
- clothing/exposure;
- action;
- pose/position;
- object;
- environment;
- camera/composition;
- expression/gaze;
- lighting/weather/time;
- visual appearance/style;
- explicit adult body/theme facets.

Incidental facts are poor browse routes.

The key test is:

> Would selecting this shelf help a user formulate the scene they want?

This keeps the system aligned with image generation rather than taxonomic purity.

---

## 8. Search is complementary, not a reason to reject all browse

Current product strengths such as:
- Japanese search;
- aliases;
- canonical English;
- post-count sorting

reduce the need for redundant browse routes.

But "search can find it" is not by itself a reason to reject a natural route.

Browse exists specifically for cases where the user knows the visual concept but not the exact tag wording.

External tag tools similarly combine direct search/autocomplete with category/tree exploration rather than requiring a single mechanism.

---

## 9. Full-population reconciliation rule

After Pass A is frozen:

1. compare independent natural routes with current routes;
2. join Japanese searchability/aliases/usage;
3. compute route growth across all 31,003 identities;
4. examine repeated families;
5. decide whether missing CORE/SUPPORTING routes improve discovery enough to ship.

Do not use per-row semantic truth alone as production authority.

A route can be semantically natural yet product-negative if it destroys shelf selectivity at population scale.

---

## 10. Runtime rule

None of this route reasoning ships.

Production receives only the minimal confirmed route additions through the existing static browse metadata/index path.

No new runtime semantic engine.
