# Recommendation semantics sidecars — Stage 8A v2

Stage 8A adds display-only meaning metadata to an existing Stage 6
`RecommendationCandidate`. It never changes the candidate object, its raw
statistics, its rank, or whether it is present.

## Semantic labels

Path: `data/semantic/recommendation_semantic_labels.csv`

| Column | Meaning |
|---|---|
| `canonical_tag` | Exact Danbooru canonical key; unique primary key |
| `semantic_role` | Reviewed Stage 8A role enum |
| `source` | Provenance label |
| `note` | Audit note |

Accepted roles are `SUBJECT_BASIC`, `BODY_PART`, `IMPLEMENT`,
`ACTION_SUPPORT`, `POSE`, `CAMERA_COMPOSITION`, `STATE_REACTION`,
`APPEARANCE_CLOTHING`, `SITUATION_RELATION`, and `UNCLASSIFIED`. A canonical
absent from this small sidecar is treated as `UNCLASSIFIED`; it remains in the
Recommendation result and receives no category badge.

## Generation hint rules

Path: `data/semantic/recommendation_generation_hints.csv`

| Column | Meaning |
|---|---|
| `rule_id` | Unique rule identity |
| `priority` | Deterministic order within the same precedence tier |
| `when_semantic_role` | Optional exact semantic role condition |
| `when_same_stat_canonical` | Optional boolean relation condition |
| `when_bucket` | Optional `common` or `rare` condition |
| `when_low_support` | Optional boolean condition; low support is `co_count <= 2` |
| `kind` | Reviewed interpretation kind enum |
| `message_ja` | Short Japanese generation-reading text |
| `source` | Provenance label |
| `note` | Audit note |

Rules produce two independent outputs. An unconditional semantic-role rule
produces `generation_hint`, which states what the classified tag can clarify
in generation. SAME_STAT, rare, and rare-plus-low-support rules produce
additive evidence/context notes. Context notes never replace the semantic-role
generation hint. Within each note class, the most constrained matching rule is
selected, then `priority` and `rule_id` break ties.

The production sidecar has no common-only `INDIRECT_SUPPORT` rules for
`BODY_PART`, `STATE_REACTION`, or `APPEARANCE_CLOTHING`. A role plus the common
bucket is not enough evidence to claim weak direct contribution.

`SAME_STAT_CANONICAL` means exact equality with one selected Special's
statistics canonical. It does not assert synonymy and does not replace Prompt
identity.

## Runtime view model

`DecoratedRecommendationCandidate` contains the original candidate plus:

- `semantic_role`
- `semantic_label_ja`
- `relation_flags`
- `generation_hint_kind`
- `generation_hint_ja`
- `evidence_note_kinds`
- `evidence_notes_ja`

The decorator is local, deterministic, and offline. It performs no filtering,
ranking, score fusion, automatic Prompt action, LLM call, network call, or API
call.
