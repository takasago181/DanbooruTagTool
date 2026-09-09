# Batch 22 R2 Integrity / False-PASS Audit

Range: 2101-2200
Rule: R2

## Static integrity
- durable blocks: 5 x 20 rows
- sequences: exactly 2101-2200
- missing sequences: 0
- duplicate sequences: 0
- batch values: all 22
- final states: PASS 100 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0
- candidate_fixes additions: 0
- new revalidation items from Batch22: 0
- semantic-support coverage delta: 0; remains 55/58

## High-risk deep review
A-risk PASS rows were all deep-reviewed and are included in the false-PASS sample:
- 2137 `downblouse`
- 2138 `downpants`
- 2139 `upskirt`
- 2140 `ass focus`
- 2141 `crotch focus`
- 2176 `breast focus`

All six keep `POSE_COMPOSITION / camera / STRUCTURED` and `CameraRequirementOverride=true` as structural visibility/composition metadata only. `STAGE_10_KNOWLEDGE_HANDOFF.md` supports minimal role-separated camera/visibility handling but explicitly leaves exact model-family camera tuning on HOLD. Therefore these PASS verdicts do not assert automatic support insertion, universal camera tags, or exact generation effectiveness.

Damage/anatomy-state rows 2163-2167 do not assert anatomy-negative interaction. Alias rows preserve exact Special identity and use canonical linkage for statistics only. Semantic-role rows remain search/support-only and do not assert direct model recognition or generation equivalence. Blank requirement fields remain UNKNOWN/not asserted rather than errors.

## Deterministic PASS sample
R2 target for 100 PASS rows: 20 rows (20%, max 20).

Sampling method: include every A-risk PASS, then deterministic spread across remaining B-risk rows and family/role groups.

Sampled sequences:
2101, 2108, 2115, 2122, 2129, 2137, 2138, 2139, 2140, 2141, 2148, 2155, 2162, 2169, 2176, 2183, 2188, 2192, 2196, 2200

Re-audit result:
- sampled PASS: 20 / 100
- false-PASS found: 0
- S/A false-PASS: 0
- expanded sample required: NO

## Cross-consistency
- 2137-2141 and 2176 use the same structural-only camera boundary consistently.
- clothing/exposure rows remain DIRECT and do not gain inferred bodypart/pose support merely from wording.
- scene/relation SUPPORT rows are not promoted to CORE_SUPPORT/default-on behavior.
- Alias/Semantic lanes remain distinct from statistical canonical linkage and generation-response claims.

## Gate
**Batch 22 R2 acceptance gate: PASS**

Safe next first-pass sequence: 2201.
Production/main modified: NO.
