# Issue #132 — Codex Semantic Guardrails V1

Status: **MANDATORY OPERATIONAL SEMANTIC SUPPLEMENT / DOES NOT ALTER FROZEN VOCABULARY**

Effective forward-review boundary:
- Lane 1: lane-local 1126+
- Lane 2: lane-local 1226+
- Lane 3: lane-local 1201+

This file refines how the already-frozen Pass-A vocabulary is applied after the manual audit of the first saved population. It does **not** add routes, local refinements, body facets, theme facets, discovery modes, or strengths.

## 1. Core question

For every identity ask:

> If a user wanted to generate this visible concept but did not know the exact Danbooru tag, which existing shelf would they naturally open first?

Do not classify from token spelling alone. Do not optimize for agreement with the current product.

## 2. Manual-audit lessons that are mandatory going forward

### 2.1 Character cosplay / named costume references

A named `character_(cosplay)`-style identity is not automatically SEARCH_ORIENTED.

When the concept is also a stable visible costume choice:
- normally use `MIXED`;
- `CLOTHING_EXPOSURE` is the natural browse route;
- `CLOTHING/COSTUME` is the natural local refinement when applicable.

Use SEARCH_ORIENTED only when name/reference search is genuinely the useful discovery mechanism and no stable browse axis materially helps.

### 2.2 Named weapons, props, devices, transformation items

A proper name does not make a visible object search-only.

If the user can intentionally add the visible item to an image:
- consider `TOOL_OBJECT`;
- weapon identities should use `OBJECT_PROP/WEAPON` when the frozen local vocabulary fits;
- other props/devices may use the applicable existing object refinement;
- use MIXED when both the proper name and generic object browsing are materially useful.

### 2.3 Clothing-state concepts

When the named concept is the state of clothing rather than merely the garment identity, prefer the clothing-state refinement when it fits.

High-attention families include:
- torn;
- unworn;
- open;
- wet;
- pulled;
- lifted;
- removed;
- displaced;
- soiled.

Do not collapse these into ordinary everyday clothing merely because the garment name is present.

### 2.4 ACTION_CONTACT vs POSE_POSITION vs RELATION_ROLE

Keep these axes separate.

- manipulation, holding, pulling, adjusting, touching, using: `ACTION_CONTACT`;
- object manipulation should use `ACTION_CONTACT/OBJECT_USE` when that local meaning fits;
- person-to-person interaction should use `ACTION_CONTACT/INTERACTION` only when the interaction itself is the concept;
- stable body geometry, posture, relative placement, sexual position: `POSE_POSITION`;
- interpersonal status, role, dominance/submission role, relationship: `RELATION_ROLE`.

Do not route an ordinary action to INTERACTION merely because another person/object is involved.
Do not add POSE_POSITION merely because every action necessarily creates some pose.

### 2.5 Body hair, nails, and body-site features

`HAIR_FACE` is for head-hair/face/eye appearance. The presence of the word "hair" is not sufficient.

Examples such as:
- pubic hair;
- armpit hair;
- nipple hair;
- testicle hair;
- nails;

must be judged as body-site/body-feature concepts when that is the user's natural discovery intent. Do not use HAIR_FACE mechanically.

### 2.6 Color / pattern / shape

Do not add `COLOR_PATTERN_SHAPE` merely because a color or pattern adjective appears.

Use it as SUPPORTING only when color/pattern/shape is an independently realistic way a user would browse for the wanted visual. Keep the target object/body/clothing concept as the stronger route when appropriate.

Sibling identities should be reviewed consistently.

### 2.7 Object vs scene

A distinct foreground prop/tool/fixture that a user intentionally adds is normally `TOOL_OBJECT`.
A location/environment/background context is `SCENE_BACKGROUND`.

Do not dual-route every door/window/counter/fixture mechanically. Ask whether the object itself and the environment are independently useful lookup intents.

### 2.8 CONTENT_RATING

Sexual, violent, or unusual content does not itself imply `CONTENT_RATING`.

Use CONTENT_RATING only when the identity is genuinely about content classification, rating, censor/meta-content status, or an equivalent frozen semantic meaning.

### 2.9 Body/theme facets

Body and theme facets are selected only when intrinsic to the identity's visual meaning.

Do not infer them from common association.
Adult/sexual identities are normal in-scope data and receive the same evidence standard as other identities.

## 3. Research minimum

Use CHECKED only when both meaning and discovery intent are genuinely clear.

Use RESEARCHED when a material ambiguity could change:
- discovery mode;
- route;
- strength;
- local refinement;
- body/theme facet;
- vocabulary-gap decision.

Minimum research behavior:
- Danbooru-specific/booru-specific term: seek direct tag/wiki evidence first when available;
- named franchise/reference concept: seek an official/reference source when the reference meaning affects discovery;
- named meme/event/phrase: seek direct/reference evidence rather than inferring from spelling;
- if direct evidence remains insufficient after a bounded useful pass: use terminal `SEMANTIC_UNRESOLVED`.

A suffix, prefix, neighboring tag, or one lexical token is never sufficient evidence by itself for an unclear identity.

## 4. Decision-reason trace codes

Every new v2 write request must attach at least one short reason code to every semantic row. These codes are audit trace only; they do not change taxonomy.

Allowed codes:
- `COSTUME_REFERENCE`
- `NAMED_PROP`
- `WEAPON_PROP`
- `CLOTHING_STATE`
- `OBJECT_USE_ACTION`
- `PERSON_INTERACTION`
- `STATIC_POSITION`
- `RELATIONSHIP_ROLE`
- `BODY_SITE_FEATURE`
- `HEAD_HAIR_FACE_FEATURE`
- `FLUID_EXCRETION`
- `COLOR_PATTERN_SECONDARY`
- `OBJECT_SCENE_BOUNDARY`
- `NAMED_REFERENCE_WITH_VISUAL_AXIS`
- `SEARCH_BY_NAME_ONLY`
- `RESEARCH_UNRESOLVED`
- `VOCABULARY_GAP`
- `OTHER_DIRECT_VISUAL`

Use multiple codes only when each materially explains the classification.

## 5. Family-consistency requirement

Do not wait until the final 31,003-row review to look for systematic drift.

During QA, explicitly compare sibling/family decisions for:
- cosplay/named costume;
- named weapon/prop/device;
- clothing-state;
- action/contact/object-use;
- pose/position;
- role/relation;
- body-hair/nails/body-feature;
- color/pattern siblings;
- object-vs-scene boundary;
- body/theme facet families.

A detected family pattern is a QA signal, not permission to bulk-reclassify unseen rows.

## 6. Versioning rule

Every forward v2 request records:
- `semantic_policy_id`;
- `semantic_policy_git_blob_sha`;
- per-row decision reason codes.

Historical rows remain valid under their historical authority. A later policy version must be added as another allowed policy; do not retroactively invalidate old accepted windows solely because a newer policy exists.

If a later policy change reveals a semantic defect, target only the affected family/ranges for QA/repair.
