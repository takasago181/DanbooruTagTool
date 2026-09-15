# Issue #94 Special gap prescreen v2

Status: **FULL 29,021-ROW MEANING-FIRST PRESCREEN COMPLETE / REGRESSION-CHECKED / NO PRODUCTION MUTATION**

## Decision model

v2 separates Stage A concept meaning from Stage B Special product fit. Lexical similarity, nearest Special score, token count, and surface patterns are audit context only; none can independently make a row a candidate.

- Stage A first recognizes whole-tag families such as ordinary object placement, named/contextual identity, garment state, sexual relation, device/restraint, fluid/reproduction, R18G body state, and specialized pose.
- Stage B then asks whether the concept helps a user discover a niche/complex concept through the deep Special dictionary.
- `CONTENT_FILTER_USED=NO`: adult, explicit, fetish, BDSM, fluid, anatomical, gore, violent, taboo, and grotesque content are not exclusion grounds.

## v2 counts

- total processed: **29,021** (`GENERAL_ONLY_GAP` input; expected 29,021)

| status | count |
|---|---|
| `LIKELY_CANDIDATE` | `297` |
| `LIKELY_GENERAL_ONLY` | `28711` |
| `POSSIBLE_DUPLICATE` | `4` |
| `NEEDS_REVIEW` | `9` |

| priority | count |
|---|---|
| `P0` | `46` |
| `P1` | `260` |
| `P2` | `4` |
| `P3` | `28711` |

Confidence distribution: HIGH=6,782, MEDIUM=22,230, LOW=9.

## Concept area distribution

Stage A whole-tag concept-family counts:

| concept area | count |
|---|---|
| `BOUNDARY_CONCEPT` | `9` |
| `GENERAL_APPEARANCE_SIZE_COLOR` | `2220` |
| `GENERAL_NAMED_OR_CONTEXTUAL` | `3580` |
| `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `753` |
| `GENERAL_ORDINARY_CLOTHING_STATE` | `172` |
| `GENERAL_ORDINARY_SUBTYPE` | `7` |
| `GENERAL_OTHER` | `21979` |
| `SPECIAL_BDSM_RESTRAINT` | `10` |
| `SPECIAL_BODY_RELATION_STATE` | `46` |
| `SPECIAL_CLOTHING_BODY_RELATION` | `24` |
| `SPECIAL_EXPOSURE_CLOTHING_STATE` | `161` |
| `SPECIAL_GARMENT_SUBTYPE` | `2` |
| `SPECIAL_INTIMATE_ADORNMENT_STATE` | `17` |
| `SPECIAL_NAMED_POSE` | `2` |
| `SPECIAL_OVERLAP_BOUNDARY` | `4` |
| `SPECIAL_R18G_BODY_STATE` | `16` |
| `SPECIAL_REPRODUCTION_FLUID` | `15` |
| `SPECIAL_SEXUAL_RELATION` | `1` |
| `SPECIAL_SEX_DEVICE` | `3` |

## v1 → v2 transition matrix

| v1 \ v2 | LIKELY_CANDIDATE | LIKELY_GENERAL_ONLY | POSSIBLE_DUPLICATE | NEEDS_REVIEW |
|---|---:|---:|---:|---:|
| `LIKELY_CANDIDATE` | 281 | 1671 | 0 | 2 |
| `LIKELY_GENERAL_ONLY` | 13 | 26050 | 0 | 0 |
| `POSSIBLE_DUPLICATE` | 0 | 0 | 4 | 0 |
| `NEEDS_REVIEW` | 3 | 990 | 0 | 7 |

v1 `LIKELY_CANDIDATE` rows moved to v2 `LIKELY_GENERAL_ONLY`: **1,671**.

## Regression false-positive set

- regression set total: **12**
- regression pass (v2 General-only): **12**
- regression fail: **0**

| canonical | Stage A | v2 | reason |
|---|---|---|---|
| `type_91_armor-piercing_shell` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `LIKELY_GENERAL_ONLY` | `weapon/ammunition compound; ‘piercing’ is not body piercing` |
| `camera_around_neck` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `LIKELY_GENERAL_ONLY` | `ordinary object or accessory placed at a body location; placement alone is General discovery` |
| `finger_on_eyewear` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `LIKELY_GENERAL_ONLY` | `ordinary object or accessory placed at a body location; placement alone is General discovery` |
| `butterfly_on_face` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `LIKELY_GENERAL_ONLY` | `ordinary object or accessory placed at a body location; placement alone is General discovery` |
| `cat_on_head` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `LIKELY_GENERAL_ONLY` | `ordinary object or accessory placed at a body location; placement alone is General discovery` |
| `gauze_on_hand` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `LIKELY_GENERAL_ONLY` | `ordinary object or accessory placed at a body location; placement alone is General discovery` |
| `hand_on_wall` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `LIKELY_GENERAL_ONLY` | `ordinary object or accessory placed at a body location; placement alone is General discovery` |
| `standing_on_box` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `LIKELY_GENERAL_ONLY` | `ordinary standing/location or object interaction; not a Special-specific pose` |
| `standing_on_sword` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `LIKELY_GENERAL_ONLY` | `ordinary standing/location or object interaction; not a Special-specific pose` |
| `standing_on_chair` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `LIKELY_GENERAL_ONLY` | `ordinary standing/location or object interaction; not a Special-specific pose` |
| `butterfly_on_head` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `LIKELY_GENERAL_ONLY` | `ordinary object or accessory placed at a body location; placement alone is General discovery` |
| `headphones_around_neck` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `LIKELY_GENERAL_ONLY` | `ordinary object or accessory placed at a body location; placement alone is General discovery` |

The regression set includes every requested strong negative control, including `type_91_armor-piercing_shell`, ordinary object/body placements, ordinary hand/finger actions, and ordinary standing locations.

## Meaning-based audit samples

- v1 Candidate audit sample: **125**
- v1 Needs-review audit sample: **125**
- deterministic seed: `9402`; these are audit samples, not a claim that the remaining population was human-reviewed.

| canonical | v1 | Stage A | Stage B | v2 | priority |
|---|---|---|---|---|---|
| `animal_ear_piercing` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `animal_holding_leash` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `apple_on_head` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `arm_on_another's_shoulder` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `backpack_on_one_shoulder` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `bandage_over_one_eye` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `bandaid_on_hand` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `bandaid_on_stomach` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `between_fingers` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `bike_shorts_under_shorts` | `LIKELY_CANDIDATE` | `GENERAL_ORDINARY_CLOTHING_STATE` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `bikini_bottom_around_leg` | `LIKELY_CANDIDATE` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `bikini_over_clothes` | `LIKELY_CANDIDATE` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `bite_mark_on_ass` | `LIKELY_CANDIDATE` | `SPECIAL_BODY_RELATION_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `biting_another's_tail` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `blood_in_hair` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `blood_on_arm` | `LIKELY_CANDIDATE` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `blood_on_weapon` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `bodystocking_only` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `book_on_breasts` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `breast_lift` | `LIKELY_CANDIDATE` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `buruma_under_skirt` | `LIKELY_CANDIDATE` | `SPECIAL_CLOTHING_BODY_RELATION` | `PLAUSIBLE_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `candle_on_head` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `cat_on_head` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `clothes_between_breasts` | `LIKELY_CANDIDATE` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `coat_on_head` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `covered_piercing` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `cross_piercing` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `drinking_straw_in_mouth` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `duck_on_head` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `eyes_visible_through_headwear` | `LIKELY_CANDIDATE` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `feet_on_table` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `finger_on_eyewear` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `finger_on_trigger` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `finger_piercing` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `floating_blood` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `flower_tattoo` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `foot_tattoo` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `fourth_position_of_the_arms` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `frog_on_head` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `goggles_around_arm` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `grabbed_breast_over_shoulder` | `LIKELY_CANDIDATE` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `grabbing_another's_hand` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `hair_between_breasts` | `LIKELY_CANDIDATE` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `hair_on_tail` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `hair_over_ass` | `LIKELY_CANDIDATE` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `half_lotus_position` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `hand_on_another's_shoulder` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `hand_on_eyewear` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `hand_on_ground` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `hand_on_own_hip` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `hand_over_own_mouth` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `hand_tattoo` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `hand_under_shirt` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `hands_on_own_legs` | `LIKELY_CANDIDATE` | `SPECIAL_BODY_RELATION_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `head_on_another's_stomach` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `head_on_back` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `head_on_head` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `head_on_table` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `heart_on_chest` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `helmet_over_eyes` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_another's_legs` | `LIKELY_CANDIDATE` | `SPECIAL_BODY_RELATION_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `holding_bass_guitar` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_cage` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_computer_mouse` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_go_stone` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_ice_cream_cone` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_leotard` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_own_legs_back` | `LIKELY_CANDIDATE` | `SPECIAL_BODY_RELATION_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `holding_ribbon_baton` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_sword_behind_back` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_unworn_scarf` | `LIKELY_CANDIDATE` | `GENERAL_ORDINARY_CLOTHING_STATE` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_vacuum_cleaner` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_with_tongue` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `implied_breast_milk` | `LIKELY_CANDIDATE` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `implied_strap-on` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `implied_tail_plug` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `ink_on_face` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `instrument_on_back` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `kujo_jotaro's_pose` | `LIKELY_CANDIDATE` | `GENERAL_NAMED_OR_CONTEXTUAL` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `leg_on_another's_leg` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `micro_shorts` | `LIKELY_CANDIDATE` | `SPECIAL_GARMENT_SUBTYPE` | `PLAUSIBLE_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `mole_under_mouth` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `neck_piercing` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `ofuda_between_fingers` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `ofuda_on_clothes` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `on_shoulder` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `other_pov` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `panties_around_thighs` | `LIKELY_CANDIDATE` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `paper_on_head` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `pokemon_on_shoulder` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `pov_cheek_grabbing_(meme)` | `LIKELY_CANDIDATE` | `GENERAL_NAMED_OR_CONTEXTUAL` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `pov_peephole` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `public_urination` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `qr_code_tattoo` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `rabbit_tattoo` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `removing_bra_under_shirt` | `LIKELY_CANDIDATE` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `scar_on_foot` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `see-through_apron` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `see-through_cardigan` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `see-through_curtains` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `see-through_hat` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `see-through_hood` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `see-through_pants` | `LIKELY_CANDIDATE` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `see-through_pelvic_curtain` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `see-through_raincoat` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `see-through_sarong` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `see-through_scarf` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `sitting_on_another's_back` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `sitting_on_lap` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `sitting_on_leg` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `snow_on_clothes` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `sonic_adventure_pose` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `spiral-only_eyes` | `LIKELY_CANDIDATE` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `standing_front_split` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `standing_on_three_legs` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `sword_over_shoulder` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `taker_pov` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `tattoo_sleeve` | `LIKELY_CANDIDATE` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `toy_sword` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `traffic_cone_on_head` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `unworn_boots` | `LIKELY_CANDIDATE` | `GENERAL_ORDINARY_CLOTHING_STATE` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `unworn_hat` | `LIKELY_CANDIDATE` | `GENERAL_ORDINARY_CLOTHING_STATE` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `unworn_lanyard` | `LIKELY_CANDIDATE` | `GENERAL_ORDINARY_CLOTHING_STATE` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `wet_leotard` | `LIKELY_CANDIDATE` | `GENERAL_ORDINARY_CLOTHING_STATE` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `whistle_around_neck` | `LIKELY_CANDIDATE` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `animal-themed_food` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `animal_ear_hood` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `anteater_tail` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `arrow_through_apple` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `arrow_through_heart` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `babydoll_lift` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `bandage_on_cheek` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `bandaid_on_cheek` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `bandeau_lift` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `bone_tail` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `braided_tail` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `bruise_on_knee` | `NEEDS_REVIEW` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `camel_tail` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `capelet_lift` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `carrot_on_stick` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `cat_tail` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `covered_knees` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `cream_on_body` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `creature_on_lap` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `dinosaur_tail` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `drawing_on_air` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `elephant_tail` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `eyewear_lift` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `female_admiral_(kancolle)_(cosplay)` | `NEEDS_REVIEW` | `GENERAL_NAMED_OR_CONTEXTUAL` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `fluffy_tail` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `furry_and_animal` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `gigantic_breasts` | `NEEDS_REVIEW` | `BOUNDARY_CONCEPT` | `BOUNDARY_REVIEW` | `NEEDS_REVIEW` | `P1` |
| `gradient_tail` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `hands_on_another's_knees` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `hanging_on` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_anchor` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_arrow` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_bell` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_binoculars` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_blade` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_bottle` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_bowl` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_candle` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_cane` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_chain` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_charm` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_chibi` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_cloth` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_cookie` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_eyeball` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_flyer` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_folder` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_gourd` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_halo` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_handcuffs` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_handkerchief` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_handlebar` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_headphones` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_hoe` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_ice` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_kite` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_kunai` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_ladder` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_lasso` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_macaron` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_marker` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_notepad` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_omikuji` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_painting` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_pan` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_pill` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_pliers` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_pole` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_portrait` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_quill` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_rabbit` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_racket` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_record` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_sash` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_scythe` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_sign` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_skull` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_snowman` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_soap` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_spoon` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_staff` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_stethoscope` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_thermometer` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_thermos` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_torpedo` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_utensil` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `holding_vial` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `implied_cheating_(relationship)` | `NEEDS_REVIEW` | `GENERAL_NAMED_OR_CONTEXTUAL` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `looking_through_scope` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `male_robin_(fire_emblem)_(cosplay)` | `NEEDS_REVIEW` | `GENERAL_NAMED_OR_CONTEXTUAL` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `marking_on_cheek` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `melting_tail` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `missing_tail` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `mixed_martial_arts` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `mole_on_collarbone` | `NEEDS_REVIEW` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `moose_tail` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `nightgown_lift` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `object_on_bulge` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `on_animal` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `on_top_of_pole` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `otter_tail` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `over-rim_eyewear` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `over_rad_squad!!_(project_sekai)` | `NEEDS_REVIEW` | `GENERAL_NAMED_OR_CONTEXTUAL` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `over_the_collar_(idolmaster)` | `NEEDS_REVIEW` | `GENERAL_NAMED_OR_CONTEXTUAL` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `paint_on_body` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `panther_tail` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `pantyshot_through_reflection` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `partially_open_shirt` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `pineapple_on_pizza` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `print_male_swimwear` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `rooster_tail` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `same-sex_bathing` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `scar_on_chin` | `NEEDS_REVIEW` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `shark_tail` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `side_chest_pose` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `snow_on_headwear` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `spiked_tail` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `spreading_own_ass` | `NEEDS_REVIEW` | `SPECIAL_BODY_RELATION_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P1` |
| `sweater_under_jacket` | `NEEDS_REVIEW` | `GENERAL_ORDINARY_CLOTHING_STATE` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `swinging_on_swing` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `swinging_on_web` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `tail_bow` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `tail_fondling` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `tube_top_pull` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |
| `wig_on_non-human` | `NEEDS_REVIEW` | `GENERAL_OTHER` | `GENERAL_ONLY` | `LIKELY_GENERAL_ONLY` | `P3` |

## v2 category spot samples

### `LIKELY_CANDIDATE` — 50 rows (deterministic sample)

| canonical | Stage A | Stage B | priority |
|---|---|---|---|
| `tattoo_between_breasts` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `see-through_sports_bra` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `gag_chinstrap` | `SPECIAL_BDSM_RESTRAINT` | `STRONG_SPECIAL_FIT` | `P0` |
| `hugging_own_legs` | `SPECIAL_BODY_RELATION_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `P1` |
| `between_breasts` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `blood_on_arm` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `P0` |
| `cloth_gag` | `SPECIAL_BDSM_RESTRAINT` | `STRONG_SPECIAL_FIT` | `P0` |
| `piercing_through_clothes` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `hand_grabbing_both_breasts` | `SPECIAL_BODY_RELATION_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `P1` |
| `spread_eagle_position` | `SPECIAL_NAMED_POSE` | `STRONG_SPECIAL_FIT` | `P0` |
| `implied_male_pregnancy` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `P0` |
| `hand_on_own_crotch` | `SPECIAL_BODY_RELATION_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `P1` |
| `pregnancy_halo` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `P0` |
| `head_between_thighs` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `presenting_own_ass` | `SPECIAL_BODY_RELATION_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `P1` |
| `bikini_bottom_lift` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `see-through_pantyhose` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `touching_another's_crotch` | `SPECIAL_BODY_RELATION_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `P1` |
| `sports_bra_peek` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `bikini_top_lift` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `panties_over_garter_belt` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `muzzle_gag` | `SPECIAL_BDSM_RESTRAINT` | `STRONG_SPECIAL_FIT` | `P0` |
| `breasts_squeezed_together` | `SPECIAL_BODY_RELATION_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `P1` |
| `through_clothes` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `blood_on_neck` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `P0` |
| `pantyhose_around_one_leg` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `holding_own_legs_back` | `SPECIAL_BODY_RELATION_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `P1` |
| `micro_bra` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `ass_visible_through_thighs` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `panties_over_leggings` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `mole_on_thigh` | `SPECIAL_INTIMATE_ADORNMENT_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `P1` |
| `implied_lactation` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `P0` |
| `spreading_own_ass` | `SPECIAL_BODY_RELATION_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `P1` |
| `bikini_under_skirt` | `SPECIAL_CLOTHING_BODY_RELATION` | `PLAUSIBLE_SPECIAL_FIT` | `P1` |
| `breast_tattoo` | `SPECIAL_INTIMATE_ADORNMENT_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `P1` |
| `blush_visible_through_clothes` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `panties_around_thighs` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `pantyhose_around_legs` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `grabbing_own_ass` | `SPECIAL_BODY_RELATION_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `P1` |
| `licking_breast` | `SPECIAL_BODY_RELATION_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `P1` |
| `imminent_breast_grab` | `SPECIAL_BODY_RELATION_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `P1` |
| `cumdrip_through_clothes` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `grabbing_another's_thighs` | `SPECIAL_BODY_RELATION_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `P1` |
| `swimsuit_over_clothes` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `scar_on_thigh` | `SPECIAL_INTIMATE_ADORNMENT_STATE` | `PLAUSIBLE_SPECIAL_FIT` | `P1` |
| `see-through_panties` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `arm_between_breasts` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `one_eye_covered` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `leg_lift` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |
| `breast_lift` | `SPECIAL_EXPOSURE_CLOTHING_STATE` | `STRONG_SPECIAL_FIT` | `P1` |

### `LIKELY_GENERAL_ONLY` — 50 rows (deterministic sample)

| canonical | Stage A | Stage B | priority |
|---|---|---|---|
| `country_lolita` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `removing_wig` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `black_bodice` | `GENERAL_APPEARANCE_SIZE_COLOR` | `GENERAL_ONLY` | `P3` |
| `thigh_corset` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `purple_mask` | `GENERAL_APPEARANCE_SIZE_COLOR` | `GENERAL_ONLY` | `P3` |
| `cupping_glass` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `draco_(constellation)` | `GENERAL_NAMED_OR_CONTEXTUAL` | `GENERAL_ONLY` | `P3` |
| `absurdly_long_tail` | `GENERAL_APPEARANCE_SIZE_COLOR` | `GENERAL_ONLY` | `P3` |
| `starter_pokemon_trio` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `holding_another's_waist` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `single_horizontal_stripe` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `orange_socks` | `GENERAL_APPEARANCE_SIZE_COLOR` | `GENERAL_ONLY` | `P3` |
| `fishnet_leggings` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `finger_frame_duo` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `P3` |
| `fanning_crotch` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `lace-trimmed_sailor_collar` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `mooring_bollard` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `cutting_mat` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `cane` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `piano` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `legskin` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `fogged_glasses` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `black_sweater_vest` | `GENERAL_APPEARANCE_SIZE_COLOR` | `GENERAL_ONLY` | `P3` |
| `poker_chip` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `adjusting_bow` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `band_uniform` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `cat_on_keyboard` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `face_chain` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `shared_cape` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `painttool_sai` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `alto_mare` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `winged_headphones` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `on_swing` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `partially_bordered` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `tailcoat` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `yellow_liquid` | `GENERAL_APPEARANCE_SIZE_COLOR` | `GENERAL_ONLY` | `P3` |
| `joker_(playing_card)` | `GENERAL_NAMED_OR_CONTEXTUAL` | `GENERAL_ONLY` | `P3` |
| `pot_on_head` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `P3` |
| `egg_sandwich` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `seal_(animal)` | `GENERAL_NAMED_OR_CONTEXTUAL` | `GENERAL_ONLY` | `P3` |
| `liquid_insides` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `kamiyama_high_school_uniform_(hyouka)` | `GENERAL_NAMED_OR_CONTEXTUAL` | `GENERAL_ONLY` | `P3` |
| `bandaid_on_thigh` | `GENERAL_OBJECT_OR_ACTION_PLACEMENT` | `GENERAL_ONLY` | `P3` |
| `military_medic` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `kitagawa_marin_(cosplay)` | `GENERAL_NAMED_OR_CONTEXTUAL` | `GENERAL_ONLY` | `P3` |
| `x_hat_ornament` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `very_long_robe` | `GENERAL_APPEARANCE_SIZE_COLOR` | `GENERAL_ONLY` | `P3` |
| `bar_phone` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `youtube_creator_award` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |
| `shin_ramyun` | `GENERAL_OTHER` | `GENERAL_ONLY` | `P3` |

### `POSSIBLE_DUPLICATE` — 4 rows (all available; population below 50)

| canonical | Stage A | Stage B | priority |
|---|---|---|---|
| `open_towel` | `SPECIAL_OVERLAP_BOUNDARY` | `POSSIBLE_DUPLICATE` | `P2` |
| `spread_ass` | `SPECIAL_OVERLAP_BOUNDARY` | `POSSIBLE_DUPLICATE` | `P2` |
| `wide_spread_legs` | `SPECIAL_OVERLAP_BOUNDARY` | `POSSIBLE_DUPLICATE` | `P2` |
| `no_bra` | `SPECIAL_OVERLAP_BOUNDARY` | `POSSIBLE_DUPLICATE` | `P2` |

### `NEEDS_REVIEW` — 9 rows (all available; population below 50)

| canonical | Stage A | Stage B | priority |
|---|---|---|---|
| `breast_rest` | `BOUNDARY_CONCEPT` | `BOUNDARY_REVIEW` | `P1` |
| `clothes_pull` | `BOUNDARY_CONCEPT` | `BOUNDARY_REVIEW` | `P1` |
| `sperm_cell` | `BOUNDARY_CONCEPT` | `BOUNDARY_REVIEW` | `P1` |
| `gigantic_breasts` | `BOUNDARY_CONCEPT` | `BOUNDARY_REVIEW` | `P1` |
| `no_pants` | `BOUNDARY_CONCEPT` | `BOUNDARY_REVIEW` | `P1` |
| `hand_on_own_thigh` | `BOUNDARY_CONCEPT` | `BOUNDARY_REVIEW` | `P1` |
| `clothes_lift` | `BOUNDARY_CONCEPT` | `BOUNDARY_REVIEW` | `P1` |
| `pregnancy_test` | `BOUNDARY_CONCEPT` | `BOUNDARY_REVIEW` | `P1` |
| `holding_pregnancy_test` | `BOUNDARY_CONCEPT` | `BOUNDARY_REVIEW` | `P1` |

## P0 additional spot-check

- P0 sample total: **46** (all available P0 rows; requested 100 where population permits)
- estimated false positives: **0 / 46 (0.0%)**
- This estimate is a conservative semantic spot-check against the Stage A/B family decision, not an independent population-wide human review.

| canonical | Stage A | Stage B | v2 | priority |
|---|---|---|---|---|
| `implied_male_pregnancy` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `lactating_into_container` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `blood_on_breasts` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `standing_doggystyle` | `SPECIAL_NAMED_POSE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `heart_butt_plug` | `SPECIAL_SEX_DEVICE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `blood_on_face` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `blood_on_feet` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `fake_pregnancy` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `blood_on_shoulder` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `blood_on_leg` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `blood_from_neck` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `gag_around_neck` | `SPECIAL_BDSM_RESTRAINT` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `forced_lactation` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `projectile_lactation` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `excessive_lactation` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `ovulation` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `blood_on_neck` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `blood_from_mouth` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `blood_on_back` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `male_pregnancy` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `implied_lactation` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `unworn_butt_plug` | `SPECIAL_SEX_DEVICE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `blood_on_mouth` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `muzzle_gag` | `SPECIAL_BDSM_RESTRAINT` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `male_lactation` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `pregnancy_halo` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `blood_on_arm` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `implied_pregnancy` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `gag_chinstrap` | `SPECIAL_BDSM_RESTRAINT` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `after_birth` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `leash_between_breasts` | `SPECIAL_BDSM_RESTRAINT` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `wraparound_tape_gag` | `SPECIAL_BDSM_RESTRAINT` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `holding_gag` | `SPECIAL_BDSM_RESTRAINT` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `explosion_gag` | `SPECIAL_BDSM_RESTRAINT` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `spread_eagle_position` | `SPECIAL_NAMED_POSE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `blood_in_mouth` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `cloth_gag` | `SPECIAL_BDSM_RESTRAINT` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `blood_on_clothes` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `blood_on_stomach` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `stuffed_gag` | `SPECIAL_BDSM_RESTRAINT` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `holding_butt_plug` | `SPECIAL_SEX_DEVICE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `multiple_pregnancy` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `blood_on_chest` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `blood_from_eyes` | `SPECIAL_R18G_BODY_STATE` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `pregnancy_mark` | `SPECIAL_REPRODUCTION_FLUID` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |
| `applying_gag` | `SPECIAL_BDSM_RESTRAINT` | `STRONG_SPECIAL_FIT` | `LIKELY_CANDIDATE` | `P0` |

## Existing 130-row calibration comparison

- effective review rows: **130**
- v2 calibration mismatches (including 12 out-of-input rows): **28**
- This is a secondary diagnostic only; v2 does not optimize against the same 130 rows.

| canonical | human | v2 | reason |
|---|---|---|---|
| `areola_slip` | `DUPLICATE_ALREADY_COVERED` | `OUTSIDE_INPUT` | `not in 29,021-row GENERAL_ONLY_GAP input` |
| `asymmetrical_docking` | `DUPLICATE_ALREADY_COVERED` | `OUTSIDE_INPUT` | `not in 29,021-row GENERAL_ONLY_GAP input` |
| `blood_on_hand` | `CANDIDATE` | `LIKELY_GENERAL_ONLY` | `ordinary hand/finger and non-intimate body interaction; no deep Special relation is established` |
| `cleavage_cutout` | `DUPLICATE_ALREADY_COVERED` | `OUTSIDE_INPUT` | `not in 29,021-row GENERAL_ONLY_GAP input` |
| `clothes_lift` | `CANDIDATE` | `NEEDS_REVIEW` | `meaning is specific but the Special-versus-General boundary needs human review` |
| `female_pubic_hair` | `DUPLICATE_ALREADY_COVERED` | `OUTSIDE_INPUT` | `not in 29,021-row GENERAL_ONLY_GAP input` |
| `hand_under_clothes` | `CANDIDATE` | `LIKELY_GENERAL_ONLY` | `ordinary hand/finger and non-intimate body interaction; no deep Special relation is established` |
| `holding_pregnancy_test` | `CANDIDATE` | `NEEDS_REVIEW` | `meaning is specific but the Special-versus-General boundary needs human review` |
| `huge_ass` | `CANDIDATE` | `LIKELY_GENERAL_ONLY` | `whole-tag meaning does not show a strong Special deep-discovery need` |
| `leash_in_mouth` | `CANDIDATE` | `LIKELY_GENERAL_ONLY` | `whole-tag meaning does not show a strong Special deep-discovery need` |
| `lifting_own_clothes` | `CANDIDATE` | `LIKELY_GENERAL_ONLY` | `whole-tag meaning does not show a strong Special deep-discovery need` |
| `male_pubic_hair` | `DUPLICATE_ALREADY_COVERED` | `OUTSIDE_INPUT` | `not in 29,021-row GENERAL_ONLY_GAP input` |
| `micro_pasties` | `DUPLICATE_ALREADY_COVERED` | `OUTSIDE_INPUT` | `not in 29,021-row GENERAL_ONLY_GAP input` |
| `mixed-sex_bathing` | `NEEDS_REVIEW` | `LIKELY_GENERAL_ONLY` | `whole-tag meaning does not show a strong Special deep-discovery need` |
| `necktie_between_breasts` | `CANDIDATE` | `LIKELY_GENERAL_ONLY` | `ordinary object or accessory placed at a body location; placement alone is General discovery` |
| `no_panties` | `DUPLICATE_ALREADY_COVERED` | `OUTSIDE_INPUT` | `not in 29,021-row GENERAL_ONLY_GAP input` |
| `oral_invitation` | `DUPLICATE_ALREADY_COVERED` | `OUTSIDE_INPUT` | `not in 29,021-row GENERAL_ONLY_GAP input` |
| `piledriver_(sex)` | `DUPLICATE_ALREADY_COVERED` | `OUTSIDE_INPUT` | `not in 29,021-row GENERAL_ONLY_GAP input` |
| `pov_crotch` | `CANDIDATE` | `LIKELY_GENERAL_ONLY` | `whole-tag meaning does not show a strong Special deep-discovery need` |
| `public_urination` | `CANDIDATE` | `LIKELY_GENERAL_ONLY` | `whole-tag meaning does not show a strong Special deep-discovery need` |
| `revealing_clothes` | `DUPLICATE_ALREADY_COVERED` | `OUTSIDE_INPUT` | `not in 29,021-row GENERAL_ONLY_GAP input` |
| `same-sex_bathing` | `NEEDS_REVIEW` | `LIKELY_GENERAL_ONLY` | `whole-tag meaning does not show a strong Special deep-discovery need` |
| `sex_from_behind` | `DUPLICATE_ALREADY_COVERED` | `OUTSIDE_INPUT` | `not in 29,021-row GENERAL_ONLY_GAP input` |
| `skindentation` | `CANDIDATE` | `LIKELY_GENERAL_ONLY` | `whole-tag meaning does not show a strong Special deep-discovery need` |
| `symmetrical_docking` | `DUPLICATE_ALREADY_COVERED` | `OUTSIDE_INPUT` | `not in 29,021-row GENERAL_ONLY_GAP input` |
| `thick_thighs` | `CANDIDATE` | `LIKELY_GENERAL_ONLY` | `whole-tag meaning does not show a strong Special deep-discovery need` |
| `thigh_gap` | `CANDIDATE` | `LIKELY_GENERAL_ONLY` | `whole-tag meaning does not show a strong Special deep-discovery need` |
| `thighhighs_under_boots` | `CANDIDATE` | `LIKELY_GENERAL_ONLY` | `ordinary garment state/layering lacks an intimate, sexual, or through-clothes discovery concept` |

## Logic changes from v1

1. Whole-tag semantic family is evaluated before any candidate status.
2. Ordinary object/body placement and ordinary standing/location controls are explicit negative gates.
3. `piercing`, `on`, `around`, `standing`, compound length, and nearest Special similarity are never sufficient evidence.
4. Strong positive families require semantic anchors: sexual relation, intimate body-site state, through-clothes/visibility state, BDSM/restraint, sex device/insertion, concrete fluid/reproductive state, R18G body state, or specialized pose.
5. Boundary concepts are sent to `NEEDS_REVIEW` instead of being promoted by structural resemblance.

## Guardrails

- v1 CSV, v1 summary, and v1 script remain unchanged.
- v2 is a prescreen only; no row is promoted into Special.
- `PRODUCTION_FILES_CHANGED=NO`
- `ISSUE70_MUTATED=NO`

Input source SHA-256: `912ab4f076ae97bb513b65b17aa16dddaf67a99f37e81311c67edd1a57c0a188`
