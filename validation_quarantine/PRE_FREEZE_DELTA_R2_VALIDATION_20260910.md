# Issue #32 — pre-freeze local delta R2 validation

Date: 2026-09-10
Branch: `dict-validation/quarantine`
Input local-scan commit: `33887fd3b839d3f3ab2abec38253d8dc44b00742`
Production `data/**`: unchanged
Rule: R2

## Verdict

**PASS_DELTA_REJECTED_NO_GENUINE_MISSING_SPECIAL**

The five quarantine-only rows discovered by the local protected-asset scan were validated as a delta only. The completed 2,788-row first pass was not rerun or altered.

Result:
- delta rows examined: 5 / 5
- `GENUINE_MISSING_SPECIAL`: 0
- promote to Special: 0
- rejected / retain provenance only: 5
- final evidence-derived Special count for the pre-freeze completeness gate: **2,788**

## Evidence boundary

The historical archive label `同名未確認候補（ユニーク）` is candidate provenance, not first-class Special authority. A meaningful English phrase, anatomical concept, pose name, or model response is also not sufficient by itself to establish a Special identity.

The local completeness scan already established that all five rows are absent from the frozen 2,788 set and from the current canonical/alias identity dictionaries, and that no Special ID or independent first-class Special authority was present in the scanned protected/ignored assets. The current retained Danbooru source / verified full knowledge-base and alias indexes were included in that scan.

External cross-checking was used only as independent corroboration and did not override project identity rules. Exact Danbooru authority for the four `*_removal` strings was not recovered. For `spread_eagle`, independent Danbooru-derived posture references use the established general pose tag `spread_eagle_position`; this supports treating the historical `spread_eagle` string as non-Special search/provenance wording rather than a missing first-class Special identity.

## Row dispositions

| Term | R2 disposition | Reason |
|---|---|---|
| `cervix_removal` | `REJECT_NO_INDEPENDENT_SPECIAL_AUTHORITY` | Historical unconfirmed candidate only; no Special ID, canonical/alias identity, or independent first-class Special authority. Anatomical meaning does not establish Special identity. |
| `fallopian_tubes_removal` | `REJECT_NO_INDEPENDENT_SPECIAL_AUTHORITY` | Same evidence pattern; no independent first-class Special authority recovered. |
| `ovaries_removal` | `REJECT_NO_INDEPENDENT_SPECIAL_AUTHORITY` | Same evidence pattern; no independent first-class Special authority recovered. |
| `uterus_removal` | `REJECT_NO_INDEPENDENT_SPECIAL_AUTHORITY` | Same evidence pattern; no independent first-class Special authority recovered. |
| `spread_eagle` | `REJECT_GENERAL_POSE_VARIANT_NOT_SPECIAL` | Historical candidate wording is not independently established as a Special. Danbooru-derived posture references use `spread_eagle_position` as the general pose tag; no evidence establishes `spread_eagle` as a separate first-class Special identity. |

All five retain `DO_NOT_PROMOTE`.

## Generation / model-scope handling

No generation-response claim was used to promote or reject Special identity. WAI17 / Illustrious / NoobAI / Anima behavior remains model-scoped. No broad+specific, actor/target/body-site, visibility, pose reliability, minimum-sufficient Prompt, or anti-support claim was converted into global production truth.

## Completeness conclusion

The local protected-asset scan itself returned `LOCAL_COMPLETENESS_DELTA_FOUND` because five explicitly retained historical candidates required follow-up. That delta has now been validated under R2 and produced **zero genuine missing Specials**.

Therefore the pre-freeze completeness condition is satisfied with final Special count **2,788**.

This result authorizes only transition to `READY_FOR_FINAL_PROMOTION_AUDIT`. It does **not** authorize production promotion, `data/**` modification, or merge to `main`. A separate independent final promotion audit remains mandatory.
