# Issue #132 — Phase 6 full discovery coverage audit

Date: 2026-09-22
Status: **FULL-POPULATION RESEARCH BASELINE COMPLETE / NO PRODUCTION CHANGE**

## 1. Why Phase 6 exists

The earlier bounded task comparison was useful as a regression check, but it is not sufficient to discover all usability gaps.

Phase 6 therefore switches the main research method to:

`full population -> deterministic census -> recurring gap clusters -> bounded semantic review -> regression tasks`

The task matrix from Phase 5 is retained only as a regression/reference set.

## 2. Authority and population

The audit reconstructs current discovery behavior from tracked accepted authority only:

- #64 General effective sidecar
- #56 accepted Special paths
- #76 Special v2 mapping/patches
- #96/#107 promoted Special metadata
- production Special generation profile
- #118 runtime identity authority
- current Unified browse mapping rules
- current explicit Special route overrides

Verified population:

- runtime identities: **31,003**
- General rows: **30,629**
- production Special rows: **3,059**
- General-only identities: **28,645**
- Special-only identities: **374**
- General+Special overlap identities: **1,984**
- Special -> #118 identity mapping: **3,059 / 3,059**
- unmapped: **0**
- ambiguous: **0**

## 3. Full census result

Final full-census buckets:

- **OK: 28,537**
- **NO_AUTHORITY: 2,393**
- **REVIEW: 73**
- **PROJECTION_GAP: 0** after accurately mirroring current `UnifiedBrowseOverlay`

Important correction:

An earlier run reported 48 apparent projection gaps. That was an audit-model defect: the first script version had not mirrored the existing generation-profile `pose / camera / scene` route enrichment. The script was corrected and the full census rerun. The corrected result is **0 mechanically proven projection gaps**.

This is important: #132 must not manufacture fixes from an inaccurate audit model.

## 4. Current discovery coverage

Identities reachable through at least one primary route or accepted Special facet:

- **28,601 / 31,003 = 92.25%**

No current route or facet:

- **2,402 / 31,003 = 7.75%**

Current multi-primary-route identities:

- **1,349**

General rows with at least one accepted secondary path:

- **680 / 30,629 = 2.22%**
- total General secondary paths: **681**

Interpretation:

The current system is not fundamentally missing browse coverage for most identities.

The weakness is concentrated in:
1. identities with no accepted browse authority;
2. a small Special `POSE_SCENE` ambiguity cluster;
3. potential multi-entry opportunities that must not be bulk-promoted without semantic review.

## 5. NO_AUTHORITY is mostly low-priority for this product goal

NO_AUTHORITY = **2,393**

By content intent:

- NON_SEXUAL: **2,293**
- SEXUAL: **41**
- CONTEXTUAL: **57**
- UNCLASSIFIED: **2**

By membership:

- General-only: **2,379**
- Special-only: **14**

Many non-sexual examples are named events, memes, proper nouns, franchise-specific terms, historical incidents, or other identities that #64 intentionally left unresolved.

Therefore:

**Do not attempt to force-classify all 2,393 rows merely to reach 100% browse coverage.**

For the current image-generation usability goal, the first meaningful no-authority review queue is only:

- **98 SEXUAL / CONTEXTUAL identities**

The audit now emits this deterministic queue as:

`adult_no_authority.csv`

## 6. REVIEW cluster

REVIEW = **73 identities**

All are related to accepted Special `POSE_SCENE` metadata with no current pose/camera/scene primary route.

Breakdown:

- **5**: `POSE_SCENE | POSE_COMPOSITION | pose_camera`
- **68**: broader/other generation families

The five strong rows align with the previously identified high-confidence pose-scene projection-gap pattern and are suitable for bounded semantic confirmation.

The remaining 68 must **not** be automatically mapped to `POSE_POSITION`.

The broad `POSE_SCENE` kind is intentionally heterogeneous. It contains examples whose actual generation role is:
- restraint action
- ordinary action
- semantic support
- body state/attribute
- direct composite
- context modifier
- clothing state
- spatial relation
- and other roles

Therefore:

`Special kind == POSE_SCENE`

is **not** sufficient authority for:

`add POSE_POSITION`.

The audit emits the full deterministic review queue as:

`pose_scene_review.csv`

## 7. Route-size / usability finding

Large top-level routes exist:

- CLOTHING_EXPOSURE: **8,972**
- TOOL_OBJECT: **5,691**
- ACTION_CONTACT: **3,928**
- BODY_SITE: **2,371**

However, under the SEXUAL + CONTEXTUAL population, the practical sizes are much smaller:

- ACTION_CONTACT: **1,370**
- CLOTHING_EXPOSURE: **1,202**
- BODY_SITE: **397**
- TOOL_OBJECT: **287**
- FLUID_EXCRETION: **189**
- RELATION_ROLE: **87**
- POSE_POSITION: **80**
- NONHUMAN_TRANSFORM: **64**

Existing General local routes already narrow the two largest adult-facing shelves:

### ACTION_CONTACT
- INTERACTION: 95 sexual / 292 contextual
- INTIMATE: 678 sexual / 92 contextual
- OBJECT_USE: 7 sexual / 22 contextual

### CLOTHING_EXPOSURE
- CLOTHING_STATE_EXPOSURE: 170 sexual / 354 contextual
- CLOTHING/EVERYDAY: 31 sexual / 433 contextual
- CLOTHING/ACCESSORY: 19 sexual / 67 contextual
- CLOTHING/COSTUME: 5 sexual / 12 contextual

Special facets are also bounded:

### Body facets
- BREAST_NIPPLE: 279 total
- MALE_GENITAL: 237
- FEMALE_GENITAL: 142
- MOUTH_ORAL: 115
- BUTTOCK_ANAL: 110
- URETHRA: 19

### Theme facets
- BDSM_RESTRAINT: 311
- INJURY_R18G: 79
- REPRO_PREGNANCY_LACTATION: 41

Conclusion:

**The current filter/local-facet structure already provides useful narrowing. A replacement browse UI is not justified by the full census.**

## 8. Heuristic multi-route candidates

The full census also generated broad REVIEW_ONLY pattern candidates:

- action + explicit body token, no body secondary: **1,038**
- color modifier, no color secondary: **1,791**
- place fixture, no object secondary: **46**
- clothing placement/state, no state secondary: **50**
- object fixture, no place secondary: **34**

These counts demonstrate why a blanket secondary-route rule is dangerous.

For example, automatically adding all color-modified tags to the color route would add a very large population and can make browse noisier rather than easier.

Therefore these are **candidate-discovery signals only**.

No route is accepted merely because it matches one of these patterns.

## 9. Product conclusion

Phase 6 changes the optimization target again, in a simpler direction.

Do **not**:
- replace the current UI;
- attempt full-population reclassification;
- add thousands of secondary routes;
- infer missing categories at runtime;
- build recommendation/scene-completion logic.

Instead:

1. preserve the existing search + browse UI;
2. fix only confirmed high-value multi-entry gaps;
3. review the 98 adult/contextual NO_AUTHORITY rows as the first no-authority population;
4. semantically resolve the 5 strong POSE_COMPOSITION/pose_camera rows;
5. treat the other 68 POSE_SCENE rows as heterogeneous review, not automatic pose mappings;
6. use large heuristic candidate families only to generate bounded review batches;
7. keep regression tasks for final validation, not gap discovery.

## 10. Next gate

### Gate A — 5 strong POSE_SCENE rows

Confirm whether the five `POSE_COMPOSITION / pose_camera` no-route identities should receive a static discovery-only route.

No family-wide rule until all five are checked.

### Gate B — 98 adult/contextual NO_AUTHORITY rows

Cluster the 98 rows by existing metadata/name pattern and determine:

- genuinely useful missing browse identity;
- searchable enough without browse;
- named/proper-noun/noise;
- needs a static route;
- remains unresolved.

### Gate C — recurring multi-route families

After A/B, rank the REVIEW_ONLY pattern families by:

- affected adult/contextual population;
- route-size impact;
- semantic precision;
- whether the current search/local route already solves the use case.

Only then propose any reusable secondary-route rule.

## 11. Evidence

Audit script:

`scripts/issue132/full_discovery_coverage_audit.py`

CI workflow:

`.github/workflows/issue132_full_discovery_audit.yml`

Final successful run:

- run: **35743383670**
- head: `520781aa6e3837cee03133bc3634456f4d1432cb`
- conclusion: **success**
- artifact: **issue132-full-discovery-audit**
- artifact id: **10699928908**
- artifact SHA-256: `0ea0cb6c9c681c315697cfbbf1ed9aecdac8dfaf33a96e1f3435fa037145c7f1`

Artifact files include:
- `identity_audit.csv`
- `adult_no_authority.csv`
- `pose_scene_review.csv`
- `pattern_candidates.csv`
- route/local/facet load CSVs
- `summary.json`

## 12. Safety

Research branch only.

No:
- main merge
- production taxonomy mutation
- production catalog rebuild
- UserData mutation
- runtime promotion
- search ranking change
- #64/#76/#118 authority rewrite
