# Issue #132 — Unified route systemic-risk audit

Date: 2026-09-23 JST
Status: **DEV/AUDIT CONTEXT ONLY / HIDDEN FROM LUNA PASS A**

## 1. Purpose

This document records possible **system-level** discovery mismatches in the current General/Special -> Unified projection.

It is not a list of confirmed bugs.

It is deliberately hidden from Luna Pass A to avoid anchoring the independent review.

After the 31,003-row independent discovery map is frozen, use this document to explain large repeated disagreement clusters.

---

## 2. Current projection summary

### PEOPLE_COUNT

Current source:
- General PERSON_COUNT -> PEOPLE_COUNT

Current UI label:
- 人物・人数

Accepted General source semantics:
- 人物・人数・役柄

Risk:
- General role/archetype concepts may be hidden behind a label that sounds count-only.
- Special role/relationship concepts instead map to RELATION_ROLE.

Audit question:
- Is a repeated PEOPLE_COUNT vs RELATION_ROLE disagreement actually a label/mapping problem?

---

### RELATION_ROLE

Current source:
- Special PERSON_RELATION -> RELATION_ROLE

Current UI label:
- 関係・役割

Risk:
- Similar role concepts can be split between General PEOPLE_COUNT and Special RELATION_ROLE depending on source authority.

Do not solve with per-row #132 overrides until the full cluster is understood.

---

### BODY_SITE

Current sources:
- General BODY_PART -> BODY_SITE
- Special BODY_STATE -> BODY_SITE

Current UI label:
- 身体・部位

Accepted General semantics:
- 身体・部位・状態
- includes injury/fluid concepts in its discovery question.

Risk:
- UI wording under-describes "state".
- General body-fluid/state tags can share BODY_SITE while comparable Special concepts may map elsewhere.

---

### HAIR_FACE

Current source:
- General HAIR_FACE -> HAIR_FACE

Special:
- no direct Special kind -> HAIR_FACE mapping

Known risk:
- Special BODY_STATE concepts whose visible defining feature is hair/face can remain under BODY_SITE.

Known Phase 1 example:
- sex_hair

Audit question:
- Is this a small exception set or a systematic Special projection gap?

---

### CLOTHING_EXPOSURE

Current sources:
- General CLOTHING -> CLOTHING_EXPOSURE
- General CLOTHING_STATE_EXPOSURE -> CLOTHING_EXPOSURE
- Special CLOTHING_EXPOSURE -> CLOTHING_EXPOSURE

Strength:
- intentionally combines identity + worn/exposure state at the Unified top level.

Risk:
- large shelf;
- distinction survives only through General local subroutes and other facets.

Audit:
- measure top-level-only additions before adding #132 routes.

---

### TOOL_OBJECT

Current sources:
- General OBJECT_PROP -> TOOL_OBJECT
- Special TOOL_OBJECT -> TOOL_OBJECT

Risk:
- environmental fixtures can be semantically object-like or scene-like.
- do not automatically dual-route every door/window/counter family.

---

### LIVING

Current source:
- General LIVING_NATURE -> LIVING

No major projection conflict identified yet.

---

### NONHUMAN_TRANSFORM

Current source:
- Special NONHUMAN_TRANSFORMATION -> NONHUMAN_TRANSFORM

Risk:
- General fantasy creature identities are LIVING, while transformation/state concepts are Special.
- verify full-population user mental model before changing anything.

---

### ACTION_CONTACT

Current sources:
- General ACTION_CONTACT -> ACTION_CONTACT
- Special ACTION_CONTACT -> ACTION_CONTACT

Strength:
- strong cross-source alignment.

Known multi-axis pressure:
- action + body target;
- action + sexual position;
- action + clothing state.

These should be evaluated as discovery multi-entry questions rather than primary-class errors.

---

### POSE_POSITION

Current direct source:
- General POSE_MOVEMENT -> POSE_POSITION

Special:
- POSE_SCENE has no direct `SpecialRoute` mapping.
- selected generation-profile roles are enriched through `UnifiedBrowseOverlay`.

Current UI label:
- ポーズ・体位

Accepted General label:
- ポーズ・動き

Known risk:
- movement/locomotion is under-described by the UI label.
- Special POSE_SCENE is broader and can lose a pose/scene route unless additional generation metadata projects it.

Known Phase 1 cluster:
- five pose_camera identities.

This is a high-priority systemic explanation candidate if Pass A produces a large mismatch.

---

### EXPRESSION_GAZE

Current sources:
- General EXPRESSION_EMOTION -> EXPRESSION_GAZE
- General GAZE_ORIENTATION -> EXPRESSION_GAZE

Strength:
- deliberate top-level merge.

Risk:
- local distinction exists as General local routes.
- verify UI remains understandable without adding a new top-level axis.

---

### FLUID_EXCRETION

Current direct source:
- Special FLUID_EXCRETION -> FLUID_EXCRETION

General:
- #64 BODY_PART discovery semantics explicitly mention body fluids, therefore some General fluid concepts may project to BODY_SITE rather than FLUID_EXCRETION.

Risk:
- cross-source inconsistency for visually similar fluid/excretion concepts.

If Pass A repeatedly selects FLUID_EXCRETION for General identities currently in BODY_SITE, inspect one mapping/systemic fix before row overlays.

---

### COMPOSITION_CAMERA

Current sources:
- General COMPOSITION_CAMERA -> COMPOSITION_CAMERA
- selected Special generation-profile camera enrichment

Risk:
- Special broad POSE_SCENE does not automatically map here.

---

### SCENE_BACKGROUND

Current sources:
- General PLACE_BACKGROUND -> SCENE_BACKGROUND
- selected Special SCENE_CONTEXT generation enrichment

Risk:
- object/place fixtures;
- broad Special scene semantics not always projected.

---

### LIGHT_TIME_WEATHER

Current source:
- General LIGHT_TIME_WEATHER -> LIGHT_TIME_WEATHER

No major cross-source conflict identified yet.

---

### COLOR_PATTERN_SHAPE

Current source:
- General COLOR_APPEARANCE -> COLOR_PATTERN_SHAPE

Accepted #64 boundary:
- independent color/pattern/shape features belong here;
- color modifiers of objects/eyes keep the target as primary.

This is important evidence against blindly adding every color-modified identity as a secondary route.

Full Pass A may still select color as SUPPORTING; production adoption is a population-scale decision.

---

### STYLE_PROCESSING

Current source:
- General STYLE_QUALITY_META -> STYLE_PROCESSING

Current UI label:
- 画風・加工

Accepted General semantics:
- includes some screen/presentation processing.

Risk:
- UI wording may under-describe screen-expression/layout processing.

---

### TEXT_SYMBOL

Current source:
- General TEXT_SYMBOL -> TEXT_SYMBOL

General local routes:
- layout
- symbol
- text

Strength:
- already has useful local narrowing.

---

### CONTENT_RATING

Current source:
- Special META_EXPRESSION -> CONTENT_RATING

Current UI label:
- 内容区分・レーティング

Special source label:
- 表現・メタ

Risk:
- `META_EXPRESSION` may be semantically broader than "rating/content classification".

If Pass A systematically selects STYLE_PROCESSING / TEXT_SYMBOL / other visual routes for these identities, inspect mapping/label scope before per-row fixes.

---

## 3. Systemic-resolution order

When a large full-population disagreement cluster appears:

1. verify whether the current UI label describes the accepted source population;
2. verify the single General/Special -> Unified mapping;
3. verify owner taxonomy authority;
4. only then consider identity-level #132 secondary routes.

This order minimizes:
- overlay size;
- runtime cost;
- code branches;
- future maintenance.

---

## 4. Do not expose to Pass A

This file is explicitly DEV/AUDIT context.

Luna Pass A should not see it.

It exists to interpret the independent full-population diff after the fact.
