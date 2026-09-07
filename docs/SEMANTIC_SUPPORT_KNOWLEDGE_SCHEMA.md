# Semantic Support Knowledge Schema — Stage 8B Pilot

Stage 8B adds an offline, reviewed sidecar for meaning-based auxiliary candidates.
It does not change Special identity, Danbooru canonical identity, Recommendation
statistics, ranking, or Prompt output unless the user explicitly presses `＋追加`.

## Special profile

`data/semantic/semantic_support_profiles.csv` has one row per explicit
`special_id` and `candidate_canonical` pair.

| Column | Meaning |
|---|---|
| `special_id` | Existing Special ID; the persistent owner key |
| `support_slot` | One of SUBJECT_BASIC, BODY_PART, IMPLEMENT, ACTION_SUPPORT, POSE, CAMERA_COMPOSITION, STATE_REACTION, or SPATIAL_ASSIGNMENT |
| `support_class` | `CORE_SUPPORT` or `OPTIONAL_VARIATION` |
| `candidate_canonical` | Exact current Danbooru canonical |
| `priority` | Reviewed display order within the explicit knowledge layer |
| `reason_ja` | Short Japanese explanation of generation use |
| `evidence_level` | SOURCE_VERIFIED, SEMANTIC_CURATED, MODEL_OBSERVED, or USER_ENV_VERIFIED |
| `evidence_source` | Provenance identifier |
| `generation_test_status` | Generation evidence status; Pilot rows use NOT_TESTED |
| `enabled` | Only true rows can appear at runtime |
| `intent_axis`, `intent_direction` | Optional intent metadata; display/ranking independent |
| `combination_mode`, `choice_group` | ADDITIVE, ALTERNATIVE, or CONTEXTUAL relation metadata |
| `evidence_ref`, `test_profile_id`, `model_scope`, `note` | Trace and review metadata |

The runtime rejects unknown Special IDs, noncanonical candidates, invalid enums,
duplicates, incomplete enabled rows, incomplete ALTERNATIVE groups, and incomplete
model-observation provenance. Disabled rows remain auditable and are hidden.

## Family profile

`data/semantic/family_support_rules.csv` has the same candidate metadata with
`family_rule_id` as its owner. The Stage 8B Pilot production file contains
the header only. Family loading and precedence are implemented and tested, but
no family rule is activated before Stage 8C coverage review.

When both layers provide the same canonical for one selected Special, the
Special row overrides that Special's family row. Other candidates form a
deterministic union. The aggregate canonical stays one UI candidate, while its
`relations` tuple keeps every selected-Special relation independently. Each
relation retains owner Special ID, source owner, slot, class, reason, intent,
combination, evidence, provenance, and generation-test trace. Relation order is
deterministic and independent of selected-Special order. Candidate rows sort by
explicit Special source, priority, then canonical.

## Runtime boundary

Only explicit enabled rows generate candidates. Missing profiles and empty
family coverage return `NO_SUGGESTION` (an empty candidate tuple). No tag-name
substring, regex, semantic similarity, severity rule, Recommendation statistic,
LLM, API, or network lookup is used. Support objects deliberately contain no
base_count, co_count, rate, or lift fields.
