# Issue #96 taxonomy final summary v1

Status: **195/195 TAXONOMY RESOLVED / JA + DUPLICATE VALIDATION PENDING / NO PRODUCTION MUTATION**

- total: **195**
- conservative auto-resolved: **137**
- bounded human-resolved: **58**
- unresolved: **0**

## Kind counts

- `ACTION_CONTACT`: **30**
- `BODY_STATE`: **30**
- `CLOTHING_EXPOSURE`: **91**
- `FLUID_EXCRETION`: **24**
- `POSE_SCENE`: **8**
- `TOOL_OBJECT`: **12**

## Body-site facet counts

- `BREAST_NIPPLE`: **45**
- `BUTTOCK_ANAL`: **22**
- `FEMALE_GENITAL`: **1**
- `MOUTH_ORAL`: **11**

## Theme counts

- `BDSM_RESTRAINT`: **11**
- `INJURY_R18G`: **17**
- `REPRO_PREGNANCY_LACTATION`: **16**

## Resolution notes

The 58 mixed/boundary rows were reviewed as a bounded set. Semantic home is independent from body-site/theme facets: gag objects stay TOOL_OBJECT, applying_gag stays ACTION_CONTACT, presenting/legs-back relations use POSE_SCENE, and morphology/mark states use BODY_STATE.
`gag_around_neck` and `holding_gag` explicitly clear the lexical MOUTH_ORAL prescreen hint because the gag is not located in the mouth in those identities.
`blood_on_hand`, `holding_pregnancy_test`, and `leash_in_mouth` receive their relevant cross-cutting theme even though their #94 concept-area family did not mechanically supply it.

`CONTENT_FILTER_USED=NO`  
`PRODUCTION_FILES_CHANGED=NO`  
`ISSUE70_MUTATED=NO`
