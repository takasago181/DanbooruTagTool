# Issue #94 final candidate/exclusion artifacts v1

Status: **MATERIALIZED FROM 324/324 FINAL HUMAN REVIEW / NO PRODUCTION MUTATION**

- final candidates: **195**
- exclusion ledger rows: **129**
  - `GENERAL_ONLY`: **124**
  - `DUPLICATE_ALREADY_COVERED`: **5**
- `CONTENT_FILTER_USED=NO`
- `PRODUCTION_FILES_CHANGED=NO`
- `ISSUE70_MUTATED=NO`

## Candidate post-count distribution

- maximum: **286,238**
- median: **736**
- minimum: **50**

| post_count bucket | candidates |
|---|---:|
| `>=100k` | 5 |
| `10k-99,999` | 33 |
| `1k-9,999` | 48 |
| `100-999` | 88 |
| `<100` | 21 |

## Candidate concept areas

| area | candidates |
|---|---:|
| `SPECIAL_EXPOSURE_CLOTHING_STATE` | 84 |
| `SPECIAL_BODY_RELATION_STATE` | 32 |
| `SPECIAL_R18G_BODY_STATE` | 16 |
| `SPECIAL_REPRODUCTION_FLUID` | 15 |
| `SPECIAL_INTIMATE_ADORNMENT_STATE` | 13 |
| `SPECIAL_BDSM_RESTRAINT` | 10 |
| `GENERAL_OTHER` | 8 |
| `BOUNDARY_CONCEPT` | 5 |
| `SPECIAL_SEX_DEVICE` | 3 |
| `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | 2 |
| `SPECIAL_CLOTHING_BODY_RELATION` | 2 |
| `SPECIAL_GARMENT_SUBTYPE` | 2 |
| `SPECIAL_NAMED_POSE` | 2 |
| `SPECIAL_SEXUAL_RELATION` | 1 |

## Highest post-count candidates

| canonical | post_count | area |
|---|---:|---|
| `clothes_lift` | 286,238 | `BOUNDARY_CONCEPT` |
| `skindentation` | 161,742 | `GENERAL_OTHER` |
| `thick_thighs` | 159,807 | `GENERAL_OTHER` |
| `ass_visible_through_thighs` | 117,628 | `SPECIAL_EXPOSURE_CLOTHING_STATE` |
| `clothes_pull` | 108,268 | `BOUNDARY_CONCEPT` |
| `thigh_gap` | 97,349 | `GENERAL_OTHER` |
| `lifting_own_clothes` | 88,148 | `GENERAL_OTHER` |
| `breast_press` | 68,311 | `SPECIAL_BODY_RELATION_STATE` |
| `breasts_apart` | 61,893 | `SPECIAL_EXPOSURE_CLOTHING_STATE` |
| `micro_bikini` | 59,624 | `SPECIAL_EXPOSURE_CLOTHING_STATE` |
| `blood_on_face` | 59,531 | `SPECIAL_R18G_BODY_STATE` |
| `mole_on_breast` | 58,430 | `SPECIAL_INTIMATE_ADORNMENT_STATE` |
| `bikini_top_only` | 43,620 | `SPECIAL_EXPOSURE_CLOTHING_STATE` |
| `bouncing_breasts` | 38,896 | `SPECIAL_EXPOSURE_CLOTHING_STATE` |
| `breasts_squeezed_together` | 37,542 | `SPECIAL_BODY_RELATION_STATE` |
| `huge_ass` | 36,503 | `GENERAL_OTHER` |
| `hand_between_own_legs` | 36,500 | `SPECIAL_EXPOSURE_CLOTHING_STATE` |
| `blood_on_clothes` | 35,529 | `SPECIAL_R18G_BODY_STATE` |
| `arm_under_breasts` | 34,473 | `SPECIAL_EXPOSURE_CLOTHING_STATE` |
| `midriff_peek` | 31,330 | `SPECIAL_EXPOSURE_CLOTHING_STATE` |

## Lowest post-count candidates

Low frequency is retained when the concept still has deep discovery value; post_count is not an admission threshold.

| canonical | post_count | area |
|---|---:|---|
| `hand_grabbing_both_breasts` | 50 | `SPECIAL_BODY_RELATION_STATE` |
| `muzzle_gag` | 50 | `SPECIAL_BDSM_RESTRAINT` |
| `highleg_shorts` | 52 | `SPECIAL_GARMENT_SUBTYPE` |
| `pantyhose_around_legs` | 54 | `SPECIAL_EXPOSURE_CLOTHING_STATE` |
| `swimsuit_around_one_leg` | 60 | `SPECIAL_EXPOSURE_CLOTHING_STATE` |
| `holding_butt_plug` | 62 | `SPECIAL_SEX_DEVICE` |
| `tail_between_breasts` | 63 | `SPECIAL_EXPOSURE_CLOTHING_STATE` |
| `framed_crotch` | 64 | `SPECIAL_EXPOSURE_CLOTHING_STATE` |
| `implied_male_pregnancy` | 65 | `SPECIAL_REPRODUCTION_FLUID` |
| `touching_another's_crotch` | 68 | `SPECIAL_BODY_RELATION_STATE` |
| `holding_another's_legs_back` | 69 | `SPECIAL_BODY_RELATION_STATE` |
| `v_over_crotch` | 69 | `SPECIAL_EXPOSURE_CLOTHING_STATE` |
| `holding_own_leg_back` | 80 | `SPECIAL_BODY_RELATION_STATE` |
| `head_between_legs` | 89 | `SPECIAL_EXPOSURE_CLOTHING_STATE` |
| `implied_lactation` | 91 | `SPECIAL_REPRODUCTION_FLUID` |
| `multiple_pregnancy` | 92 | `SPECIAL_REPRODUCTION_FLUID` |
| `tattoo_between_breasts` | 92 | `SPECIAL_EXPOSURE_CLOTHING_STATE` |
| `bikini_top_peek` | 96 | `SPECIAL_EXPOSURE_CLOTHING_STATE` |
| `fake_pregnancy` | 96 | `SPECIAL_REPRODUCTION_FLUID` |
| `biting_ass` | 97 | `SPECIAL_BODY_RELATION_STATE` |

## Outputs

- `docs/issue94/special_gap_candidates_v1.csv` — 195 final candidate rows, sorted by post_count descending.
- `docs/issue94/special_gap_exclusion_ledger_v1.csv` — 124 General-only + 5 substantive duplicate rows.

These are audit deliverables only. They do not promote any candidate into the production Special dictionary.
